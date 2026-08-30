import sys
import json
import os
from typing import Dict, List, Optional, Any
from urllib.parse import unquote, urlparse

_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

from src.api import NyxCompiler
from src.core.backend_capabilities import BACKENDS
from src.core.ast_nodes import FunctionDefNode, StructDefNode, TraitDefNode, VarDeclNode, ProgramNode
from src.core.language_surface import (
    BUILTIN_NAMES,
    EXPERIMENTAL_KEYWORDS,
    STABLE_KEYWORDS,
    TYPE_NAMES,
)

# Public aliases are retained for clients/tests that import this module.
KEYWORDS = list(STABLE_KEYWORDS)
TYPES = list(TYPE_NAMES)

_BUILTIN_SIGNATURES = {
    "print": "fn print(...args) -> void",
    "input": "fn input(prompt: string = \"\") -> string",
    "addr": "unsafe fn addr(value) -> uintptr",
    "peek": "unsafe fn peek(address: uintptr) -> int",
    "memdump": "unsafe fn memdump(address: uintptr, count: int = 16) -> void",
    "channel": "fn channel<T>() -> Channel<T>",
    "Ok": "fn Ok<T>(value: T) -> Result<T, string>",
    "Err": "fn Err<E>(error: E) -> Result<int, E>",
    "len": "fn len<T>(value: T) -> int",
    "to_string": "fn to_string<T>(value: T) -> string",
    "to_int": "fn to_int(value: string) -> int",
    "contains": "fn contains(value: string, part: string) -> bool",
    "is_number": "fn is_number(value: string) -> bool",
    "delay_ms": "fn delay_ms(milliseconds: int) -> void",
}
_BUILTIN_DOCS = {
    "print": "Core language output function",
    "input": "Reads a line from standard input",
    "addr": "Returns the address of a value inside an unsafe boundary",
    "peek": "Reads an integer from a raw address inside an unsafe boundary",
    "memdump": "Prints bytes from a raw address inside an unsafe boundary",
}
BUILTINS = [
    {
        "label": name,
        "detail": _BUILTIN_SIGNATURES[name],
        "doc": _BUILTIN_DOCS.get(name, "Nyx core runtime function"),
    }
    for name in BUILTIN_NAMES
]

class LanguageServer:
    def __init__(self):
        self.documents: Dict[str, str] = {}
        self.parsed_asts: Dict[str, ProgramNode] = {}

    def read_message(self) -> Optional[dict]:
        headers = {}
        while True:
            line = sys.stdin.buffer.readline().decode('utf-8')
            if not line or line == '\r\n' or line == '\n':
                break
            if ':' in line:
                k, v = line.split(':', 1)
                headers[k.strip().lower()] = v.strip()

        if 'content-length' not in headers:
            return None

        length = int(headers['content-length'])
        body = sys.stdin.buffer.read(length).decode('utf-8')
        return json.loads(body)

    def send_response(self, response_dict: dict):
        body = json.dumps(response_dict)
        header = f"Content-Length: {len(body.encode('utf-8'))}\r\nContent-Type: application/json-rpc; charset=utf-8\r\n\r\n"
        sys.stdout.buffer.write(header.encode('utf-8'))
        sys.stdout.buffer.write(body.encode('utf-8'))
        sys.stdout.buffer.flush()

    def send_diagnostics(self, uri: str, diagnostics: list):
        self.send_response({
            "jsonrpc": "2.0",
            "method": "textDocument/publishDiagnostics",
            "params": {
                "uri": uri,
                "diagnostics": diagnostics
            }
        })

    def get_fs_path(self, uri: str) -> str:
        parsed = urlparse(uri)
        path = unquote(parsed.path) if parsed.scheme == "file" else uri
        if parsed.netloc:
            path = f"//{parsed.netloc}{path}"
        if os.name == 'nt' and path.startswith("/") and len(path) > 2 and path[2] == ':':
            path = path[1:]
        return os.path.normpath(path)

    def validate_document(self, uri: str, text: str):
        filepath = self.get_fs_path(uri)
        base_dir = os.path.dirname(os.path.abspath(filepath)) if filepath else os.getcwd()
        result = NyxCompiler(base_dir).check_source(text, filename=filepath)
        diagnostics = []
        if result.success and result.ast is not None:
            self.parsed_asts[uri] = result.ast
        else:
            self.parsed_asts.pop(uri, None)
            for diagnostic in result.diagnostics:
                line = max(0, diagnostic.line - 1)
                col = max(0, diagnostic.column - 1)
                diagnostics.append({
                    "range": {
                        "start": {"line": line, "character": col},
                        "end": {"line": line, "character": col + diagnostic.length}
                    },
                    "severity": 1,
                    "code": diagnostic.code,
                    "source": "nyx",
                    "message": f"[{diagnostic.code}] {diagnostic.message}"
                })

        self.send_diagnostics(uri, diagnostics)

    def get_word_at_position(self, text: str, line_idx: int, char_idx: int) -> str:
        lines = text.splitlines()
        if line_idx >= len(lines):
            return ""
        line = lines[line_idx]
        if char_idx >= len(line):
            char_idx = len(line) - 1
        if char_idx < 0:
            return ""

        # Find word boundaries
        start = char_idx
        while start > 0 and (line[start - 1].isalnum() or line[start - 1] == '_'):
            start -= 1
        end = char_idx
        while end < len(line) and (line[end].isalnum() or line[end] == '_'):
            end += 1
        return line[start:end]

    def handle_hover(self, uri: str, pos: dict) -> Optional[dict]:
        text = self.documents.get(uri, "")
        word = self.get_word_at_position(text, pos.get("line", 0), pos.get("character", 0))
        if not word:
            return None

        # Check builtins
        for b in BUILTINS:
            if b["label"] == word:
                return {
                    "contents": {
                        "kind": "markdown",
                        "value": f"```nyx\n{b['detail']}\n```\n\n{b['doc']}"
                    }
                }

        # Check types
        if word in TYPES:
            return {
                "contents": {
                    "kind": "markdown",
                    "value": f"```nyx\ntype {word}\n```\n\nNyx primitive/built-in type."
                }
            }

        # Search AST declarations
        ast = self.parsed_asts.get(uri)
        if ast:
            for s in ast.statements:
                if isinstance(s, FunctionDefNode) and s.name == word:
                    params_s = ", ".join(self._format_param(p) for p in s.params)
                    ret_s = f" -> {s.return_type}" if s.return_type else ""
                    return {
                        "contents": {
                            "kind": "markdown",
                            "value": f"```nyx\nfn {s.name}({params_s}){ret_s}\n```"
                        }
                    }
                elif isinstance(s, StructDefNode) and s.name == word:
                    fields_s = ", ".join(self._format_param(f) for f in s.fields)
                    return {
                        "contents": {
                            "kind": "markdown",
                            "value": f"```nyx\nstruct {s.name} {{ {fields_s} }}\n```"
                        }
                    }

        return None

    def _format_param(self, p: Any) -> str:
        if isinstance(p, tuple):
            return f"{p[0]}: {p[1]}" if len(p) > 1 and p[1] else str(p[0])
        if hasattr(p, "name"):
            type_node = getattr(p, "type_annot", None) or getattr(p, "type_node", None)
            t = getattr(type_node, "name", str(type_node)) if type_node else ""
            return f"{p.name}: {t}" if t else p.name
        return str(p)

    def handle_completion(self, uri: str, pos: dict) -> list:
        items = []

        # 1. Directives
        target_names = "|".join(BACKENDS)
        items.append({"label": "#target", "kind": 15, "detail": f"#target <{target_names}>", "documentation": "Sets compiler backend target"})
        items.append({"label": "#native include", "kind": 15, "detail": "#native include <header>", "documentation": "Includes C/C++ native header"})
        items.append({"label": "#native link", "kind": 15, "detail": '#native link "lib"', "documentation": "Links system library"})
        items.append({"label": "#native raw", "kind": 15, "detail": "#native raw { ... }", "documentation": "Inline C++ code block"})
        items.append({"label": "#native use", "kind": 15, "detail": '#native use "namespace"', "documentation": "Using namespace directive"})

        # 1. Keywords
        for kw in KEYWORDS:
            items.append({"label": kw, "kind": 14, "detail": "Nyx stable keyword"})
        for kw in EXPERIMENTAL_KEYWORDS:
            items.append({
                "label": kw,
                "kind": 14,
                "detail": "Nyx experimental keyword",
                "documentation": "Parsed by the frontend; cross-target semantics are not stable yet.",
            })

        # 2. Builtins
        for b in BUILTINS:
            items.append({"label": b["label"], "kind": 3, "detail": b["detail"], "documentation": b["doc"]})

        # 3. Types
        for t in TYPES:
            items.append({"label": t, "kind": 7, "detail": "Type"})

        # 4. AST Functions and Structs (including imported ones)
        ast = self.parsed_asts.get(uri)
        if ast:
            for s in ast.statements:
                if isinstance(s, FunctionDefNode):
                    params_s = ", ".join(self._format_param(p) for p in s.params)
                    ret_s = f" -> {s.return_type}" if s.return_type else ""
                    items.append({
                        "label": s.name,
                        "kind": 3, # Function
                        "detail": f"fn {s.name}({params_s}){ret_s}",
                        "documentation": f"Declared in {getattr(s, '_origin_module', 'local file')}"
                    })
                elif isinstance(s, StructDefNode):
                    items.append({
                        "label": s.name,
                        "kind": 22, # Struct
                        "detail": f"struct {s.name}",
                        "documentation": f"Declared in {getattr(s, '_origin_module', 'local file')}"
                    })

        return items

    def handle_definition(self, uri: str, pos: dict) -> Optional[dict]:
        text = self.documents.get(uri, "")
        word = self.get_word_at_position(text, pos.get("line", 0), pos.get("character", 0))
        if not word:
            return None

        ast = self.parsed_asts.get(uri)
        if ast:
            for s in ast.statements:
                if isinstance(s, (FunctionDefNode, StructDefNode, TraitDefNode)) and getattr(s, "name", None) == word:
                    target_file = getattr(s, "_origin_module", self.get_fs_path(uri))
                    target_uri = f"file:///{target_file.replace(os.sep, '/')}"
                    line_no = max(0, getattr(s, "line", 1) - 1)
                    col_no = max(0, getattr(s, "col", 1) - 1)
                    return {
                        "uri": target_uri,
                        "range": {
                            "start": {"line": line_no, "character": col_no},
                            "end": {"line": line_no, "character": col_no + len(word)}
                        }
                    }

        return None

    def run(self):
        while True:
            msg = self.read_message()
            if not msg:
                break

            method = msg.get("method")
            msg_id = msg.get("id")
            params = msg.get("params", {})

            if method == "initialize":
                self.send_response({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "capabilities": {
                            "textDocumentSync": 1,
                            "hoverProvider": True,
                            "completionProvider": {
                                "resolveProvider": False,
                                "triggerCharacters": [".", ":", ">", "\"", "{", "#", " ", "<", "/"]
                            },
                            "definitionProvider": True
                        }
                    }
                })
            elif method == "textDocument/didOpen":
                doc = params.get("textDocument", {})
                uri = doc.get("uri")
                text = doc.get("text", "")
                self.documents[uri] = text
                self.validate_document(uri, text)
            elif method == "textDocument/didChange":
                doc = params.get("textDocument", {})
                uri = doc.get("uri")
                changes = params.get("contentChanges", [])
                if changes:
                    text = changes[-1].get("text", "")
                    self.documents[uri] = text
                    self.validate_document(uri, text)
            elif method == "textDocument/hover":
                doc = params.get("textDocument", {})
                pos = params.get("position", {})
                hover_res = self.handle_hover(doc.get("uri", ""), pos)
                self.send_response({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": hover_res
                })
            elif method == "textDocument/completion":
                doc = params.get("textDocument", {})
                pos = params.get("position", {})
                comp_items = self.handle_completion(doc.get("uri", ""), pos)
                self.send_response({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": comp_items
                })
            elif method == "textDocument/definition":
                doc = params.get("textDocument", {})
                pos = params.get("position", {})
                def_res = self.handle_definition(doc.get("uri", ""), pos)
                self.send_response({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": def_res
                })
            elif method == "shutdown":
                self.send_response({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": None
                })
            elif method == "exit":
                sys.exit(0)

# Backwards compatibility for integrations that imported the original typo.
NyxuageServer = LanguageServer


if __name__ == "__main__":
    LanguageServer().run()
