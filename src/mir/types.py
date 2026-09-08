"""Target-independent type identities for the experimental MIR."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from src.ir.types import IRType


@dataclass(frozen=True, slots=True)
class MIRType:
    name: str
    arguments: Tuple["MIRType", ...] = ()
    optional: bool = False
    pointer: bool = False
    parameter_types: Tuple["MIRType", ...] = ()
    return_type: "MIRType | None" = None

    @property
    def is_function(self) -> bool:
        return self.return_type is not None

    def canonical(self) -> str:
        if self.is_function:
            parameters = ",".join(item.canonical() for item in self.parameter_types)
            rendered = f"fn({parameters})->{self.return_type.canonical()}"
        else:
            rendered = self.name
            if self.arguments:
                rendered += "<" + ",".join(item.canonical() for item in self.arguments) + ">"
            if self.pointer:
                rendered = "*" + rendered
        if self.optional:
            rendered += "?"
        return rendered

    def __str__(self) -> str:
        return self.canonical()


def from_hir_type(value: IRType) -> MIRType:
    return MIRType(
        name=value.name,
        arguments=tuple(from_hir_type(item) for item in value.arguments),
        optional=value.optional,
        pointer=value.pointer,
        parameter_types=tuple(from_hir_type(item) for item in value.parameter_types),
        return_type=from_hir_type(value.return_type) if value.return_type is not None else None,
    )
