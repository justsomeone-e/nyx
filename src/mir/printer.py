"""Deterministic human-readable MIR printer."""

from __future__ import annotations

from .model import (
    AssertTerminator,
    AssignStatement,
    BinaryRValue,
    CallTerminator,
    ConstOperand,
    CopyOperand,
    DropTerminator,
    GotoTerminator,
    MIRModule,
    MoveOperand,
    NopStatement,
    Place,
    ReturnTerminator,
    StorageDeadStatement,
    StorageLiveStatement,
    SwitchIntTerminator,
    UnaryRValue,
    UnreachableTerminator,
    UseRValue,
)


def _place(value: Place) -> str:
    rendered = f"_{value.local}"
    for projection in value.projections:
        name = type(projection).__name__
        if name == "FieldProjection":
            rendered += f".{projection.name}"
        elif name == "IndexProjection":
            rendered += f"[_{projection.local}]"
        else:
            rendered = f"(*{rendered})"
    return rendered


def _operand(value: object) -> str:
    if isinstance(value, ConstOperand):
        return f"const {value.value!r}: {value.type}"
    if isinstance(value, CopyOperand):
        return f"copy {_place(value.place)}"
    if isinstance(value, MoveOperand):
        return f"move {_place(value.place)}"
    raise TypeError(f"Unknown MIR operand {type(value).__name__}")


def _rvalue(value: object) -> str:
    if isinstance(value, UseRValue):
        return _operand(value.operand)
    if isinstance(value, BinaryRValue):
        return f"{value.op}({_operand(value.left)}, {_operand(value.right)}): {value.type}"
    if isinstance(value, UnaryRValue):
        return f"{value.op}({_operand(value.operand)}): {value.type}"
    raise TypeError(f"Unknown MIR rvalue {type(value).__name__}")


def _statement(value: object) -> str:
    if isinstance(value, AssignStatement):
        return f"{_place(value.place)} = {_rvalue(value.value)}"
    if isinstance(value, StorageLiveStatement):
        return f"StorageLive(_{value.local})"
    if isinstance(value, StorageDeadStatement):
        return f"StorageDead(_{value.local})"
    if isinstance(value, NopStatement):
        return "nop"
    raise TypeError(f"Unknown MIR statement {type(value).__name__}")


def _terminator(value: object) -> str:
    if isinstance(value, GotoTerminator):
        return f"goto -> bb{value.target}"
    if isinstance(value, SwitchIntTerminator):
        targets = ", ".join(f"{key}: bb{target}" for key, target in value.targets)
        return f"switchInt({_operand(value.discriminator)}) -> [{targets}, otherwise: bb{value.otherwise}]"
    if isinstance(value, ReturnTerminator):
        return "return"
    if isinstance(value, CallTerminator):
        arguments = ", ".join(_operand(item) for item in value.arguments)
        destination = _place(value.destination) if value.destination is not None else "_"
        target = f"bb{value.target}" if value.target is not None else "unreachable"
        unwind = f", unwind bb{value.unwind}" if value.unwind is not None else ""
        return f"{destination} = call {value.function}({arguments}) -> {target}{unwind}"
    if isinstance(value, DropTerminator):
        unwind = f", unwind bb{value.unwind}" if value.unwind is not None else ""
        return f"drop {_place(value.place)} -> bb{value.target}{unwind}"
    if isinstance(value, AssertTerminator):
        unwind = f", unwind bb{value.unwind}" if value.unwind is not None else ""
        return (
            f"assert({_operand(value.condition)} == {str(value.expected).lower()}, "
            f"{value.message!r}) -> bb{value.target}{unwind}"
        )
    if isinstance(value, UnreachableTerminator):
        return "unreachable"
    raise TypeError(f"Unknown MIR terminator {type(value).__name__}")


def print_mir(module: MIRModule) -> str:
    lines = [f"mir v{module.schema_version} {module.source_name!r} target {module.target} {{"]
    for function in module.functions:
        parameters = ", ".join(f"_{local_id}" for local_id in function.parameters)
        lines.append(f"  fn {function.name} [{function.symbol}]({parameters}) {{")
        for local in function.locals:
            lines.append(f"    let _{local.id}: {local.type} // {local.kind} {local.name}")
        for block in function.blocks:
            lines.append(f"    bb{block.id}:")
            for statement in block.statements:
                lines.append(f"      {_statement(statement)}")
            lines.append(f"      {_terminator(block.terminator)}")
        lines.append("  }")
    lines.append("}")
    return "\n".join(lines) + "\n"
