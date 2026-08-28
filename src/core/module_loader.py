import os
import sys
from typing import Dict, List, Set, Optional, Tuple

_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

from src.core.lexer import Lexer
from src.core.parser import Parser
from src.core.ast_nodes import ProgramNode, ImportNode, FunctionDefNode, StructDefNode, TraitDefNode, ImplBlockNode, TypeAliasNode, ASTNode
from src.core.diagnostics import DiagnosticEmitter

class ModuleLoader:
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir or os.getcwd()
        self.stdlib_dir = os.path.join(_root_dir, "src", "stdlib")
        self.loaded_modules: Dict[str, ProgramNode] = {}
        self.import_stack: List[str] = []
        self.symbol_origins: Dict[str, str] = {}
        self.collected_declarations: List[ASTNode] = []

    def resolve_module_path(self, import_path: str, current_file: str) -> Tuple[Optional[str], List[str]]:
        """Resolves module path to an absolute filesystem path and returns all searched candidate paths."""
        searched = []
        
        # 1. Standard Library: std/math, std::math, std/str
        if import_path.startswith("std/") or import_path.startswith("std::"):
            submodule = import_path.replace("std::", "").replace("std/", "")
            for ext in (".nyx", ".he", ""):
                base = submodule if submodule.endswith(ext) else submodule + ext
                cand = os.path.join(self.stdlib_dir, base)
                if cand not in searched: searched.append(cand)
                if os.path.exists(cand):
                    return cand, searched
            return None, searched

        # 2. Local relative import: ./utils, ../math, helper.nyx
        curr_dir = os.path.dirname(os.path.abspath(current_file)) if current_file and current_file != "<memory>" else self.base_dir
        cand1 = os.path.normpath(os.path.join(curr_dir, import_path))
        for ext in (".nyx", ".he", ""):
            cand_f = cand1 if cand1.endswith(ext) else cand1 + ext
            if cand_f not in searched: searched.append(cand_f)
            if os.path.exists(cand_f):
                return cand_f, searched
        for idx in ("index.nyx", "index.he"):
            cand_idx = os.path.join(cand1, idx)
            if cand_idx not in searched: searched.append(cand_idx)
            if os.path.exists(cand_idx):
                return cand_idx, searched
            
        return None, searched

    def load_program(self, root_filepath: str, source: Optional[str] = None) -> ProgramNode:
        """Loads root program and transitively resolves all imported modules."""
        abs_root = os.path.abspath(root_filepath) if root_filepath != "<memory>" else "<memory>"
        self.import_stack = [abs_root]
        self.symbol_origins = {}
        self.collected_declarations = []
        
        if source is None:
            with open(abs_root, "r", encoding="utf-8") as f:
                source = f.read()

        tokens = Lexer(source, root_filepath).tokenize()
        root_ast = Parser(tokens, source, root_filepath).parse()
        
        root_stmts: List[ASTNode] = []

        # Process imports in root program
        for stmt in root_ast.statements:
            if isinstance(stmt, ImportNode):
                self._process_import(stmt, abs_root, source)
            else:
                root_stmts.append(stmt)
                
        # Merge all collected imported declarations before root statements
        root_ast.statements = self.collected_declarations + root_stmts
        return root_ast

    def _process_import(self, imp: ImportNode, parent_file: str, parent_source: str):
        target_path, searched = self.resolve_module_path(imp.path, parent_file)
        if not target_path:
            DiagnosticEmitter.emit_error(
                parent_file, parent_source, imp.line, imp.col,
                "E1301", f"Module Not Found: '{imp.path}'",
                length=len(imp.path) + 2,
                searched=searched,
                help_msg="Verify file location and spelling."
            )
            return

        # Circular import check
        if target_path in self.import_stack:
            cycle = " -> ".join(self.import_stack + [target_path])
            DiagnosticEmitter.emit_error(
                parent_file, parent_source, imp.line, imp.col,
                "E1300", "Circular Module Import Detected",
                length=len(imp.path) + 2,
                help_msg=f"Break the circular dependency cycle: {cycle}"
            )
            return

        # If module already parsed and cached, we still verify symbols
        if target_path in self.loaded_modules:
            module_ast = self.loaded_modules[target_path]
        else:
            self.import_stack.append(target_path)
            with open(target_path, "r", encoding="utf-8") as f:
                mod_src = f.read()
                
            tokens = Lexer(mod_src, target_path).tokenize()
            module_ast = Parser(tokens, mod_src, target_path).parse()
            
            # Transitively resolve nested imports first (Topological Ordering)
            for s in module_ast.statements:
                if isinstance(s, ImportNode):
                    self._process_import(s, target_path, mod_src)
                    
            self.loaded_modules[target_path] = module_ast
            self.import_stack.pop()

        # Collect exported declarations from this module
        for s in module_ast.statements:
            if isinstance(s, (FunctionDefNode, StructDefNode, TraitDefNode, ImplBlockNode, TypeAliasNode)):
                sym_name = getattr(s, "name", None)
                if not sym_name:
                    continue

                # Selective import filter: import { abs_val } from "std/math"
                if imp.symbols and sym_name not in imp.symbols:
                    continue

                origin = getattr(s, "_origin_module", target_path)
                s._origin_module = origin

                # Ambiguous symbol collision check
                if sym_name in self.symbol_origins and self.symbol_origins[sym_name] != origin:
                    prev_origin = self.symbol_origins[sym_name]
                    DiagnosticEmitter.emit_error(
                        parent_file, parent_source, imp.line, imp.col,
                        "E1302", f"Ambiguous Symbol Collision: '{sym_name}'",
                        length=len(imp.path) + 2,
                        note=f"'{sym_name}' is exported by both '{os.path.basename(prev_origin)}' and '{os.path.basename(origin)}'.",
                        help_msg="Use selective import: import { specific_symbol } from \"...\" to resolve ambiguity."
                    )
                elif sym_name not in self.symbol_origins:
                    self.symbol_origins[sym_name] = origin
                    self.collected_declarations.append(s)
