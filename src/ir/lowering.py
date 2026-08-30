"""Lower the parser AST into immutable, target-neutral structured typed HIR."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from src.core import ast_nodes as ast

from .builtins import BUILTIN_TYPES, INTRINSIC_TYPES
from .model import (
    IRAssign,
    IRArray,
    IRAssert,
    IRAwait,
    IRBinary,
    IRBreak,
    IRCall,
    IRContinue,
    IRDefer,
    IREnum,
    IREnumMember,
    IRExpr,
    IRExprStatement,
    IRExternFunction,
    IRFor,
    IRFunction,
    IRGuard,
    IRIf,
    IRImpl,
    IRIndexAccess,
    IRLambda,
    IRLiteral,
    IRMatch,
    IRMatchCase,
    IRMemberAccess,
    IRModule,
    IRNativeDirective,
    IRNode,
    IRNullCoalesce,
    IRParameter,
    IRReference,
    IRReturn,
    IRSpawn,
    IRStatement,
    IRStruct,
    IRTestBlock,
    IRThrow,
    IRTrait,
    IRTryCatch,
    IRTypeAlias,
    IRUnary,
    IRUnsafeBlock,
    IRVarDecl,
    IRWhile,
    SourceSpan,
)
from .types import (
    ANY,
    BOOL,
    FLOAT,
    INT,
    NULL,
    STRING,
    VOID,
    IRType,
    array_of,
    from_inferred_name,
    from_type_node,
    function_type,
    task_of,
)


class IRLoweringError(ValueError):
    def __init__(self, message: str, span: SourceSpan):
        self.message = message
        self.span = span
        super().__init__(f"{span.source}:{span.line}:{span.column}: {message}")


@dataclass(frozen=True, slots=True)
class _Symbol:
    name: str
    identity: str
    type: IRType
    kind: str


class _Scopes:
    def __init__(self):
        self.frames: List[Dict[str, _Symbol]] = [{}]

    def push(self) -> None:
        self.frames.append({})

    def pop(self) -> None:
        if len(self.frames) == 1:
            raise RuntimeError("Cannot pop the HIR module scope")
        self.frames.pop()

    def declare(self, symbol: _Symbol, span: SourceSpan) -> None:
        frame = self.frames[-1]
        if symbol.name in frame:
            raise IRLoweringError(f"Duplicate symbol '{symbol.name}' in the same scope", span)
        frame[symbol.name] = symbol

    def resolve(self, name: str) -> Optional[_Symbol]:
        for frame in reversed(self.frames):
            if name in frame:
                return frame[name]
        return None


class HIRLowerer:
    def __init__(self, program: ast.ProgramNode, source_name: str = "<memory>"):
        self.program = program
        self.source_name = source_name
        self.scopes = _Scopes()
        self.counter = 0
        self.current_owner = "module"
        self.function_symbols: Dict[str, _Symbol] = {}
        self.struct_fields: Dict[str, Dict[str, IRType]] = {}

    def lower(self) -> IRModule:
        self._declare_builtins()
        # Builtins live in a parent lexical frame so ordinary Nyx declarations
        # can shadow names such as ``len`` without becoming duplicate symbols.
        self.scopes.push()
        try:
            self._predeclare_top_level()
            items = tuple(self._lower_top_level(item) for item in self.program.statements)
            return IRModule(self.source_name, self.program.target, items)
        finally:
            self.scopes.pop()

    def _declare_builtins(self) -> None:
        for name, value_type in BUILTIN_TYPES.items():
            symbol = _Symbol(name, f"builtin::{name}", value_type, "builtin")
            self.scopes.declare(symbol, SourceSpan(self.source_name, 1, 1))
        for name, value_type in INTRINSIC_TYPES.items():
            symbol = _Symbol(name, f"intrinsic::{name}", value_type, "intrinsic")
            self.scopes.declare(symbol, SourceSpan(self.source_name, 1, 1))

    def _predeclare_top_level(self) -> None:
        for node in self.program.statements:
            span = self._span(node)
            if isinstance(node, ast.FunctionDefNode):
                params = tuple(from_type_node(param.type_annot) for param in node.params)
                result = from_type_node(node.return_type, ANY)
                public_result = task_of(result) if node.is_async else result
                symbol = _Symbol(
                    node.name,
                    f"function::{node.name}",
                    function_type(params, public_result),
                    "function",
                )
            elif isinstance(node, ast.ExternFnDeclNode):
                params = tuple(from_type_node(param.type_annot) for param in node.params)
                result = from_type_node(node.return_type, VOID)
                symbol = _Symbol(node.name, f"extern::{node.abi}::{node.name}", function_type(params, result), "extern")
            elif isinstance(node, ast.StructDefNode):
                symbol = _Symbol(node.name, f"type::struct::{node.name}", IRType(node.name), "struct")
                self.struct_fields[node.name] = {
                    field.name: from_type_node(field.type_annot) for field in node.fields
                }
            elif isinstance(node, ast.TraitDefNode):
                symbol = _Symbol(node.name, f"type::trait::{node.name}", IRType(node.name), "trait")
            elif isinstance(node, ast.TypeAliasNode):
                symbol = _Symbol(node.name, f"type::alias::{node.name}", from_type_node(node.actual_type), "alias")
            elif isinstance(node, ast.EnumDefNode):
                symbol = _Symbol(node.name, f"type::enum::{node.name}", IRType(node.name), "enum")
            else:
                continue
            self.scopes.declare(symbol, span)
            if symbol.kind in ("function", "extern"):
                self.function_symbols[node.name] = symbol

    def _lower_top_level(self, node: ast.ASTNode) -> IRNode:
        if isinstance(node, ast.FunctionDefNode):
            return self._lower_function(node, self._require_symbol(node.name, node).identity)
        if isinstance(node, ast.StructDefNode):
            symbol = self._require_symbol(node.name, node)
            fields = tuple(self._parameter(field, f"{symbol.identity}::field::{field.name}") for field in node.fields)
            return IRStruct(
                self._span(node), node.name, symbol.identity, fields,
                tuple(node.generic_params), node.doc_comment,
            )
        if isinstance(node, ast.TraitDefNode):
            symbol = self._require_symbol(node.name, node)
            methods = tuple(
                self._lower_function(method, f"{symbol.identity}::method::{method.name}")
                for method in node.methods
            )
            return IRTrait(self._span(node), node.name, symbol.identity, methods)
        if isinstance(node, ast.ImplBlockNode):
            methods = tuple(
                self._lower_function(method, f"impl::{node.target_type}::method::{method.name}")
                for method in node.methods
            )
            return IRImpl(self._span(node), node.trait_name, node.target_type, methods)
        if isinstance(node, ast.TypeAliasNode):
            symbol = self._require_symbol(node.name, node)
            return IRTypeAlias(self._span(node), node.name, symbol.identity, from_type_node(node.actual_type))
        if isinstance(node, ast.EnumDefNode):
            symbol = self._require_symbol(node.name, node)
            members = tuple(
                IREnumMember(name, self._lower_expr(value) if value is not None else None)
                for name, value in node.members
            )
            return IREnum(self._span(node), node.name, symbol.identity, members)
        if isinstance(node, ast.ExternFnDeclNode):
            symbol = self._require_symbol(node.name, node)
            params = tuple(
                self._parameter(param, f"{symbol.identity}::param::{index}::{param.name}")
                for index, param in enumerate(node.params)
            )
            return IRExternFunction(
                self._span(node), node.abi, node.name, symbol.identity, params,
                from_type_node(node.return_type, VOID), node.is_varargs,
            )
        if isinstance(node, ast.NativeIncludeNode):
            return self._native(node, "include", node.header)
        if isinstance(node, ast.NativeLinkNode):
            return self._native(node, "link", node.library)
        if isinstance(node, ast.NativeRawNode):
            return self._native(node, "raw", node.raw)
        if isinstance(node, ast.NativeUseNode):
            return self._native(node, "use", node.target)
        statement = self._lower_statement(node)
        return statement

    def _native(self, node: ast.ASTNode, kind: str, value: str) -> IRNativeDirective:
        return IRNativeDirective(
            self._span(node), kind, value, str(getattr(node, "_origin_module", "")),
        )

    def _lower_function(self, node: ast.FunctionDefNode, identity: str) -> IRFunction:
        previous_owner = self.current_owner
        self.current_owner = identity
        self.scopes.push()
        try:
            params: List[IRParameter] = []
            for index, parameter in enumerate(node.params):
                symbol_id = f"{identity}::param::{index}::{parameter.name}"
                param_type = from_type_node(parameter.type_annot)
                symbol = _Symbol(parameter.name, symbol_id, param_type, "parameter")
                self.scopes.declare(symbol, self._span(node))
                default = self._lower_expr(parameter.default_val) if parameter.default_val is not None else None
                params.append(IRParameter(parameter.name, symbol_id, param_type, default))
            body = self._lower_block(node.body, create_scope=False)
            return IRFunction(
                self._span(node), node.name, identity, tuple(params),
                from_type_node(node.return_type, ANY), body,
                tuple(node.generic_params), node.is_async, node.doc_comment,
            )
        finally:
            self.scopes.pop()
            self.current_owner = previous_owner

    def _parameter(self, node: ast.FunctionParam, identity: str) -> IRParameter:
        return IRParameter(
            node.name,
            identity,
            from_type_node(node.type_annot),
            self._lower_expr(node.default_val) if node.default_val is not None else None,
        )

    def _lower_block(
        self,
        statements: Sequence[ast.ASTNode],
        *,
        create_scope: bool = True,
    ) -> Tuple[IRStatement, ...]:
        if create_scope:
            self.scopes.push()
        try:
            return tuple(self._lower_statement(statement) for statement in statements)
        finally:
            if create_scope:
                self.scopes.pop()

    def _lower_statement(self, node: ast.ASTNode) -> IRStatement:
        span = self._span(node)
        if isinstance(node, ast.VarDeclNode):
            expr = self._lower_expr(node.expr)
            value_type = from_type_node(node.type_annot, expr.type)
            symbol = _Symbol(node.name, self._next_symbol(node.name), value_type, "variable")
            self.scopes.declare(symbol, span)
            return IRVarDecl(span, node.name, symbol.identity, value_type, expr, node.is_const)
        if isinstance(node, ast.AssignNode):
            if isinstance(node.target, ast.IdentifierNode) and self.scopes.resolve(node.target.name) is None:
                expr = self._lower_expr(node.expr)
                symbol = _Symbol(node.target.name, self._next_symbol(node.target.name), expr.type, "variable")
                self.scopes.declare(symbol, span)
                return IRVarDecl(span, node.target.name, symbol.identity, expr.type, expr)
            return IRAssign(span, self._lower_expr(node.target), self._lower_expr(node.expr))
        if isinstance(node, ast.ReturnNode):
            return IRReturn(span, self._lower_expr(node.expr) if node.expr is not None else None)
        if isinstance(node, ast.IfNode):
            condition = self._lower_expr(node.condition)
            then_branch = self._lower_block(node.then_branch)
            elif_branches = tuple(
                (self._lower_expr(branch_condition), self._lower_block(branch))
                for branch_condition, branch in node.elif_branches
            )
            else_branch = self._lower_block(node.else_branch) if node.else_branch is not None else None
            return IRIf(span, condition, then_branch, elif_branches, else_branch)
        if isinstance(node, ast.WhileNode):
            return IRWhile(span, self._lower_expr(node.condition), self._lower_block(node.body))
        if isinstance(node, ast.ForNode):
            start = self._lower_expr(node.start_expr) if node.start_expr is not None else None
            end = self._lower_expr(node.end_expr) if node.end_expr is not None else None
            collection = self._lower_expr(node.collection_expr) if node.collection_expr is not None else None
            item_type = INT
            if collection is not None and collection.type.name in ("Array", "Buffer") and collection.type.arguments:
                item_type = collection.type.arguments[0]
            self.scopes.push()
            try:
                symbol = _Symbol(node.var_name, self._next_symbol(node.var_name), item_type, "loop-variable")
                self.scopes.declare(symbol, span)
                body = self._lower_block(node.body, create_scope=False)
            finally:
                self.scopes.pop()
            return IRFor(span, node.var_name, symbol.identity, start, end, collection, body)
        if isinstance(node, ast.BreakNode):
            return IRBreak(span)
        if isinstance(node, ast.ContinueNode):
            return IRContinue(span)
        if isinstance(node, ast.ThrowNode):
            return IRThrow(span, self._lower_expr(node.expr))
        if isinstance(node, ast.DeferNode):
            return IRDefer(span, self._lower_expr(node.expr))
        if isinstance(node, ast.GuardNode):
            return IRGuard(span, self._lower_expr(node.condition), self._lower_block(node.else_body))
        if isinstance(node, ast.UnsafeBlockNode):
            return IRUnsafeBlock(span, self._lower_block(node.body))
        if isinstance(node, ast.CriticalBlockNode):
            # Embedded targets still use the legacy freestanding emitter.  HIR
            # retains the block boundary until a dedicated embedded HIR node is
            # introduced; hosted targets are rejected by the type checker.
            return IRUnsafeBlock(span, self._lower_block(node.body))
        if isinstance(node, ast.SpawnNode):
            return IRSpawn(span, self._lower_block(node.body))
        if isinstance(node, ast.AssertNode):
            return IRAssert(span, self._lower_expr(node.condition), node.message)
        if isinstance(node, ast.TestBlockNode):
            return IRTestBlock(span, node.description, self._lower_block(node.body))
        if isinstance(node, ast.TryCatchNode):
            try_body = self._lower_block(node.try_body)
            self.scopes.push()
            try:
                error_symbol = _Symbol(node.err_name, self._next_symbol(node.err_name), STRING, "catch")
                self.scopes.declare(error_symbol, span)
                catch_body = self._lower_block(node.catch_body, create_scope=False)
            finally:
                self.scopes.pop()
            return IRTryCatch(span, try_body, node.err_name, error_symbol.identity, catch_body)
        if isinstance(node, ast.MatchNode):
            cases: List[IRMatchCase] = []
            for pattern, body_node in node.cases:
                self.scopes.push()
                try:
                    lowered_pattern = self._lower_pattern(pattern)
                    body_nodes = body_node if isinstance(body_node, list) else [body_node]
                    body = self._lower_block(body_nodes, create_scope=False)
                finally:
                    self.scopes.pop()
                cases.append(IRMatchCase(lowered_pattern, body))
            return IRMatch(span, self._lower_expr(node.expr), tuple(cases))
        if self._is_expression(node):
            return IRExprStatement(span, self._lower_expr(node))
        raise IRLoweringError(f"Unsupported statement node '{type(node).__name__}'", span)

    def _lower_pattern(self, node: ast.ASTNode) -> IRExpr:
        if isinstance(node, ast.IdentifierNode):
            if node.name == "_":
                return IRReference(self._span(node), ANY, "_", "pattern::_")
            symbol = _Symbol(node.name, self._next_symbol(node.name), ANY, "pattern-binding")
            self.scopes.declare(symbol, self._span(node))
            return IRReference(self._span(node), ANY, node.name, symbol.identity)
        if isinstance(node, ast.FunctionCallNode):
            args = tuple(self._lower_pattern(argument) for argument in node.args)
            symbol = self.scopes.resolve(node.callee)
            return IRCall(
                self._span(node),
                self._call_result_type(symbol),
                node.callee,
                symbol.identity if symbol else f"pattern-constructor::{node.callee}",
                args,
            )
        return self._lower_expr(node)

    def _lower_expr(self, node: Optional[ast.ASTNode]) -> IRExpr:
        if node is None:
            raise IRLoweringError("Missing expression", SourceSpan(self.source_name, 1, 1))
        span = self._span(node)
        if isinstance(node, ast.NumberNode):
            return IRLiteral(span, FLOAT if isinstance(node.value, float) else INT, node.value)
        if isinstance(node, ast.StringNode):
            return IRLiteral(span, STRING, node.value)
        if isinstance(node, ast.BooleanNode):
            return IRLiteral(span, BOOL, node.value)
        if isinstance(node, ast.NullNode):
            return IRLiteral(span, NULL, None)
        if isinstance(node, ast.IdentifierNode):
            symbol = self.scopes.resolve(node.name)
            if symbol is None:
                raise IRLoweringError(f"Unresolved identifier '{node.name}'", span)
            return IRReference(span, symbol.type, node.name, symbol.identity)
        if isinstance(node, ast.BinaryOpNode):
            if node.op == "|>":
                return self._lower_pipeline(node)
            left = self._lower_expr(node.left)
            right = self._lower_expr(node.right)
            return IRBinary(span, self._binary_type(node, left, right), left, node.op, right)
        if isinstance(node, ast.UnaryOpNode):
            expr = self._lower_expr(node.expr)
            value_type = BOOL if node.op in ("!", "not") else expr.type
            return IRUnary(span, value_type, node.op, expr)
        if isinstance(node, ast.AwaitNode):
            expr = self._lower_expr(node.expr)
            result_type = expr.type.arguments[0] if expr.type.name == "Task" and expr.type.arguments else ANY
            return IRAwait(span, result_type, expr)
        if isinstance(node, ast.FunctionCallNode):
            args = tuple(self._lower_expr(argument) for argument in node.args)
            if isinstance(node.callee, ast.MemberAccessNode):
                receiver = self._lower_expr(node.callee.obj)
                result_type = from_inferred_name(getattr(node, "inferred_type", None), ANY)
                method_symbol = f"method::{receiver.type.canonical()}::{node.callee.member}"
                return IRCall(
                    span,
                    result_type,
                    node.callee.member,
                    method_symbol,
                    args,
                    receiver,
                )
            if not isinstance(node.callee, str):
                raise IRLoweringError(
                    f"Unsupported callable expression '{type(node.callee).__name__}'",
                    self._span(node.callee),
                )
            symbol = self.scopes.resolve(node.callee)
            if symbol is None:
                raise IRLoweringError(f"Unresolved function or constructor '{node.callee}'", span)
            return IRCall(span, self._call_result_type(symbol), node.callee, symbol.identity, args)
        if isinstance(node, ast.MemberAccessNode):
            obj = self._lower_expr(node.obj)
            value_type = self.struct_fields.get(obj.type.name, {}).get(node.member, ANY)
            if node.is_safe:
                value_type = value_type.with_optional()
            return IRMemberAccess(span, value_type, obj, node.member, node.is_safe)
        if isinstance(node, ast.IndexAccessNode):
            obj = self._lower_expr(node.obj)
            index = self._lower_expr(node.index_expr)
            value_type = obj.type.arguments[0] if obj.type.name in ("Array", "Buffer") and obj.type.arguments else ANY
            return IRIndexAccess(span, value_type, obj, index)
        if isinstance(node, ast.ArrayNode):
            elements = tuple(self._lower_expr(element) for element in node.elements)
            element_type = self._common_type(tuple(element.type for element in elements))
            return IRArray(span, array_of(element_type), elements)
        if isinstance(node, ast.NullCoalesceNode):
            left = self._lower_expr(node.left)
            right = self._lower_expr(node.right)
            value_type = left.type.with_optional(False) if left.type.name != "null" else right.type
            return IRNullCoalesce(span, value_type, left, right)
        if isinstance(node, ast.LambdaNode):
            self.counter += 1
            lambda_identity = f"{self.current_owner}::lambda::{self.counter}"
            self.scopes.push()
            try:
                params: List[IRParameter] = []
                for index, name in enumerate(node.params):
                    symbol_id = f"{lambda_identity}::param::{index}::{name}"
                    self.scopes.declare(_Symbol(name, symbol_id, ANY, "lambda-param"), span)
                    params.append(IRParameter(name, symbol_id, ANY))
                body = self._lower_expr(node.body)
            finally:
                self.scopes.pop()
            return IRLambda(span, function_type((param.type for param in params), body.type), tuple(params), body)
        raise IRLoweringError(f"Unsupported expression node '{type(node).__name__}'", span)

    def _lower_pipeline(self, node: ast.BinaryOpNode) -> IRCall:
        left = self._lower_expr(node.left)
        if isinstance(node.right, ast.IdentifierNode):
            callee = node.right.name
            raw_args: Tuple[ast.ASTNode, ...] = ()
        elif isinstance(node.right, ast.FunctionCallNode):
            callee = node.right.callee
            raw_args = tuple(node.right.args)
        else:
            raise IRLoweringError("Pipeline target must be a function name or call", self._span(node.right))
        symbol = self.scopes.resolve(callee)
        if symbol is None:
            raise IRLoweringError(f"Unresolved pipeline function '{callee}'", self._span(node.right))
        args = (left,) + tuple(self._lower_expr(argument) for argument in raw_args)
        return IRCall(self._span(node), self._call_result_type(symbol), callee, symbol.identity, args)

    def _binary_type(self, node: ast.BinaryOpNode, left: IRExpr, right: IRExpr) -> IRType:
        inferred = from_inferred_name(getattr(node, "inferred_type", None), ANY)
        if not inferred.is_unknown:
            return inferred
        if node.op in ("==", "!=", "<", ">", "<=", ">=", "and", "or", "&&", "||"):
            return BOOL
        if node.op == "+" and (left.type.name == "string" or right.type.name == "string"):
            return STRING
        if left.type.name == "float" or right.type.name == "float":
            return FLOAT
        return left.type if not left.type.is_unknown else right.type

    @staticmethod
    def _common_type(types: Tuple[IRType, ...]) -> IRType:
        if not types:
            return ANY
        current = types[0]
        for item in types[1:]:
            if current == item:
                continue
            if current.is_numeric and item.is_numeric:
                current = FLOAT
            else:
                return ANY
        return current

    @staticmethod
    def _call_result_type(symbol: Optional[_Symbol]) -> IRType:
        if symbol is None:
            return ANY
        if symbol.kind == "struct":
            return symbol.type
        if symbol.type.is_function:
            return symbol.type.return_type or VOID
        return ANY

    @staticmethod
    def _is_expression(node: ast.ASTNode) -> bool:
        return isinstance(node, (
            ast.NumberNode, ast.StringNode, ast.BooleanNode, ast.NullNode,
            ast.IdentifierNode, ast.BinaryOpNode, ast.UnaryOpNode,
            ast.AwaitNode,
            ast.FunctionCallNode, ast.MemberAccessNode, ast.IndexAccessNode,
            ast.ArrayNode, ast.NullCoalesceNode, ast.LambdaNode,
        ))

    def _require_symbol(self, name: str, node: ast.ASTNode) -> _Symbol:
        symbol = self.scopes.resolve(name)
        if symbol is None:
            raise IRLoweringError(f"Missing predeclared symbol '{name}'", self._span(node))
        return symbol

    def _next_symbol(self, name: str) -> str:
        self.counter += 1
        return f"{self.current_owner}::local::{self.counter}::{name}"

    def _span(self, node: object) -> SourceSpan:
        return SourceSpan(
            self.source_name,
            max(1, int(getattr(node, "line", 1) or 1)),
            max(1, int(getattr(node, "col", 1) or 1)),
        )


def lower_to_hir(program: ast.ProgramNode, source_name: str = "<memory>") -> IRModule:
    return HIRLowerer(program, source_name).lower()
