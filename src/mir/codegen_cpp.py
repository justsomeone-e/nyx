"""C++20 emitter for the legalized scalar/control-flow MIR pilot."""

from __future__ import annotations

import json
import math
import re

from .legalization import MIRLegalizationError, legalize_mir
from .model import (
    AssertTerminator,
    AssignStatement,
    BinaryRValue,
    CallTerminator,
    CastRValue,
    ConstOperand,
    CopyOperand,
    GotoTerminator,
    MIRFunction,
    MIRModule,
    MoveOperand,
    NopStatement,
    Operand,
    Place,
    ReturnTerminator,
    StorageDeadStatement,
    StorageLiveStatement,
    SwitchIntTerminator,
    SwitchValueTerminator,
    UnaryRValue,
    UnreachableTerminator,
    UseRValue,
)
from .types import MIRType


class MIRCodegenError(ValueError):
    code = "MIRG1010"

    def __init__(self, message: str):
        super().__init__(f"{self.code}: {message}")


_INTEGER_TYPES = frozenset({"int", "i8", "i16", "i32", "i64", "u8", "u16", "u32", "u64"})
_FLOAT_TYPES = frozenset({"float", "f32", "f64"})


def _identifier(value: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9_]", "_", value)
    if not clean or clean[0].isdigit():
        clean = "_" + clean
    return clean


class _CppEmitter:
    def __init__(self, module: MIRModule):
        self.module = module
        self.function_names = {
            function.symbol: ("main" if function.name == "main" else f"nyx_fn_{_identifier(function.name)}")
            for function in module.functions
        }
        self.current: MIRFunction | None = None
        self.local_types: dict[int, MIRType] = {}

    def emit(self) -> str:
        declarations = [self._prototype(function) + ";" for function in self.module.functions]
        definitions = [self._function(function) for function in self.module.functions]
        parts = [
            "// Experimental Nyx legalized MIR -> C++20 output.",
            "// The production Typed HIR C++ backend remains the parity oracle.",
            "#include <bit>",
            "#include <cstdint>",
            "#include <iostream>",
            "#include <limits>",
            "#include <stdexcept>",
            "#include <string>",
            "#include <utility>",
            "",
            self._runtime(),
            "",
            *declarations,
            "",
            *definitions,
        ]
        return "\n".join(parts).rstrip() + "\n"

    @staticmethod
    def _runtime() -> str:
        return """namespace nyx_mir_runtime {
inline std::int64_t from_bits(std::uint64_t value) {
    return std::bit_cast<std::int64_t>(value);
}
inline std::uint64_t to_bits(std::int64_t value) {
    return std::bit_cast<std::uint64_t>(value);
}
inline std::int64_t add(std::int64_t left, std::int64_t right) {
    return from_bits(to_bits(left) + to_bits(right));
}
inline std::int64_t sub(std::int64_t left, std::int64_t right) {
    return from_bits(to_bits(left) - to_bits(right));
}
inline std::int64_t mul(std::int64_t left, std::int64_t right) {
    return from_bits(to_bits(left) * to_bits(right));
}
inline std::int64_t neg(std::int64_t value) {
    return from_bits(std::uint64_t{0} - to_bits(value));
}
inline std::int64_t div(std::int64_t left, std::int64_t right) {
    if (right == 0) throw std::runtime_error("division by zero");
    if (left == std::numeric_limits<std::int64_t>::min() && right == -1) return left;
    return left / right;
}
inline std::int64_t rem(std::int64_t left, std::int64_t right) {
    if (right == 0) throw std::runtime_error("remainder by zero");
    if (left == std::numeric_limits<std::int64_t>::min() && right == -1) return 0;
    return left % right;
}
inline std::int64_t shl(std::int64_t left, std::int64_t right) {
    return from_bits(to_bits(left) << (to_bits(right) & 63U));
}
inline std::int64_t shr(std::int64_t left, std::int64_t right) {
    return left >> (to_bits(right) & 63U);
}
template <typename Value>
void print_one(bool& first, const Value& value) {
    if (!first) std::cout << ' ';
    first = false;
    std::cout << value;
}
template <typename... Values>
void print(const Values&... values) {
    bool first = true;
    std::cout << std::boolalpha;
    (print_one(first, values), ...);
    std::cout << '\\n';
}
}  // namespace nyx_mir_runtime"""

    def _prototype(self, function: MIRFunction) -> str:
        name = self.function_names[function.symbol]
        if function.name == "main":
            return "int main()"
        parameters = ", ".join(
            f"{self._type(function.locals[local].type)} _{local}"
            for local in function.parameters
        )
        return f"static {self._type(function.locals[function.return_local].type)} {name}({parameters})"

    def _function(self, function: MIRFunction) -> str:
        self.current = function
        self.local_types = {local.id: local.type for local in function.locals}
        lines = [self._prototype(function) + " {"]
        parameter_ids = set(function.parameters)
        for local in function.locals:
            if local.id in parameter_ids or local.type.name == "void":
                continue
            if function.name == "main" and local.id == function.return_local and local.type.name == "any":
                continue
            lines.append(f"    {self._type(local.type)} _{local.id}{{}};")
        if function.blocks:
            lines.append("    goto bb0;")
        for block in function.blocks:
            lines.append(f"bb{block.id}:")
            for statement in block.statements:
                lines.extend(self._statement(statement))
            lines.extend(self._terminator(block.terminator))
        lines.append("}")
        self.current = None
        self.local_types = {}
        return "\n".join(lines)

    def _statement(self, statement: object) -> list[str]:
        if isinstance(statement, AssignStatement):
            destination_type = self.local_types[statement.place.local]
            if destination_type.name == "void":
                return []
            if self.current is not None and self.current.name == "main" and statement.place.local == 0:
                raise MIRCodegenError("MIR main may not assign its synthetic 'any' return local")
            return [f"    {self._place(statement.place)} = {self._rvalue(statement.value)};"]
        if isinstance(statement, (StorageLiveStatement, StorageDeadStatement, NopStatement)):
            return []
        raise MIRCodegenError(f"illegal statement reached C++ emitter: {type(statement).__name__}")

    def _terminator(self, terminator: object) -> list[str]:
        if isinstance(terminator, GotoTerminator):
            return [f"    goto bb{terminator.target};"]
        if isinstance(terminator, SwitchIntTerminator):
            discriminator = self._operand(terminator.discriminator)
            lines: list[str] = []
            for index, (value, target) in enumerate(terminator.targets):
                prefix = "if" if index == 0 else "else if"
                lines.append(f"    {prefix} ({discriminator} == {self._constant(value)}) goto bb{target};")
            lines.append(f"    else goto bb{terminator.otherwise};" if terminator.targets else f"    goto bb{terminator.otherwise};")
            return lines
        if isinstance(terminator, SwitchValueTerminator):
            discriminator = self._operand(terminator.discriminator)
            lines = []
            for index, (value, target) in enumerate(terminator.targets):
                prefix = "if" if index == 0 else "else if"
                lines.append(f"    {prefix} ({discriminator} == {self._constant(value)}) goto bb{target};")
            lines.append(f"    else goto bb{terminator.otherwise};" if terminator.targets else f"    goto bb{terminator.otherwise};")
            return lines
        if isinstance(terminator, CallTerminator):
            if terminator.target is None:
                raise MIRCodegenError(f"call '{terminator.function}' has no continuation")
            arguments = ", ".join(self._operand(argument) for argument in terminator.arguments)
            if terminator.function == "builtin::print":
                lines = [f"    nyx_mir_runtime::print({arguments});"]
            elif terminator.function in self.function_names:
                call = f"{self.function_names[terminator.function]}({arguments})"
                if terminator.destination is None or self.local_types[terminator.destination.local].name == "void":
                    lines = [f"    {call};"]
                else:
                    lines = [f"    {self._place(terminator.destination)} = {call};"]
            else:
                raise MIRCodegenError(f"illegal runtime call reached C++ emitter: {terminator.function}")
            lines.append(f"    goto bb{terminator.target};")
            return lines
        if isinstance(terminator, AssertTerminator):
            expected = "true" if terminator.expected else "false"
            message = json.dumps(terminator.message, ensure_ascii=False)
            return [
                f"    if (static_cast<bool>({self._operand(terminator.condition)}) != {expected}) ",
                f"        throw std::runtime_error({message});",
                f"    goto bb{terminator.target};",
            ]
        if isinstance(terminator, ReturnTerminator):
            assert self.current is not None
            if self.current.name == "main":
                return ["    return 0;"]
            result_type = self.local_types[self.current.return_local]
            if result_type.name == "void":
                return ["    return;"]
            return [f"    return _{self.current.return_local};"]
        if isinstance(terminator, UnreachableTerminator):
            return ["    throw std::runtime_error(\"reached unreachable MIR terminator\");"]
        raise MIRCodegenError(f"illegal terminator reached C++ emitter: {type(terminator).__name__}")

    def _rvalue(self, value: object) -> str:
        if isinstance(value, UseRValue):
            return self._operand(value.operand)
        if isinstance(value, BinaryRValue):
            return self._binary(value)
        if isinstance(value, UnaryRValue):
            operand = self._operand(value.operand)
            if value.op in ("!", "not"):
                return f"(!static_cast<bool>({operand}))"
            if value.op == "-" and value.type.name in _INTEGER_TYPES:
                return f"nyx_mir_runtime::neg({operand})"
            if value.op in ("+", "-"):
                return f"({value.op}{operand})"
            if value.op == "~":
                return f"nyx_mir_runtime::from_bits(~nyx_mir_runtime::to_bits({operand}))"
            raise MIRCodegenError(f"unsupported unary operation '{value.op}'")
        if isinstance(value, CastRValue):
            return f"static_cast<{self._type(value.type)}>({self._operand(value.operand)})"
        raise MIRCodegenError(f"illegal rvalue reached C++ emitter: {type(value).__name__}")

    def _binary(self, value: BinaryRValue) -> str:
        left = self._operand(value.left)
        right = self._operand(value.right)
        left_type = self._operand_type(value.left)
        right_type = self._operand_type(value.right)
        if value.op in ("==", "!=", "<", "<=", ">", ">="):
            return f"({left} {value.op} {right})"
        if value.op in ("+", "-", "*", "/", "%") and (
            left_type.name in _FLOAT_TYPES or right_type.name in _FLOAT_TYPES
        ):
            return f"({left} {value.op} {right})"
        if value.op == "+" and (left_type.name == "string" or right_type.name == "string"):
            return f"({left} + {right})"
        runtime_ops = {
            "+": "add", "-": "sub", "*": "mul", "/": "div", "%": "rem",
            "<<": "shl", ">>": "shr",
        }
        if value.op in runtime_ops:
            return f"nyx_mir_runtime::{runtime_ops[value.op]}({left}, {right})"
        if value.op in ("&", "|", "^"):
            return (
                "nyx_mir_runtime::from_bits("
                f"nyx_mir_runtime::to_bits({left}) {value.op} nyx_mir_runtime::to_bits({right}))"
            )
        raise MIRCodegenError(f"unsupported binary operation '{value.op}'")

    def _operand(self, operand: Operand) -> str:
        if isinstance(operand, ConstOperand):
            return self._typed_constant(operand)
        if isinstance(operand, (CopyOperand, MoveOperand)):
            return self._place(operand.place)
        raise MIRCodegenError(f"illegal operand reached C++ emitter: {type(operand).__name__}")

    def _operand_type(self, operand: Operand) -> MIRType:
        if isinstance(operand, ConstOperand):
            return operand.type
        if isinstance(operand, (CopyOperand, MoveOperand)):
            return self.local_types[operand.place.local]
        raise MIRCodegenError(f"unknown operand type: {type(operand).__name__}")

    @staticmethod
    def _place(place: Place) -> str:
        if place.projections:
            raise MIRCodegenError("projected place reached scalar C++ emitter")
        return f"_{place.local}"

    def _typed_constant(self, operand: ConstOperand) -> str:
        value = operand.value
        if operand.type.name in _INTEGER_TYPES:
            bits = int(value) & ((1 << 64) - 1)
            return f"nyx_mir_runtime::from_bits(UINT64_C({bits}))"
        if operand.type.name in _FLOAT_TYPES:
            number = float(value)
            if math.isnan(number):
                return "std::numeric_limits<double>::quiet_NaN()"
            if math.isinf(number):
                sign = "" if number > 0 else "-"
                return f"{sign}std::numeric_limits<double>::infinity()"
            return repr(number)
        if operand.type.name == "bool":
            return "true" if bool(value) else "false"
        if operand.type.name == "string":
            return json.dumps(str(value), ensure_ascii=False)
        if operand.type.name == "char":
            return f"U{json.dumps(str(value), ensure_ascii=False)}"
        raise MIRCodegenError(f"unsupported constant type '{operand.type}'")

    @staticmethod
    def _constant(value: object) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, int):
            return str(value)
        if isinstance(value, float):
            return repr(value)
        if isinstance(value, str):
            return json.dumps(value, ensure_ascii=False)
        raise MIRCodegenError(f"unsupported switch constant {value!r}")

    @staticmethod
    def _type(value: MIRType) -> str:
        if value.name == "void":
            return "void"
        if value.name == "bool":
            return "bool"
        if value.name in _INTEGER_TYPES:
            return "std::int64_t"
        if value.name in _FLOAT_TYPES:
            return "double"
        if value.name == "string":
            return "std::string"
        if value.name == "char":
            return "char32_t"
        raise MIRCodegenError(f"unsupported C++ MIR type '{value}'")


def emit_legalized_cpp(module: MIRModule) -> str:
    """Validate and emit the M5 C++ pilot without semantic fallback."""
    try:
        legalized = legalize_mir(module, "cpp", require_emitter=True)
    except MIRLegalizationError:
        raise
    return _CppEmitter(legalized).emit()
