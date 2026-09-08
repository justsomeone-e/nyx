"""Verified pass pipeline for experimental MIR."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Tuple

from .model import MIRModule
from .serialization import fingerprint
from .verifier import verify_mir


class MIRPass(Protocol):
    name: str

    def run(self, module: MIRModule) -> MIRModule:
        ...


@dataclass(frozen=True, slots=True)
class MIRPassRecord:
    name: str
    changed: bool
    before_fingerprint: str
    after_fingerprint: str


@dataclass(frozen=True, slots=True)
class MIRPassResult:
    module: MIRModule
    records: Tuple[MIRPassRecord, ...]


class MIRPassManager:
    def __init__(self, passes: tuple[MIRPass, ...] = ()):
        self.passes = tuple(passes)

    def run(self, module: MIRModule) -> MIRPassResult:
        current = verify_mir(module)
        records = []
        for transform in self.passes:
            before = fingerprint(current)
            candidate = transform.run(current)
            if not isinstance(candidate, MIRModule):
                raise TypeError(f"MIR pass {transform.name} must return MIRModule")
            if candidate.schema_version != current.schema_version:
                raise ValueError(f"MIR pass {transform.name} changed the schema version")
            if candidate.source_name != current.source_name or candidate.target != current.target:
                raise ValueError(f"MIR pass {transform.name} changed module identity")
            verify_mir(candidate)
            after = fingerprint(candidate)
            records.append(MIRPassRecord(transform.name, before != after, before, after))
            current = candidate
        return MIRPassResult(current, tuple(records))
