from typing import Any

class TokenType:
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
    
    ASYNC = "ASYNC"
    AWAIT = "AWAIT"
    SPAWN = "SPAWN"
    CHANNEL = "CHANNEL"
    
    TEST = "TEST"
    ASSERT = "ASSERT"
    
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
    IMPORT = "IMPORT"
    FROM = "FROM"
    AS = "AS"
    
    PRINT = "PRINT"
    ADDR = "ADDR"
    PEEK = "PEEK"
    MEMDUMP = "MEMDUMP"
    INPUT = "INPUT"
    
    IDENT = "IDENT"
    NUMBER = "NUMBER"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    NULL = "NULL"
    DOC_COMMENT = "DOC_COMMENT"
    
    ASSIGN = "ASSIGN"
    ARROW = "ARROW"
    FAT_ARROW = "FAT_ARROW"
    PIPE = "PIPE"
    SAFE_NAV = "SAFE_NAV"
    NULL_COALESCE = "NULL_COALESCE"
    
    PLUS = "PLUS"
    MINUS = "MINUS"
    MUL = "MUL"
    DIV = "DIV"
    MOD = "MOD"
    
    EQ = "EQ"
    NEQ = "NEQ"
    GTE = "GTE"
    LTE = "LTE"
    GT = "GT"
    LT = "LT"
    
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    COMMA = "COMMA"
    COLON = "COLON"
    DOT = "DOT"
    DOTDOT = "DOTDOT"
    QUESTION = "QUESTION"
    SEMICOLON = "SEMICOLON"
    
    TARGET_DIR = "TARGET"
    NATIVE_INCLUDE = "NATIVE_INCLUDE"
    NATIVE_LINK = "NATIVE_LINK"
    NATIVE_RAW = "NATIVE_RAW"
    NATIVE_USE = "NATIVE_USE"
    EOF = "EOF"

class Token:
    def __init__(self, type_: str, value: Any, line: int, col: int):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, L:{self.line}:{self.col})"
