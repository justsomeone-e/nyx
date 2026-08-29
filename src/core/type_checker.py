from typing import Dict, List, Optional, Any, Set
import sys
from .ast_nodes import (
    ASTNode, ProgramNode, NumberNode, StringNode, BooleanNode, NullNode,
    IdentifierNode, BinaryOpNode, UnaryOpNode, NullCoalesceNode, MemberAccessNode,
    IndexAccessNode, ArrayNode, LambdaNode, FunctionCallNode, VarDeclNode,
    AssignNode, TypeAliasNode, StructDefNode, TraitDefNode, ImplBlockNode,
    EnumDefNode, UnsafeBlockNode, SpawnNode, TestBlockNode, AssertNode,
    FunctionDefNode, MatchNode, TryCatchNode, IfNode, WhileNode, ForNode,
    ReturnNode, BreakNode, ContinueNode, TypeNode, NativeIncludeNode,
    NativeLinkNode, NativeRawNode, NativeUseNode, ExternFnDeclNode,
    DeferNode, GuardNode
)
from .diagnostics import DiagnosticEmitter

class TypeChecker:
    def __init__(self, ast: ProgramNode, filepath: str = '<anonymous>', source: str = ''):
        self.ast = ast
        self.filepath = filepath
        self.source = source
        self.scopes: List[Dict[str, str]] = [{}]
        self.struct_defs: Dict[str, Dict[str, str]] = {}
        self.func_defs: Dict[str, Dict[str, Any]] = {}
        self.is_inside_unsafe = False
        self.current_return_type: Optional[str] = None
        
        # Prepopulate builtin runtime functions
        self.builtins = {
            'print': 'void', 'input': 'string', 'to_string': 'string',
            'to_int': 'int', 'contains': 'bool', 'is_number': 'bool',
            'addr': 'uintptr', 'peek': 'uintptr', 'memdump': 'void',
            'delay_ms': 'void', 'channel': 'Channel', 'Ok': 'Result',
            'Err': 'Result', 'len': 'int'
        }
        for b, t in self.builtins.items():
            self.scopes[0][b] = t

    def current_scope(self) -> Dict[str, str]:
        return self.scopes[-1]

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()

    def lookup(self, name: str) -> Optional[str]:
        for s in reversed(self.scopes):
            if name in s:
                return s[name]
        return None

    def declare(self, name: str, type_name: str):
        self.current_scope()[name] = type_name

    def is_type_compatible(self, type_node: Optional[TypeNode], actual: str) -> bool:
        if not type_node or actual in ('any', None):
            return True
        if type_node.is_optional and actual == 'null':
            return True
        # Optional types accept their base type: int? accepts int
        if type_node.is_optional:
            base_name = type_node.name
            if self.is_compatible(base_name, actual):
                return True
        expected_str = str(type_node)
        return self.is_compatible(expected_str, actual)

    def is_compatible(self, expected: str, actual: str) -> bool:
        if expected in ('any', None) or actual in ('any', None):
            return True
        if expected == actual:
            return True
        # Strip optional suffix for base type comparison
        exp_base = expected.rstrip('?')
        act_base = actual.rstrip('?')
        if exp_base == act_base:
            return True
        # Pointer compatibility (*void can accept any *T or vice versa)
        if exp_base.startswith('*') and act_base.startswith('*'):
            return True
        # int can widen to float
        if exp_base == 'float' and act_base == 'int':
            return True
        # Function pointer / callback compatibility
        if (exp_base.startswith('fn(') or exp_base.startswith('fn->') or exp_base.startswith('function')) and (act_base.startswith('fn(') or act_base.startswith('fn->') or act_base.startswith('function')):
            exp_ret = exp_base.split('->')[-1].strip() if '->' in exp_base else 'any'
            act_ret = act_base.split('->')[-1].strip() if '->' in act_base else 'any'
            return self.is_compatible(exp_ret, act_ret)
        # Generic prefix compatibility: Result<T, E> matches Result, Array<T> matches Array
        if (exp_base.startswith('Result') and act_base.startswith('Result')) or (exp_base.startswith('Array') and act_base.startswith('Array')):
            return True
        # null compatibility with Option / Nullable types
        if actual == 'null' and ('?' in expected or 'Option' in expected):
            return True
        return False

    def check(self):
        # 1st Pass: Register all Structs & Functions
        for stmt in self.ast.statements:
            if isinstance(stmt, StructDefNode):
                fields = {}
                for f in stmt.fields:
                    f_type = f.type_annot.name if f.type_annot else 'any'
                    fields[f.name] = f_type
                self.struct_defs[stmt.name] = fields
                self.declare(stmt.name, stmt.name)
            elif isinstance(stmt, FunctionDefNode):
                ret_t = stmt.return_type.name if stmt.return_type else 'any'
                params = [(p.name, p.type_annot.name if p.type_annot else 'any') for p in stmt.params]
                self.func_defs[stmt.name] = {'ret': ret_t, 'params': params}
                self.declare(stmt.name, f'fn->{ret_t}')
            elif isinstance(stmt, ExternFnDeclNode):
                ret_t = str(stmt.return_type) if stmt.return_type else 'void'
                params = [(p.name, str(p.type_annot) if p.type_annot else 'any') for p in stmt.params]
                self.func_defs[stmt.name] = {'ret': ret_t, 'params': params, 'is_extern': True}
                self.declare(stmt.name, f'fn->{ret_t}')

        # 2nd Pass: Full Semantic Analysis & Type Inference
        for stmt in self.ast.statements:
            self.visit(stmt)

    def visit(self, node: Optional[ASTNode]):
        if not node:
            return

        if isinstance(node, (NativeIncludeNode, NativeLinkNode, NativeRawNode, NativeUseNode, ExternFnDeclNode)):
            return

        if isinstance(node, VarDeclNode):
            self.visit(node.expr)
            val_type = self.infer_type(node.expr)
            if node.type_annot:
                if not self.is_type_compatible(node.type_annot, val_type):
                    declared_name = f"{node.type_annot.name}?" if node.type_annot.is_optional else node.type_annot.name
                    DiagnosticEmitter.emit_error(
                        self.filepath, self.source, node.line, node.col,
                        "E2001", f"Type mismatch in variable declaration '{node.name}'",
                        expected=declared_name,
                        found=val_type,
                        help_msg=f"Cannot assign value of type '{val_type}' to variable '{node.name}' of type '{declared_name}'."
                    )
                self.declare(node.name, node.type_annot.name)
                node.inferred_type = node.type_annot.name
            else:
                self.declare(node.name, val_type)
                node.inferred_type = val_type

        elif isinstance(node, AssignNode):
            val_type = self.infer_type(node.expr)
            if isinstance(node.target, IdentifierNode):
                existing = self.lookup(node.target.name)
                if existing and not self.is_compatible(existing, val_type):
                    DiagnosticEmitter.emit_error(
                        self.filepath, self.source, node.line, node.col,
                        "E2002", f"Type mismatch in assignment to '{node.target.name}'",
                        expected=existing,
                        found=val_type,
                        help_msg=f"Cannot assign value of type '{val_type}' to variable '{node.target.name}' of type '{existing}'."
                    )
                elif not existing:
                    self.declare(node.target.name, val_type)
            self.visit(node.target)
            self.visit(node.expr)

        elif isinstance(node, FunctionDefNode):
            self.enter_scope()
            prev_ret = self.current_return_type
            self.current_return_type = str(node.return_type) if node.return_type else None
            for p in node.params:
                p_type = str(p.type_annot) if p.type_annot else 'any'
                self.declare(p.name, p_type)
            for s in node.body:
                self.visit(s)
            self.current_return_type = prev_ret
            self.exit_scope()

        elif isinstance(node, ReturnNode):
            if node.expr:
                ret_val_type = self.infer_type(node.expr)
                if self.current_return_type and not self.is_compatible(self.current_return_type, ret_val_type):
                    DiagnosticEmitter.emit_error(
                        self.filepath, self.source, node.line, node.col,
                        "E2004", f"Return type mismatch in function",
                        expected=self.current_return_type,
                        found=ret_val_type,
                        help_msg=f"Function was declared with return type '{self.current_return_type}', but returns a value of type '{ret_val_type}'."
                    )

        elif isinstance(node, StructDefNode):
            pass

        elif isinstance(node, UnsafeBlockNode):
            prev = self.is_inside_unsafe
            self.is_inside_unsafe = True
            self.enter_scope()
            for s in node.body:
                self.visit(s)
            self.exit_scope()
            self.is_inside_unsafe = prev

        elif isinstance(node, DeferNode):
            self.visit(node.expr)

        elif isinstance(node, GuardNode):
            self.infer_type(node.condition)
            self.enter_scope()
            for s in node.else_body: self.visit(s)
            self.exit_scope()

        elif isinstance(node, IfNode):
            self.infer_type(node.condition)
            self.enter_scope()
            for s in node.then_branch: self.visit(s)
            self.exit_scope()
            for cond, branch in node.elif_branches:
                self.infer_type(cond)
                self.enter_scope()
                for s in branch: self.visit(s)
                self.exit_scope()
            if node.else_branch:
                self.enter_scope()
                for s in node.else_branch: self.visit(s)
                self.exit_scope()

        elif isinstance(node, WhileNode):
            self.infer_type(node.condition)
            self.enter_scope()
            for s in node.body: self.visit(s)
            self.exit_scope()

        elif isinstance(node, ForNode):
            self.enter_scope()
            if node.collection_expr:
                c_type = self.infer_type(node.collection_expr)
                elem_type = c_type.replace('Array<', '').replace('>', '') if 'Array<' in c_type else 'any'
                self.declare(node.var_name, elem_type)
            else:
                self.declare(node.var_name, 'int')
            for s in node.body: self.visit(s)
            self.exit_scope()

        elif isinstance(node, MatchNode):
            self.infer_type(node.expr)
            for pat, stmt in node.cases:
                self.enter_scope()
                self.visit(stmt)
                self.exit_scope()

        elif isinstance(node, TryCatchNode):
            self.enter_scope()
            for s in node.try_body: self.visit(s)
            self.exit_scope()
            self.enter_scope()
            self.declare(node.err_name, 'Exception')
            for s in node.catch_body: self.visit(s)
            self.exit_scope()

        elif isinstance(node, FunctionCallNode):
            if node.callee in ('peek', 'memdump') and not self.is_inside_unsafe:
                DiagnosticEmitter.emit_error(
                    self.filepath, self.source, node.line, node.col,
                    'E1050', f'Unsafe memory operation \'{node.callee}()\' called outside of unsafe block',
                    expected='unsafe { ... } block',
                    found='safe context',
                    help_msg='Wrap raw pointer dereferencing and memory inspections inside \'unsafe { ... }\'.'
                )
            
            # Check argument types if function is known
            if node.callee in self.func_defs:
                param_specs = self.func_defs[node.callee]['params']
                if len(node.args) != len(param_specs):
                    DiagnosticEmitter.emit_error(
                        self.filepath, self.source, node.line, node.col,
                        "E2007", f"Function '{node.callee}' expected {len(param_specs)} arguments, but got {len(node.args)}",
                        expected=f"{len(param_specs)} arguments",
                        found=f"{len(node.args)} arguments",
                        help_msg=f"Provide exactly {len(param_specs)} arguments to '{node.callee}()'."
                    )
                for idx, arg in enumerate(node.args):
                    if idx < len(param_specs):
                        p_name, p_type = param_specs[idx]
                        arg_type = self.infer_type(arg)
                        if not self.is_compatible(p_type, arg_type):
                            DiagnosticEmitter.emit_error(
                                self.filepath, self.source, arg.line, arg.col,
                                "E2003", f"Argument type mismatch for parameter '{p_name}' in call to '{node.callee}()'",
                                expected=p_type,
                                found=arg_type,
                                help_msg=f"Function '{node.callee}' expects type '{p_type}' for argument '{p_name}', but received '{arg_type}'."
                            )
            elif node.callee in self.struct_defs:
                struct_fields = list(self.struct_defs[node.callee].items())
                for idx, arg in enumerate(node.args):
                    if idx < len(struct_fields):
                        f_name, f_type = struct_fields[idx]
                        arg_type = self.infer_type(arg)
                        if not self.is_compatible(f_type, arg_type):
                            DiagnosticEmitter.emit_error(
                                self.filepath, self.source, arg.line, arg.col,
                                "E2006", f"Struct field '{f_name}' type mismatch in constructor for '{node.callee}'",
                                expected=f_type,
                                found=arg_type,
                                help_msg=f"Struct '{node.callee}' field '{f_name}' has type '{f_type}', but received '{arg_type}'."
                            )
                            
            for a in node.args:
                self.visit(a)

        elif isinstance(node, MemberAccessNode):
            self.visit(node.obj)

        elif isinstance(node, BinaryOpNode):
            l_t = self.infer_type(node.left)
            r_t = self.infer_type(node.right)
            if l_t != 'any' and r_t != 'any' and node.op in ('-', '*', '/', '%') and ('string' in (l_t, r_t) or 'bool' in (l_t, r_t)):
                DiagnosticEmitter.emit_error(
                    self.filepath, self.source, node.line, node.col,
                    "E2005", f"Operator '{node.op}' is not supported between types '{l_t}' and '{r_t}'",
                    expected=f"numeric operands for '{node.op}'",
                    found=f"'{l_t}' {node.op} '{r_t}'",
                    help_msg=f"Operator '{node.op}' requires arithmetic operands (int or float)."
                )
            self.visit(node.left)
            self.visit(node.right)

    def infer_type(self, node: Optional[ASTNode]) -> str:
        if not node:
            return 'void'
        if isinstance(node, NumberNode):
            return 'float' if isinstance(node.value, float) else 'int'
        if isinstance(node, StringNode):
            return 'string'
        if isinstance(node, BooleanNode):
            return 'bool'
        if isinstance(node, NullNode):
            return 'null'
        if isinstance(node, ArrayNode):
            if node.elements:
                inner = self.infer_type(node.elements[0])
                return f'Array<{inner}>'
            return 'Array<any>'
        if isinstance(node, IdentifierNode):
            t = self.lookup(node.name)
            if not t:
                DiagnosticEmitter.emit_error(
                    self.filepath, self.source, node.line, node.col,
                    "E2002", f"Undefined variable '{node.name}'",
                    expected="declared variable",
                    found=f"'{node.name}'",
                    help_msg=f"Variable '{node.name}' is referenced before declaration or outside its scope."
                )
            return t if t else 'any'
        if isinstance(node, BinaryOpNode):
            if node.op in ('==', '!=', '>', '<', '>=', '<=', 'and', 'or', '&&', '||'):
                return 'bool'
            l_t = self.infer_type(node.left)
            r_t = self.infer_type(node.right)
            if l_t == 'string' and r_t == 'string' and node.op == '+':
                return 'string'
            if l_t == 'float' or r_t == 'float':
                return 'float'
            return l_t if l_t != 'any' else r_t
        if isinstance(node, FunctionCallNode):
            if node.callee in self.struct_defs:
                return node.callee
            if node.callee in self.func_defs:
                return self.func_defs[node.callee]['ret']
            if node.callee in self.builtins:
                return self.builtins[node.callee]
            return 'any'
        if isinstance(node, MemberAccessNode):
            obj_t = self.infer_type(node.obj)
            if obj_t in self.struct_defs and node.member in self.struct_defs[obj_t]:
                return self.struct_defs[obj_t][node.member]
            return 'any'
        return 'any'
