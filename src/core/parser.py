import sys
import os
from typing import List, Dict, Any, Optional, Tuple, Set

# Import tokens and AST nodes
try:
    from .tokens import TokenType, Token
    from .diagnostics import DiagnosticEmitter
    from .ast_nodes import *
except (ImportError, ValueError):
    from tokens import TokenType, Token
    from diagnostics import DiagnosticEmitter
    from ast_nodes import *

# =========================================================
# 1. RUST-GRADE DIAGNOSTIC EMITTER
# =========================================================
class DiagnosticEmitter:
    @staticmethod
    def emit_error(filepath: str, source: str, line: int, col: int, code: str, title: str, expected: str = "", found: str = "", help_msg: str = ""):
        lines = source.splitlines()
        line_content = lines[line - 1] if 0 < line <= len(lines) else ""
        pointer = " " * max(0, col - 1) + "^^^^^"
        
        print(f"\n\033[91m\033[1merror[{code}]: {title}\033[0m")
        print(f"  \033[94m-->\033[0m {filepath}:{line}:{col}")
        print(f"   \033[94m|\033[0m")
        print(f"\033[94m{line:2d} |\033[0m {line_content}")
        print(f"   \033[94m|\033[0m \033[91m{pointer}\033[0m")
        if expected or found:
            print(f"   \033[94m=\033[0m \033[1mexpected:\033[0m \033[92m{expected}\033[0m")
            print(f"   \033[94m=\033[0m \033[1mfound:   \033[0m \033[91m{found}\033[0m")
        if help_msg:
            print(f"   \033[94m=\033[0m \033[96m\033[1mhelp:\033[0m {help_msg}")
        print()
        sys.exit(1)

    @staticmethod
    def emit_warning(filepath: str, line: int, col: int, code: str, msg: str):
        print(f"\033[93m\033[1mwarning[{code}]:\033[0m {msg} (at {filepath}:{line}:{col})")

# =========================================================
# 2. RECURSIVE DESCENT PARSER
# =========================================================
class Parser:
    def __init__(self, tokens: List[Token], source: str, filepath: str = "<source>"):
        self.tokens = tokens
        self.source = source
        self.filepath = filepath
        self.pos = 0
        self.target = "hecpp"
        self.last_doc_comment = ""

    def current(self) -> Token:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else self.tokens[-1]

    def peek(self, offset: int = 1) -> Token:
        idx = self.pos + offset
        return self.tokens[idx] if idx < len(self.tokens) else self.tokens[-1]

    def advance(self) -> Token:
        tok = self.current()
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def expect(self, token_type: str, err_code: str = "E1001", help_msg: str = "") -> Token:
        tok = self.current()
        if tok.type != token_type:
            DiagnosticEmitter.emit_error(
                self.filepath, self.source, tok.line, tok.col,
                err_code, f"Unexpected token",
                expected=token_type, found=f"{tok.type} ('{tok.value}')",
                help_msg=help_msg
            )
        return self.advance()

    def match(self, *token_types: str) -> bool:
        if self.current().type in token_types:
            self.advance()
            return True
        return False

    def parse(self) -> ProgramNode:
        statements: List[ASTNode] = []
        if self.current().type == TokenType.TARGET_DIR:
            self.target = self.advance().value

        while self.current().type != TokenType.EOF:
            if self.match(TokenType.SEMICOLON):
                continue
            if self.current().type == TokenType.DOC_COMMENT:
                self.last_doc_comment = self.advance().value
                continue
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
                self.last_doc_comment = ""
            while self.match(TokenType.SEMICOLON):
                pass

        return ProgramNode(self.target, statements)

    # -----------------------------------------------------
    # Types Parser: int, string, User?, *int, Array<T>, Map<K, V>
    # -----------------------------------------------------
    def parse_type(self) -> TypeNode:
        tok = self.current()
        is_pointer = False
        if self.match(TokenType.MUL):
            is_pointer = True

        name = self.expect(TokenType.IDENT, "E1002", "Expected a valid type name like int, string, float, bool").value
        generic_args: List[TypeNode] = []
        
        # Generic arguments: Array<int>, Map<string, User>
        if self.match(TokenType.LT):
            while self.current().type not in (TokenType.GT, TokenType.EOF):
                generic_args.append(self.parse_type())
                self.match(TokenType.COMMA)
            self.expect(TokenType.GT, "E1003", "Close generic arguments with '>'")

        is_optional = False
        if self.match(TokenType.QUESTION):
            is_optional = True

        return TypeNode(name, is_optional, is_pointer, generic_args, tok.line, tok.col)

    # -----------------------------------------------------
    # Statements Parser
    # -----------------------------------------------------
    def parse_statement(self) -> Optional[ASTNode]:
        tok = self.current()

        # Native Directives
        if tok.type == TokenType.NATIVE_INCLUDE:
            self.advance()
            return NativeIncludeNode(tok.value, tok.line, tok.col)

        if tok.type == TokenType.NATIVE_LINK:
            self.advance()
            return NativeLinkNode(tok.value, tok.line, tok.col)

        if tok.type == TokenType.NATIVE_RAW:
            self.advance()
            return NativeRawNode(tok.value, tok.line, tok.col)

        # Extern Function Declaration: extern "C" fn puts(s: string) -> int
        if tok.type == TokenType.EXTERN:
            self.advance()
            abi = "C"
            if self.current().type == TokenType.STRING:
                abi = self.advance().value
            self.expect(TokenType.FN, "E1010", "Expected 'fn' after 'extern' declaration")
            fn_name = self.expect(TokenType.IDENT, "E1011", "Expected external function name").value
            self.expect(TokenType.LPAREN)
            params: List[FunctionParam] = []
            is_varargs = False
            while self.current().type not in (TokenType.RPAREN, TokenType.EOF):
                if self.current().type == TokenType.DOTDOT or self.current().value == "...":
                    self.advance()
                    is_varargs = True
                    break
                pname = self.expect(TokenType.IDENT).value
                ptype = None
                if self.match(TokenType.COLON):
                    ptype = self.parse_type()
                params.append(FunctionParam(pname, ptype))
                if not self.match(TokenType.COMMA):
                    break
            self.expect(TokenType.RPAREN)
            ret_type = TypeNode("void")
            if self.match(TokenType.ARROW):
                ret_type = self.parse_type()
            return ExternFnDeclNode(abi, fn_name, params, ret_type, is_varargs, tok.line, tok.col)

        # Import Statement: import "path", use "path", import { a, b } from "path", import "path" as alias
        if tok.type in (TokenType.IMPORT, TokenType.USE):
            self.advance()
            symbols = []
            if self.match(TokenType.LBRACE):
                while self.current().type not in (TokenType.RBRACE, TokenType.EOF):
                    symbols.append(self.expect(TokenType.IDENT).value)
                    self.match(TokenType.COMMA)
                self.expect(TokenType.RBRACE)
                self.expect(TokenType.FROM, "E1005", "Expected 'from' after import symbols block")
            
            path_tok = self.expect(TokenType.STRING, "E1006", "Expected module path string literal like 'std/math' or './utils'")
            path = path_tok.value
            alias = None
            if self.match(TokenType.AS):
                alias = self.expect(TokenType.IDENT).value
            return ImportNode(path, alias, symbols, tok.line, tok.col)

        # Variable Declaration: var x: int = 10, let y = 20
        if tok.type in (TokenType.VAR, TokenType.LET, TokenType.SET, TokenType.CONST):
            is_const = (tok.type == TokenType.CONST)
            self.advance()
            name = self.expect(TokenType.IDENT).value
            type_annot = None
            if self.match(TokenType.COLON):
                type_annot = self.parse_type()
            self.expect(TokenType.ASSIGN, "E1004", f"Initialize variable '{name}' with a value using '='")
            expr = self.parse_expression()
            return VarDeclNode(name, type_annot, expr, is_const, tok.line, tok.col)

        # Type Alias: type UserID = int
        if tok.type == TokenType.TYPE_ALIAS:
            self.advance()
            alias_name = self.expect(TokenType.IDENT).value
            self.expect(TokenType.ASSIGN)
            actual = self.parse_type()
            return TypeAliasNode(alias_name, actual, tok.line, tok.col)

        # Trait Definition: trait Printable { fn print_self() }
        if tok.type == TokenType.TRAIT:
            self.advance()
            trait_name = self.expect(TokenType.IDENT).value
            self.expect(TokenType.LBRACE)
            methods: List[FunctionDefNode] = []
            while self.current().type not in (TokenType.RBRACE, TokenType.EOF):
                if self.current().type == TokenType.FN:
                    methods.append(self.parse_function())
                else:
                    self.advance()
            self.expect(TokenType.RBRACE)
            return TraitDefNode(trait_name, methods, tok.line, tok.col)

        # Impl Block: impl Printable for User { ... } / impl User { ... }
        if tok.type == TokenType.IMPL:
            self.advance()
            first_ident = self.expect(TokenType.IDENT).value
            trait_name = None
            target_type = first_ident
            if self.current().type == TokenType.IDENT and self.current().value == "for":
                self.advance()
                trait_name = first_ident
                target_type = self.expect(TokenType.IDENT).value
            self.expect(TokenType.LBRACE)
            methods: List[FunctionDefNode] = []
            while self.current().type not in (TokenType.RBRACE, TokenType.EOF):
                if self.current().type == TokenType.FN:
                    methods.append(self.parse_function())
                else:
                    self.advance()
            self.expect(TokenType.RBRACE)
            return ImplBlockNode(trait_name, target_type, methods, tok.line, tok.col)

        # Struct Definition: struct Point<T> { x: T, y: T }
        if tok.type == TokenType.STRUCT:
            self.advance()
            name = self.expect(TokenType.IDENT).value
            generic_params = []
            if self.match(TokenType.LT):
                while self.current().type not in (TokenType.GT, TokenType.EOF):
                    generic_params.append(self.expect(TokenType.IDENT).value)
                    self.match(TokenType.COMMA)
                self.expect(TokenType.GT)

            fields: List[FunctionParam] = []
            if self.match(TokenType.LBRACE):
                while self.current().type not in (TokenType.RBRACE, TokenType.EOF):
                    if self.current().type not in (TokenType.RBRACE, TokenType.COMMA, TokenType.SEMICOLON):
                        fname = self.advance().value
                        ftype = None
                        if self.match(TokenType.COLON):
                            ftype = self.parse_type()
                        fields.append(FunctionParam(fname, ftype))
                    while self.match(TokenType.COMMA) or self.match(TokenType.SEMICOLON):
                        pass
                self.expect(TokenType.RBRACE)
            elif self.match(TokenType.COLON):
                while self.current().type not in (TokenType.EOF, TokenType.SEMICOLON):
                    fname = self.advance().value
                    ftype = None
                    if self.match(TokenType.COLON):
                        ftype = self.parse_type()
                    fields.append(FunctionParam(fname, ftype))
                    while self.match(TokenType.COMMA) or self.match(TokenType.SEMICOLON):
                        pass
            return StructDefNode(name, fields, generic_params, self.last_doc_comment, tok.line, tok.col)

        # Enum Definition: enum Color { Red, Green, Blue = 5 }
        if tok.type == TokenType.ENUM:
            self.advance()
            name = self.expect(TokenType.IDENT).value
            members = []
            if self.match(TokenType.LBRACE):
                while self.current().type not in (TokenType.RBRACE, TokenType.EOF):
                    if self.current().type == TokenType.IDENT:
                        m_name = self.advance().value
                        val = None
                        if self.match(TokenType.ASSIGN):
                            val = self.parse_expression()
                        members.append((m_name, val))
                    self.match(TokenType.COMMA)
                self.expect(TokenType.RBRACE)
            return EnumDefNode(name, members, tok.line, tok.col)

        # Unsafe Block: unsafe { ... }
        if tok.type == TokenType.UNSAFE:
            self.advance()
            body = self.parse_block()
            return UnsafeBlockNode(body, tok.line, tok.col)

        # Concurrency: spawn { ... }
        if tok.type == TokenType.SPAWN:
            self.advance()
            body = self.parse_block()
            return SpawnNode(body, tok.line, tok.col)

        # Testing Block: test "addition works" { ... }
        if tok.type == TokenType.TEST:
            self.advance()
            desc = self.expect(TokenType.STRING, "E1005", "Provide a string description for the test").value
            body = self.parse_block()
            return TestBlockNode(desc, body, tok.line, tok.col)

        # Standalone Block: { ... }
        if tok.type == TokenType.LBRACE:
            body = self.parse_block()
            return UnsafeBlockNode(body, tok.line, tok.col)

        # Assert: assert(x > 0, "must be positive")
        if tok.type == TokenType.ASSERT:
            self.advance()
            self.expect(TokenType.LPAREN)
            cond = self.parse_expression()
            msg = None
            if self.match(TokenType.COMMA):
                msg = self.expect(TokenType.STRING).value
            self.expect(TokenType.RPAREN)
            return AssertNode(cond, msg, tok.line, tok.col)

        # Function Definition (Sync or Async)
        if tok.type in (TokenType.FN, TokenType.ASYNC):
            return self.parse_function()

        # Match Pattern Matching
        if tok.type == TokenType.MATCH:
            self.advance()
            expr = self.parse_expression()
            cases = []
            if self.match(TokenType.LBRACE):
                while self.current().type not in (TokenType.RBRACE, TokenType.EOF):
                    pat = self.parse_expression()
                    self.expect(TokenType.FAT_ARROW)
                    stmt = self.parse_statement()
                    cases.append((pat, stmt))
                    self.match(TokenType.COMMA)
                self.expect(TokenType.RBRACE)
            return MatchNode(expr, cases, tok.line, tok.col)

        # Try-Catch
        if tok.type == TokenType.TRY:
            self.advance()
            try_body = self.parse_block()
            self.expect(TokenType.CATCH)
            err_name = "e"
            if self.current().type == TokenType.IDENT:
                err_name = self.advance().value
            catch_body = self.parse_block()
            return TryCatchNode(try_body, err_name, catch_body, tok.line, tok.col)

        # Conditionals
        if tok.type == TokenType.IF:
            self.advance()
            cond = self.parse_expression()
            then_body = self.parse_block()
            elif_branches = []
            else_body = None
            while self.current().type == TokenType.ELIF:
                self.advance()
                elif_cond = self.parse_expression()
                elif_body = self.parse_block()
                elif_branches.append((elif_cond, elif_body))
            if self.current().type == TokenType.ELSE:
                self.advance()
                else_body = self.parse_block()
            return IfNode(cond, then_body, elif_branches, else_body, tok.line, tok.col)

        # Loops
        if tok.type in (TokenType.LOOP, TokenType.WHILE):
            self.advance()
            cond = BooleanNode(True, tok.line, tok.col) if self.current().type in (TokenType.LBRACE, TokenType.COLON) else self.parse_expression()
            body = self.parse_block()
            return WhileNode(cond, body, tok.line, tok.col)

        if tok.type == TokenType.FOR:
            self.advance()
            var_name = self.expect(TokenType.IDENT).value
            self.expect(TokenType.IN)
            first_expr = self.parse_expression()
            if self.match(TokenType.DOTDOT):
                end_expr = self.parse_expression()
                body = self.parse_block()
                return ForNode(var_name, first_expr, end_expr, None, body, tok.line, tok.col)
            else:
                body = self.parse_block()
                return ForNode(var_name, None, None, first_expr, body, tok.line, tok.col)

        if tok.type == TokenType.RETURN:
            self.advance()
            expr = self.parse_expression() if self.current().type not in (TokenType.EOF, TokenType.RBRACE, TokenType.COMMA) else None
            return ReturnNode(expr, tok.line, tok.col)
        if tok.type == TokenType.BREAK:
            self.advance()
            return BreakNode(tok.line, tok.col)
        if tok.type == TokenType.CONTINUE:
            self.advance()
            return ContinueNode(tok.line, tok.col)

        # General Expressions / Reverse arrow / Assignments
        expr = self.parse_expression()
        if self.match(TokenType.ARROW):
            var_name = self.expect(TokenType.IDENT).value
            return VarDeclNode(var_name, None, expr, False, tok.line, tok.col)
        if self.match(TokenType.ASSIGN):
            val_expr = self.parse_expression()
            return AssignNode(expr, val_expr, tok.line, tok.col)

        return expr

    def parse_function(self) -> FunctionDefNode:
        tok = self.current()
        is_async = False
        if tok.type == TokenType.ASYNC:
            is_async = True
            self.advance()

        self.expect(TokenType.FN)
        name = self.expect(TokenType.IDENT).value

        # Generics: fn first<T>(list: Array<T>) -> T
        generic_params = []
        if self.match(TokenType.LT):
            while self.current().type not in (TokenType.GT, TokenType.EOF):
                generic_params.append(self.expect(TokenType.IDENT).value)
                self.match(TokenType.COMMA)
            self.expect(TokenType.GT)

        self.expect(TokenType.LPAREN)
        params: List[FunctionParam] = []
        while self.current().type not in (TokenType.RPAREN, TokenType.EOF):
            if self.current().type == TokenType.IDENT:
                pname = self.advance().value
                ptype = None
                if self.match(TokenType.COLON):
                    ptype = self.parse_type()
                params.append(FunctionParam(pname, ptype))
            self.match(TokenType.COMMA)
        self.expect(TokenType.RPAREN)

        # Return type: -> int
        ret_type = None
        if self.match(TokenType.ARROW):
            ret_type = self.parse_type()

        body = self.parse_block()
        return FunctionDefNode(name, params, ret_type, body, generic_params, is_async, self.last_doc_comment, tok.line, tok.col)

    def parse_block(self) -> List[ASTNode]:
        statements: List[ASTNode] = []
        if self.match(TokenType.LBRACE):
            while self.current().type not in (TokenType.RBRACE, TokenType.EOF):
                if self.match(TokenType.SEMICOLON):
                    continue
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
                while self.match(TokenType.SEMICOLON):
                    pass
            self.expect(TokenType.RBRACE)
        elif self.match(TokenType.COLON):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return statements

    def parse_expression(self) -> ASTNode:
        return self.parse_pipeline()

    def parse_pipeline(self) -> ASTNode:
        node = self.parse_null_coalesce()
        while self.match(TokenType.PIPE):
            # Can be function call or lambda
            if self.current().type in (TokenType.IDENT, TokenType.PRINT, TokenType.INPUT):
                callee_name = self.advance().value
                node = FunctionCallNode(callee_name, [node])
            else:
                expr = self.parse_null_coalesce()
                node = BinaryOpNode(node, "|>", expr)
        return node

    def parse_null_coalesce(self) -> ASTNode:
        node = self.parse_logic_or()
        while self.match(TokenType.NULL_COALESCE):
            right = self.parse_logic_or()
            node = NullCoalesceNode(node, right)
        return node

    def parse_logic_or(self) -> ASTNode:
        node = self.parse_logic_and()
        while self.match(TokenType.OR):
            right = self.parse_logic_and()
            node = BinaryOpNode(node, "or", right)
        return node

    def parse_logic_and(self) -> ASTNode:
        node = self.parse_equality()
        while self.match(TokenType.AND):
            right = self.parse_equality()
            node = BinaryOpNode(node, "and", right)
        return node

    def parse_equality(self) -> ASTNode:
        node = self.parse_relational()
        while self.current().type in (TokenType.EQ, TokenType.NEQ):
            op = self.advance().value
            right = self.parse_relational()
            node = BinaryOpNode(node, op, right)
        return node

    def parse_relational(self) -> ASTNode:
        node = self.parse_additive()
        while self.current().type in (TokenType.GT, TokenType.GTE, TokenType.LT, TokenType.LTE):
            op = self.advance().value
            right = self.parse_additive()
            node = BinaryOpNode(node, op, right)
        return node

    def parse_additive(self) -> ASTNode:
        node = self.parse_multiplicative()
        while self.current().type in (TokenType.PLUS, TokenType.MINUS):
            op = self.advance().value
            right = self.parse_multiplicative()
            node = BinaryOpNode(node, op, right)
        return node

    def parse_multiplicative(self) -> ASTNode:
        node = self.parse_unary()
        while self.current().type in (TokenType.MUL, TokenType.DIV, TokenType.MOD):
            op = self.advance().value
            right = self.parse_unary()
            node = BinaryOpNode(node, op, right)
        return node

    def parse_unary(self) -> ASTNode:
        if self.current().type in (TokenType.MINUS, TokenType.NOT, TokenType.MUL):
            op = self.advance().value
            expr = self.parse_unary()
            return UnaryOpNode(op, expr)
        return self.parse_postfix()

    def parse_postfix(self) -> ASTNode:
        node = self.parse_primary()
        while True:
            # Safe navigation: user?.name
            if self.match(TokenType.SAFE_NAV):
                member_name = self.advance().value
                node = MemberAccessNode(node, member_name, is_safe=True)
            # Regular Member access: user.name or obj.method()
            elif self.match(TokenType.DOT):
                member_name = self.advance().value
                if self.match(TokenType.LPAREN):
                    args = self.parse_args()
                    callee_str = f"{node.name}.{member_name}" if isinstance(node, IdentifierNode) else member_name
                    node = FunctionCallNode(callee_str, args)
                else:
                    node = MemberAccessNode(node, member_name, is_safe=False)
            # Array index: arr[0]
            elif self.match(TokenType.LBRACKET):
                idx = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                node = IndexAccessNode(node, idx)
            # Function Call: fn(a, b)
            elif isinstance(node, IdentifierNode) and self.match(TokenType.LPAREN):
                args = self.parse_args()
                node = FunctionCallNode(node.name, args)
            else:
                break
        return node

    def parse_args(self) -> List[ASTNode]:
        args: List[ASTNode] = []
        if not self.match(TokenType.RPAREN):
            while True:
                args.append(self.parse_expression())
                if self.match(TokenType.COMMA):
                    continue
                self.expect(TokenType.RPAREN)
                break
        return args

    def parse_primary(self) -> ASTNode:
        tok = self.current()
        if tok.type == TokenType.NUMBER: return NumberNode(self.advance().value, tok.line, tok.col)
        if tok.type == TokenType.STRING: return StringNode(self.advance().value, tok.line, tok.col)
        if tok.type == TokenType.BOOLEAN: return BooleanNode(self.advance().value, tok.line, tok.col)
        if tok.type == TokenType.NULL:
            self.advance()
            return NullNode(tok.line, tok.col)
        if tok.type == TokenType.IDENT:
            name = self.advance().value
            # Check for lambda: x => x * 2
            if self.match(TokenType.FAT_ARROW):
                body = self.parse_expression()
                return LambdaNode([name], body, tok.line, tok.col)
            return IdentifierNode(name, tok.line, tok.col)

        # Builtins
        if tok.type in (TokenType.PRINT, TokenType.INPUT, TokenType.ADDR, TokenType.PEEK, TokenType.MEMDUMP, TokenType.CHANNEL):
            func_name = self.advance().value
            if self.match(TokenType.LT):
                # Generic channel<int>()
                t = self.parse_type()
                self.expect(TokenType.GT)
            self.expect(TokenType.LPAREN)
            args = self.parse_args()
            return FunctionCallNode(func_name, args, tok.line, tok.col)

        # (a, b) => a + b (Lambda or Parenthesized expression)
        if self.match(TokenType.LPAREN):
            if self.match(TokenType.RPAREN):
                if self.match(TokenType.FAT_ARROW):
                    body = self.parse_expression()
                    return LambdaNode([], body, tok.line, tok.col)
                return NullNode(tok.line, tok.col)
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr

        # Array literal [1, 2, 3]
        if self.match(TokenType.LBRACKET):
            elements: List[ASTNode] = []
            if not self.match(TokenType.RBRACKET):
                while True:
                    elements.append(self.parse_expression())
                    if self.match(TokenType.COMMA):
                        continue
                    self.expect(TokenType.RBRACKET)
                    break
            return ArrayNode(elements, tok.line, tok.col)

        DiagnosticEmitter.emit_error(
            self.filepath, self.source, tok.line, tok.col,
            "E1000", "Unexpected token in expression",
            expected="expression, literal, or identifier",
            found=f"{tok.type} ('{tok.value}')"
        )

# =========================================================
# 3. SEMANTIC ANALYZER & TYPE CHECKER
# =========================================================
class TypeChecker:
    def __init__(self, ast: ProgramNode, source: str, filepath: str):
        self.ast = ast
        self.source = source
        self.filepath = filepath
        self.symbol_table: Dict[str, str] = {
            "print": "fn", "input": "fn", "addr": "fn", "peek": "fn", "memdump": "fn",
            "delay_ms": "fn", "to_int": "fn", "to_str": "fn", "to_string": "fn",
            "is_number": "fn", "contains": "fn"
        }
        self.is_inside_unsafe = False
        self.warnings: List[str] = []

    def check(self):
        for stmt in self.ast.statements:
            self.visit(stmt)

    def visit(self, node: ASTNode):
        if isinstance(node, VarDeclNode):
            inferred = self.infer_type(node.expr)
            if node.type_annot:
                expected = node.type_annot.name
                if node.type_annot.is_optional and inferred == "null":
                    pass
                elif expected != "any" and inferred != "any" and expected != inferred and not (expected == "float" and inferred == "int"):
                    DiagnosticEmitter.emit_error(
                        self.filepath, self.source, node.line, node.col,
                        "E1024", f"Type mismatch in variable declaration '{node.name}'",
                        expected=expected, found=inferred,
                        help_msg=f"Consider converting the value to '{expected}' or change the type annotation."
                    )
            self.symbol_table[node.name] = node.type_annot.name if node.type_annot else inferred

        elif isinstance(node, UnsafeBlockNode):
            prev = self.is_inside_unsafe
            self.is_inside_unsafe = True
            for s in node.body:
                self.visit(s)
            self.is_inside_unsafe = prev

        elif isinstance(node, FunctionCallNode):
            # Check unsafe memory calls
            if node.callee in ("peek", "memdump") and not self.is_inside_unsafe:
                DiagnosticEmitter.emit_error(
                    self.filepath, self.source, node.line, node.col,
                    "E1050", f"Unsafe memory operation '{node.callee}()' called outside of unsafe block",
                    expected="unsafe { ... } block",
                    found="safe context",
                    help_msg="Wrap raw pointer dereferencing and memory inspections inside 'unsafe { ... }'."
                )
            for a in node.args:
                self.visit(a)

        elif isinstance(node, FunctionDefNode):
            for s in node.body:
                self.visit(s)

        elif isinstance(node, IfNode):
            for s in node.then_branch: self.visit(s)
            for _, b in node.elif_branches:
                for s in b: self.visit(s)
            if node.else_branch:
                for s in node.else_branch: self.visit(s)

        elif isinstance(node, WhileNode):
            for s in node.body: self.visit(s)

        elif isinstance(node, ForNode):
            self.symbol_table[node.var_name] = "int"
            for s in node.body: self.visit(s)

    def infer_type(self, node: ASTNode) -> str:
        if isinstance(node, NumberNode):
            return "float" if isinstance(node.value, float) else "int"
        if isinstance(node, StringNode):
            return "string"
        if isinstance(node, BooleanNode):
            return "bool"
        if isinstance(node, NullNode):
            return "null"
        if isinstance(node, ArrayNode):
            return "Array"
        if isinstance(node, IdentifierNode):
            return self.symbol_table.get(node.name, "any")
        if isinstance(node, BinaryOpNode):
            if node.op in ("==", "!=", ">", "<", ">=", "<=", "and", "or"):
                return "bool"
            return self.infer_type(node.left)
        return "any"
