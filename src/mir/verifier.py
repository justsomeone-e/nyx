"""Structural and type verification for experimental Nyx MIR."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

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
    DropTerminator,
    DerefProjection,
    FieldProjection,
    GotoTerminator,
    IndexProjection,
    MIRBasicBlock,
    MIRFunction,
    MIRModule,
    MIRSpan,
    MoveOperand,
    Operand,
    Place,
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
    MIR_SCHEMA_VERSION,
)
from .types import MIRType


@dataclass(frozen=True, slots=True)
class MIRVerificationIssue:
    code: str
    message: str
    span: MIRSpan


class MIRVerificationError(ValueError):
    def __init__(self, issues: Iterable[MIRVerificationIssue]):
        self.issues = tuple(issues)
        summary = "; ".join(f"{issue.code}: {issue.message}" for issue in self.issues)
        super().__init__(summary)


class MIRVerifier:
    def __init__(self, module: MIRModule):
        self.module = module
        self.issues: list[MIRVerificationIssue] = []

    def collect(self) -> tuple[MIRVerificationIssue, ...]:
        if not isinstance(self.module, MIRModule):
            fallback = MIRSpan("<mir>", 1, 1)
            return (MIRVerificationIssue("MIR0000", "Root value is not MIRModule", fallback),)
        if self.module.schema_version != MIR_SCHEMA_VERSION:
            self._issue(
                "MIR0001",
                f"Unsupported MIR schema {self.module.schema_version}; expected {MIR_SCHEMA_VERSION}",
                self._module_span(),
            )
        symbols = [function.symbol for function in self.module.functions]
        if len(symbols) != len(set(symbols)):
            self._issue("MIR0002", "Function symbols must be unique", self._module_span())
        for function in self.module.functions:
            self._verify_function(function)
        return tuple(self.issues)

    def _verify_function(self, function: MIRFunction) -> None:
        self._verify_span(function.span)
        local_ids = [local.id for local in function.locals]
        if local_ids != list(range(len(function.locals))):
            self._issue("MIR0100", "Local ids must be dense and ordered from zero", function.span)
        local_map = {local.id: local for local in function.locals}
        if function.return_local not in local_map:
            self._issue("MIR0101", "Return local does not exist", function.span)
        elif local_map[function.return_local].kind != "return":
            self._issue("MIR0102", "Return local must have kind 'return'", function.span)
        if len(function.parameters) != len(set(function.parameters)):
            self._issue("MIR0103", "Parameter local ids must be unique", function.span)
        for parameter in function.parameters:
            if parameter not in local_map:
                self._issue("MIR0104", f"Parameter local {parameter} does not exist", function.span)
            elif local_map[parameter].kind != "parameter":
                self._issue("MIR0105", f"Local {parameter} is not a parameter", function.span)
        for local in function.locals:
            self._verify_span(local.span)
            if not isinstance(local.type, MIRType):
                self._issue("MIR0106", f"Local {local.id} has an invalid type", local.span)

        block_ids = [block.id for block in function.blocks]
        if not function.blocks:
            self._issue("MIR0200", "Function requires an entry block", function.span)
            return
        if block_ids != list(range(len(function.blocks))):
            self._issue("MIR0201", "Block ids must be dense and ordered from zero", function.span)
        valid_blocks = set(block_ids)
        for block in function.blocks:
            self._verify_block(block, local_map, valid_blocks)

    def _verify_block(self, block: MIRBasicBlock, locals_by_id: dict, valid_blocks: set[int]) -> None:
        for statement in block.statements:
            span = getattr(statement, "span", self._module_span())
            self._verify_span(span)
            if isinstance(statement, AssignStatement):
                destination_type = self._place_type(statement.place, locals_by_id, span)
                value_type = self._rvalue_type(statement.value, locals_by_id, span)
                if (
                    destination_type is not None
                    and value_type is not None
                    and not statement.place.projections
                    and destination_type != value_type
                ):
                    self._issue(
                        "MIR0300",
                        f"Assignment type mismatch: {destination_type} <- {value_type}",
                        span,
                    )
            elif isinstance(statement, (StorageLiveStatement, StorageDeadStatement)):
                self._require_local(statement.local, locals_by_id, span)
            elif type(statement).__name__ != "NopStatement":
                self._issue("MIR0301", f"Unknown statement {type(statement).__name__}", span)

        terminator = block.terminator
        span = getattr(terminator, "span", self._module_span())
        self._verify_span(span)
        if isinstance(terminator, GotoTerminator):
            self._require_block(terminator.target, valid_blocks, span)
        elif isinstance(terminator, SwitchIntTerminator):
            self._operand_type(terminator.discriminator, locals_by_id, span)
            values = [value for value, _ in terminator.targets]
            if len(values) != len(set(values)):
                self._issue("MIR0400", "Switch values must be unique", span)
            for _, target in terminator.targets:
                self._require_block(target, valid_blocks, span)
            self._require_block(terminator.otherwise, valid_blocks, span)
        elif isinstance(terminator, SwitchValueTerminator):
            self._operand_type(terminator.discriminator, locals_by_id, span)
            values = [repr(value) for value, _ in terminator.targets]
            if len(values) != len(set(values)):
                self._issue("MIR0404", "Switch values must be unique", span)
            for _, target in terminator.targets:
                self._require_block(target, valid_blocks, span)
            self._require_block(terminator.otherwise, valid_blocks, span)
        elif isinstance(terminator, CallTerminator):
            for argument in terminator.arguments:
                self._operand_type(argument, locals_by_id, span)
            if terminator.destination is not None:
                self._place_type(terminator.destination, locals_by_id, span)
                if terminator.target is None:
                    self._issue("MIR0401", "Call destination requires a continuation target", span)
            if terminator.target is not None:
                self._require_block(terminator.target, valid_blocks, span)
            if terminator.unwind is not None:
                self._require_block(terminator.unwind, valid_blocks, span)
                if terminator.error_destination is None:
                    self._issue("MIR0405", "Unwind edge requires an error destination", span)
            if terminator.error_destination is not None:
                self._place_type(terminator.error_destination, locals_by_id, span)
        elif isinstance(terminator, DropTerminator):
            self._place_type(terminator.place, locals_by_id, span)
            self._require_block(terminator.target, valid_blocks, span)
            if terminator.unwind is not None:
                self._require_block(terminator.unwind, valid_blocks, span)
        elif isinstance(terminator, AssertTerminator):
            condition_type = self._operand_type(terminator.condition, locals_by_id, span)
            if condition_type is not None and condition_type.name != "bool":
                self._issue("MIR0402", "Assert condition must be bool", span)
            self._require_block(terminator.target, valid_blocks, span)
            if terminator.unwind is not None:
                self._require_block(terminator.unwind, valid_blocks, span)
        elif isinstance(terminator, ThrowTerminator):
            self._operand_type(terminator.value, locals_by_id, span)
            if terminator.target is not None:
                self._require_block(terminator.target, valid_blocks, span)
                if terminator.destination is None:
                    self._issue("MIR0406", "Caught throw requires an error destination", span)
            if terminator.destination is not None:
                self._place_type(terminator.destination, locals_by_id, span)
        elif not isinstance(terminator, (ReturnTerminator, UnreachableTerminator)):
            self._issue("MIR0403", "Block requires exactly one known terminator", span)

    def _rvalue_type(self, value: object, locals_by_id: dict, span: MIRSpan) -> MIRType | None:
        if isinstance(value, UseRValue):
            return self._operand_type(value.operand, locals_by_id, span)
        if isinstance(value, BinaryRValue):
            self._operand_type(value.left, locals_by_id, span)
            self._operand_type(value.right, locals_by_id, span)
            return value.type
        if isinstance(value, UnaryRValue):
            self._operand_type(value.operand, locals_by_id, span)
            return value.type
        if isinstance(value, CastRValue):
            self._operand_type(value.operand, locals_by_id, span)
            return value.type
        if isinstance(value, AggregateRValue):
            for operand in value.operands:
                self._operand_type(operand, locals_by_id, span)
            return value.type
        if isinstance(value, DiscriminantRValue):
            self._operand_type(value.operand, locals_by_id, span)
            return value.type
        if isinstance(value, PayloadRValue):
            self._operand_type(value.operand, locals_by_id, span)
            if value.index < 0:
                self._issue("MIR0503", "Payload index must be non-negative", span)
            return value.type
        self._issue("MIR0500", f"Unknown rvalue {type(value).__name__}", span)
        return None

    def _operand_type(self, operand: Operand, locals_by_id: dict, span: MIRSpan) -> MIRType | None:
        if isinstance(operand, ConstOperand):
            if not isinstance(operand.type, MIRType):
                self._issue("MIR0502", "Constant operand has an invalid type", span)
                return None
            return operand.type
        if isinstance(operand, (CopyOperand, MoveOperand)):
            return self._place_type(operand.place, locals_by_id, span)
        self._issue("MIR0501", f"Unknown operand {type(operand).__name__}", span)
        return None

    def _place_type(self, place: Place, locals_by_id: dict, span: MIRSpan) -> MIRType | None:
        local = self._require_local(place.local, locals_by_id, span)
        for projection in place.projections:
            if isinstance(projection, IndexProjection):
                self._require_local(projection.local, locals_by_id, span)
            elif not isinstance(projection, (FieldProjection, DerefProjection)):
                self._issue("MIR0602", f"Unknown place projection {type(projection).__name__}", span)
        return local.type if local is not None else None

    def _require_local(self, local_id: int, locals_by_id: dict, span: MIRSpan):
        local = locals_by_id.get(local_id)
        if local is None:
            self._issue("MIR0600", f"Unknown local {local_id}", span)
        return local

    def _require_block(self, block_id: int, valid_blocks: set[int], span: MIRSpan) -> None:
        if block_id not in valid_blocks:
            self._issue("MIR0601", f"Unknown block {block_id}", span)

    def _verify_span(self, span: object) -> None:
        if not isinstance(span, MIRSpan):
            self._issue("MIR0700", "Invalid source span", self._module_span())
        elif span.line < 1 or span.column < 1 or span.length < 1:
            self._issue("MIR0701", "Source span coordinates must be positive", span)

    def _module_span(self) -> MIRSpan:
        if self.module.functions:
            return self.module.functions[0].span
        return MIRSpan(self.module.source_name or "<mir>", 1, 1)

    def _issue(self, code: str, message: str, span: MIRSpan) -> None:
        self.issues.append(MIRVerificationIssue(code, message, span))


def collect_mir_issues(module: MIRModule) -> tuple[MIRVerificationIssue, ...]:
    return MIRVerifier(module).collect()


def verify_mir(module: MIRModule) -> MIRModule:
    issues = collect_mir_issues(module)
    if issues:
        raise MIRVerificationError(issues)
    return module
