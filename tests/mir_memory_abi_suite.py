from dataclasses import replace
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.api import NyxCompiler
from src.mir import (
    AggregateRValue,
    AssignStatement,
    BorrowRValue,
    ConstOperand,
    CopyOperand,
    DropTerminator,
    DerefProjection,
    GotoTerminator,
    LayoutEngine,
    MIRFunctionBuilder,
    MIRInterpreter,
    MIRModule,
    MIRSpan,
    MIRStructDef,
    MIRType,
    MoveOperand,
    Place,
    ReturnTerminator,
    ReleaseStatement,
    RetainStatement,
    UseRValue,
    check_c_adapter,
    classify_function_abi,
    collect_mir_issues,
    from_json,
    lower_hir_to_mir,
    to_json,
)


def _lower(path: Path):
    checked = NyxCompiler(str(ROOT)).check_file(str(path))
    assert checked.success and checked.hir is not None, checked.diagnostics
    return lower_hir_to_mir(checked.hir)


def _ownership_modules() -> tuple[MIRModule, MIRModule]:
    span = MIRSpan("ownership.nyx", 1, 1)
    int_type = MIRType("int")

    moved = MIRFunctionBuilder("moved", "function::moved", MIRType("void"), span)
    value = moved.new_local("value", int_type)
    sink = moved.new_local("sink", int_type)
    after = moved.new_local("after", int_type)
    entry = moved.new_block()
    moved.push_statement(entry, AssignStatement(
        Place(value), UseRValue(ConstOperand(int_type, 7)), span
    ))
    moved.push_statement(entry, AssignStatement(
        Place(sink), UseRValue(MoveOperand(Place(value))), span
    ))
    moved.push_statement(entry, AssignStatement(
        Place(after), UseRValue(CopyOperand(Place(value))), span
    ))
    moved.set_terminator(entry, ReturnTerminator(span))

    dropped = MIRFunctionBuilder("dropped", "function::dropped", MIRType("void"), span)
    drop_value = dropped.new_local("value", int_type)
    first = dropped.new_block()
    second = dropped.new_block()
    exit_block = dropped.new_block()
    dropped.push_statement(first, AssignStatement(
        Place(drop_value), UseRValue(ConstOperand(int_type, 9)), span
    ))
    dropped.set_terminator(first, DropTerminator(Place(drop_value), second, None, span))
    dropped.set_terminator(second, DropTerminator(Place(drop_value), exit_block, None, span))
    dropped.set_terminator(exit_block, ReturnTerminator(span))

    return (
        MIRModule("ownership.nyx", "cpp", (moved.finish(),)),
        MIRModule("ownership.nyx", "cpp", (dropped.finish(),)),
    )


def _borrow_module() -> MIRModule:
    span = MIRSpan("borrow.nyx", 1, 1)
    int_type = MIRType("int")
    pointer_type = MIRType("int", pointer=True)
    builder = MIRFunctionBuilder("borrowed", "function::borrowed", int_type, span)
    value = builder.new_local("value", int_type)
    reference = builder.new_local("reference", pointer_type)
    entry = builder.new_block()
    builder.push_statement(entry, AssignStatement(
        Place(value), UseRValue(ConstOperand(int_type, 42)), span
    ))
    builder.push_statement(entry, AssignStatement(
        Place(reference), BorrowRValue(Place(value), False, pointer_type), span
    ))
    builder.push_statement(entry, RetainStatement(Place(reference), span))
    builder.push_statement(entry, AssignStatement(
        Place(0),
        UseRValue(CopyOperand(Place(reference, (DerefProjection(),)))),
        span,
    ))
    builder.push_statement(entry, ReleaseStatement(Place(reference), span))
    builder.set_terminator(entry, ReturnTerminator(span))
    return MIRModule("borrow.nyx", "cpp", (builder.finish(),))


def run_mir_memory_abi_suite() -> bool:
    print("=" * 70)
    print("NYX M4 MIR AGGREGATE / MEMORY / ABI CONTRACT")
    print("=" * 70)

    aggregate_module = _lower(ROOT / "tests" / "fixtures" / "mir" / "m4_aggregates.nyx")
    assert from_json(to_json(aggregate_module)) == aggregate_module
    observed = MIRInterpreter(aggregate_module).run().output
    assert observed == ("1 9 9", "Nyx", "9", "2", "3"), observed

    payload_module = _lower(ROOT / "tour" / "solutions" / "17_results" / "result01.nyx")
    assert MIRInterpreter(payload_module).run().output == ("hello",)
    static_enum_module = _lower(ROOT / "tour" / "solutions" / "07_enums" / "enums03.nyx")
    assert MIRInterpreter(static_enum_module).run().output == (
        "Traffic light transitions verified!",
    )

    moved, dropped = _ownership_modules()
    assert "MIR0801" in {issue.code for issue in collect_mir_issues(moved)}
    assert "MIR0804" in {issue.code for issue in collect_mir_issues(dropped)}
    borrowed = _borrow_module()
    assert not collect_mir_issues(borrowed)
    assert MIRInterpreter(borrowed).run("borrowed").value == 42

    point = next(
        definition
        for definition in aggregate_module.type_definitions
        if isinstance(definition, MIRStructDef) and definition.name == "Point"
    )
    native = LayoutEngine(aggregate_module, "cpp")
    wasm = LayoutEngine(aggregate_module, "wasm")
    point_native = native.layout_of(MIRType(point.name))
    assert (point_native.size, point_native.alignment) == (16, 8)
    assert tuple(field.offset for field in point_native.fields) == (0, 8)
    assert native.layout_of(MIRType("Array", (MIRType("int"),))).size == 24
    assert wasm.layout_of(MIRType("Array", (MIRType("int"),))).size == 12

    synthetic = aggregate_module.functions[-1]
    point_return = replace(
        synthetic,
        locals=(replace(synthetic.locals[0], type=MIRType("Point")),) + synthetic.locals[1:],
    )
    direct = classify_function_abi(
        replace(aggregate_module, functions=(point_return,)),
        point_return,
        "cpp",
    )
    assert direct.result.mode == "direct"
    assert check_c_adapter(aggregate_module, point_return).result_reason == "compatible"

    print(
        "[PASS] aggregate value copies, projected places, collection iteration, enum payloads, "
        "move/drop analysis, x64/wasm32 layouts, calling convention and C adapters"
    )
    return True


if __name__ == "__main__":
    raise SystemExit(0 if run_mir_memory_abi_suite() else 1)
