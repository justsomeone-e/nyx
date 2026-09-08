"""Executable reference semantics for the scalar/control-flow MIR subset."""

from __future__ import annotations

from dataclasses import dataclass
import math

from .model import (
    AssertTerminator,
    AggregateRValue,
    AssignStatement,
    BinaryRValue,
    CastRValue,
    CallTerminator,
    ConstOperand,
    CopyOperand,
    DiscriminantRValue,
    GotoTerminator,
    MIRFunction,
    MIRModule,
    MoveOperand,
    NopStatement,
    Operand,
    PayloadRValue,
    ReturnTerminator,
    StorageDeadStatement,
    StorageLiveStatement,
    SwitchIntTerminator,
    SwitchValueTerminator,
    ThrowTerminator,
    UnaryRValue,
    UnreachableTerminator,
    UseRValue,
)
from .verifier import verify_mir


_UNINITIALIZED = object()
_I64_MASK = (1 << 64) - 1
_I64_SIGN = 1 << 63


class MIRTrap(RuntimeError):
    pass


class _MIRUserThrow(Exception):
    def __init__(self, value: object):
        self.value = value
        super().__init__(str(value))


@dataclass(frozen=True, slots=True)
class MIRExecutionResult:
    value: object
    output: tuple[str, ...]
    steps: int


class MIRInterpreter:
    def __init__(self, module: MIRModule, *, max_steps: int = 100_000):
        self.module = verify_mir(module)
        self.max_steps = max_steps
        self.output: list[str] = []
        self.steps = 0
        self.functions = {function.symbol: function for function in module.functions}
        self.functions.update({function.name: function for function in module.functions})

    def run(self, entry: str | None = None, arguments: tuple[object, ...] = ()) -> MIRExecutionResult:
        try:
            if entry is not None:
                value = self._call(self._function(entry), arguments)
            else:
                value = None
                top_level = self.functions.get("function::__nyx_top_level")
                if top_level is not None:
                    value = self._call(top_level, ())
                main = self.functions.get("main")
                if main is not None:
                    value = self._call(main, arguments)
        except _MIRUserThrow as thrown:
            raise MIRTrap(f"uncaught Nyx throw: {self._format(thrown.value)}") from None
        return MIRExecutionResult(value, tuple(self.output), self.steps)

    def _function(self, name: str) -> MIRFunction:
        function = self.functions.get(name)
        if function is None:
            raise MIRTrap(f"Unknown MIR function '{name}'")
        return function

    def _call(self, function: MIRFunction, arguments: tuple[object, ...]) -> object:
        if len(arguments) != len(function.parameters):
            raise MIRTrap(
                f"Function '{function.name}' expected {len(function.parameters)} arguments, got {len(arguments)}"
            )
        locals_: list[object] = [_UNINITIALIZED] * len(function.locals)
        for local_id, value in zip(function.parameters, arguments):
            locals_[local_id] = value
        block_id = 0
        while True:
            self._tick()
            block = function.blocks[block_id]
            for statement in block.statements:
                self._tick()
                if isinstance(statement, AssignStatement):
                    if statement.place.projections:
                        raise MIRTrap("Projected assignment is not available before M4")
                    locals_[statement.place.local] = self._rvalue(statement.value, locals_)
                elif isinstance(statement, StorageLiveStatement):
                    locals_[statement.local] = _UNINITIALIZED
                elif isinstance(statement, StorageDeadStatement):
                    locals_[statement.local] = _UNINITIALIZED
                elif not isinstance(statement, NopStatement):
                    raise MIRTrap(f"Unsupported MIR statement {type(statement).__name__}")

            terminator = block.terminator
            if isinstance(terminator, GotoTerminator):
                block_id = terminator.target
            elif isinstance(terminator, SwitchIntTerminator):
                discriminator = self._operand(terminator.discriminator, locals_)
                block_id = next(
                    (target for value, target in terminator.targets if discriminator == value),
                    terminator.otherwise,
                )
            elif isinstance(terminator, SwitchValueTerminator):
                discriminator = self._operand(terminator.discriminator, locals_)
                block_id = next(
                    (target for value, target in terminator.targets if discriminator == value),
                    terminator.otherwise,
                )
            elif isinstance(terminator, ReturnTerminator):
                value = locals_[function.return_local]
                return None if value is _UNINITIALIZED else value
            elif isinstance(terminator, CallTerminator):
                values = tuple(self._operand(argument, locals_) for argument in terminator.arguments)
                try:
                    value = self._invoke(terminator.function, values)
                except _MIRUserThrow as thrown:
                    if terminator.unwind is None or terminator.error_destination is None:
                        raise
                    if terminator.error_destination.projections:
                        raise MIRTrap("Projected unwind destinations require M4")
                    locals_[terminator.error_destination.local] = thrown.value
                    block_id = terminator.unwind
                    continue
                if terminator.destination is not None:
                    if terminator.destination.projections:
                        raise MIRTrap("Projected call destinations require M4")
                    locals_[terminator.destination.local] = value
                if terminator.target is None:
                    raise MIRTrap(f"Call to '{terminator.function}' has no continuation")
                block_id = terminator.target
            elif isinstance(terminator, AssertTerminator):
                actual = bool(self._operand(terminator.condition, locals_))
                if actual != terminator.expected:
                    raise MIRTrap(terminator.message)
                block_id = terminator.target
            elif isinstance(terminator, ThrowTerminator):
                value = self._operand(terminator.value, locals_)
                if terminator.target is None:
                    raise _MIRUserThrow(value)
                if terminator.destination is None or terminator.destination.projections:
                    raise MIRTrap("Caught throw requires a direct destination")
                locals_[terminator.destination.local] = value
                block_id = terminator.target
            elif isinstance(terminator, UnreachableTerminator):
                raise MIRTrap("Reached unreachable MIR terminator")
            else:
                raise MIRTrap(f"Unsupported MIR terminator {type(terminator).__name__}")

    def _invoke(self, symbol: str, arguments: tuple[object, ...]) -> object:
        if symbol in self.functions:
            return self._call(self.functions[symbol], arguments)
        name = symbol.split("::")[-1]
        if name == "print":
            self.output.append(" ".join(self._format(value) for value in arguments))
            return None
        if name == "to_string":
            return self._format(arguments[0])
        if name == "to_int":
            return self._wrap_i64(int(arguments[0]))
        if name == "contains":
            return arguments[1] in arguments[0]
        if name == "is_number":
            try:
                float(arguments[0])
                return True
            except (TypeError, ValueError):
                return False
        if name == "len":
            return len(arguments[0])
        if name == "Ok":
            return ("Ok", arguments[0])
        if name == "Err":
            return ("Err", arguments[0])
        raise MIRTrap(f"Reference interpreter has no implementation for call '{symbol}'")

    def _rvalue(self, value: object, locals_: list[object]) -> object:
        if isinstance(value, UseRValue):
            return self._operand(value.operand, locals_)
        if isinstance(value, BinaryRValue):
            left = self._operand(value.left, locals_)
            right = self._operand(value.right, locals_)
            return self._binary(value.op, left, right, value.type.name)
        if isinstance(value, UnaryRValue):
            operand = self._operand(value.operand, locals_)
            if value.op in ("!", "not"):
                return not bool(operand)
            if value.op == "-":
                result = -operand
                return self._wrap_i64(result) if value.type.name.startswith(("i", "u")) or value.type.name == "int" else result
            if value.op == "+":
                return operand
            if value.op == "~":
                return self._wrap_i64(~int(operand))
            raise MIRTrap(f"Unsupported unary operation '{value.op}'")
        if isinstance(value, CastRValue):
            operand = self._operand(value.operand, locals_)
            if value.type.name in ("float", "f32", "f64"):
                return float(operand)
            if value.type.name == "bool":
                return bool(operand)
            if value.type.name == "string":
                return self._format(operand)
            if value.type.name == "int" or value.type.name.startswith(("i", "u")):
                return self._wrap_i64(int(operand))
            return operand
        if isinstance(value, AggregateRValue):
            operands = tuple(self._operand(item, locals_) for item in value.operands)
            if value.kind == "array":
                return list(operands)
            if value.kind in ("enum", "result", "option"):
                return (value.name,) + operands
            if value.kind == "struct":
                return {"__type__": value.name, "fields": list(operands)}
            raise MIRTrap(f"Unsupported aggregate kind '{value.kind}'")
        if isinstance(value, DiscriminantRValue):
            operand = self._operand(value.operand, locals_)
            if operand is None:
                return "None"
            if isinstance(operand, tuple) and operand:
                return operand[0]
            if isinstance(operand, dict) and "__tag__" in operand:
                return operand["__tag__"]
            return type(operand).__name__
        if isinstance(value, PayloadRValue):
            operand = self._operand(value.operand, locals_)
            if isinstance(operand, tuple) and len(operand) > value.index + 1:
                return operand[value.index + 1]
            raise MIRTrap(f"Aggregate has no payload {value.index}")
        raise MIRTrap(f"Unsupported MIR rvalue {type(value).__name__}")

    def _operand(self, operand: Operand, locals_: list[object]) -> object:
        if isinstance(operand, ConstOperand):
            return operand.value
        if isinstance(operand, (CopyOperand, MoveOperand)):
            if operand.place.projections:
                raise MIRTrap("Projected operands require M4")
            value = locals_[operand.place.local]
            if value is _UNINITIALIZED:
                raise MIRTrap(f"Read of uninitialized or moved local _{operand.place.local}")
            if isinstance(operand, MoveOperand):
                locals_[operand.place.local] = _UNINITIALIZED
            return value
        raise MIRTrap(f"Unsupported MIR operand {type(operand).__name__}")

    def _binary(self, op: str, left: object, right: object, result_type: str) -> object:
        if op == "+":
            result = left + right
        elif op == "-":
            result = left - right
        elif op == "*":
            result = left * right
        elif op == "/":
            if right == 0:
                raise MIRTrap("division by zero")
            result = left / right if result_type in ("float", "f32", "f64") else math.trunc(left / right)
        elif op == "%":
            if right == 0:
                raise MIRTrap("remainder by zero")
            quotient = math.trunc(left / right)
            result = left - quotient * right
        elif op == "==":
            return left == right
        elif op == "!=":
            return left != right
        elif op == "<":
            return left < right
        elif op == "<=":
            return left <= right
        elif op == ">":
            return left > right
        elif op == ">=":
            return left >= right
        elif op in ("&", "|", "^"):
            result = {"&": int(left) & int(right), "|": int(left) | int(right), "^": int(left) ^ int(right)}[op]
        elif op in ("<<", ">>"):
            result = int(left) << int(right) if op == "<<" else int(left) >> int(right)
        else:
            raise MIRTrap(f"Unsupported binary operation '{op}'")
        if result_type == "int" or result_type.startswith(("i", "u")):
            return self._wrap_i64(int(result))
        return result

    def _tick(self) -> None:
        self.steps += 1
        if self.steps > self.max_steps:
            raise MIRTrap(f"MIR execution exceeded {self.max_steps} steps")

    @staticmethod
    def _wrap_i64(value: int) -> int:
        value &= _I64_MASK
        return value - (1 << 64) if value & _I64_SIGN else value

    @staticmethod
    def _format(value: object) -> str:
        if value is True:
            return "true"
        if value is False:
            return "false"
        if value is None:
            return "null"
        if isinstance(value, float):
            if math.isnan(value):
                return "nan"
            if math.isinf(value):
                return "inf" if value > 0 else "-inf"
        if isinstance(value, tuple) and value and isinstance(value[0], str):
            payload = ", ".join(MIRInterpreter._format(item) for item in value[1:])
            return f"{value[0]}({payload})"
        return str(value)
