"""Executable WebAssembly emitter for the legalized integer/control MIR pilot."""

from __future__ import annotations

import re

from src.codegen.wasm_ir import F64, I32, I64, VOID, FunctionIR, Instruction, ModuleIR

from .codegen_cpp import MIRCodegenError
from .legalization import legalize_mir
from .model import (
    AssertTerminator,
    AssignStatement,
    BinaryRValue,
    CallTerminator,
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
    UnaryRValue,
    UnreachableTerminator,
    UseRValue,
)
from .types import MIRType


def _identifier(value: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9_]", "_", value)
    return clean if clean and not clean[0].isdigit() else "_" + clean


class _WasmEmitter:
    def __init__(self, module: MIRModule):
        self.module = module
        self.function_names = {
            function.symbol: _identifier(function.name) for function in module.functions
        }
        self.function_names.update({
            function.name: self.function_names[function.symbol] for function in module.functions
        })
        if len(set(self.function_names[function.symbol] for function in module.functions)) != len(module.functions):
            raise MIRCodegenError("MIR function names collide after WebAssembly identifier normalization")
        self.functions = {function.symbol: function for function in module.functions}
        self.functions.update({function.name: function for function in module.functions})
        self.current: MIRFunction | None = None
        self.local_types: dict[int, MIRType] = {}
        self.local_names: dict[int, str] = {}

    def lower(self) -> ModuleIR:
        functions = self._integer_runtime() + [self._function(function) for function in self.module.functions]
        return ModuleIR(self.module.source_name, functions, [], 2048)

    @staticmethod
    def _integer_runtime() -> list[FunctionIR]:
        minimum = -(1 << 63)
        common = [
            Instruction("local.get", "right"), Instruction("i64.eqz"),
            Instruction("if"), Instruction("unreachable"), Instruction("end"),
            Instruction("local.get", "left"), Instruction("i64.const", minimum), Instruction("i64.eq"),
            Instruction("local.get", "right"), Instruction("i64.const", -1), Instruction("i64.eq"),
            Instruction("i32.and"),
        ]
        divide = FunctionIR(
            "__nyx_mir_div", [("left", I64), ("right", I64)], I64,
            body=common + [
                Instruction("if_result", I64), Instruction("i64.const", minimum), Instruction("else"),
                Instruction("local.get", "left"), Instruction("local.get", "right"),
                Instruction("i64.div_s"), Instruction("end"),
            ], export=False,
        )
        remainder = FunctionIR(
            "__nyx_mir_rem", [("left", I64), ("right", I64)], I64,
            body=common + [
                Instruction("if_result", I64), Instruction("i64.const", 0), Instruction("else"),
                Instruction("local.get", "left"), Instruction("local.get", "right"),
                Instruction("i64.rem_s"), Instruction("end"),
            ], export=False,
        )
        return [divide, remainder]

    def _function(self, function: MIRFunction) -> FunctionIR:
        self.current = function
        self.local_types = {local.id: local.type for local in function.locals}
        self.local_names = {local.id: f"l{local.id}" for local in function.locals}
        result = self._type(function.locals[function.return_local].type, function)
        params = [
            (self.local_names[local], self._type(function.locals[local].type, function))
            for local in function.parameters
        ]
        parameter_ids = set(function.parameters)
        locals_ = [
            (self.local_names[local.id], self._type(local.type, function))
            for local in function.locals
            if local.id not in parameter_ids and self._type(local.type, function) != VOID
        ]
        locals_.append(("pc", I32))
        body = [Instruction("i32.const", function.blocks[0].id), Instruction("local.set", "pc")]
        body.extend((Instruction("block", "function_exit"), Instruction("loop", "dispatch")))
        for block in function.blocks:
            body.extend((
                Instruction("local.get", "pc"),
                Instruction("i32.const", block.id),
                Instruction("i32.eq"),
                Instruction("if"),
            ))
            for statement in block.statements:
                self._statement(statement, body)
            self._terminator(block.terminator, body)
            body.append(Instruction("end"))
        body.extend((Instruction("unreachable"), Instruction("end"), Instruction("end")))
        if result != VOID:
            body.append(Instruction("unreachable"))
        lowered = FunctionIR(self.function_names[function.symbol], params, result, locals_, body)
        self.current = None
        self.local_types = {}
        self.local_names = {}
        return lowered

    def _statement(self, statement: object, body: list[Instruction]) -> None:
        if isinstance(statement, AssignStatement):
            if statement.place.projections:
                raise MIRCodegenError("projected assignment reached the scalar WebAssembly emitter")
            body.extend(self._rvalue(statement.value))
            body.append(Instruction("local.set", self.local_names[statement.place.local]))
            return
        if isinstance(statement, (StorageLiveStatement, StorageDeadStatement, NopStatement)):
            return
        raise MIRCodegenError(f"illegal statement reached WebAssembly emitter: {type(statement).__name__}")

    def _terminator(self, value: object, body: list[Instruction]) -> None:
        if isinstance(value, GotoTerminator):
            self._goto(value.target, body)
            return
        if isinstance(value, SwitchIntTerminator):
            operand_type = self._operand_type(value.discriminator)
            for expected, target in value.targets:
                body.extend(self._operand(value.discriminator))
                body.append(Instruction(f"{self._type(operand_type)}.const", expected))
                body.append(Instruction(f"{self._type(operand_type)}.eq"))
                body.append(Instruction("if"))
                self._goto(target, body)
                body.append(Instruction("end"))
            self._goto(value.otherwise, body)
            return
        if isinstance(value, CallTerminator):
            if value.target is None:
                raise MIRCodegenError(f"call '{value.function}' has no continuation")
            callee = self.functions.get(value.function)
            if callee is None:
                raise MIRCodegenError(f"runtime call '{value.function}' reached the pure WebAssembly pilot")
            for argument in value.arguments:
                body.extend(self._operand(argument))
            body.append(Instruction("call", self.function_names[value.function]))
            result_type = self._type(callee.locals[callee.return_local].type, callee)
            if value.destination is not None and result_type != VOID:
                body.append(Instruction("local.set", self.local_names[value.destination.local]))
            elif result_type != VOID:
                body.append(Instruction("drop"))
            self._goto(value.target, body)
            return
        if isinstance(value, AssertTerminator):
            body.extend(self._operand(value.condition))
            if value.expected:
                body.append(Instruction("i32.eqz"))
            body.extend((Instruction("if"), Instruction("unreachable"), Instruction("end")))
            self._goto(value.target, body)
            return
        if isinstance(value, ReturnTerminator):
            assert self.current is not None
            result_type = self._type(self.current.locals[self.current.return_local].type, self.current)
            if result_type != VOID:
                body.append(Instruction("local.get", self.local_names[self.current.return_local]))
            body.append(Instruction("return"))
            return
        if isinstance(value, UnreachableTerminator):
            body.append(Instruction("unreachable"))
            return
        raise MIRCodegenError(f"illegal terminator reached WebAssembly emitter: {type(value).__name__}")

    @staticmethod
    def _goto(target: int, body: list[Instruction]) -> None:
        body.extend((
            Instruction("i32.const", target),
            Instruction("local.set", "pc"),
            Instruction("br", "dispatch"),
        ))

    def _rvalue(self, value: object) -> list[Instruction]:
        if isinstance(value, UseRValue):
            return self._operand(value.operand)
        if isinstance(value, BinaryRValue):
            left_type = self._operand_type(value.left)
            wasm_type = self._type(left_type)
            operations = {
                "+": "add", "-": "sub", "*": "mul",
                "&": "and", "|": "or", "^": "xor", "<<": "shl", ">>": "shr_s",
                "==": "eq", "!=": "ne", "<": "lt_s", "<=": "le_s", ">": "gt_s", ">=": "ge_s",
            }
            operation = operations.get(value.op)
            if value.op in ("/", "%"):
                helper = "__nyx_mir_div" if value.op == "/" else "__nyx_mir_rem"
                return self._operand(value.left) + self._operand(value.right) + [Instruction("call", helper)]
            if operation is None:
                raise MIRCodegenError(f"unsupported WebAssembly binary operation '{value.op}'")
            return self._operand(value.left) + self._operand(value.right) + [
                Instruction(f"{wasm_type}.{operation}")
            ]
        if isinstance(value, UnaryRValue):
            operand = self._operand(value.operand)
            if value.op in ("!", "not"):
                return operand + [Instruction("i32.eqz")]
            if value.op == "+":
                return operand
            if value.op == "-":
                return [Instruction("i64.const", 0)] + operand + [Instruction("i64.sub")]
            if value.op == "~":
                return operand + [Instruction("i64.const", -1), Instruction("i64.xor")]
            raise MIRCodegenError(f"unsupported WebAssembly unary operation '{value.op}'")
        raise MIRCodegenError(f"illegal rvalue reached WebAssembly emitter: {type(value).__name__}")

    def _operand(self, value: Operand) -> list[Instruction]:
        if isinstance(value, ConstOperand):
            wasm_type = self._type(value.type)
            constant = int(value.value) if value.type.name == "bool" else value.value
            return [Instruction(f"{wasm_type}.const", constant)]
        if isinstance(value, (CopyOperand, MoveOperand)):
            if value.place.projections:
                raise MIRCodegenError("projected operand reached the scalar WebAssembly emitter")
            return [Instruction("local.get", self.local_names[value.place.local])]
        raise MIRCodegenError(f"illegal operand reached WebAssembly emitter: {type(value).__name__}")

    def _operand_type(self, value: Operand) -> MIRType:
        if isinstance(value, ConstOperand):
            return value.type
        if isinstance(value, (CopyOperand, MoveOperand)):
            return self.local_types[value.place.local]
        raise MIRCodegenError(f"unknown WebAssembly operand type: {type(value).__name__}")

    @staticmethod
    def _type(value: MIRType, function: MIRFunction | None = None) -> str:
        if value.name == "any" and function is not None and function.name == "main":
            return VOID
        if value.name == "void":
            return VOID
        if value.name == "bool":
            return I32
        if value.name == "int":
            return I64
        if value.name in ("float", "f64"):
            return F64
        raise MIRCodegenError(f"unsupported WebAssembly MIR type '{value}'")


def lower_legalized_wasm(module: MIRModule) -> ModuleIR:
    return _WasmEmitter(legalize_mir(module, "wasm", require_emitter=True)).lower()


def emit_legalized_wasm(module: MIRModule) -> bytes:
    return lower_legalized_wasm(module).to_wasm()


def emit_legalized_wat(module: MIRModule) -> str:
    return lower_legalized_wasm(module).to_wat()
