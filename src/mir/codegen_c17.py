"""C17 source emitter for legalized scalar/control-flow MIR."""

from __future__ import annotations

import json
import math
import re

from .codegen_cpp import MIRCodegenError
from .legalization import legalize_mir
from .model import (
    AssertTerminator, AssignStatement, BinaryRValue, CallTerminator,
    ConstOperand, CopyOperand, GotoTerminator, MIRFunction, MIRModule,
    MoveOperand, NopStatement, Operand, ReturnTerminator,
    StorageDeadStatement, StorageLiveStatement, SwitchIntTerminator,
    SwitchValueTerminator, UnaryRValue, UnreachableTerminator, UseRValue,
)
from .types import MIRType


_PRELUDE = r'''/* Experimental Nyx legalized MIR -> C17 output. */
#include <inttypes.h>
#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct NyxAllocation {
    char *value;
    struct NyxAllocation *next;
} NyxAllocation;

static NyxAllocation *nyx_allocations = NULL;

static void nyx_cleanup(void) {
    while (nyx_allocations != NULL) {
        NyxAllocation *allocation = nyx_allocations;
        nyx_allocations = allocation->next;
        free(allocation->value);
        free(allocation);
    }
}

static char *nyx_track_string(size_t length) {
    char *value = (char *)malloc(length);
    NyxAllocation *allocation = (NyxAllocation *)malloc(sizeof(NyxAllocation));
    if (value == NULL || allocation == NULL) {
        free(value);
        free(allocation);
        fputs("Nyx C17 allocation failed\n", stderr);
        exit(1);
    }
    allocation->value = value;
    allocation->next = nyx_allocations;
    nyx_allocations = allocation;
    return value;
}

static const char *nyx_concat(const char *left, const char *right) {
    size_t left_length = strlen(left);
    size_t right_length = strlen(right);
    char *result = nyx_track_string(left_length + right_length + 1);
    memcpy(result, left, left_length);
    memcpy(result + left_length, right, right_length + 1);
    return result;
}

static uint64_t nyx_i64_bits(int64_t value) {
    uint64_t bits;
    memcpy(&bits, &value, sizeof(bits));
    return bits;
}

static int64_t nyx_i64_from_bits(uint64_t bits) {
    int64_t value;
    memcpy(&value, &bits, sizeof(value));
    return value;
}

static int64_t nyx_i64_add(int64_t left, int64_t right) {
    return nyx_i64_from_bits(nyx_i64_bits(left) + nyx_i64_bits(right));
}

static int64_t nyx_i64_sub(int64_t left, int64_t right) {
    return nyx_i64_from_bits(nyx_i64_bits(left) - nyx_i64_bits(right));
}

static int64_t nyx_i64_mul(int64_t left, int64_t right) {
    return nyx_i64_from_bits(nyx_i64_bits(left) * nyx_i64_bits(right));
}

static int64_t nyx_i64_div(int64_t left, int64_t right) {
    if (right == 0) { fputs("division by zero\n", stderr); exit(1); }
    if (left == INT64_MIN && right == -1) return INT64_MIN;
    return left / right;
}

static int64_t nyx_i64_rem(int64_t left, int64_t right) {
    if (right == 0) { fputs("remainder by zero\n", stderr); exit(1); }
    if (left == INT64_MIN && right == -1) return 0;
    return left % right;
}

static int64_t nyx_i64_shl(int64_t left, int64_t right) {
    return nyx_i64_from_bits(nyx_i64_bits(left) << (nyx_i64_bits(right) & 63U));
}

static int64_t nyx_i64_shr(int64_t left, int64_t right) {
    uint64_t count = nyx_i64_bits(right) & 63U;
    uint64_t bits = nyx_i64_bits(left);
    if (count == 0) return left;
    uint64_t shifted = bits >> count;
    if ((bits & (UINT64_C(1) << 63)) != 0) shifted |= UINT64_MAX << (64U - count);
    return nyx_i64_from_bits(shifted);
}

static int64_t nyx_i64_neg(int64_t value) {
    return nyx_i64_from_bits(UINT64_C(0) - nyx_i64_bits(value));
}

static void nyx_print_i64(int64_t value) { printf("%" PRId64, value); }
static void nyx_print_f64(double value) { printf("%.16g", value); }
static void nyx_print_bool(bool value) { fputs(value ? "true" : "false", stdout); }
static void nyx_print_string(const char *value) { fputs(value, stdout); }'''


def _identifier(value: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9_]", "_", value)
    if not clean or clean[0].isdigit():
        clean = "_" + clean
    return clean


class _C17Emitter:
    def __init__(self, module: MIRModule):
        self.module = module
        self.function_names = {
            function.symbol: f"nyx_fn_{_identifier(function.name)}"
            for function in module.functions
        }
        self.function_names.update({
            function.name: self.function_names[function.symbol]
            for function in module.functions
        })
        self.functions = {function.symbol: function for function in module.functions}
        self.functions.update({function.name: function for function in module.functions})
        self.current: MIRFunction | None = None
        self.local_types: dict[int, MIRType] = {}

    def emit(self) -> str:
        parts = [_PRELUDE, "", "/* Nyx function declarations. */"]
        parts.extend(self._prototype(function) + ";" for function in self.module.functions)
        parts.append("")
        parts.extend(self._function(function) + "\n" for function in self.module.functions)
        parts.append(self._entry_point())
        return "\n".join(parts).rstrip() + "\n"

    def _prototype(self, function: MIRFunction) -> str:
        parameters = ", ".join(
            f"{self._type(function.locals[local].type, function)} l{local}"
            for local in function.parameters
        ) or "void"
        return f"static {self._type(function.locals[function.return_local].type, function)} {self.function_names[function.symbol]}({parameters})"

    def _entry_point(self) -> str:
        by_name = {function.name: function for function in self.module.functions}
        entry = by_name.get("main") or by_name.get("__nyx_top_level")
        lines = ["int main(void) {", "    if (atexit(nyx_cleanup) != 0) return 1;"]
        if entry is not None:
            call = f"{self.function_names[entry.symbol]}()"
            result = self._type(entry.locals[entry.return_local].type, entry)
            lines.append(f"    {call};" if result == "void" else f"    (void){call};")
        lines.extend(("    return 0;", "}"))
        return "\n".join(lines)

    def _function(self, function: MIRFunction) -> str:
        self.current = function
        self.local_types = {local.id: local.type for local in function.locals}
        lines = [self._prototype(function) + " {"]
        parameter_ids = set(function.parameters)
        for local in function.locals:
            rendered = self._type(local.type, function)
            if local.id in parameter_ids or rendered == "void":
                continue
            lines.append(f"    {rendered} l{local.id} = {self._default(local.type)};")
        lines.extend(("    int pc = 0;", "    for (;;) {", "        switch (pc) {"))
        for block in function.blocks:
            lines.append(f"        case {block.id}:")
            for statement in block.statements:
                lines.extend(f"            {line}" for line in self._statement(statement))
            lines.extend(f"            {line}" for line in self._terminator(block.terminator))
        lines.extend(("        default:", "            fputs(\"invalid MIR block\\n\", stderr);", "            exit(1);", "        }", "    }", "}"))
        self.current = None
        self.local_types = {}
        return "\n".join(lines)

    def _statement(self, value: object) -> list[str]:
        if isinstance(value, AssignStatement):
            if value.place.projections:
                raise MIRCodegenError("projected assignment reached the scalar C17 emitter")
            if self.local_types[value.place.local].name in ("void", "any"):
                return []
            return [f"l{value.place.local} = {self._rvalue(value.value)};"]
        if isinstance(value, (StorageLiveStatement, StorageDeadStatement, NopStatement)):
            return []
        raise MIRCodegenError(f"illegal statement reached C17 emitter: {type(value).__name__}")

    def _terminator(self, value: object) -> list[str]:
        if isinstance(value, GotoTerminator):
            return self._goto(value.target)
        if isinstance(value, (SwitchIntTerminator, SwitchValueTerminator)):
            discriminator = self._operand(value.discriminator)
            discriminator_type = self._operand_type(value.discriminator)
            lines: list[str] = []
            for expected, target in value.targets:
                rendered = self._constant(expected, discriminator_type)
                comparison = (
                    f"strcmp({discriminator}, {rendered}) == 0"
                    if discriminator_type.name == "string"
                    else f"{discriminator} == {rendered}"
                )
                lines.append(f"if ({comparison}) {{")
                lines.extend(f"    {line}" for line in self._goto(target))
                lines.append("}")
            lines.extend(self._goto(value.otherwise))
            return lines
        if isinstance(value, CallTerminator):
            if value.target is None:
                raise MIRCodegenError(f"call '{value.function}' has no continuation")
            arguments = ", ".join(self._operand(argument) for argument in value.arguments)
            if value.function == "builtin::print":
                lines = []
                for index, argument in enumerate(value.arguments):
                    if index:
                        lines.append("fputc(' ', stdout);")
                    lines.append(f"{self._print_function(self._operand_type(argument))}({self._operand(argument)});")
                lines.append("fputc('\\n', stdout);")
                return lines + self._goto(value.target)
            if value.function not in self.function_names:
                raise MIRCodegenError(f"illegal runtime call reached C17 emitter: {value.function}")
            call = f"{self.function_names[value.function]}({arguments})"
            callee = self.functions[value.function]
            result = self._type(callee.locals[callee.return_local].type, callee)
            line = (
                f"l{value.destination.local} = {call};"
                if value.destination is not None and result != "void"
                else f"{call};"
            )
            return [line] + self._goto(value.target)
        if isinstance(value, AssertTerminator):
            expected = "true" if value.expected else "false"
            message = json.dumps(value.message, ensure_ascii=False)
            return [
                f"if (((bool)({self._operand(value.condition)})) != {expected}) {{",
                f"    fputs({message}, stderr);",
                "    fputc('\\n', stderr);",
                "    exit(1);",
                "}",
            ] + self._goto(value.target)
        if isinstance(value, ReturnTerminator):
            assert self.current is not None
            result = self._type(self.current.locals[self.current.return_local].type, self.current)
            return ["return;"] if result == "void" else ["return l0;"]
        if isinstance(value, UnreachableTerminator):
            return ["fputs(\"reached unreachable MIR terminator\\n\", stderr);", "exit(1);"]
        raise MIRCodegenError(f"illegal terminator reached C17 emitter: {type(value).__name__}")

    @staticmethod
    def _goto(target: int) -> list[str]:
        return [f"pc = {target};", "continue;"]

    def _rvalue(self, value: object) -> str:
        if isinstance(value, UseRValue):
            return self._operand(value.operand)
        if isinstance(value, BinaryRValue):
            return self._binary(value)
        if isinstance(value, UnaryRValue):
            operand = self._operand(value.operand)
            if value.op in ("!", "not"):
                return f"!({operand})"
            if value.op == "+":
                return operand
            if value.op == "-" and value.type.name == "int":
                return f"nyx_i64_neg({operand})"
            if value.op == "-":
                return f"-({operand})"
            if value.op == "~":
                return f"nyx_i64_from_bits(~nyx_i64_bits({operand}))"
            raise MIRCodegenError(f"unsupported C17 unary operation '{value.op}'")
        raise MIRCodegenError(f"illegal rvalue reached C17 emitter: {type(value).__name__}")

    def _binary(self, value: BinaryRValue) -> str:
        left = self._operand(value.left)
        right = self._operand(value.right)
        left_type = self._operand_type(value.left)
        right_type = self._operand_type(value.right)
        if value.op in ("==", "!=", "<", "<=", ">", ">="):
            if left_type.name == "string" and right_type.name == "string":
                relation = {"==": "== 0", "!=": "!= 0", "<": "< 0", "<=": "<= 0", ">": "> 0", ">=": ">= 0"}[value.op]
                return f"(strcmp({left}, {right}) {relation})"
            return f"({left} {value.op} {right})"
        if value.op == "+" and left_type.name == "string" and right_type.name == "string":
            return f"nyx_concat({left}, {right})"
        if left_type.name in ("float", "f64") or right_type.name in ("float", "f64"):
            if value.op in ("+", "-", "*", "/"):
                return f"({left} {value.op} {right})"
            if value.op == "%":
                return f"fmod({left}, {right})"
        operations = {
            "+": "nyx_i64_add", "-": "nyx_i64_sub", "*": "nyx_i64_mul",
            "/": "nyx_i64_div", "%": "nyx_i64_rem", "<<": "nyx_i64_shl",
            ">>": "nyx_i64_shr",
        }
        if value.op in operations:
            return f"{operations[value.op]}({left}, {right})"
        if value.op in ("&", "|", "^"):
            return f"nyx_i64_from_bits(nyx_i64_bits({left}) {value.op} nyx_i64_bits({right}))"
        raise MIRCodegenError(f"unsupported C17 binary operation '{value.op}'")

    def _operand(self, value: Operand) -> str:
        if isinstance(value, ConstOperand):
            return self._typed_constant(value)
        if isinstance(value, (CopyOperand, MoveOperand)):
            if value.place.projections:
                raise MIRCodegenError("projected operand reached the scalar C17 emitter")
            return f"l{value.place.local}"
        raise MIRCodegenError(f"illegal operand reached C17 emitter: {type(value).__name__}")

    def _operand_type(self, value: Operand) -> MIRType:
        if isinstance(value, ConstOperand):
            return value.type
        if isinstance(value, (CopyOperand, MoveOperand)):
            return self.local_types[value.place.local]
        raise MIRCodegenError(f"unknown C17 operand type: {type(value).__name__}")

    @staticmethod
    def _typed_constant(value: ConstOperand) -> str:
        if value.type.name == "int":
            bits = int(value.value) & ((1 << 64) - 1)
            return f"nyx_i64_from_bits(UINT64_C({bits}))"
        if value.type.name == "string":
            return json.dumps(str(value.value), ensure_ascii=False)
        if value.type.name == "bool":
            return "true" if value.value else "false"
        if value.type.name in ("float", "f64"):
            number = float(value.value)
            if math.isnan(number):
                return "NAN"
            if math.isinf(number):
                return "INFINITY" if number > 0 else "-INFINITY"
            return repr(number)
        raise MIRCodegenError(f"unsupported C17 constant type '{value.type}'")

    @staticmethod
    def _constant(value: object, value_type: MIRType) -> str:
        if value_type.name == "string":
            return json.dumps(str(value), ensure_ascii=False)
        if value_type.name == "bool":
            return "true" if bool(value) else "false"
        return str(value)

    @staticmethod
    def _type(value: MIRType, function: MIRFunction | None = None) -> str:
        if value.name == "any" and function is not None and function.name in ("main", "__nyx_top_level"):
            return "void"
        mapping = {
            "void": "void", "bool": "bool", "int": "int64_t",
            "float": "double", "f64": "double", "string": "const char *",
        }
        rendered = mapping.get(value.name)
        if rendered is None or value.optional or value.pointer or value.arguments:
            raise MIRCodegenError(f"unsupported C17 MIR type '{value}'")
        return rendered

    @staticmethod
    def _default(value: MIRType) -> str:
        return {"bool": "false", "int": "INT64_C(0)", "float": "0.0", "f64": "0.0", "string": "\"\""}.get(value.name, "0")

    @staticmethod
    def _print_function(value: MIRType) -> str:
        mapping = {
            "bool": "nyx_print_bool", "int": "nyx_print_i64",
            "float": "nyx_print_f64", "f64": "nyx_print_f64",
            "string": "nyx_print_string",
        }
        result = mapping.get(value.name)
        if result is None:
            raise MIRCodegenError(f"C17 print does not support MIR type '{value}'")
        return result


def emit_legalized_c17(module: MIRModule) -> str:
    return _C17Emitter(legalize_mir(module, "c", require_emitter=True)).emit()
