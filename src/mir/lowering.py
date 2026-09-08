"""Deliberately narrow Typed HIR to MIR skeleton lowering for M1.

M2 owns expression and control-flow lowering. M1 only proves declarations,
locals, blocks, terminators, serialization, and verification without fabricating
semantics for function bodies.
"""

from __future__ import annotations

from src.ir.model import IRFunction, IRModule, IRStatement, SourceSpan

from .builder import MIRFunctionBuilder
from .model import MIRModule, MIRSpan, ReturnTerminator
from .types import from_hir_type
from .verifier import verify_mir


class MIRLoweringError(ValueError):
    def __init__(self, message: str, span: MIRSpan):
        self.message = message
        self.span = span
        super().__init__(f"{span.source}:{span.line}:{span.column}: {message}")


def _span(value: SourceSpan) -> MIRSpan:
    return MIRSpan(value.source, value.line, value.column, value.length)


def lower_hir_skeleton(hir: IRModule) -> MIRModule:
    """Lower the semantics-free M1 subset and reject everything assigned to M2+."""
    top_level_statements = tuple(item for item in hir.items if isinstance(item, IRStatement))
    if top_level_statements:
        span = _span(top_level_statements[0].span)
        raise MIRLoweringError("M1 does not lower top-level executable statements", span)

    functions = []
    for item in hir.items:
        if not isinstance(item, IRFunction):
            continue
        span = _span(item.span)
        if item.body:
            raise MIRLoweringError(
                f"M1 only lowers empty function bodies; '{item.name}' requires M2 lowering",
                span,
            )
        builder = MIRFunctionBuilder(item.name, item.symbol, from_hir_type(item.return_type), span)
        for parameter in item.params:
            builder.new_local(
                parameter.name,
                from_hir_type(parameter.type),
                kind="parameter",
                span=span,
            )
        entry = builder.new_block()
        builder.set_terminator(entry, ReturnTerminator(span))
        functions.append(builder.finish())

    module = MIRModule(hir.source_name, hir.target, tuple(functions))
    verify_mir(module)
    return module
