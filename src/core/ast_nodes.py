from typing import List, Any, Optional

class ASTNode:
    def __init__(self, line: int = 1, col: int = 1):
        self.line = line
        self.col = col

class ProgramNode(ASTNode):
    def __init__(self, target: str, statements: List[ASTNode]):
        super().__init__()
        self.target = target
        self.statements = statements

class TypeNode(ASTNode):
    def __init__(self, name: str, is_optional: bool = False, is_pointer: bool = False, generic_args: Optional[List['TypeNode']] = None, line: int = 1, col: int = 1, is_fn_type: bool = False, param_types: Optional[List['TypeNode']] = None, return_type: Optional['TypeNode'] = None):
        super().__init__(line, col)
        self.name = name
        self.is_optional = is_optional
        self.is_pointer = is_pointer
        self.generic_args = generic_args or []
        self.is_fn_type = is_fn_type
        self.param_types = param_types if isinstance(param_types, list) else []
        self.return_type = return_type

    def __str__(self):
        if self.is_fn_type:
            params = ", ".join(str(p) for p in self.param_types)
            ret = str(self.return_type) if self.return_type else "void"
            return f"fn({params}) -> {ret}"
        base = f"*{self.name}" if self.is_pointer else self.name
        if self.generic_args:
            args_s = ", ".join(str(a) for a in self.generic_args)
            base += f"<{args_s}>"
        return f"{base}?" if self.is_optional else base

class VarDeclNode(ASTNode):
    def __init__(self, name: str, type_annot: Optional[TypeNode], expr: ASTNode, is_const: bool = False, line: int = 1, col: int = 1, is_volatile: bool = False):
        super().__init__(line, col)
        self.name = name
        self.type_annot = type_annot
        self.expr = expr
        self.is_const = is_const
        self.is_volatile = is_volatile

class AssignNode(ASTNode):
    def __init__(self, target: ASTNode, expr: ASTNode, line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.target = target
        self.expr = expr

class NumberNode(ASTNode):
    def __init__(self, value: Any, line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.value = value

class StringNode(ASTNode):
    def __init__(self, value: str, line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.value = value

class BooleanNode(ASTNode):
    def __init__(self, value: bool, line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.value = value

class NullNode(ASTNode):
    def __init__(self, line: int = 1, col: int = 1):
        super().__init__(line, col)

class IdentifierNode(ASTNode):
    def __init__(self, name: str, line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.name = name

class BinaryOpNode(ASTNode):
    def __init__(self, left: ASTNode, op: str, right: ASTNode, line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.left = left
        self.op = op
        self.right = right

class UnaryOpNode(ASTNode):
    def __init__(self, op: str, expr: ASTNode, line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.op = op
        self.expr = expr

class AwaitNode(ASTNode):
    def __init__(self, expr: ASTNode, line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.expr = expr

class FunctionParam:
    def __init__(self, name: str, type_annot: Optional[TypeNode] = None, default_val: Optional[ASTNode] = None):
        self.name = name
        self.type_annot = type_annot
        self.default_val = default_val

class FunctionDefNode(ASTNode):
    def __init__(self, name: str, params: List[FunctionParam], return_type: Optional[TypeNode], body: List[ASTNode], generic_params: Optional[List[str]] = None, is_async: bool = False, doc_comment: str = "", line: int = 1, col: int = 1, is_interrupt: bool = False):
        super().__init__(line, col)
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body
        self.is_async = is_async
        self.generic_params = generic_params or []
        self.doc_comment = doc_comment
        self.is_interrupt = is_interrupt

class LambdaNode(ASTNode):
    def __init__(self, params: List[str], body: ASTNode, line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.params = params
        self.body = body

class StructDefNode(ASTNode):
    def __init__(self, name: str, fields: List[FunctionParam], generic_params: Optional[List[str]] = None, doc_comment: str = "", line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.name = name
        self.fields = fields
        self.generic_params = generic_params or []
        self.doc_comment = doc_comment

class TraitDefNode(ASTNode):
    def __init__(self, name: str, methods: List[FunctionDefNode], line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.name = name
        self.methods = methods

class ImplBlockNode(ASTNode):
    def __init__(self, trait_name: Optional[str], target_type: str, methods: List[FunctionDefNode], line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.trait_name = trait_name
        self.target_type = target_type
        self.methods = methods

class TypeAliasNode(ASTNode):
    def __init__(self, name: str, actual_type: TypeNode, line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.name = name
        self.actual_type = actual_type

class EnumDefNode(ASTNode):
    def __init__(self, name: str, members: List[Any], line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.name = name
        self.members = members

class UnsafeBlockNode(ASTNode):
    def __init__(self, body: List[ASTNode], line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.body = body

class CriticalBlockNode(ASTNode):
    def __init__(self, body: List[ASTNode], line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.body = body

class SpawnNode(ASTNode):
    def __init__(self, body: List[ASTNode], line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.body = body

class TestBlockNode(ASTNode):
    def __init__(self, description: str, body: List[ASTNode], line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.description = description
        self.body = body

class AssertNode(ASTNode):
    def __init__(self, condition: ASTNode, message: Optional[str] = None, line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.condition = condition
        self.message = message

class MatchNode(ASTNode):
    def __init__(self, expr: ASTNode, cases: List[Any], line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.expr = expr
        self.cases = cases

class TryCatchNode(ASTNode):
    def __init__(self, try_body: List[ASTNode], err_name: str, catch_body: List[ASTNode], line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.try_body = try_body
        self.err_name = err_name
        self.catch_body = catch_body

class MemberAccessNode(ASTNode):
    def __init__(self, obj: ASTNode, member: str, is_safe: bool = False, line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.obj = obj
        self.member = member
        self.is_safe = is_safe

class NullCoalesceNode(ASTNode):
    def __init__(self, left: ASTNode, right: ASTNode, line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.left = left
        self.right = right

class ArrayNode(ASTNode):
    def __init__(self, elements: List[ASTNode], line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.elements = elements

class IndexAccessNode(ASTNode):
    def __init__(self, obj: ASTNode, index_expr: ASTNode, line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.obj = obj
        self.index_expr = index_expr

class IfNode(ASTNode):
    def __init__(self, condition: ASTNode, then_branch: List[ASTNode], elif_branches: List[Any], else_branch: Optional[List[ASTNode]], line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.condition = condition
        self.then_branch = then_branch
        self.elif_branches = elif_branches
        self.else_branch = else_branch

class WhileNode(ASTNode):
    def __init__(self, condition: ASTNode, body: List[ASTNode], line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.condition = condition
        self.body = body

class ForNode(ASTNode):
    def __init__(self, var_name: str, start_expr: Optional[ASTNode], end_expr: Optional[ASTNode], collection_expr: Optional[ASTNode], body: List[ASTNode], line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.var_name = var_name
        self.start_expr = start_expr
        self.end_expr = end_expr
        self.collection_expr = collection_expr
        self.body = body

class ReturnNode(ASTNode):
    def __init__(self, expr: Optional[ASTNode], line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.expr = expr

class ThrowNode(ASTNode):
    def __init__(self, expr: ASTNode, line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.expr = expr

class BreakNode(ASTNode): pass
class ContinueNode(ASTNode): pass

class DeferNode(ASTNode):
    def __init__(self, expr: ASTNode, line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.expr = expr

class GuardNode(ASTNode):
    def __init__(self, condition: ASTNode, else_body: List[ASTNode], line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.condition = condition
        self.else_body = else_body

class FunctionCallNode(ASTNode):
    def __init__(self, callee: str, args: List[ASTNode], line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.callee = callee
        self.args = args

class ImportNode(ASTNode):
    def __init__(self, path: str, alias: Optional[str] = None, symbols: Optional[List[str]] = None, line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.path = path
        self.alias = alias
        self.symbols = symbols or []

class NativeIncludeNode(ASTNode):
    def __init__(self, header: str, line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.header = header

class NativeLinkNode(ASTNode):
    def __init__(self, library: str, line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.library = library

class NativeRawNode(ASTNode):
    def __init__(self, raw: str, line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.raw = raw

class NativeUseNode(ASTNode):
    def __init__(self, target: str, line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.target = target

class ExternFnDeclNode(ASTNode):
    def __init__(self, abi: str, name: str, params: List[FunctionParam], return_type: TypeNode, is_varargs: bool = False, line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.abi = abi
        self.name = name
        self.params = params
        self.return_type = return_type
        self.is_varargs = is_varargs


