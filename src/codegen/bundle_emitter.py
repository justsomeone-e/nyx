import os
import struct
from typing import List, Dict, Any, Optional, Tuple

from src.core.ast_nodes import (
    ASTNode, ProgramNode, FunctionDefNode, VarDeclNode, AssignNode,
    NumberNode, StringNode, BooleanNode, NullNode, IdentifierNode,
    BinaryOpNode, UnaryOpNode, IfNode, WhileNode, ForNode,
    ReturnNode, BreakNode, ContinueNode, FunctionCallNode, TypeNode
)

# WASM Value Types
WASM_TYPE_I32 = 0x7F
WASM_TYPE_I64 = 0x7E
WASM_TYPE_F32 = 0x7D
WASM_TYPE_F64 = 0x7C
WASM_TYPE_VOID = 0x40

# WASM Opcodes
OP_UNREACHABLE = 0x00
OP_NOP = 0x01
OP_BLOCK = 0x02
OP_LOOP = 0x03
OP_IF = 0x04
OP_ELSE = 0x05
OP_END = 0x0B
OP_BR = 0x0C
OP_BR_IF = 0x0D
OP_RETURN = 0x0F
OP_CALL = 0x10
OP_DROP = 0x1A

OP_LOCAL_GET = 0x20
OP_LOCAL_SET = 0x21
OP_LOCAL_TEE = 0x22
OP_GLOBAL_GET = 0x23
OP_GLOBAL_SET = 0x24

OP_I32_LOAD = 0x28
OP_I32_LOAD8_U = 0x2D
OP_I32_STORE = 0x36
OP_I32_STORE8 = 0x3A

OP_I32_CONST = 0x41
OP_I64_CONST = 0x42
OP_F64_CONST = 0x44

OP_I32_EQZ = 0x45
OP_I32_EQ = 0x46
OP_I32_NE = 0x47
OP_I32_LT_S = 0x48
OP_I32_LT_U = 0x49
OP_I32_GT_S = 0x4A
OP_I32_GT_U = 0x4B
OP_I32_LE_S = 0x4C
OP_I32_LE_U = 0x4D
OP_I32_GE_S = 0x4E
OP_I32_GE_U = 0x4F

OP_I32_ADD = 0x6A
OP_I32_SUB = 0x6B
OP_I32_MUL = 0x6C
OP_I32_DIV_S = 0x6D
OP_I32_REM_S = 0x6F
OP_I32_AND = 0x71
OP_I32_OR = 0x72
OP_I32_XOR = 0x73
OP_I32_SHL = 0x74
OP_I32_SHR_S = 0x75
OP_I32_SHR_U = 0x76

OP_I64_SHL = 0x86
OP_I64_OR = 0x84
OP_I64_EXTEND_I32_U = 0xAD

OP_F64_EQ = 0x61
OP_F64_NE = 0x62
OP_F64_LT = 0x63
OP_F64_GT = 0x64
OP_F64_LE = 0x65
OP_F64_GE = 0x66
OP_F64_NEG = 0x8C
OP_F64_ADD = 0xA0
OP_F64_SUB = 0xA1
OP_F64_MUL = 0xA2
OP_F64_DIV = 0xA3


def encode_u32(val: int) -> bytes:
    res = bytearray()
    val = int(val)
    while True:
        byte = val & 0x7F
        val >>= 7
        if val != 0:
            byte |= 0x80
        res.append(byte)
        if val == 0:
            break
    return bytes(res)


def encode_sleb128(val: int) -> bytes:
    res = bytearray()
    val = int(val)
    more = True
    while more:
        byte = val & 0x7F
        val >>= 7
        if (val == 0 and (byte & 0x40) == 0) or (val == -1 and (byte & 0x40) != 0):
            more = False
        else:
            byte |= 0x80
        res.append(byte)
    return bytes(res)


def encode_f64(val: float) -> bytes:
    return struct.pack("<d", float(val))


class WasmFunctionCompiler:
    def __init__(self, fn_node: FunctionDefNode, fn_table: Dict[str, int]):
        self.fn_node = fn_node
        self.fn_table = fn_table
        self.locals: Dict[str, Tuple[int, str]] = {}
        self.local_types: List[int] = []
        self.num_params = 0
        self.control_stack: List[Tuple[str, Optional[str]]] = []
        self.ret_type = getattr(fn_node.return_type, "name", "void") if fn_node.return_type else "void"
        self._init_params()

    def _init_params(self):
        idx = 0
        for p in self.fn_node.params:
            p_type = getattr(p.type_annot, "name", "int") if hasattr(p, "type_annot") and p.type_annot else "int"
            if p_type == "string":
                self.locals[f"{p.name}_ptr"] = (idx, "i32")
                self.locals[f"{p.name}_len"] = (idx + 1, "i32")
                self.locals[p.name] = (idx, "string")
                idx += 2
            elif p_type == "float":
                self.locals[p.name] = (idx, "float")
                idx += 1
            else:
                self.locals[p.name] = (idx, "int")
                idx += 1
        self.num_params = idx

    def allocate_local(self, name: str, type_str: str = "int") -> int:
        idx = self.num_params + len(self.local_types)
        wasm_t = WASM_TYPE_F64 if type_str == "float" else (WASM_TYPE_I64 if type_str == "i64" else WASM_TYPE_I32)
        self.local_types.append(wasm_t)
        self.locals[name] = (idx, type_str)
        return idx

    def allocate_temp(self, type_str: str = "int") -> int:
        temp_name = f"__tmp_{len(self.local_types)}"
        return self.allocate_local(temp_name, type_str)

    def compile_bytecode(self) -> Tuple[List[int], bytes]:
        code = bytearray()
        for stmt in self.fn_node.body:
            code.extend(self._compile_stmt_bytes(stmt))

        if self.ret_type == "int" or self.ret_type == "bool":
            code.extend([OP_I32_CONST] + list(encode_sleb128(0)))
        elif self.ret_type == "float":
            code.extend([OP_F64_CONST] + list(encode_f64(0.0)))
        elif self.ret_type == "string":
            code.extend([OP_I64_CONST] + list(encode_sleb128(0)))

        code.append(OP_END)
        return self.local_types, bytes(code)

    def _compile_stmt_bytes(self, stmt: ASTNode) -> bytes:
        code = bytearray()
        if isinstance(stmt, VarDeclNode):
            val_type = "float" if isinstance(stmt.expr, NumberNode) and isinstance(stmt.expr.value, float) else "int"
            local_idx = self.allocate_local(stmt.name, val_type)
            code.extend(self._compile_expr_bytes(stmt.expr))
            code.append(OP_LOCAL_SET)
            code.extend(encode_u32(local_idx))

        elif isinstance(stmt, AssignNode):
            target_name = stmt.target.name if isinstance(stmt.target, IdentifierNode) else str(stmt.target)
            if target_name not in self.locals:
                local_idx = self.allocate_local(target_name, "int")
            else:
                local_idx, _ = self.locals[target_name]
            code.extend(self._compile_expr_bytes(stmt.expr))
            code.append(OP_LOCAL_SET)
            code.extend(encode_u32(local_idx))

        elif isinstance(stmt, IfNode):
            code.extend(self._compile_expr_bytes(stmt.condition))
            code.extend([OP_IF, WASM_TYPE_VOID])
            for s in stmt.then_branch:
                code.extend(self._compile_stmt_bytes(s))
            if stmt.else_branch or stmt.elif_branches:
                code.append(OP_ELSE)
                if stmt.elif_branches:
                    for elif_cond, elif_body in stmt.elif_branches:
                        code.extend(self._compile_expr_bytes(elif_cond))
                        code.extend([OP_IF, WASM_TYPE_VOID])
                        for s in elif_body:
                            code.extend(self._compile_stmt_bytes(s))
                        code.append(OP_ELSE)
                if stmt.else_branch:
                    for s in stmt.else_branch:
                        code.extend(self._compile_stmt_bytes(s))
                if stmt.elif_branches:
                    for _ in stmt.elif_branches:
                        code.append(OP_END)
            code.append(OP_END)

        elif isinstance(stmt, WhileNode):
            self.control_stack.append(("block", None))
            self.control_stack.append(("loop", None))
            code.extend([OP_BLOCK, WASM_TYPE_VOID])
            code.extend([OP_LOOP, WASM_TYPE_VOID])
            code.extend(self._compile_expr_bytes(stmt.condition))
            code.append(OP_I32_EQZ)
            code.append(OP_BR_IF)
            code.extend(encode_u32(1))
            for s in stmt.body:
                code.extend(self._compile_stmt_bytes(s))
            code.append(OP_BR)
            code.extend(encode_u32(0))
            code.append(OP_END)
            code.append(OP_END)
            self.control_stack.pop()
            self.control_stack.pop()

        elif isinstance(stmt, ForNode):
            loop_var_idx = self.allocate_local(stmt.var_name, "int")
            end_val_idx = self.allocate_temp("int")
            code.extend(self._compile_expr_bytes(stmt.start_expr or NumberNode(0)))
            code.append(OP_LOCAL_SET)
            code.extend(encode_u32(loop_var_idx))
            code.extend(self._compile_expr_bytes(stmt.end_expr or NumberNode(0)))
            code.append(OP_LOCAL_SET)
            code.extend(encode_u32(end_val_idx))
            self.control_stack.append(("block", None))
            self.control_stack.append(("loop", None))
            code.extend([OP_BLOCK, WASM_TYPE_VOID])
            code.extend([OP_LOOP, WASM_TYPE_VOID])
            code.append(OP_LOCAL_GET)
            code.extend(encode_u32(loop_var_idx))
            code.append(OP_LOCAL_GET)
            code.extend(encode_u32(end_val_idx))
            code.append(OP_I32_GT_S)
            code.append(OP_BR_IF)
            code.extend(encode_u32(1))
            for s in stmt.body:
                code.extend(self._compile_stmt_bytes(s))
            code.append(OP_LOCAL_GET)
            code.extend(encode_u32(loop_var_idx))
            code.extend([OP_I32_CONST] + list(encode_sleb128(1)))
            code.append(OP_I32_ADD)
            code.append(OP_LOCAL_SET)
            code.extend(encode_u32(loop_var_idx))
            code.append(OP_BR)
            code.extend(encode_u32(0))
            code.append(OP_END)
            code.append(OP_END)
            self.control_stack.pop()
            self.control_stack.pop()

        elif isinstance(stmt, BreakNode):
            depth = 0
            for kind, _ in reversed(self.control_stack):
                if kind == "block":
                    break
                depth += 1
            code.append(OP_BR)
            code.extend(encode_u32(depth))

        elif isinstance(stmt, ContinueNode):
            depth = 0
            for kind, _ in reversed(self.control_stack):
                if kind == "loop":
                    break
                depth += 1
            code.append(OP_BR)
            code.extend(encode_u32(depth))

        elif isinstance(stmt, ReturnNode):
            if stmt.expr:
                if self.ret_type == "string":
                    code.extend(self._compile_string_return_bytes(stmt.expr))
                else:
                    code.extend(self._compile_expr_bytes(stmt.expr))
            code.append(OP_RETURN)

        else:
            code.extend(self._compile_expr_bytes(stmt))
            if hasattr(stmt, "is_expr") or isinstance(stmt, (BinaryOpNode, FunctionCallNode)):
                code.append(OP_DROP)

        return bytes(code)

    def _compile_expr_bytes(self, expr: ASTNode) -> bytes:
        code = bytearray()
        if isinstance(expr, NumberNode):
            if isinstance(expr.value, float):
                code.append(OP_F64_CONST)
                code.extend(encode_f64(expr.value))
            else:
                code.append(OP_I32_CONST)
                code.extend(encode_sleb128(int(expr.value)))

        elif isinstance(expr, BooleanNode):
            code.append(OP_I32_CONST)
            code.extend(encode_sleb128(1 if expr.value else 0))

        elif isinstance(expr, NullNode):
            code.append(OP_I32_CONST)
            code.extend(encode_sleb128(0))

        elif isinstance(expr, IdentifierNode):
            if expr.name in self.locals:
                idx, _ = self.locals[expr.name]
                code.append(OP_LOCAL_GET)
                code.extend(encode_u32(idx))
            else:
                code.append(OP_I32_CONST)
                code.extend(encode_sleb128(0))

        elif isinstance(expr, UnaryOpNode):
            if expr.op in ("-", "neg"):
                code.extend([OP_I32_CONST] + list(encode_sleb128(0)))
                code.extend(self._compile_expr_bytes(expr.expr))
                code.append(OP_I32_SUB)
            elif expr.op in ("not", "!"):
                code.extend(self._compile_expr_bytes(expr.expr))
                code.append(OP_I32_EQZ)
            elif expr.op == "~":
                code.extend(self._compile_expr_bytes(expr.expr))
                code.extend([OP_I32_CONST] + list(encode_sleb128(-1)))
                code.append(OP_I32_XOR)

        elif isinstance(expr, BinaryOpNode):
            code.extend(self._compile_expr_bytes(expr.left))
            code.extend(self._compile_expr_bytes(expr.right))
            op_map = {
                "+": OP_I32_ADD, "-": OP_I32_SUB, "*": OP_I32_MUL, "/": OP_I32_DIV_S,
                "%": OP_I32_REM_S, "<<": OP_I32_SHL, ">>": OP_I32_SHR_S,
                "&": OP_I32_AND, "|": OP_I32_OR, "^": OP_I32_XOR,
                "==": OP_I32_EQ, "!=": OP_I32_NE, "<": OP_I32_LT_S,
                "<=": OP_I32_LE_S, ">": OP_I32_GT_S, ">=": OP_I32_GE_S,
                "and": OP_I32_AND, "or": OP_I32_OR
            }
            if expr.op in op_map:
                code.append(op_map[expr.op])

        elif isinstance(expr, FunctionCallNode):
            callee = expr.callee if isinstance(expr.callee, str) else getattr(expr.callee, "name", "")
            if callee in self.fn_table:
                fn_idx = self.fn_table[callee]
                for arg in expr.args:
                    code.extend(self._compile_expr_bytes(arg))
                code.append(OP_CALL)
                code.extend(encode_u32(fn_idx))
            elif callee == "to_string" and len(expr.args) == 1:
                code.extend(self._compile_expr_bytes(expr.args[0]))
            else:
                code.append(OP_I32_CONST)
                code.extend(encode_sleb128(0))

        return bytes(code)

    def _compile_string_return_bytes(self, expr: ASTNode) -> bytes:
        code = bytearray()
        out_ptr_idx = self.allocate_temp("i32")

        if isinstance(expr, IdentifierNode) and f"{expr.name}_ptr" in self.locals:
            in_ptr_idx, _ = self.locals[f"{expr.name}_ptr"]
            in_len_idx, _ = self.locals[f"{expr.name}_len"]
            code.append(OP_LOCAL_GET)
            code.extend(encode_u32(in_len_idx))
            code.append(OP_CALL)
            code.extend(encode_u32(1))
            code.append(OP_LOCAL_TEE)
            code.extend(encode_u32(out_ptr_idx))
            code.append(OP_LOCAL_GET)
            code.extend(encode_u32(in_ptr_idx))
            code.append(OP_LOCAL_GET)
            code.extend(encode_u32(in_len_idx))
            code.extend([0xFC, 0x0A, 0x00, 0x00])
            code.append(OP_LOCAL_GET)
            code.extend(encode_u32(in_len_idx))
            code.append(OP_I64_EXTEND_I32_U)
            code.extend([OP_I64_CONST] + list(encode_sleb128(32)))
            code.append(OP_I64_SHL)
            code.append(OP_LOCAL_GET)
            code.extend(encode_u32(out_ptr_idx))
            code.append(OP_I64_EXTEND_I32_U)
            code.append(OP_I64_OR)

        elif isinstance(expr, StringNode):
            str_bytes = expr.value.encode("utf-8")
            s_len = len(str_bytes)
            code.extend([OP_I32_CONST] + list(encode_sleb128(s_len)))
            code.append(OP_CALL)
            code.extend(encode_u32(1))
            code.append(OP_LOCAL_SET)
            code.extend(encode_u32(out_ptr_idx))

            for offset, b in enumerate(str_bytes):
                code.append(OP_LOCAL_GET)
                code.extend(encode_u32(out_ptr_idx))
                code.extend([OP_I32_CONST] + list(encode_sleb128(b)))
                code.extend([OP_I32_STORE8, 0x00])
                code.extend(encode_u32(offset))

            code.extend([OP_I64_CONST] + list(encode_sleb128(s_len)))
            code.extend([OP_I64_CONST] + list(encode_sleb128(32)))
            code.append(OP_I64_SHL)
            code.append(OP_LOCAL_GET)
            code.extend(encode_u32(out_ptr_idx))
            code.append(OP_I64_EXTEND_I32_U)
            code.append(OP_I64_OR)

        elif isinstance(expr, BinaryOpNode) and expr.op == "+":
            parts = self._flatten_concat(expr)
            total_len_idx = self.allocate_temp("i32")
            cur_offset_idx = self.allocate_temp("i32")

            code.extend([OP_I32_CONST] + list(encode_sleb128(0)))
            for p in parts:
                if isinstance(p, StringNode):
                    code.extend([OP_I32_CONST] + list(encode_sleb128(len(p.value.encode("utf-8")))))
                    code.append(OP_I32_ADD)
                elif isinstance(p, IdentifierNode) and f"{p.name}_len" in self.locals:
                    len_idx, _ = self.locals[f"{p.name}_len"]
                    code.append(OP_LOCAL_GET)
                    code.extend(encode_u32(len_idx))
                    code.append(OP_I32_ADD)
            code.append(OP_LOCAL_SET)
            code.extend(encode_u32(total_len_idx))

            code.append(OP_LOCAL_GET)
            code.extend(encode_u32(total_len_idx))
            code.append(OP_CALL)
            code.extend(encode_u32(1))
            code.append(OP_LOCAL_SET)
            code.extend(encode_u32(out_ptr_idx))

            code.extend([OP_I32_CONST] + list(encode_sleb128(0)))
            code.append(OP_LOCAL_SET)
            code.extend(encode_u32(cur_offset_idx))

            for p in parts:
                if isinstance(p, StringNode):
                    p_bytes = p.value.encode("utf-8")
                    for b in p_bytes:
                        code.append(OP_LOCAL_GET)
                        code.extend(encode_u32(out_ptr_idx))
                        code.append(OP_LOCAL_GET)
                        code.extend(encode_u32(cur_offset_idx))
                        code.append(OP_I32_ADD)
                        code.extend([OP_I32_CONST] + list(encode_sleb128(b)))
                        code.extend([OP_I32_STORE8, 0x00, 0x00])
                        code.append(OP_LOCAL_GET)
                        code.extend(encode_u32(cur_offset_idx))
                        code.extend([OP_I32_CONST] + list(encode_sleb128(1)))
                        code.append(OP_I32_ADD)
                        code.append(OP_LOCAL_SET)
                        code.extend(encode_u32(cur_offset_idx))

                elif isinstance(p, IdentifierNode) and f"{p.name}_ptr" in self.locals:
                    p_ptr_idx, _ = self.locals[f"{p.name}_ptr"]
                    p_len_idx, _ = self.locals[f"{p.name}_len"]
                    code.append(OP_LOCAL_GET)
                    code.extend(encode_u32(out_ptr_idx))
                    code.append(OP_LOCAL_GET)
                    code.extend(encode_u32(cur_offset_idx))
                    code.append(OP_I32_ADD)
                    code.append(OP_LOCAL_GET)
                    code.extend(encode_u32(p_ptr_idx))
                    code.append(OP_LOCAL_GET)
                    code.extend(encode_u32(p_len_idx))
                    code.extend([0xFC, 0x0A, 0x00, 0x00])
                    code.append(OP_LOCAL_GET)
                    code.extend(encode_u32(cur_offset_idx))
                    code.append(OP_LOCAL_GET)
                    code.extend(encode_u32(p_len_idx))
                    code.append(OP_I32_ADD)
                    code.append(OP_LOCAL_SET)
                    code.extend(encode_u32(cur_offset_idx))

            code.append(OP_LOCAL_GET)
            code.extend(encode_u32(total_len_idx))
            code.append(OP_I64_EXTEND_I32_U)
            code.extend([OP_I64_CONST] + list(encode_sleb128(32)))
            code.append(OP_I64_SHL)
            code.append(OP_LOCAL_GET)
            code.extend(encode_u32(out_ptr_idx))
            code.append(OP_I64_EXTEND_I32_U)
            code.append(OP_I64_OR)

        else:
            code.extend(self._compile_expr_bytes(expr))
            code.append(OP_I64_EXTEND_I32_U)

        return bytes(code)

    def _flatten_concat(self, node: ASTNode) -> List[ASTNode]:
        if isinstance(node, BinaryOpNode) and node.op == "+":
            return self._flatten_concat(node.left) + self._flatten_concat(node.right)
        if isinstance(node, FunctionCallNode) and getattr(node, "callee", "") == "to_string" and len(node.args) == 1:
            return [node.args[0]]
        return [node]

    def compile_wat(self) -> List[str]:
        lines = []
        for name, (idx, type_str) in self.locals.items():
            if idx >= self.num_params and not name.startswith("__tmp_"):
                wtype = "f64" if type_str == "float" else ("i64" if type_str == "i64" else "i32")
                lines.append(f"    (local ${name} {wtype})")

        for stmt in self.fn_node.body:
            lines.extend(self._compile_stmt_wat(stmt))

        return lines

    def _compile_stmt_wat(self, stmt: ASTNode) -> List[str]:
        lines = []
        if isinstance(stmt, VarDeclNode):
            val_type = "float" if isinstance(stmt.expr, NumberNode) and isinstance(stmt.expr.value, float) else "int"
            self.allocate_local(stmt.name, val_type)
            lines.append(f"    (local.set ${stmt.name} {self._compile_expr_wat(stmt.expr)})")

        elif isinstance(stmt, AssignNode):
            target_name = stmt.target.name if isinstance(stmt.target, IdentifierNode) else str(stmt.target)
            lines.append(f"    (local.set ${target_name} {self._compile_expr_wat(stmt.expr)})")

        elif isinstance(stmt, IfNode):
            lines.append(f"    (if {self._compile_expr_wat(stmt.condition)}")
            lines.append("      (then")
            for s in stmt.then_branch:
                lines.extend(self._compile_stmt_wat(s))
            lines.append("      )")
            if stmt.else_branch:
                lines.append("      (else")
                for s in stmt.else_branch:
                    lines.extend(self._compile_stmt_wat(s))
                lines.append("      )")
            lines.append("    )")

        elif isinstance(stmt, WhileNode):
            lines.append("    (block $B")
            lines.append("      (loop $L")
            lines.append(f"        (br_if $B (i32.eqz {self._compile_expr_wat(stmt.condition)}))")
            for s in stmt.body:
                lines.extend(self._compile_stmt_wat(s))
            lines.append("        (br $L)")
            lines.append("      )")
            lines.append("    )")

        elif isinstance(stmt, ForNode):
            loop_var = stmt.var_name
            self.allocate_local(loop_var, "int")
            start_s = self._compile_expr_wat(stmt.start_expr or NumberNode(0))
            end_s = self._compile_expr_wat(stmt.end_expr or NumberNode(0))
            lines.append(f"    (local.set ${loop_var} {start_s})")
            lines.append(f"    (block $B_{loop_var}")
            lines.append(f"      (loop $L_{loop_var}")
            lines.append(f"        (br_if $B_{loop_var} (i32.gt_s (local.get ${loop_var}) {end_s}))")
            for s in stmt.body:
                lines.extend(self._compile_stmt_wat(s))
            lines.append(f"        (local.set ${loop_var} (i32.add (local.get ${loop_var}) (i32.const 1)))")
            lines.append(f"        (br $L_{loop_var})")
            lines.append("      )")
            lines.append("    )")

        elif isinstance(stmt, ReturnNode):
            if stmt.expr:
                if self.ret_type == "string":
                    lines.extend(self._compile_string_return_wat(stmt.expr))
                else:
                    lines.append(f"    {self._compile_expr_wat(stmt.expr)}")
            lines.append("    (return)")

        return lines

    def _compile_expr_wat(self, expr: ASTNode) -> str:
        if isinstance(expr, NumberNode):
            if isinstance(expr.value, float):
                return f"(f64.const {expr.value})"
            return f"(i32.const {expr.value})"
        if isinstance(expr, BooleanNode):
            return "(i32.const 1)" if expr.value else "(i32.const 0)"
        if isinstance(expr, IdentifierNode):
            return f"(local.get ${expr.name})"
        if isinstance(expr, UnaryOpNode):
            if expr.op in ("-", "neg"):
                return f"(i32.sub (i32.const 0) {self._compile_expr_wat(expr.expr)})"
            if expr.op in ("not", "!"):
                return f"(i32.eqz {self._compile_expr_wat(expr.expr)})"
        if isinstance(expr, BinaryOpNode):
            left_s = self._compile_expr_wat(expr.left)
            right_s = self._compile_expr_wat(expr.right)
            op_map = {
                "+": "i32.add", "-": "i32.sub", "*": "i32.mul", "/": "i32.div_s",
                "%": "i32.rem_s", "<<": "i32.shl", ">>": "i32.shr_s",
                "&": "i32.and", "|": "i32.or", "^": "i32.xor",
                "==": "i32.eq", "!=": "i32.ne", "<": "i32.lt_s",
                "<=": "i32.le_s", ">": "i32.gt_s", ">=": "i32.ge_s",
                "and": "i32.and", "or": "i32.or"
            }
            wat_op = op_map.get(expr.op, "i32.add")
            return f"({wat_op} {left_s} {right_s})"
        return "(i32.const 0)"

    def _compile_string_return_wat(self, expr: ASTNode) -> List[str]:
        lines = []
        if isinstance(expr, IdentifierNode) and f"{expr.name}_ptr" in self.locals:
            lines.extend([
                "    (local $out_ptr i32)",
                f"    (local.set $out_ptr (call $__nyx_alloc (local.get ${expr.name}_len)))",
                f"    (memory.copy (local.get $out_ptr) (local.get ${expr.name}_ptr) (local.get ${expr.name}_len))",
                f"    (i64.or (i64.shl (i64.extend_i32_u (local.get ${expr.name}_len)) (i64.const 32)) (i64.extend_i32_u (local.get $out_ptr)))"
            ])
        else:
            lines.append("    (i64.const 0)")
        return lines


class BundleEmitter:
    def __init__(self, ast: ProgramNode, module_name: str = "nyx_module"):
        self.ast = ast
        self.module_name = module_name

    def get_exported_functions(self) -> List[FunctionDefNode]:
        fns = []
        for s in self.ast.statements:
            if isinstance(s, FunctionDefNode) and not s.name.startswith("_") and s.name != "main":
                fns.append(s)
        return fns

    def _get_function_table(self) -> Dict[str, int]:
        table = {
            "__nyx_abi_version": 0,
            "__nyx_alloc": 1,
            "__nyx_free": 2,
        }
        for i, fn in enumerate(self.get_exported_functions()):
            table[fn.name] = 3 + i
        return table

    def emit_wat(self) -> str:
        lines = [
            f";; Auto-generated by nyx bundle ({self.module_name}) - ABI v1",
            "(module",
            '  (memory (export "memory") 2)',
            '  (global $heap_ptr (mut i32) (i32.const 2048))',
            "",
            "  ;; --- ABI Version ---",
            '  (func $__nyx_abi_version (export "__nyx_abi_version") (result i32)',
            "    (i32.const 1)",
            "  )",
            "",
            "  ;; --- Bump Pointer Allocator ---",
            '  (func $__nyx_alloc (export "__nyx_alloc") (param $size i32) (result i32)',
            "    (local $ptr i32)",
            "    (local.set $ptr (global.get $heap_ptr))",
            "    ;; 8-byte alignment",
            "    (global.set $heap_ptr (i32.and (i32.add (i32.add (local.get $ptr) (local.get $size)) (i32.const 7)) (i32.const -8)))",
            "    (local.get $ptr)",
            "  )",
            "",
            '  (func $__nyx_free (export "__nyx_free") (param $ptr i32) (param $size i32)',
            "    ;; Caller-owned free entry point",
            "  )",
            ""
        ]

        fn_table = self._get_function_table()

        for fn in self.get_exported_functions():
            param_defs = []
            for p in fn.params:
                p_type = getattr(p.type_annot, "name", "int") if hasattr(p, "type_annot") and p.type_annot else "int"
                if p_type == "string":
                    param_defs.append(f"(param ${p.name}_ptr i32) (param ${p.name}_len i32)")
                elif p_type == "float":
                    param_defs.append(f"(param ${p.name} f64)")
                else:
                    param_defs.append(f"(param ${p.name} i32)")

            params_s = " ".join(param_defs)
            ret_type = getattr(fn.return_type, "name", "void") if fn.return_type else "void"

            if ret_type == "string":
                ret_s = "(result i64)"
            elif ret_type == "float":
                ret_s = "(result f64)"
            elif ret_type == "void":
                ret_s = ""
            else:
                ret_s = "(result i32)"

            lines.append(f'  (func ${fn.name} (export "{fn.name}") {params_s} {ret_s}')
            compiler = WasmFunctionCompiler(fn, fn_table)
            lines.extend(compiler.compile_wat())
            lines.append("  )")
            lines.append("")

        lines.append(")")
        return "\n".join(lines)

    def emit_wasm_bytes(self) -> bytes:
        wasm = bytearray(b"\x00\x61\x73\x6d\x01\x00\x00\x00")
        exported_fns = self.get_exported_functions()
        fn_table = self._get_function_table()

        types: List[Tuple[Tuple[int, ...], Tuple[int, ...]]] = [
            ((), (WASM_TYPE_I32,)),
            ((WASM_TYPE_I32,), (WASM_TYPE_I32,)),
            ((WASM_TYPE_I32, WASM_TYPE_I32), ()),
        ]

        fn_type_indices: List[int] = [0, 1, 2]

        for fn in exported_fns:
            param_types: List[int] = []
            for p in fn.params:
                p_t = getattr(p.type_annot, "name", "int") if hasattr(p, "type_annot") and p.type_annot else "int"
                if p_t == "string":
                    param_types.extend([WASM_TYPE_I32, WASM_TYPE_I32])
                elif p_t == "float":
                    param_types.append(WASM_TYPE_F64)
                else:
                    param_types.append(WASM_TYPE_I32)

            ret_t = getattr(fn.return_type, "name", "void") if fn.return_type else "void"
            if ret_t == "string":
                return_types: Tuple[int, ...] = (WASM_TYPE_I64,)
            elif ret_t == "float":
                return_types = (WASM_TYPE_F64,)
            elif ret_t == "void":
                return_types = ()
            else:
                return_types = (WASM_TYPE_I32,)

            sig = (tuple(param_types), return_types)
            if sig not in types:
                types.append(sig)
            fn_type_indices.append(types.index(sig))

        type_sec = bytearray()
        type_sec.extend(encode_u32(len(types)))
        for params, results in types:
            type_sec.append(0x60)
            type_sec.extend(encode_u32(len(params)))
            type_sec.extend(params)
            type_sec.extend(encode_u32(len(results)))
            type_sec.extend(results)

        wasm.append(0x01)
        wasm.extend(encode_u32(len(type_sec)))
        wasm.extend(type_sec)

        fn_sec = bytearray()
        fn_sec.extend(encode_u32(len(fn_type_indices)))
        for type_idx in fn_type_indices:
            fn_sec.extend(encode_u32(type_idx))

        wasm.append(0x03)
        wasm.extend(encode_u32(len(fn_sec)))
        wasm.extend(fn_sec)

        mem_sec = bytearray([0x01, 0x00, 0x02])
        wasm.append(0x05)
        wasm.extend(encode_u32(len(mem_sec)))
        wasm.extend(mem_sec)

        glob_sec = bytearray([0x01, WASM_TYPE_I32, 0x01, OP_I32_CONST, 0x80, 0x10, OP_END])
        wasm.append(0x06)
        wasm.extend(encode_u32(len(glob_sec)))
        wasm.extend(glob_sec)

        exp_sec = bytearray()
        exp_count = 4 + len(exported_fns)
        exp_sec.extend(encode_u32(exp_count))

        exp_sec.extend(self._encode_string("memory") + bytes([0x02, 0x00]))
        exp_sec.extend(self._encode_string("__nyx_abi_version") + bytes([0x00, 0x00]))
        exp_sec.extend(self._encode_string("__nyx_alloc") + bytes([0x00, 0x01]))
        exp_sec.extend(self._encode_string("__nyx_free") + bytes([0x00, 0x02]))

        for i, fn in enumerate(exported_fns):
            fn_idx = 3 + i
            exp_sec.extend(self._encode_string(fn.name) + bytes([0x00]) + encode_u32(fn_idx))

        wasm.append(0x07)
        wasm.extend(encode_u32(len(exp_sec)))
        wasm.extend(exp_sec)

        code_sec = bytearray()
        total_fns = 3 + len(exported_fns)
        code_sec.extend(encode_u32(total_fns))

        code_sec.extend(self._encode_fn_body([], bytes([OP_I32_CONST, 0x01, OP_END])))

        alloc_bytes = bytes([
            OP_GLOBAL_GET, 0x00,
            OP_LOCAL_TEE, 0x01,
            OP_LOCAL_GET, 0x00,
            OP_I32_ADD,
            OP_I32_CONST, 0x07,
            OP_I32_ADD,
            OP_I32_CONST, 0x78,
            OP_I32_AND,
            OP_GLOBAL_SET, 0x00,
            OP_LOCAL_GET, 0x01,
            OP_END
        ])
        code_sec.extend(self._encode_fn_body([WASM_TYPE_I32], alloc_bytes))
        code_sec.extend(self._encode_fn_body([], bytes([OP_END])))

        for fn in exported_fns:
            compiler = WasmFunctionCompiler(fn, fn_table)
            local_types, body_code = compiler.compile_bytecode()
            code_sec.extend(self._encode_fn_body(local_types, body_code))

        wasm.append(0x0A)
        wasm.extend(encode_u32(len(code_sec)))
        wasm.extend(code_sec)

        return bytes(wasm)

    def _encode_string(self, s: str) -> bytes:
        utf8 = s.encode("utf-8")
        return encode_u32(len(utf8)) + utf8

    def _encode_fn_body(self, locals_list: List[int], opcodes: bytes) -> bytes:
        body = bytearray()
        if not locals_list:
            body.append(0x00)
        else:
            groups: List[Tuple[int, int]] = []
            for t in locals_list:
                if groups and groups[-1][1] == t:
                    groups[-1] = (groups[-1][0] + 1, t)
                else:
                    groups.append((1, t))
            body.extend(encode_u32(len(groups)))
            for count, t in groups:
                body.extend(encode_u32(count))
                body.append(t)

        body.extend(opcodes)
        return encode_u32(len(body)) + bytes(body)

    def emit_mjs(self) -> str:
        lines = [
            f"// Auto-generated by nyx bundle ({self.module_name}.mjs) - ABI v1",
            "// Target: ES2022 / Node.js / Browser WebAssembly Runtime",
            "",
            "const instanceCache = new Map();",
            "let wasmInstance = null;",
            "let wasmMemory = null;",
            "let alloc = null;",
            "let dealloc = null;",
            "",
            "export async function initNyxModule(source) {",
            f"  const cacheKey = typeof source === 'string' ? source : './{self.module_name}.wasm';",
            "  if (instanceCache.has(cacheKey)) {",
            "    const cached = await instanceCache.get(cacheKey);",
            "    setupInstance(cached);",
            "    return createPublicApi();",
            "  }",
            "",
            "  const initPromise = (async () => {",
            "    const importObject = {",
            "      env: {",
            "        print: (v) => console.log(v),",
            "        abort: () => { throw new WebAssembly.RuntimeError('Nyx Aborted'); }",
            "      }",
            "    };",
            "",
            "    let instance;",
            "    const isNode = typeof process !== 'undefined' && process.versions && process.versions.node;",
            "",
            "    if (typeof source === 'string' || !source) {",
            f"      const targetPath = source || './{self.module_name}.wasm';",
            "      if (isNode && !targetPath.startsWith('http://') && !targetPath.startsWith('https://')) {",
            "        const fs = await import('fs/promises');",
            "        const bytes = await fs.readFile(targetPath);",
            "        const instantiated = await WebAssembly.instantiate(bytes, importObject);",
            "        instance = instantiated.instance;",
            "      } else {",
            "        const res = await fetch(targetPath);",
            "        if (!res.ok) throw new Error(`Failed to load WASM from ${targetPath}: HTTP ${res.status}`);",
            "        const instantiated = await WebAssembly.instantiateStreaming(res, importObject);",
            "        instance = instantiated.instance;",
            "      }",
            "    } else if (source instanceof URL) {",
            "      const res = await fetch(source);",
            "      const instantiated = await WebAssembly.instantiateStreaming(res, importObject);",
            "      instance = instantiated.instance;",
            "    } else if (source instanceof ArrayBuffer || source instanceof Uint8Array) {",
            "      const instantiated = await WebAssembly.instantiate(source, importObject);",
            "      instance = instantiated.instance;",
            "    } else if (source instanceof WebAssembly.Module) {",
            "      instance = await WebAssembly.instantiate(source, importObject);",
            "    } else {",
            "      throw new TypeError('Invalid WASM source provided to initNyxModule');",
            "    }",
            "",
            "    const abiVer = instance.exports.__nyx_abi_version ? instance.exports.__nyx_abi_version() : 0;",
            "    if (abiVer !== 1) {",
            "      throw new Error(`Incompatible Nyx ABI version: expected 1, found ${abiVer}`);",
            "    }",
            "",
            "    return instance;",
            "  })();",
            "",
            "  instanceCache.set(cacheKey, initPromise);",
            "  const readyInstance = await initPromise;",
            "  setupInstance(readyInstance);",
            "  return createPublicApi();",
            "}",
            "",
            "function setupInstance(instance) {",
            "  wasmInstance = instance;",
            "  wasmMemory = instance.exports.memory;",
            "  alloc = instance.exports.__nyx_alloc;",
            "  dealloc = instance.exports.__nyx_free;",
            "}",
            "",
            "function getMemoryBuffer() {",
            "  return new Uint8Array(wasmMemory.buffer);",
            "}",
            "",
            "function passStringToWasm(str) {",
            "  if (str === null || str === undefined || str === '') {",
            "    return { ptr: 0, len: 0 };",
            "  }",
            "  const encoded = new TextEncoder().encode(str);",
            "  const ptr = alloc(encoded.length);",
            "  const view = getMemoryBuffer();",
            "  view.set(encoded, ptr);",
            "  return { ptr, len: encoded.length };",
            "}",
            "",
            "function readStringFromPacked(packedBigInt) {",
            "  if (!packedBigInt || packedBigInt === 0n) return '';",
            "  const val = BigInt(packedBigInt);",
            "  const ptr = Number(val & 0xFFFFFFFFn);",
            "  const len = Number((val >> 32n) & 0xFFFFFFFFn);",
            "  if (len === 0 || ptr === 0) return '';",
            "  if (ptr + len > wasmMemory.buffer.byteLength) {",
            "    throw new RangeError(`WASM memory access out of bounds: ptr=${ptr}, len=${len}, max=${wasmMemory.buffer.byteLength}`);",
            "  }",
            "  const view = getMemoryBuffer();",
            "  const bytes = view.subarray(ptr, ptr + len);",
            "  const decoded = new TextDecoder('utf-8').decode(bytes);",
            "  if (ptr !== 0 && dealloc) dealloc(ptr, len);",
            "  return decoded;",
            "}",
            "",
            "function createPublicApi() {",
            "  return {",
        ]

        for fn in self.get_exported_functions():
            lines.append(f"    {fn.name}: {fn.name},")
        lines.append("  };")
        lines.append("}")
        lines.append("")

        for fn in self.get_exported_functions():
            param_names = [p.name for p in fn.params]
            params_s = ", ".join(param_names)
            lines.append(f"export function {fn.name}({params_s}) {{")
            lines.append("  if (!wasmInstance) throw new Error('Nyx module not initialized. Call await initNyxModule(...) first.');")

            allocated_cleanups = []
            call_args = []

            for p in fn.params:
                p_t = getattr(p.type_annot, "name", "int") if hasattr(p, "type_annot") and p.type_annot else "int"
                if p_t == "string":
                    lines.append(f"  const _{p.name}_boxed = passStringToWasm({p.name});")
                    call_args.append(f"_{p.name}_boxed.ptr, _{p.name}_boxed.len")
                    allocated_cleanups.append(f"if (_{p.name}_boxed.ptr !== 0 && dealloc) dealloc(_{p.name}_boxed.ptr, _{p.name}_boxed.len);")
                elif p_t == "float":
                    call_args.append(f"Number({p.name})")
                else:
                    call_args.append(f"({p.name} | 0)")

            call_args_str = ", ".join(call_args)
            ret_t = getattr(fn.return_type, "name", "void") if fn.return_type else "void"

            if allocated_cleanups:
                lines.append("  try {")
                if ret_t == "string":
                    lines.append(f"    const packed = wasmInstance.exports.{fn.name}({call_args_str});")
                    lines.append("    return readStringFromPacked(packed);")
                elif ret_t == "void":
                    lines.append(f"    wasmInstance.exports.{fn.name}({call_args_str});")
                else:
                    lines.append(f"    return wasmInstance.exports.{fn.name}({call_args_str});")
                lines.append("  } finally {")
                for c in allocated_cleanups:
                    lines.append(f"    {c}")
                lines.append("  }")
            else:
                if ret_t == "string":
                    lines.append(f"  const packed = wasmInstance.exports.{fn.name}({call_args_str});")
                    lines.append("  return readStringFromPacked(packed);")
                elif ret_t == "void":
                    lines.append(f"  wasmInstance.exports.{fn.name}({call_args_str});")
                else:
                    lines.append(f"  return wasmInstance.exports.{fn.name}({call_args_str});")
            lines.append("}")
            lines.append("")

        return "\n".join(lines)

    def emit_dts(self) -> str:
        lines = [
            f"// Auto-generated by nyx bundle ({self.module_name}.d.ts) - ABI v1",
            "// Type definitions for nyx WebAssembly Polyglot Module",
            "",
            "export interface NyxModule {",
        ]

        type_map = {
            "int": "number",
            "float": "number",
            "string": "string",
            "bool": "boolean",
            "void": "void"
        }

        for fn in self.get_exported_functions():
            params = []
            for p in fn.params:
                p_t = getattr(p.type_annot, "name", "any") if hasattr(p, "type_annot") and p.type_annot else "any"
                params.append(f"{p.name}: {type_map.get(p_t, 'any')}")
            p_str = ", ".join(params)
            ret_t = getattr(fn.return_type, "name", "void") if fn.return_type else "void"
            ts_ret = type_map.get(ret_t, "void")
            lines.append(f"  {fn.name}({p_str}): {ts_ret};")

        lines.extend([
            "}",
            "",
            "export function initNyxModule(source?: string | URL | ArrayBuffer | Uint8Array | WebAssembly.Module): Promise<NyxModule>;",
            ""
        ])

        for fn in self.get_exported_functions():
            params = []
            for p in fn.params:
                p_t = getattr(p.type_annot, "name", "any") if hasattr(p, "type_annot") and p.type_annot else "any"
                params.append(f"{p.name}: {type_map.get(p_t, 'any')}")
            p_str = ", ".join(params)
            ret_t = getattr(fn.return_type, "name", "void") if fn.return_type else "void"
            ts_ret = type_map.get(ret_t, "void")
            lines.append(f"export function {fn.name}({p_str}): {ts_ret};")

        return "\n".join(lines) + "\n"

    def emit_react(self) -> str:
        lines = [
            "'use client';",
            f"// Auto-generated by nyx bundle ({self.module_name}.react.tsx) - React 19 Suspense Hook",
            "import { use } from 'react';",
            f"import {{ initNyxModule, type NyxModule }} from './{self.module_name}.mjs';",
            f"export * from './{self.module_name}.mjs';",
            "",
            "const modulePromiseCache = new Map<string, Promise<NyxModule>>();",
            "",
            f"function getModulePromise(wasmUrl: string = './{self.module_name}.wasm'): Promise<NyxModule> {{",
            "  if (!modulePromiseCache.has(wasmUrl)) {",
            "    modulePromiseCache.set(wasmUrl, initNyxModule(wasmUrl));",
            "  }",
            "  return modulePromiseCache.get(wasmUrl)!;",
            "}",
            "",
            f"export function useNyxModule(wasmUrl: string = './{self.module_name}.wasm'): NyxModule {{",
            "  return use(getModulePromise(wasmUrl));",
            "}",
            ""
        ]
        return "\n".join(lines)