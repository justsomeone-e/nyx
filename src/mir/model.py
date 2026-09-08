"""Immutable control-flow MIR model.

The schema is experimental and independent from public Typed HIR schema v1.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from .types import MIRType


MIR_SCHEMA_VERSION = 1


@dataclass(frozen=True, slots=True)
class MIRSpan:
    source: str
    line: int
    column: int
    length: int = 1


@dataclass(frozen=True, slots=True)
class FieldProjection:
    name: str


@dataclass(frozen=True, slots=True)
class IndexProjection:
    local: int


@dataclass(frozen=True, slots=True)
class DerefProjection:
    pass


Projection = FieldProjection | IndexProjection | DerefProjection


@dataclass(frozen=True, slots=True)
class Place:
    local: int
    projections: Tuple[Projection, ...] = ()


@dataclass(frozen=True, slots=True)
class ConstOperand:
    type: MIRType
    value: object


@dataclass(frozen=True, slots=True)
class CopyOperand:
    place: Place


@dataclass(frozen=True, slots=True)
class MoveOperand:
    place: Place


Operand = ConstOperand | CopyOperand | MoveOperand


@dataclass(frozen=True, slots=True)
class UseRValue:
    operand: Operand


@dataclass(frozen=True, slots=True)
class BinaryRValue:
    op: str
    left: Operand
    right: Operand
    type: MIRType


@dataclass(frozen=True, slots=True)
class UnaryRValue:
    op: str
    operand: Operand
    type: MIRType


@dataclass(frozen=True, slots=True)
class CastRValue:
    kind: str
    operand: Operand
    type: MIRType


@dataclass(frozen=True, slots=True)
class AggregateRValue:
    kind: str
    name: str
    operands: Tuple[Operand, ...]
    type: MIRType


@dataclass(frozen=True, slots=True)
class DiscriminantRValue:
    operand: Operand
    type: MIRType


@dataclass(frozen=True, slots=True)
class PayloadRValue:
    operand: Operand
    index: int
    type: MIRType


RValue = (
    UseRValue
    | BinaryRValue
    | UnaryRValue
    | CastRValue
    | AggregateRValue
    | DiscriminantRValue
    | PayloadRValue
)


@dataclass(frozen=True, slots=True)
class AssignStatement:
    place: Place
    value: RValue
    span: MIRSpan


@dataclass(frozen=True, slots=True)
class StorageLiveStatement:
    local: int
    span: MIRSpan


@dataclass(frozen=True, slots=True)
class StorageDeadStatement:
    local: int
    span: MIRSpan


@dataclass(frozen=True, slots=True)
class NopStatement:
    span: MIRSpan


Statement = AssignStatement | StorageLiveStatement | StorageDeadStatement | NopStatement


@dataclass(frozen=True, slots=True)
class GotoTerminator:
    target: int
    span: MIRSpan


@dataclass(frozen=True, slots=True)
class SwitchIntTerminator:
    discriminator: Operand
    targets: Tuple[Tuple[int, int], ...]
    otherwise: int
    span: MIRSpan


@dataclass(frozen=True, slots=True)
class SwitchValueTerminator:
    discriminator: Operand
    targets: Tuple[Tuple[object, int], ...]
    otherwise: int
    span: MIRSpan


@dataclass(frozen=True, slots=True)
class ReturnTerminator:
    span: MIRSpan


@dataclass(frozen=True, slots=True)
class CallTerminator:
    function: str
    arguments: Tuple[Operand, ...]
    destination: Place | None
    target: int | None
    unwind: int | None
    span: MIRSpan
    error_destination: Place | None = None


@dataclass(frozen=True, slots=True)
class DropTerminator:
    place: Place
    target: int
    unwind: int | None
    span: MIRSpan


@dataclass(frozen=True, slots=True)
class AssertTerminator:
    condition: Operand
    expected: bool
    message: str
    target: int
    unwind: int | None
    span: MIRSpan


@dataclass(frozen=True, slots=True)
class UnreachableTerminator:
    span: MIRSpan


@dataclass(frozen=True, slots=True)
class ThrowTerminator:
    value: Operand
    target: int | None
    destination: Place | None
    span: MIRSpan


Terminator = (
    GotoTerminator
    | SwitchIntTerminator
    | SwitchValueTerminator
    | ReturnTerminator
    | CallTerminator
    | DropTerminator
    | AssertTerminator
    | UnreachableTerminator
    | ThrowTerminator
)


@dataclass(frozen=True, slots=True)
class MIRLocal:
    id: int
    name: str
    type: MIRType
    kind: str
    span: MIRSpan


@dataclass(frozen=True, slots=True)
class MIRBasicBlock:
    id: int
    statements: Tuple[Statement, ...]
    terminator: Terminator


@dataclass(frozen=True, slots=True)
class MIRFunction:
    name: str
    symbol: str
    locals: Tuple[MIRLocal, ...]
    parameters: Tuple[int, ...]
    return_local: int
    blocks: Tuple[MIRBasicBlock, ...]
    span: MIRSpan


@dataclass(frozen=True, slots=True)
class MIRModule:
    source_name: str
    target: str
    functions: Tuple[MIRFunction, ...]
    schema_version: int = MIR_SCHEMA_VERSION
