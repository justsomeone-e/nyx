"""Target legalization contracts for the experimental MIR pipeline.

Legalization is a hard gate: a backend may only receive operations explicitly
listed by its profile. M5 currently migrates C++ and LLVM plus deliberately
bounded WebAssembly, Rust, JavaScript, Python, and C17 pilots.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable

from src.core.backend_capabilities import normalize_backend_name, resolve_backend

from .model import (
    AggregateRValue,
    AssertTerminator,
    AssignStatement,
    BinaryRValue,
    BorrowRValue,
    CallTerminator,
    CastRValue,
    ConstantIndexProjection,
    ConstOperand,
    CopyOperand,
    DeinitStatement,
    DerefProjection,
    DiscriminantRValue,
    DropTerminator,
    FieldProjection,
    GotoTerminator,
    IndexProjection,
    MIRFunction,
    MIRModule,
    MIRSpan,
    MIREnumDef,
    MIRStructDef,
    MoveOperand,
    NopStatement,
    PayloadRValue,
    Place,
    ReleaseStatement,
    RetainStatement,
    ReturnTerminator,
    StorageDeadStatement,
    StorageLiveStatement,
    SwitchIntTerminator,
    SwitchValueTerminator,
    ThrowTerminator,
    UnaryRValue,
    UnreachableTerminator,
    UseRValue,
    VariantProjection,
)
from .types import MIRType
from .verifier import verify_mir


MIR_LEGALIZATION_SCHEMA_VERSION = 2
MIR_BACKEND_MIGRATION_ORDER = ("cpp", "llvm", "wasm", "rust", "js", "python", "c")


@dataclass(frozen=True, slots=True)
class MIRBackendProfile:
    target: str
    migration_rank: int
    migration_status: str
    integer_width: int
    overflow: str
    exceptions: bool
    threads: bool
    ownership: str
    abi: str
    legal_statements: frozenset[str]
    legal_rvalues: frozenset[str]
    legal_terminators: frozenset[str]
    legal_projections: frozenset[str]
    legal_types: frozenset[str]
    legal_runtime_calls: frozenset[str]
    legal_binary_ops: frozenset[str]
    legal_unary_ops: frozenset[str]

    @property
    def emitter_available(self) -> bool:
        return self.migration_status == "pilot"

    def to_dict(self) -> dict[str, object]:
        return {
            "target": self.target,
            "migration_rank": self.migration_rank,
            "migration_status": self.migration_status,
            "integer_width": self.integer_width,
            "overflow": self.overflow,
            "exceptions": self.exceptions,
            "threads": self.threads,
            "ownership": self.ownership,
            "abi": self.abi,
            "legal_statements": sorted(self.legal_statements),
            "legal_rvalues": sorted(self.legal_rvalues),
            "legal_terminators": sorted(self.legal_terminators),
            "legal_projections": sorted(self.legal_projections),
            "legal_types": sorted(self.legal_types),
            "legal_runtime_calls": sorted(self.legal_runtime_calls),
            "legal_binary_ops": sorted(self.legal_binary_ops),
            "legal_unary_ops": sorted(self.legal_unary_ops),
        }


_SCALAR_STATEMENTS = frozenset({
    AssignStatement.__name__,
    StorageLiveStatement.__name__,
    StorageDeadStatement.__name__,
    NopStatement.__name__,
})
_SCALAR_RVALUES = frozenset({
    UseRValue.__name__,
    BinaryRValue.__name__,
    UnaryRValue.__name__,
    CastRValue.__name__,
})
_SCALAR_TERMINATORS = frozenset({
    GotoTerminator.__name__,
    SwitchIntTerminator.__name__,
    SwitchValueTerminator.__name__,
    ReturnTerminator.__name__,
    CallTerminator.__name__,
    AssertTerminator.__name__,
    UnreachableTerminator.__name__,
})
_SCALAR_TYPES = frozenset({"void", "bool", "string", "int", "float", "f64"})
_SCALAR_RUNTIME = frozenset({"builtin::print"})
_SCALAR_BINARY_OPS = frozenset({
    "+", "-", "*", "/", "%", "&", "|", "^", "<<", ">>",
    "==", "!=", "<", "<=", ">", ">=",
})
_SCALAR_UNARY_OPS = frozenset({"!", "not", "+", "-", "~"})


def _profile(
    target: str,
    rank: int,
    *,
    status: str,
    integer_width: int,
    exceptions: bool,
    threads: bool,
    ownership: str,
    abi: str,
) -> MIRBackendProfile:
    return MIRBackendProfile(
        target=target,
        migration_rank=rank,
        migration_status=status,
        integer_width=integer_width,
        overflow="wrap",
        exceptions=exceptions,
        threads=threads,
        ownership=ownership,
        abi=abi,
        legal_statements=_SCALAR_STATEMENTS,
        legal_rvalues=_SCALAR_RVALUES,
        legal_terminators=_SCALAR_TERMINATORS,
        legal_projections=frozenset(),
        legal_types=_SCALAR_TYPES,
        legal_runtime_calls=_SCALAR_RUNTIME,
        legal_binary_ops=_SCALAR_BINARY_OPS,
        legal_unary_ops=_SCALAR_UNARY_OPS,
    )


MIR_BACKEND_PROFILES = {
    "cpp": _profile(
        "cpp", 1, status="pilot", integer_width=64, exceptions=True,
        threads=True, ownership="native-raii", abi="native-x64",
    ),
    "llvm": _profile(
        "llvm", 2, status="pilot", integer_width=64, exceptions=False,
        threads=False, ownership="explicit-runtime", abi="native-x64",
    ),
    "wasm": _profile(
        "wasm", 3, status="pilot", integer_width=64, exceptions=False,
        threads=False, ownership="linear-memory-runtime", abi="bundle-v1-wasm32",
    ),
    "rust": _profile(
        "rust", 4, status="pilot", integer_width=64, exceptions=False,
        threads=False, ownership="rust-values", abi="rust-2021",
    ),
    "js": _profile(
        "js", 5, status="pilot", integer_width=64, exceptions=True,
        threads=False, ownership="garbage-collected", abi="node-es2022",
    ),
    "python": _profile(
        "python", 6, status="pilot", integer_width=64, exceptions=True,
        threads=False, ownership="garbage-collected", abi="python-3",
    ),
    "c": _profile(
        "c", 7, status="pilot", integer_width=64, exceptions=False,
        threads=False, ownership="explicit-runtime", abi="c17-native",
    ),
}

# C++ is migrated first and therefore owns the initial aggregate legalization
# surface. Other targets remain deliberately scalar until their runtime/layout
# adapters are implemented and tested.
MIR_BACKEND_PROFILES["cpp"] = replace(
    MIR_BACKEND_PROFILES["cpp"],
    legal_rvalues=MIR_BACKEND_PROFILES["cpp"].legal_rvalues | frozenset({
        AggregateRValue.__name__, BorrowRValue.__name__, DiscriminantRValue.__name__,
        PayloadRValue.__name__,
    }),
    legal_statements=MIR_BACKEND_PROFILES["cpp"].legal_statements | frozenset({
        DeinitStatement.__name__, ReleaseStatement.__name__, RetainStatement.__name__,
    }),
    legal_terminators=MIR_BACKEND_PROFILES["cpp"].legal_terminators | frozenset({
        DropTerminator.__name__, ThrowTerminator.__name__,
    }),
    legal_projections=frozenset({
        DerefProjection.__name__, FieldProjection.__name__, IndexProjection.__name__,
        ConstantIndexProjection.__name__,
    }),
    legal_types=MIR_BACKEND_PROFILES["cpp"].legal_types | frozenset({"Array", "Option", "Result"}),
    legal_runtime_calls=MIR_BACKEND_PROFILES["cpp"].legal_runtime_calls | frozenset({
        "builtin::len", "builtin::to_string",
    }),
)

# The first MIR-to-Wasm slice is deliberately pure and integer-focused. Heap
# values, host calls, casts, and aggregate ABI lowering stay behind the gate.
MIR_BACKEND_PROFILES["wasm"] = replace(
    MIR_BACKEND_PROFILES["wasm"],
    legal_rvalues=frozenset({
        BinaryRValue.__name__, UnaryRValue.__name__, UseRValue.__name__,
    }),
    legal_terminators=frozenset({
        AssertTerminator.__name__, CallTerminator.__name__, GotoTerminator.__name__,
        ReturnTerminator.__name__, SwitchIntTerminator.__name__, UnreachableTerminator.__name__,
    }),
    legal_types=frozenset({"void", "bool", "int"}),
    legal_runtime_calls=frozenset(),
)

# Rust starts with the full scalar/control-flow surface but keeps casts,
# aggregates, explicit cleanup, and target runtime bindings out of the pilot.
MIR_BACKEND_PROFILES["rust"] = replace(
    MIR_BACKEND_PROFILES["rust"],
    legal_rvalues=frozenset({
        AggregateRValue.__name__, BinaryRValue.__name__, CastRValue.__name__,
        UnaryRValue.__name__, UseRValue.__name__,
    }),
    legal_projections=frozenset({
        FieldProjection.__name__, IndexProjection.__name__, ConstantIndexProjection.__name__,
    }),
    legal_types=MIR_BACKEND_PROFILES["rust"].legal_types | frozenset({"Array"}),
    legal_runtime_calls=MIR_BACKEND_PROFILES["rust"].legal_runtime_calls | frozenset({
        "builtin::len", "builtin::to_string",
    }),
)

# JavaScript uses BigInt for the Nyx i64 contract. Casts and heap/aggregate
# values remain excluded until their host representation is versioned.
MIR_BACKEND_PROFILES["js"] = replace(
    MIR_BACKEND_PROFILES["js"],
    legal_rvalues=frozenset({
        AggregateRValue.__name__, BinaryRValue.__name__, CastRValue.__name__,
        DiscriminantRValue.__name__, PayloadRValue.__name__, UnaryRValue.__name__,
        UseRValue.__name__,
    }),
    legal_projections=frozenset({
        FieldProjection.__name__, IndexProjection.__name__, ConstantIndexProjection.__name__,
    }),
    legal_types=MIR_BACKEND_PROFILES["js"].legal_types | frozenset({"Array", "Option", "Result"}),
    legal_runtime_calls=MIR_BACKEND_PROFILES["js"].legal_runtime_calls | frozenset({
        "builtin::len", "builtin::to_string",
    }),
)

# Python has arbitrary-precision integers, so the emitter inserts explicit
# signed-i64 normalization. Casts and aggregate values remain gated.
MIR_BACKEND_PROFILES["python"] = replace(
    MIR_BACKEND_PROFILES["python"],
    legal_rvalues=frozenset({
        AggregateRValue.__name__, BinaryRValue.__name__, CastRValue.__name__,
        DiscriminantRValue.__name__, PayloadRValue.__name__, UnaryRValue.__name__,
        UseRValue.__name__,
    }),
    legal_projections=frozenset({
        FieldProjection.__name__, IndexProjection.__name__, ConstantIndexProjection.__name__,
    }),
    legal_types=MIR_BACKEND_PROFILES["python"].legal_types | frozenset({"Array", "Option", "Result"}),
    legal_runtime_calls=MIR_BACKEND_PROFILES["python"].legal_runtime_calls | frozenset({
        "builtin::len", "builtin::to_string",
    }),
)

# C17 uses explicit bit conversions and a tiny tracked string runtime. Casts,
# projections, aggregate values, and cleanup edges remain gated.
MIR_BACKEND_PROFILES["c"] = replace(
    MIR_BACKEND_PROFILES["c"],
    legal_rvalues=frozenset({
        BinaryRValue.__name__, UnaryRValue.__name__, UseRValue.__name__,
    }),
)


@dataclass(frozen=True, slots=True)
class MIRLegalizationIssue:
    code: str
    message: str
    span: MIRSpan
    target: str


class MIRLegalizationError(ValueError):
    def __init__(self, issues: Iterable[MIRLegalizationIssue]):
        self.issues = tuple(issues)
        summary = "; ".join(f"{issue.code}: {issue.message}" for issue in self.issues)
        super().__init__(summary)


def resolve_mir_backend_profile(target: str) -> MIRBackendProfile | None:
    canonical = normalize_backend_name(target)
    if resolve_backend(canonical) is None:
        return None
    return MIR_BACKEND_PROFILES.get(canonical)


def mir_backend_manifest() -> dict[str, object]:
    return {
        "schema_version": MIR_LEGALIZATION_SCHEMA_VERSION,
        "migration_order": list(MIR_BACKEND_MIGRATION_ORDER),
        "profiles": [MIR_BACKEND_PROFILES[name].to_dict() for name in MIR_BACKEND_MIGRATION_ORDER],
    }


class _Legalizer:
    def __init__(self, module: MIRModule, target: str, *, require_emitter: bool):
        self.module = module
        self.target = normalize_backend_name(target)
        self.profile = resolve_mir_backend_profile(self.target)
        self.require_emitter = require_emitter
        self.issues: list[MIRLegalizationIssue] = []
        self.user_functions = {function.symbol for function in module.functions}
        self.type_definitions = {definition.name: definition for definition in module.type_definitions}

    def collect(self) -> tuple[MIRLegalizationIssue, ...]:
        span = self._module_span()
        if resolve_backend(self.target) is None:
            self._issue("MIRG1000", f"Unknown MIR target '{self.target}'", span)
            return tuple(self.issues)
        if self.profile is None:
            self._issue(
                "MIRG1001",
                f"Target '{self.target}' has no MIR legalization profile",
                span,
            )
            return tuple(self.issues)
        if self.require_emitter and not self.profile.emitter_available:
            self._issue(
                "MIRG1009",
                f"Target '{self.target}' has a legalization contract but no migrated MIR emitter",
                span,
            )
            return tuple(self.issues)
        for definition in self.module.type_definitions:
            if self.target in {"cpp", "rust", "js", "python"} and isinstance(definition, MIRStructDef):
                for field in definition.fields:
                    self._type(field.type, span)
                continue
            if self.target in {"cpp", "js", "python"} and isinstance(definition, MIREnumDef):
                for variant in definition.variants:
                    for payload_type in variant.payload_types:
                        self._type(payload_type, span)
                continue
            kind = "enum" if isinstance(definition, MIREnumDef) else "aggregate"
            self._issue(
                "MIRG1002",
                f"Target '{self.target}' MIR pilot does not yet legalize {kind} type '{definition.name}'",
                span,
            )
        for function in self.module.functions:
            self._function(function)
        return tuple(self.issues)

    def _function(self, function: MIRFunction) -> None:
        assert self.profile is not None
        discarded_any = {
            terminator.destination.local
            for block in function.blocks
            for terminator in (block.terminator,)
            if isinstance(terminator, CallTerminator)
            and terminator.destination is not None
            and terminator.function in self.user_functions
            and any(
                candidate.symbol == terminator.function
                and candidate.name == "main"
                and candidate.locals[candidate.return_local].type.name == "any"
                for candidate in self.module.functions
            )
        }
        for local in function.locals:
            if local.type.name == "any" and local.id == function.return_local and function.name == "main":
                continue
            if local.type.name == "any" and local.id in discarded_any:
                continue
            self._type(local.type, local.span)
        for block in function.blocks:
            for statement in block.statements:
                name = type(statement).__name__
                if name not in self.profile.legal_statements:
                    self._issue("MIRG1003", f"Statement '{name}' is not legal for target '{self.target}'", statement.span)
                    continue
                if isinstance(statement, AssignStatement):
                    self._place(statement.place, statement.span)
                    self._rvalue(statement.value, statement.span)
                elif isinstance(statement, (RetainStatement, ReleaseStatement, DeinitStatement)):
                    self._place(statement.place, statement.span)
            terminator = block.terminator
            name = type(terminator).__name__
            if name not in self.profile.legal_terminators:
                self._issue("MIRG1006", f"Terminator '{name}' is not legal for target '{self.target}'", terminator.span)
                continue
            self._terminator(terminator)

    def _rvalue(self, value: object, span: MIRSpan) -> None:
        assert self.profile is not None
        name = type(value).__name__
        if name not in self.profile.legal_rvalues:
            self._issue("MIRG1004", f"Rvalue '{name}' is not legal for target '{self.target}'", span)
            return
        if isinstance(value, UseRValue):
            self._operand(value.operand, span)
        elif isinstance(value, BinaryRValue):
            self._operand(value.left, span)
            self._operand(value.right, span)
            self._type(value.type, span)
            if value.op not in self.profile.legal_binary_ops:
                self._issue(
                    "MIRG1010",
                    f"Binary operation '{value.op}' is not legal for target '{self.target}'",
                    span,
                )
        elif isinstance(value, UnaryRValue):
            self._operand(value.operand, span)
            self._type(value.type, span)
            if value.op not in self.profile.legal_unary_ops:
                self._issue(
                    "MIRG1010",
                    f"Unary operation '{value.op}' is not legal for target '{self.target}'",
                    span,
                )
        elif isinstance(value, CastRValue):
            self._operand(value.operand, span)
            self._type(value.type, span)
        elif isinstance(value, AggregateRValue):
            allowed_kinds = {
                "cpp": {"array", "struct", "enum", "option", "result"},
                "rust": {"array", "struct"},
                "js": {"array", "struct", "enum", "option", "result"},
                "python": {"array", "struct", "enum", "option", "result"},
            }.get(self.target, set())
            if value.kind not in allowed_kinds:
                self._issue(
                    "MIRG1004",
                    f"Aggregate kind '{value.kind}' is not legal for target '{self.target}'",
                    span,
                )
            for operand in value.operands:
                self._operand(operand, span)
            self._type(value.type, span)
        elif isinstance(value, DiscriminantRValue):
            self._operand(value.operand, span)
            self._type(value.type, span)
        elif isinstance(value, PayloadRValue):
            self._operand(value.operand, span)
            self._type(value.type, span)
        elif isinstance(value, BorrowRValue):
            self._place(value.place, span)
            self._type(value.type, span)

    def _terminator(self, value: object) -> None:
        if isinstance(value, (SwitchIntTerminator, SwitchValueTerminator)):
            self._operand(value.discriminator, value.span)
        elif isinstance(value, CallTerminator):
            for argument in value.arguments:
                self._operand(argument, value.span)
            if value.destination is not None:
                self._place(value.destination, value.span)
            if value.unwind is not None or value.error_destination is not None:
                self._issue(
                    "MIRG1008",
                    f"Unwind edges are not legalized by the '{self.target}' MIR pilot",
                    value.span,
                )
            if value.function not in self.user_functions and value.function not in self.profile.legal_runtime_calls:
                self._issue(
                    "MIRG1007",
                    f"Runtime call '{value.function}' is not legal for target '{self.target}'",
                    value.span,
                )
        elif isinstance(value, AssertTerminator):
            self._operand(value.condition, value.span)
            if value.unwind is not None:
                self._issue(
                    "MIRG1008",
                    f"Unwind edges are not legalized by the '{self.target}' MIR pilot",
                    value.span,
                )
        elif isinstance(value, ThrowTerminator):
            self._operand(value.value, value.span)
            if value.destination is not None:
                self._place(value.destination, value.span)
        elif isinstance(value, DropTerminator):
            self._place(value.place, value.span)
            if value.unwind is not None:
                self._issue(
                    "MIRG1008",
                    f"Unwind edges are not legalized by the '{self.target}' MIR pilot",
                    value.span,
                )

    def _operand(self, value: object, span: MIRSpan) -> None:
        if isinstance(value, ConstOperand):
            self._type(value.type, span)
        elif isinstance(value, (CopyOperand, MoveOperand)):
            self._place(value.place, span)

    def _place(self, place: Place, span: MIRSpan) -> None:
        assert self.profile is not None
        for projection in place.projections:
            name = type(projection).__name__
            if name not in self.profile.legal_projections:
                self._issue(
                    "MIRG1005",
                    f"Projection '{name}' is not legal for target '{self.target}'",
                    span,
                )

    def _type(self, value: MIRType, span: MIRSpan) -> None:
        assert self.profile is not None
        if self.target == "cpp" and value.pointer:
            self._type(replace(value, pointer=False), span)
            return
        if self.target in {"cpp", "rust", "js", "python"} and value.optional:
            self._type(replace(value, optional=False), span)
            return
        if self.target in {"cpp", "rust", "js", "python"} and value.name == "Array" and len(value.arguments) == 1:
            self._type(value.arguments[0], span)
            return
        if self.target in {"cpp", "js", "python"} and value.name in ("Option", "Result") and value.arguments:
            for argument in value.arguments:
                if argument.name != "any":
                    self._type(argument, span)
            return
        if (
            self.target in {"cpp", "rust", "js", "python"}
            and isinstance(
                self.type_definitions.get(value.name),
                (MIRStructDef, MIREnumDef) if self.target != "rust" else MIRStructDef,
            )
            and not value.arguments
        ):
            return
        if value.optional or value.pointer or value.is_function or value.arguments:
            self._issue("MIRG1002", f"Type '{value}' is not legal for target '{self.target}'", span)
            return
        if value.name not in self.profile.legal_types:
            self._issue("MIRG1002", f"Type '{value}' is not legal for target '{self.target}'", span)

    def _issue(self, code: str, message: str, span: MIRSpan) -> None:
        self.issues.append(MIRLegalizationIssue(code, message, span, self.target))

    def _module_span(self) -> MIRSpan:
        if self.module.functions:
            return self.module.functions[0].span
        return MIRSpan(self.module.source_name, 1, 1)


def collect_legalization_issues(
    module: MIRModule,
    target: str,
    *,
    require_emitter: bool = False,
) -> tuple[MIRLegalizationIssue, ...]:
    verify_mir(module)
    return _Legalizer(module, target, require_emitter=require_emitter).collect()


def legalize_mir(
    module: MIRModule,
    target: str,
    *,
    require_emitter: bool = False,
) -> MIRModule:
    """Return verified target-legal MIR or raise with stable diagnostics."""
    issues = collect_legalization_issues(module, target, require_emitter=require_emitter)
    if issues:
        raise MIRLegalizationError(issues)
    return module
