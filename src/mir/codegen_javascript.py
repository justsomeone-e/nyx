"""Node.js ES2022 emitter for legalized scalar/control-flow MIR."""

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


_RUNTIME = r'''"use strict";

const nyxI64 = value => BigInt.asIntN(64, value);
const nyxDiv = (left, right) => {
  if (right === 0n) throw new Error("division by zero");
  return nyxI64(left / right);
};
const nyxRem = (left, right) => {
  if (right === 0n) throw new Error("remainder by zero");
  return nyxI64(left % right);
};
const nyxDisplay = value => {
  if (value === true) return "true";
  if (value === false) return "false";
  if (typeof value === "number") {
    if (Number.isNaN(value)) return "nan";
    if (value === Infinity) return "inf";
    if (value === -Infinity) return "-inf";
    if (Object.is(value, -0)) return "0";
  }
  return String(value);
};'''


def _identifier(value: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9_$]", "_", value)
    if not clean or clean[0].isdigit():
        clean = "_" + clean
    return clean


class _JavaScriptEmitter:
    def __init__(self, module: MIRModule):
        self.module = module
        self.function_names = {
            function.symbol: f"nyxFn_{_identifier(function.name)}"
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
        parts = ["// Experimental Nyx legalized MIR -> Node.js ES2022 output.", _RUNTIME, ""]
        parts.extend(self._function(function) + "\n" for function in self.module.functions)
        by_name = {function.name: function for function in self.module.functions}
        entry = by_name.get("main") or by_name.get("__nyx_top_level")
        if entry is not None:
            parts.append(f"{self.function_names[entry.symbol]}();")
        return "\n".join(parts).rstrip() + "\n"

    def _function(self, function: MIRFunction) -> str:
        self.current = function
        self.local_types = {local.id: local.type for local in function.locals}
        parameters = ", ".join(f"l{local}" for local in function.parameters)
        lines = [f"function {self.function_names[function.symbol]}({parameters}) {{"]
        parameter_ids = set(function.parameters)
        for local in function.locals:
            if local.id in parameter_ids or local.type.name in ("void", "any"):
                continue
            lines.append(f"  let l{local.id} = {self._default(local.type)};")
        lines.extend(("  let pc = 0;", "  while (true) {", "    switch (pc) {"))
        for block in function.blocks:
            lines.append(f"      case {block.id}: {{")
            for statement in block.statements:
                lines.extend(f"        {line}" for line in self._statement(statement))
            lines.extend(f"        {line}" for line in self._terminator(block.terminator))
            lines.append("      }")
        lines.extend(("      default: throw new Error(\"invalid MIR block\");", "    }", "  }", "}"))
        self.current = None
        self.local_types = {}
        return "\n".join(lines)

    def _statement(self, value: object) -> list[str]:
        if isinstance(value, AssignStatement):
            if value.place.projections:
                raise MIRCodegenError("projected assignment reached the scalar JavaScript emitter")
            if self.local_types[value.place.local].name in ("void", "any"):
                return []
            return [f"l{value.place.local} = {self._rvalue(value.value)};"]
        if isinstance(value, (StorageLiveStatement, StorageDeadStatement, NopStatement)):
            return []
        raise MIRCodegenError(f"illegal statement reached JavaScript emitter: {type(value).__name__}")

    def _terminator(self, value: object) -> list[str]:
        if isinstance(value, GotoTerminator):
            return self._goto(value.target)
        if isinstance(value, SwitchIntTerminator):
            discriminator = self._operand(value.discriminator)
            value_type = self._operand_type(value.discriminator)
            lines: list[str] = []
            for expected, target in value.targets:
                rendered = ("true" if bool(expected) else "false") if value_type.name == "bool" else f"{expected}n"
                lines.append(f"if ({discriminator} === {rendered}) {{")
                lines.extend(f"  {line}" for line in self._goto(target))
                lines.append("}")
            lines.extend(self._goto(value.otherwise))
            return lines
        if isinstance(value, SwitchValueTerminator):
            discriminator = self._operand(value.discriminator)
            lines = []
            for expected, target in value.targets:
                lines.append(f"if ({discriminator} === {self._constant(expected)}) {{")
                lines.extend(f"  {line}" for line in self._goto(target))
                lines.append("}")
            lines.extend(self._goto(value.otherwise))
            return lines
        if isinstance(value, CallTerminator):
            if value.target is None:
                raise MIRCodegenError(f"call '{value.function}' has no continuation")
            arguments = ", ".join(self._operand(argument) for argument in value.arguments)
            if value.function == "builtin::print":
                line = f"console.log([{arguments}].map(nyxDisplay).join(\" \"));"
            elif value.function in self.function_names:
                call = f"{self.function_names[value.function]}({arguments})"
                callee = self.functions[value.function]
                if value.destination is not None and callee.locals[callee.return_local].type.name not in ("void", "any"):
                    line = f"l{value.destination.local} = {call};"
                else:
                    line = f"{call};"
            else:
                raise MIRCodegenError(f"illegal runtime call reached JavaScript emitter: {value.function}")
            return [line] + self._goto(value.target)
        if isinstance(value, AssertTerminator):
            expected = "true" if value.expected else "false"
            return [
                f"if (Boolean({self._operand(value.condition)}) !== {expected}) throw new Error({json.dumps(value.message)});"
            ] + self._goto(value.target)
        if isinstance(value, ReturnTerminator):
            assert self.current is not None
            result = self.current.locals[self.current.return_local].type
            return ["return;"] if result.name in ("void", "any") else ["return l0;"]
        if isinstance(value, UnreachableTerminator):
            return ["throw new Error(\"reached unreachable MIR terminator\");"]
        raise MIRCodegenError(f"illegal terminator reached JavaScript emitter: {type(value).__name__}")

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
                return f"!Boolean({operand})"
            if value.op == "+":
                return operand
            if value.op == "-" and value.type.name == "int":
                return f"nyxI64(-({operand}))"
            if value.op == "-":
                return f"-({operand})"
            if value.op == "~":
                return f"nyxI64(~({operand}))"
            raise MIRCodegenError(f"unsupported JavaScript unary operation '{value.op}'")
        raise MIRCodegenError(f"illegal rvalue reached JavaScript emitter: {type(value).__name__}")

    def _binary(self, value: BinaryRValue) -> str:
        left = self._operand(value.left)
        right = self._operand(value.right)
        left_type = self._operand_type(value.left)
        right_type = self._operand_type(value.right)
        if value.op in ("==", "!=", "<", "<=", ">", ">="):
            operation = {"==": "===", "!=": "!=="}.get(value.op, value.op)
            return f"({left} {operation} {right})"
        if value.op == "+" and (left_type.name == "string" or right_type.name == "string"):
            return f"String({left}) + String({right})"
        if left_type.name in ("float", "f64") or right_type.name in ("float", "f64"):
            if value.op in ("+", "-", "*", "/", "%"):
                return f"({left} {value.op} {right})"
        if value.op in ("+", "-", "*", "&", "|", "^"):
            return f"nyxI64(({left}) {value.op} ({right}))"
        if value.op == "/":
            return f"nyxDiv({left}, {right})"
        if value.op == "%":
            return f"nyxRem({left}, {right})"
        if value.op in ("<<", ">>"):
            return f"nyxI64(({left}) {value.op} BigInt.asUintN(6, {right}))"
        raise MIRCodegenError(f"unsupported JavaScript binary operation '{value.op}'")

    def _operand(self, value: Operand) -> str:
        if isinstance(value, ConstOperand):
            return self._typed_constant(value)
        if isinstance(value, (CopyOperand, MoveOperand)):
            if value.place.projections:
                raise MIRCodegenError("projected operand reached the scalar JavaScript emitter")
            return f"l{value.place.local}"
        raise MIRCodegenError(f"illegal operand reached JavaScript emitter: {type(value).__name__}")

    def _operand_type(self, value: Operand) -> MIRType:
        if isinstance(value, ConstOperand):
            return value.type
        if isinstance(value, (CopyOperand, MoveOperand)):
            return self.local_types[value.place.local]
        raise MIRCodegenError(f"unknown JavaScript operand type: {type(value).__name__}")

    @staticmethod
    def _typed_constant(value: ConstOperand) -> str:
        if value.type.name == "int":
            return f"{value.value}n"
        if value.type.name == "string":
            return json.dumps(str(value.value), ensure_ascii=False)
        if value.type.name == "bool":
            return "true" if value.value else "false"
        if value.type.name in ("float", "f64"):
            number = float(value.value)
            if math.isnan(number): return "NaN"
            if math.isinf(number): return "Infinity" if number > 0 else "-Infinity"
            return repr(number)
        raise MIRCodegenError(f"unsupported JavaScript constant type '{value.type}'")

    @staticmethod
    def _constant(value: object) -> str:
        if value is True: return "true"
        if value is False: return "false"
        if isinstance(value, int): return f"{value}n"
        return json.dumps(value, ensure_ascii=False)

    @staticmethod
    def _default(value: MIRType) -> str:
        return {"bool": "false", "int": "0n", "float": "0", "f64": "0", "string": '""'}.get(value.name, "undefined")


def emit_legalized_javascript(module: MIRModule) -> str:
    return _JavaScriptEmitter(legalize_mir(module, "js", require_emitter=True)).emit()
