import sys
import os
import re
from typing import List, Dict, Any, Optional

# =========================================================
# 1. TOKENS DEFINITION
# =========================================================
class TokenType:
    # Declarations & Modifiers
    VAR = "VAR"
    LET = "LET"
    SET = "SET"
    CONST = "CONST"
    FN = "FN"
    STRUCT = "STRUCT"
    TRAIT = "TRAIT"
    IMPL = "IMPL"
    TYPE_ALIAS = "TYPE_ALIAS"
    ENUM = "ENUM"
    UNSAFE = "UNSAFE"
    EXTERN = "EXTERN"
    
    # Concurrency & Async
    ASYNC = "ASYNC"
    AWAIT = "AWAIT"
    SPAWN = "SPAWN"
    CHANNEL = "CHANNEL"
    
    # Testing & Verification
    TEST = "TEST"
    ASSERT = "ASSERT"
    
    # Flow Control
    IF = "IF"
    ELSE = "ELSE"
    ELIF = "ELIF"
    FOR = "FOR"
    IN = "IN"
    LOOP = "LOOP"
    WHILE = "WHILE"
    MATCH = "MATCH"
    TRY = "TRY"
    CATCH = "CATCH"
    THROW = "THROW"
    RETURN = "RETURN"
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"
    USE = "USE"
    
    # Builtins
    PRINT = "PRINT"
    ADDR = "ADDR"
    PEEK = "PEEK"
    MEMDUMP = "MEMDUMP"
    INPUT = "INPUT"
    
    # Literals
    IDENT = "IDENT"
    NUMBER = "NUMBER"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    NULL = "NULL"
    DOC_COMMENT = "DOC_COMMENT"
    
    # Operators & Delimiters
    ASSIGN = "ASSIGN"         # =
    ARROW = "ARROW"           # ->
    FAT_ARROW = "FAT_ARROW"   # =>
    PIPE = "PIPE"             # |>
    SAFE_NAV = "SAFE_NAV"     # ?.
    NULL_COALESCE = "NULL_COALESCE" # ??
    
    PLUS = "PLUS"             # +
    MINUS = "MINUS"           # -
    MUL = "MUL"               # *
    DIV = "DIV"               # /
    MOD = "MOD"               # %
    
    EQ = "EQ"                 # ==
    NEQ = "NEQ"               # !=
    GTE = "GTE"               # >=
    LTE = "LTE"               # <=
    GT = "GT"                 # >
    LT = "LT"                 # <
    
    AND = "AND"               # and, &&
    OR = "OR"                 # or, ||
    NOT = "NOT"               # not, !
    
    LPAREN = "LPAREN"         # (
    RPAREN = "RPAREN"         # )
    LBRACKET = "LBRACKET"     # [
    RBRACKET = "RBRACKET"     # ]
    LBRACE = "LBRACE"         # {
    RBRACE = "RBRACE"         # }
    COMMA = "COMMA"           # ,
    COLON = "COLON"           # :
    DOT = "DOT"               # .
    DOTDOT = "DOTDOT"         # ..
    QUESTION = "QUESTION"     # ?
    
    TARGET_DIR = "TARGET"
    EOF = "EOF"

class Token:
    def __init__(self, type_: str, value: Any, line: int, col: int):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, L:{self.line}:{self.col})"

# =========================================================
# 2. LEXER
# =========================================================
class Lexer:
    def __init__(self, source: str, filepath: str = "<memory>"):
        self.source = source
        self.filepath = filepath
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens: List[Token] = []

    def error(self, msg: str):
        lines = self.source.splitlines()
        line_content = lines[self.line - 1] if self.line <= len(lines) else ""
        pointer = " " * max(0, self.col - 1) + "^^^"
        print(f"\nerror[E0001]: Lexer Error in {self.filepath}:{self.line}:{self.col}")
        print(f"  {self.line:4d} | {line_content}")
        print(f"       | {pointer}")
        print(f"  = note: {msg}\n")
        sys.exit(1)

    def tokenize(self) -> List[Token]:
        length = len(self.source)
        while self.pos < length:
            ch = self.source[self.pos]

            if ch == '\n':
                self.line += 1
                self.col = 1
                self.pos += 1
                continue
            if ch.isspace():
                self.col += 1
                self.pos += 1
                continue

            # Doc comment: /// ...
            if self.source[self.pos:self.pos+3] == "///":
                start_col = self.col
                self.pos += 3
                self.col += 3
                start_doc = self.pos
                while self.pos < length and self.source[self.pos] != '\n':
                    self.pos += 1
                    self.col += 1
                doc_text = self.source[start_doc:self.pos].strip()
                self.tokens.append(Token(TokenType.DOC_COMMENT, doc_text, self.line, start_col))
                continue

            # Regular line comment: // ...
            if self.source[self.pos:self.pos+2] == "//":
                while self.pos < length and self.source[self.pos] != '\n':
                    self.pos += 1
                continue

            # Block comment: /* ... */
            if self.source[self.pos:self.pos+2] == "/*":
                self.pos += 2
                self.col += 2
                while self.pos + 1 < length and not (self.source[self.pos] == '*' and self.source[self.pos + 1] == '/'):
                    if self.source[self.pos] == '\n':
                        self.line += 1
                        self.col = 1
                    else:
                        self.col += 1
                    self.pos += 1
                self.pos += 2
                self.col += 2
                continue

            # Directives (#target)
            if ch == '#' and self.source[self.pos:self.pos+7] == "#target":
                start_col = self.col
                self.pos += 7
                self.col += 7
                while self.pos < length and self.source[self.pos].isspace() and self.source[self.pos] != '\n':
                    self.pos += 1
                    self.col += 1
                start_val = self.pos
                while self.pos < length and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
                    self.pos += 1
                    self.col += 1
                target_val = self.source[start_val:self.pos]
                self.tokens.append(Token(TokenType.TARGET_DIR, target_val, self.line, start_col))
                continue

            # Multi-character symbols
            if self.source[self.pos:self.pos+2] == "?.":
                self.tokens.append(Token(TokenType.SAFE_NAV, "?.", self.line, self.col))
                self.pos += 2; self.col += 2; continue
            if self.source[self.pos:self.pos+2] == "??":
                self.tokens.append(Token(TokenType.NULL_COALESCE, "??", self.line, self.col))
                self.pos += 2; self.col += 2; continue
            if self.source[self.pos:self.pos+2] == "=>":
                self.tokens.append(Token(TokenType.FAT_ARROW, "=>", self.line, self.col))
                self.pos += 2; self.col += 2; continue
            if self.source[self.pos:self.pos+2] == "->":
                self.tokens.append(Token(TokenType.ARROW, "->", self.line, self.col))
                self.pos += 2; self.col += 2; continue
            if self.source[self.pos:self.pos+2] == "|>":
                self.tokens.append(Token(TokenType.PIPE, "|>", self.line, self.col))
                self.pos += 2; self.col += 2; continue
            if self.source[self.pos:self.pos+2] == "..":
                self.tokens.append(Token(TokenType.DOTDOT, "..", self.line, self.col))
                self.pos += 2; self.col += 2; continue
            if self.source[self.pos:self.pos+2] == "==":
                self.tokens.append(Token(TokenType.EQ, "==", self.line, self.col))
                self.pos += 2; self.col += 2; continue
            if self.source[self.pos:self.pos+2] == "!=":
                self.tokens.append(Token(TokenType.NEQ, "!=", self.line, self.col))
                self.pos += 2; self.col += 2; continue
            if self.source[self.pos:self.pos+2] == ">=":
                self.tokens.append(Token(TokenType.GTE, ">=", self.line, self.col))
                self.pos += 2; self.col += 2; continue
            if self.source[self.pos:self.pos+2] == "<=":
                self.tokens.append(Token(TokenType.LTE, "<=", self.line, self.col))
                self.pos += 2; self.col += 2; continue
            if self.source[self.pos:self.pos+2] == "&&":
                self.tokens.append(Token(TokenType.AND, "and", self.line, self.col))
                self.pos += 2; self.col += 2; continue
            if self.source[self.pos:self.pos+2] == "||":
                self.tokens.append(Token(TokenType.OR, "or", self.line, self.col))
                self.pos += 2; self.col += 2; continue

            # String literals
            if ch in ('"', "'"):
                quote = ch
                start_col = self.col
                self.pos += 1
                self.col += 1
                buf = []
                while self.pos < length and self.source[self.pos] != quote:
                    if self.source[self.pos] == '\\' and self.pos + 1 < length:
                        esc = self.source[self.pos + 1]
                        if esc == 'n': buf.append('\n')
                        elif esc == 't': buf.append('\t')
                        elif esc == 'r': buf.append('\r')
                        elif esc == '\\': buf.append('\\')
                        elif esc == quote: buf.append(quote)
                        else: buf.append(esc)
                        self.pos += 2
                        self.col += 2
                    else:
                        if self.source[self.pos] == '\n':
                            self.line += 1
                            self.col = 1
                        else:
                            self.col += 1
                        buf.append(self.source[self.pos])
                        self.pos += 1
                if self.pos >= length:
                    self.error("Unterminated string literal")
                self.pos += 1
                self.col += 1
                self.tokens.append(Token(TokenType.STRING, "".join(buf), self.line, start_col))
                continue

            # Numbers (hex, float, int)
            if ch.isdigit() or (ch == '.' and self.pos + 1 < length and self.source[self.pos + 1].isdigit()):
                start_col = self.col
                start_pos = self.pos
                if ch == '0' and self.pos + 1 < length and self.source[self.pos + 1] in ('x', 'X'):
                    self.pos += 2
                    self.col += 2
                    while self.pos < length and (self.source[self.pos].isdigit() or self.source[self.pos] in "abcdefABCDEF"):
                        self.pos += 1
                        self.col += 1
                    val = int(self.source[start_pos:self.pos], 16)
                    self.tokens.append(Token(TokenType.NUMBER, val, self.line, start_col))
                    continue

                is_float = False
                while self.pos < length and (self.source[self.pos].isdigit() or self.source[self.pos] == '.'):
                    if self.source[self.pos] == '.':
                        if self.pos + 1 < length and self.source[self.pos + 1] == '.':
                            break
                        is_float = True
                    self.pos += 1
                    self.col += 1
                raw_num = self.source[start_pos:self.pos]
                val = float(raw_num) if is_float else int(raw_num)
                self.tokens.append(Token(TokenType.NUMBER, val, self.line, start_col))
                continue

            # Identifiers and Keywords ($ accepted)
            if ch.isalpha() or ch == '_' or ch == '$':
                start_col = self.col
                start_pos = self.pos
                while self.pos < length and (self.source[self.pos].isalnum() or self.source[self.pos] in ('_', '$')):
                    self.pos += 1
                    self.col += 1
                ident = self.source[start_pos:self.pos]
                clean = ident.lstrip('$')

                kw = {
                    "var": TokenType.VAR, "let": TokenType.LET, "set": TokenType.SET, "const": TokenType.CONST,
                    "fn": TokenType.FN, "def": TokenType.FN,
                    "struct": TokenType.STRUCT, "trait": TokenType.TRAIT, "impl": TokenType.IMPL,
                    "type": TokenType.TYPE_ALIAS, "enum": TokenType.ENUM,
                    "unsafe": TokenType.UNSAFE, "extern": TokenType.EXTERN,
                    "async": TokenType.ASYNC, "await": TokenType.AWAIT, "spawn": TokenType.SPAWN, "channel": TokenType.CHANNEL,
                    "test": TokenType.TEST, "assert": TokenType.ASSERT,
                    "return": TokenType.RETURN, "continue": TokenType.CONTINUE, "break": TokenType.BREAK,
                    "if": TokenType.IF, "else": TokenType.ELSE, "elif": TokenType.ELIF,
                    "for": TokenType.FOR, "in": TokenType.IN, "loop": TokenType.LOOP, "while": TokenType.WHILE,
                    "match": TokenType.MATCH, "try": TokenType.TRY, "catch": TokenType.CATCH, "throw": TokenType.THROW,
                    "use": TokenType.USE, "import": TokenType.USE,
                    "print": TokenType.PRINT, "input": TokenType.INPUT,
                    "addr": TokenType.ADDR, "peek": TokenType.PEEK, "memdump": TokenType.MEMDUMP,
                    "and": TokenType.AND, "or": TokenType.OR, "not": TokenType.NOT,
                    "true": TokenType.BOOLEAN, "false": TokenType.BOOLEAN, "null": TokenType.NULL
                }

                if clean in kw:
                    tt = kw[clean]
                    v = True if clean == "true" else (False if clean == "false" else (None if clean == "null" else clean))
                    self.tokens.append(Token(tt, v, self.line, start_col))
                else:
                    self.tokens.append(Token(TokenType.IDENT, clean, self.line, start_col))
                continue

            single = {
                '=': TokenType.ASSIGN, '+': TokenType.PLUS, '-': TokenType.MINUS,
                '*': TokenType.MUL, '/': TokenType.DIV, '%': TokenType.MOD,
                '>': TokenType.GT, '<': TokenType.LT, '!': TokenType.NOT,
                '(': TokenType.LPAREN, ')': TokenType.RPAREN,
                '[': TokenType.LBRACKET, ']': TokenType.RBRACKET,
                '{': TokenType.LBRACE, '}': TokenType.RBRACE,
                ',': TokenType.COMMA, ':': TokenType.COLON, '.': TokenType.DOT,
                '?': TokenType.QUESTION
            }
            if ch in single:
                self.tokens.append(Token(single[ch], ch, self.line, self.col))
                self.pos += 1
                self.col += 1
                continue

            self.error(f"Unexpected character: '{ch}'")

        self.tokens.append(Token(TokenType.EOF, "EOF", self.line, self.col))
        return self.tokens

# =========================================================
# 3. TYPED AST NODES
# =========================================================
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
    def __init__(self, name: str, is_optional: bool = False, is_pointer: bool = False, generic_args: Optional[List['TypeNode']] = None, line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.name = name
        self.is_optional = is_optional
        self.is_pointer = is_pointer
        self.generic_args = generic_args or []

    def __str__(self):
        base = f"*{self.name}" if self.is_pointer else self.name
        if self.generic_args:
            args_s = ", ".join(str(a) for a in self.generic_args)
            base += f"<{args_s}>"
        return f"{base}?" if self.is_optional else base

class VarDeclNode(ASTNode):
    def __init__(self, name: str, type_annot: Optional[TypeNode], expr: ASTNode, is_const: bool = False, line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.name = name
        self.type_annot = type_annot
        self.expr = expr
        self.is_const = is_const

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

class FunctionParam:
    def __init__(self, name: str, type_annot: Optional[TypeNode] = None):
        self.name = name
        self.type_annot = type_annot

class FunctionDefNode(ASTNode):
    def __init__(self, name: str, params: List[FunctionParam], return_type: Optional[TypeNode], body: List[ASTNode], generic_params: Optional[List[str]] = None, is_async: bool = False, doc_comment: str = "", line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body
        self.generic_params = generic_params or []
        self.is_async = is_async
        self.doc_comment = doc_comment

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
    def __init__(self, var_name: str, start_expr: ASTNode, end_expr: ASTNode, body: List[ASTNode], line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.var_name = var_name
        self.start_expr = start_expr
        self.end_expr = end_expr
        self.body = body

class ReturnNode(ASTNode):
    def __init__(self, expr: Optional[ASTNode], line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.expr = expr

class BreakNode(ASTNode): pass
class ContinueNode(ASTNode): pass

class FunctionCallNode(ASTNode):
    def __init__(self, callee: str, args: List[ASTNode], line: int = 1, col: int = 1):
        super().__init__(line, col)
        self.callee = callee
        self.args = args
