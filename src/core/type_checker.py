from typing import Dict, List, Optional, Any, Set
import sys
from .ast_nodes import (
    ASTNode, ProgramNode, NumberNode, StringNode, BooleanNode, NullNode,
    IdentifierNode, BinaryOpNode, UnaryOpNode, AwaitNode, NullCoalesceNode, ConditionalExprNode, MemberAccessNode,
    IndexAccessNode, ArrayNode, LambdaNode, FunctionCallNode, VarDeclNode,
    AssignNode, TypeAliasNode, StructDefNode, TraitDefNode, ImplBlockNode,
    EnumDefNode, UnsafeBlockNode, SpawnNode, TestBlockNode, AssertNode,
    FunctionDefNode, MatchNode, MatchExprNode, TryCatchNode, IfNode, WhileNode, ForNode,
    ReturnNode, ThrowNode, BreakNode, ContinueNode, TypeNode, NativeIncludeNode,
    NativeLinkNode, NativeRawNode, NativeUseNode, ExternFnDeclNode,
    DeferNode, GuardNode
)
from .diagnostics import DiagnosticEmitter

_INT64_MIN = -(1 << 63)
_INT64_MAX = (1 << 63) - 1
_INTEGER_TYPES = frozenset(("int", "i8", "i16", "i32", "i64", "u8", "u16", "u32", "u64", "uintptr"))
_FIXED_INTEGER_RANGES = {
    "i8": (-(1 << 7), (1 << 7) - 1),
    "i16": (-(1 << 15), (1 << 15) - 1),
    "i32": (-(1 << 31), (1 << 31) - 1),
    "i64": (_INT64_MIN, _INT64_MAX),
    "int": (_INT64_MIN, _INT64_MAX),
    "u8": (0, (1 << 8) - 1),
    "u16": (0, (1 << 16) - 1),
    "u32": (0, (1 << 32) - 1),
    "u64": (0, (1 << 64) - 1),
    "uintptr": (0, (1 << 64) - 1),
}
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
        self.current_is_async = False
        
        # Prepopulate builtin runtime functions
        self.builtins = {
            'print': 'void', 'input': 'string', 'to_string': 'string',
            'to_int': 'int', 'contains': 'bool', 'is_number': 'bool',
            'addr': 'uintptr', 'peek': 'uintptr', 'memdump': 'void',
            'delay_ms': 'void', 'channel': 'Channel', 'Ok': 'Result',
            'Err': 'Result', 'len': 'int', 'ord': 'int', 'char_code_at': 'int',
            'args': 'Array<string>'
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
        if exp_base in _INTEGER_TYPES and act_base in _INTEGER_TYPES:
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
        if (
            (exp_base.startswith('Result') and act_base.startswith('Result'))
            or (exp_base.startswith('Array') and act_base.startswith('Array'))
            or (exp_base.startswith('Task') and act_base.startswith('Task'))
        ):
            return True
        # null compatibility with Option / Nullable types
        if actual == 'null' and ('?' in expected or 'Option' in expected):
            return True
        return False

    def _check_fixed_integer_literal(self, node: VarDeclNode):
        if not node.type_annot or not isinstance(node.expr, NumberNode):
            return
        type_name = node.type_annot.name
        bounds = _FIXED_INTEGER_RANGES.get(type_name)
        value = node.expr.value
        if not bounds or not isinstance(value, int) or isinstance(value, bool):
            return
        if not (bounds[0] <= value <= bounds[1]):
            DiagnosticEmitter.emit_error(
                self.filepath, self.source, node.expr.line, node.expr.col,
                "E2024", f"Integer literal does not fit in '{type_name}'",
                expected=f"{bounds[0]}..{bounds[1]}",
                found=str(value),
                help_msg=f"Choose a value representable by {type_name} or use a wider integer type.",
            )

    def check(self):
        self._validate_integer_literals(self.ast)

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
                ret_t = str(stmt.return_type) if stmt.return_type else 'any'
                params = [(p.name, str(p.type_annot) if p.type_annot else 'any') for p in stmt.params]
                public_ret = f'Task<{ret_t}>' if stmt.is_async else ret_t
                self.func_defs[stmt.name] = {
                    'ret': ret_t,
                    'public_ret': public_ret,
                    'params': params,
                    'is_async': stmt.is_async,
                }
                self.declare(stmt.name, f'fn->{public_ret}')
            elif isinstance(stmt, ExternFnDeclNode):
                ret_t = str(stmt.return_type) if stmt.return_type else 'void'
                params = [(p.name, str(p.type_annot) if p.type_annot else 'any') for p in stmt.params]
                self.func_defs[stmt.name] = {'ret': ret_t, 'params': params, 'is_extern': True}
                self.declare(stmt.name, f'fn->{ret_t}')

        # 2nd Pass: Full Semantic Analysis & Type Inference
        for stmt in self.ast.statements:
            self.visit(stmt)

    def _validate_integer_literals(self, value: object):
        """Reject invalid source literals before inference can skip a subtree."""
        if isinstance(value, NumberNode):
            if (
                isinstance(value.value, int)
                and not isinstance(value.value, bool)
                and not (_INT64_MIN <= value.value <= _INT64_MAX)
            ):
                DiagnosticEmitter.emit_error(
                    self.filepath, self.source, value.line, value.col,
                    "E2012", "Integer literal is outside the signed 64-bit range",
                    expected=f"{_INT64_MIN}..{_INT64_MAX}",
                    found=str(value.value),
                    help_msg="Use a signed 64-bit literal or compute the wrapped value at runtime.",
                )
        if isinstance(value, ASTNode):
            for child in vars(value).values():
                self._validate_integer_literals(child)
        elif isinstance(value, (list, tuple)):
            for child in value:
                self._validate_integer_literals(child)

    def _require_bool_condition(self, node: ASTNode, context: str):
        actual = self.infer_type(node)
        if actual not in ('bool', 'any'):
            DiagnosticEmitter.emit_error(
                self.filepath, self.source, node.line, node.col,
                "E2013", f"{context} condition must have type 'bool'",
                expected="bool",
                found=actual,
                help_msg="Compare the value explicitly instead of relying on implicit truthiness.",
            )

    def visit(self, node: Optional[ASTNode]):
        if not node:
            return

        if isinstance(node, (NativeIncludeNode, NativeLinkNode, NativeRawNode, NativeUseNode, ExternFnDeclNode)):
            return

        if isinstance(node, VarDeclNode):
            self._check_fixed_integer_literal(node)
            self.visit(node.expr)
            val_type = self.infer_type(node.expr)
            if node.type_annot:
                if not self.is_type_compatible(node.type_annot, val_type):
                    declared_name = str(node.type_annot)
                    DiagnosticEmitter.emit_error(
                        self.filepath, self.source, node.line, node.col,
                        "E2001", f"Type mismatch in variable declaration '{node.name}'",
                        expected=declared_name,
                        found=val_type,
                        help_msg=f"Cannot assign value of type '{val_type}' to variable '{node.name}' of type '{declared_name}'."
                    )
                declared_name = str(node.type_annot)
                self.declare(node.name, declared_name)
                node.inferred_type = declared_name
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
            prev_async = self.current_is_async
            self.current_return_type = str(node.return_type) if node.return_type else None
            self.current_is_async = node.is_async
            for p in node.params:
                p_type = str(p.type_annot) if p.type_annot else 'any'
                self.declare(p.name, p_type)
            for s in node.body:
                self.visit(s)
            self.current_return_type = prev_ret
            self.current_is_async = prev_async
            self.exit_scope()

        elif isinstance(node, ReturnNode):
            if node.expr:
                self.visit(node.expr)
                ret_val_type = self.infer_type(node.expr)
                if self.current_return_type and not self.is_compatible(self.current_return_type, ret_val_type):
                    DiagnosticEmitter.emit_error(
                        self.filepath, self.source, node.line, node.col,
                        "E2004", f"Return type mismatch in function",
                        expected=self.current_return_type,
                        found=ret_val_type,
                        help_msg=f"Function was declared with return type '{self.current_return_type}', but returns a value of type '{ret_val_type}'."
                    )

        elif isinstance(node, ThrowNode):
            self.visit(node.expr)

        elif isinstance(node, AwaitNode):
            self.visit(node.expr)
            self.infer_type(node)

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
            self._require_bool_condition(node.condition, "guard")
            self.enter_scope()
            for s in node.else_body: self.visit(s)
            self.exit_scope()

        elif isinstance(node, IfNode):
            self._require_bool_condition(node.condition, "if")
            self.enter_scope()
            for s in node.then_branch: self.visit(s)
            self.exit_scope()
            for cond, branch in node.elif_branches:
                self._require_bool_condition(cond, "elif")
                self.enter_scope()
                for s in branch: self.visit(s)
                self.exit_scope()
            if node.else_branch:
                self.enter_scope()
                for s in node.else_branch: self.visit(s)
                self.exit_scope()

        elif isinstance(node, WhileNode):
            self._require_bool_condition(node.condition, "while")
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
            self.declare(node.err_name, 'string')
            for s in node.catch_body: self.visit(s)
            self.exit_scope()

        elif isinstance(node, ArrayNode):
            for element in node.elements:
                self.visit(element)

        elif isinstance(node, IndexAccessNode):
            index_type = self.infer_type(node.index_expr)
            if index_type not in _INTEGER_TYPES and index_type != 'any':
                DiagnosticEmitter.emit_error(
                    self.filepath, self.source, node.index_expr.line, node.index_expr.col,
                    'E2005', 'Collection index must be an integer',
                    expected='integer index',
                    found=index_type,
                    help_msg='Convert the index to an integer before indexing.',
                )
            self.visit(node.obj)
            self.visit(node.index_expr)

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

        elif isinstance(node, (ConditionalExprNode, MatchExprNode)):
            self.infer_type(node)

    def infer_type(self, node: Optional[ASTNode]) -> str:
        if not node:
            return 'void'
        t = 'any'
        if isinstance(node, NumberNode):
            inferred = 'float' if isinstance(node.value, float) else 'int'
            node.inferred_type = inferred
            return inferred
        if isinstance(node, StringNode):
            node.inferred_type = 'string'
            return 'string'
        if isinstance(node, BooleanNode):
            node.inferred_type = 'bool'
            return 'bool'
        if isinstance(node, NullNode):
            node.inferred_type = 'null'
            return 'null'
        if isinstance(node, ArrayNode):
            if node.elements:
                inner = self.infer_type(node.elements[0])
                for element in node.elements[1:]:
                    self.infer_type(element)
                inferred = f'Array<{inner}>'
            else:
                inferred = 'Array<any>'
            node.inferred_type = inferred
            return inferred
        if isinstance(node, IndexAccessNode):
            collection_type = self.infer_type(node.obj)
            self.infer_type(node.index_expr)
            if collection_type.startswith('Array<') and collection_type.endswith('>'):
                inferred = collection_type[6:-1]
            elif collection_type == 'string':
                inferred = 'string'
            else:
                inferred = 'any'
            node.inferred_type = inferred
            return inferred
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
            inferred = t if t else 'any'
            node.inferred_type = inferred
            return inferred
        if isinstance(node, BinaryOpNode):
            l_t = self.infer_type(node.left)
            r_t = self.infer_type(node.right)
            if node.op in ('==', '!=', '>', '<', '>=', '<=', 'and', 'or', '&&', '||'):
                inferred = 'bool'
            elif l_t == 'string' and r_t == 'string' and node.op == '+':
                inferred = 'string'
            elif l_t == 'float' or r_t == 'float':
                inferred = 'float'
            else:
                inferred = l_t if l_t != 'any' else r_t
            node.inferred_type = inferred
            return inferred
        if isinstance(node, AwaitNode):
            if not self.current_is_async:
                DiagnosticEmitter.emit_error(
                    self.filepath, self.source, node.line, node.col,
                    "E2010", "'await' is only valid inside an async function",
                    expected="async fn context",
                    found="synchronous context",
                    help_msg="Mark the containing function 'async' or remove 'await'.",
                )
            operand_type = self.infer_type(node.expr)
            if operand_type == 'any':
                node.inferred_type = 'any'
                return 'any'
            if not (operand_type.startswith('Task<') and operand_type.endswith('>')):
                DiagnosticEmitter.emit_error(
                    self.filepath, self.source, node.line, node.col,
                    "E2011", "'await' operand is not a Task",
                    expected="Task<T>",
                    found=operand_type,
                    help_msg="Await an async function call or another Task value.",
                )
            inferred = operand_type[5:-1]
            node.inferred_type = inferred
            return inferred
        if isinstance(node, ConditionalExprNode):
            self._require_bool_condition(node.condition, "if expression")
            branch_types = [self.infer_type(node.then_expr)]
            for condition, branch in node.elif_branches:
                self._require_bool_condition(condition, "elif expression")
                branch_types.append(self.infer_type(branch))
            branch_types.append(self.infer_type(node.else_expr))
            concrete = [value for value in branch_types if value != 'any']
            if not concrete:
                inferred = 'any'
            elif all(value == concrete[0] for value in concrete):
                inferred = concrete[0]
            elif all(value in ('int', 'float') for value in concrete):
                inferred = 'float'
            else:
                DiagnosticEmitter.emit_error(
                    self.filepath, self.source, node.line, node.col,
                    "E2001", "Conditional expression branches produce incompatible types",
                    expected=concrete[0],
                    found=", ".join(branch_types),
                    help_msg="Make every if/elif/else branch produce the same type.",
                )
                inferred = 'any'
            node.inferred_type = inferred
            return inferred
        if isinstance(node, MatchExprNode):
            subject_type = self.infer_type(node.expr)
            branch_types = []
            wildcard_indexes = []
            for index, (pattern, value) in enumerate(node.cases):
                is_wildcard = isinstance(pattern, IdentifierNode) and pattern.name == "_"
                if is_wildcard:
                    wildcard_indexes.append(index)
                elif isinstance(pattern, IdentifierNode):
                    DiagnosticEmitter.emit_error(
                        self.filepath, self.source, pattern.line, pattern.col,
                        "E2015", "Match expression identifiers are not binding patterns yet",
                        expected="literal pattern or _ fallback",
                        found=pattern.name,
                        help_msg="Use a literal arm now; Result/enum destructuring is a separate Maya feature.",
                    )
                else:
                    pattern_type = self.infer_type(pattern)
                    if not (
                        self.is_compatible(subject_type, pattern_type)
                        or self.is_compatible(pattern_type, subject_type)
                    ):
                        DiagnosticEmitter.emit_error(
                            self.filepath, self.source, pattern.line, pattern.col,
                            "E2001", "Match expression pattern type is incompatible with its subject",
                            expected=subject_type,
                            found=pattern_type,
                            help_msg="Use patterns with the same type as the matched value.",
                        )
                branch_types.append(self.infer_type(value))
            if wildcard_indexes != [len(node.cases) - 1]:
                DiagnosticEmitter.emit_error(
                    self.filepath, self.source, node.line, node.col,
                    "E2014", "Match expression must end with an exhaustive '_' fallback",
                    expected="_ => fallback as the final arm",
                    found="missing or non-final wildcard",
                    help_msg="A value-producing match must produce a value on every path.",
                )
            concrete = [value for value in branch_types if value != 'any']
            if not concrete:
                inferred = 'any'
            elif all(value == concrete[0] for value in concrete):
                inferred = concrete[0]
            elif all(value in ('int', 'float') for value in concrete):
                inferred = 'float'
            else:
                DiagnosticEmitter.emit_error(
                    self.filepath, self.source, node.line, node.col,
                    "E2001", "Match expression arms produce incompatible types",
                    expected=concrete[0],
                    found=", ".join(branch_types),
                    help_msg="Make every match arm produce the same type.",
                )
                inferred = 'any'
            node.inferred_type = inferred
            return inferred
        if isinstance(node, FunctionCallNode):
            if node.callee in self.struct_defs:
                inferred = node.callee
            elif node.callee in self.func_defs:
                inferred = self.func_defs[node.callee].get(
                    'public_ret',
                    self.func_defs[node.callee]['ret'],
                )
            elif node.callee in self.builtins:
                inferred = self.builtins[node.callee]
            else:
                inferred = 'any'
            node.inferred_type = inferred
            return inferred
        if isinstance(node, MemberAccessNode):
            obj_t = self.infer_type(node.obj)
            if obj_t in self.struct_defs and node.member in self.struct_defs[obj_t]:
                inferred = self.struct_defs[obj_t][node.member]
                node.inferred_type = inferred
                return inferred
            node.inferred_type = 'any'
            return 'any'
        node.inferred_type = 'any'
        return 'any'
