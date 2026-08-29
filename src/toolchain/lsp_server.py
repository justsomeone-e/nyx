import sys
import json
import os
import re
from typing import Dict, List, Optional, Any

_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

from src.core.lexer import Lexer
from src.core.parser import Parser
from src.core.type_checker import TypeChecker
from src.core.module_loader import ModuleLoader
from src.core.diagnostics import DiagnosticEmitter, DiagnosticError
from src.core.ast_nodes import FunctionDefNode, StructDefNode, TraitDefNode, VarDeclNode, ProgramNode

# Core language keywords and builtins for intelligent completion
KEYWORDS = [
    "fn", "var", "val", "return", "if", "else", "while", "for", "in",
    "struct", "trait", "impl", "import", "from", "as", "test",
    "match", "unsafe", "Ok", "Err", "null", "true", "false"
]
BUILTINS = [
    {"label": "print", "detail": "fn print(...args)", "doc": "Core language output function"},
    {"label": "input", "detail": "fn input(prompt: string) -> string", "doc": "Reads a line from standard input"},
    {"label": "addr", "detail": "unsafe fn addr(var_name: string) -> int", "doc": "Returns variable memory address"},
    {"label": "peek", "detail": "unsafe fn peek(addr: int) -> int", "doc": "Direct memory read"},
    {"label": "memdump", "detail": "unsafe fn memdump(addr: int, count: int)", "doc": "Dumps memory buffer"}
]
TYPES = ["int", "float", "string", "bool", "Array", "Result", "Option", "void"]

class NyxuageServer:
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
        path = uri.replace("file:///", "").replace("file://", "")
        if os.name == 'nt' and path.startswith("/") and len(path) > 2 and path[2] == ':':
            path = path[1:]
        return os.path.normpath(path)

    def validate_document(self, uri: str, text: str):
        diagnostics = []
        filepath = self.get_fs_path(uri)
        orig_exit = DiagnosticEmitter.EXIT_ON_ERROR
        DiagnosticEmitter.EXIT_ON_ERROR = False

        try:
            base_dir = os.path.dirname(os.path.abspath(filepath)) if filepath else os.getcwd()
            loader = ModuleLoader(base_dir=base_dir)
            ast = loader.load_program(filepath, text)
            self.parsed_asts[uri] = ast
            TypeChecker(ast, filepath, text).check()
        except DiagnosticError as de:
            line = max(0, de.line - 1)
            col = max(0, de.col - 1)
            diagnostics.append({
                "range": {
                    "start": {"line": line, "character": col},
                    "end": {"line": line, "character": col + 8}
                },
                "severity": 1,
                "code": de.code,
                "source": "nyx",
                "message": f"[{de.code}] {de.title}"
            })
        except Exception as e:
            err_str = str(e)
            m = re.search(r':(\d+):(\d+)', err_str)
            line = max(0, int(m.group(1)) - 1) if m else 0
            col = max(0, int(m.group(2)) - 1) if m else 0
            diagnostics.append({
                "range": {
                    "start": {"line": line, "character": col},
                    "end": {"line": line, "character": col + 8}
                },
                "severity": 1,
                "source": "nyx",
                "message": err_str
            })
        finally:
            DiagnosticEmitter.EXIT_ON_ERROR = orig_exit

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
            t = getattr(p.type_node, "name", str(p.type_node)) if getattr(p, "type_node", None) else ""
            return f"{p.name}: {t}" if t else p.name
        return str(p)

    def handle_completion(self, uri: str, pos: dict) -> list:
        items = []

        # 1. Directives
        items.append({"label": "#target", "kind": 15, "detail": "#target <hecpp|heasm|hereact|hejs|hers|hepy|hewasm>", "documentation": "Sets compiler backend target"})
        items.append({"label": "#native include", "kind": 15, "detail": "#native include <header>", "documentation": "Includes C/C++ native header"})
        items.append({"label": "#native link", "kind": 15, "detail": '#native link "lib"', "documentation": "Links system library"})
        items.append({"label": "#native raw", "kind": 15, "detail": "#native raw { ... }", "documentation": "Inline C++ code block"})
        items.append({"label": "#native use", "kind": 15, "detail": '#native use "namespace"', "documentation": "Using namespace directive"})

        # 1. Keywords
        for kw in KEYWORDS:
            items.append({"label": kw, "kind": 14, "detail": "Keyword"})

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
                    try:
                        line_no = max(0, int(getattr(s, "line", 1)) - 1)
                    except:
                        line_no = 0
                    try:
                        col_no = max(0, int(getattr(s, "col", 1)) - 1)
                    except:
                        col_no = 0
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

if __name__ == "__main__":
    NyxuageServer().run()
