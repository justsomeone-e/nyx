from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.api import NyxCompiler
from src.codegen.cpp_toolchain import CppToolchain
from src.mir import (
    AssignStatement,
    BorrowRValue,
    CallTerminator,
    ConstOperand,
    CopyOperand,
    DeinitStatement,
    DerefProjection,
    DropTerminator,
    MIR_BACKEND_MIGRATION_ORDER,
    MIR_BACKEND_PROFILES,
    MIRFunctionBuilder,
    MIRInterpreter,
    MIRLegalizationError,
    MIRModule,
    MIRSpan,
    MIRType,
    MoveOperand,
    Place,
    ReleaseStatement,
    RetainStatement,
    ReturnTerminator,
    UseRValue,
    collect_legalization_issues,
    emit_legalized_c17,
    emit_legalized_cpp,
    emit_legalized_javascript,
    emit_legalized_llvm,
    emit_legalized_python,
    emit_legalized_rust,
    emit_legalized_wasm,
    emit_legalized_wat,
    legalize_mir,
    lower_hir_to_mir,
    mir_backend_manifest,
)


SCALAR_FIXTURE = ROOT / "tests" / "fixtures" / "mir" / "m2_scalar.nyx"
AGGREGATE_FIXTURE = ROOT / "tests" / "fixtures" / "mir" / "m4_aggregates.nyx"
PAYLOAD_FIXTURE = ROOT / "tour" / "solutions" / "17_results" / "result01.nyx"
CONTROL_FIXTURE = ROOT / "tests" / "fixtures" / "mir" / "m3_control.nyx"


def _lower(path: Path):
    checked = NyxCompiler(str(ROOT)).check_file(str(path), target="cpp")
    assert checked.success and checked.hir is not None, checked.diagnostics
    return lower_hir_to_mir(checked.hir)


def _lower_source(source: str, filename: str):
    checked = NyxCompiler(str(ROOT)).check_source(source, filename=filename, target="cpp")
    assert checked.success and checked.hir is not None, checked.diagnostics
    return lower_hir_to_mir(checked.hir)


def _run_legacy_cpp() -> str:
    result = subprocess.run(
        [sys.executable, str(ROOT / "src" / "cli.py"), "run", str(SCALAR_FIXTURE), "--target", "cpp"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout.replace("\r\n", "\n")


def _compile_and_run_cpp(source: str) -> str:
    with tempfile.TemporaryDirectory(prefix="nyx_mir_codegen_") as temporary:
        source_path = Path(temporary) / "program.cpp"
        executable = Path(temporary) / ("program.exe" if os.name == "nt" else "program")
        source_path.write_text(source, encoding="utf-8", newline="\n")
        compiled, detail = CppToolchain.compile_cpp(str(source_path), str(executable))
        assert compiled, detail
        return_code, output = CppToolchain.run_executable(str(executable), timeout=30)
        assert return_code == 0, output
        return output.replace("\r\n", "\n")


def _compile_and_run_c17(source: str) -> str:
    clang = shutil.which("clang")
    assert clang is not None, "clang is required by the C17 MIR runtime gate"
    with tempfile.TemporaryDirectory(prefix="nyx_mir_c17_") as temporary:
        source_path = Path(temporary) / "program.c"
        executable = Path(temporary) / ("program.exe" if os.name == "nt" else "program")
        source_path.write_text(source, encoding="utf-8", newline="\n")
        compiled = subprocess.run(
            [clang, "-std=c17", "-O2", str(source_path), "-o", str(executable)],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30,
        )
        assert compiled.returncode == 0, compiled.stdout + compiled.stderr + "\n" + source
        executed = subprocess.run(
            [str(executable)], capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=30,
        )
        assert executed.returncode == 0, executed.stdout + executed.stderr
        return executed.stdout.replace("\r\n", "\n")


def _compile_and_run_llvm(source: str) -> str:
    clang = shutil.which("clang")
    assert clang is not None, "clang is required by the existing LLVM conformance target"
    with tempfile.TemporaryDirectory(prefix="nyx_mir_llvm_") as temporary:
        source_path = Path(temporary) / "program.ll"
        executable = Path(temporary) / ("program.exe" if os.name == "nt" else "program")
        source_path.write_text(source, encoding="utf-8", newline="\n")
        compiled = subprocess.run(
            [clang, "-O2", str(source_path), "-o", str(executable)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        assert compiled.returncode == 0, compiled.stdout + compiled.stderr + "\n" + source
        executed = subprocess.run(
            [str(executable)], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30
        )
        assert executed.returncode == 0, executed.stdout + executed.stderr
        return executed.stdout.replace("\r\n", "\n")


def _compile_and_run_rust(source: str) -> str:
    rustc = shutil.which("rustc")
    assert rustc is not None, "rustc is required by the Rust MIR runtime gate"
    with tempfile.TemporaryDirectory(prefix="nyx_mir_rust_") as temporary:
        source_path = Path(temporary) / "program.rs"
        executable = Path(temporary) / ("program.exe" if os.name == "nt" else "program")
        source_path.write_text(source, encoding="utf-8", newline="\n")
        compiled = subprocess.run(
            [rustc, "--edition=2021", "-O", str(source_path), "-o", str(executable)],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60,
        )
        assert compiled.returncode == 0, compiled.stdout + compiled.stderr + "\n" + source
        executed = subprocess.run(
            [str(executable)], capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=30,
        )
        assert executed.returncode == 0, executed.stdout + executed.stderr
        return executed.stdout.replace("\r\n", "\n")


def _run_javascript(source: str) -> str:
    node = shutil.which("node")
    assert node is not None, "Node.js is required by the JavaScript MIR runtime gate"
    with tempfile.TemporaryDirectory(prefix="nyx_mir_js_") as temporary:
        source_path = Path(temporary) / "program.mjs"
        source_path.write_text(source, encoding="utf-8", newline="\n")
        executed = subprocess.run(
            [node, str(source_path)], capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=30,
        )
        assert executed.returncode == 0, executed.stdout + executed.stderr + "\n" + source
        return executed.stdout.replace("\r\n", "\n")


def _run_python(source: str) -> str:
    with tempfile.TemporaryDirectory(prefix="nyx_mir_python_") as temporary:
        source_path = Path(temporary) / "program.py"
        source_path.write_text(source, encoding="utf-8", newline="\n")
        executed = subprocess.run(
            [sys.executable, str(source_path)], capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=30,
        )
        assert executed.returncode == 0, executed.stdout + executed.stderr + "\n" + source
        return executed.stdout.replace("\r\n", "\n")


def _run_wasm_export(
    wasm: bytes,
    function: str,
    *arguments: int,
    expect_trap: bool = False,
) -> str:
    node = shutil.which("node")
    assert node is not None, "Node.js is required for the WebAssembly runtime gate"
    with tempfile.TemporaryDirectory(prefix="nyx_mir_wasm_") as temporary:
        wasm_path = Path(temporary) / "program.wasm"
        script_path = Path(temporary) / "run.mjs"
        wasm_path.write_bytes(wasm)
        encoded_arguments = ", ".join(f"{argument}n" for argument in arguments)
        script_path.write_text(
            "import fs from 'node:fs';\n"
            "const bytes = fs.readFileSync(new URL('./program.wasm', import.meta.url));\n"
            "const { instance } = await WebAssembly.instantiate(bytes, {});\n"
            f"console.log(String(instance.exports[{json.dumps(function)}]({encoded_arguments})));\n",
            encoding="utf-8",
            newline="\n",
        )
        executed = subprocess.run(
            [node, str(script_path)], capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=30,
        )
        if expect_trap:
            assert executed.returncode != 0, "WebAssembly call unexpectedly succeeded"
            assert "RuntimeError" in executed.stderr, executed.stdout + executed.stderr
            return ""
        assert executed.returncode == 0, executed.stdout + executed.stderr
        return executed.stdout.replace("\r\n", "\n")


def _ownership_module() -> MIRModule:
    span = MIRSpan("m5-ownership.nyx", 1, 1)
    int_type = MIRType("int")
    pointer_type = MIRType("int", pointer=True)
    builder = MIRFunctionBuilder("main", "function::main", MIRType("any"), span)
    value = builder.new_local("value", int_type)
    reference = builder.new_local("reference", pointer_type)
    observed = builder.new_local("observed", int_type)
    sink = builder.new_local("sink", int_type)
    entry = builder.new_block()
    after_print = builder.new_block()
    exit_block = builder.new_block()
    builder.push_statement(entry, AssignStatement(
        Place(value), UseRValue(ConstOperand(int_type, 42)), span
    ))
    builder.push_statement(entry, AssignStatement(
        Place(reference), BorrowRValue(Place(value), False, pointer_type), span
    ))
    builder.push_statement(entry, RetainStatement(Place(reference), span))
    builder.push_statement(entry, AssignStatement(
        Place(observed),
        UseRValue(CopyOperand(Place(reference, (DerefProjection(),)))),
        span,
    ))
    builder.push_statement(entry, ReleaseStatement(Place(reference), span))
    builder.push_statement(entry, AssignStatement(
        Place(sink), UseRValue(MoveOperand(Place(observed))), span
    ))
    builder.push_statement(entry, DeinitStatement(Place(reference), span))
    builder.set_terminator(entry, CallTerminator(
        "builtin::print", (CopyOperand(Place(sink)),), None, after_print, None, span
    ))
    builder.set_terminator(after_print, DropTerminator(Place(sink), exit_block, None, span))
    builder.set_terminator(exit_block, ReturnTerminator(span))
    return MIRModule("m5-ownership.nyx", "cpp", (builder.finish(),))


def run_mir_legalization_suite() -> bool:
    print("=" * 70)
    print("NYX M5 MIR LEGALIZATION / C++ MIGRATION PILOT")
    print("=" * 70)

    manifest = mir_backend_manifest()
    assert json.loads(json.dumps(manifest)) == manifest
    assert tuple(manifest["migration_order"]) == MIR_BACKEND_MIGRATION_ORDER
    assert tuple(profile["target"] for profile in manifest["profiles"]) == MIR_BACKEND_MIGRATION_ORDER
    assert all(
        MIR_BACKEND_PROFILES[target].migration_status == "pilot"
        for target in MIR_BACKEND_MIGRATION_ORDER
    )

    scalar = _lower(SCALAR_FIXTURE)
    assert legalize_mir(scalar, "native", require_emitter=True) is scalar
    assert not collect_legalization_issues(scalar, "cpp", require_emitter=True)
    expected = MIRInterpreter(scalar).run().output
    assert expected == ("13",), expected

    generated = emit_legalized_cpp(scalar)
    assert "nyx_mir_runtime::add" in generated
    assert "goto bb" in generated
    migrated_output = _compile_and_run_cpp(generated)
    assert migrated_output == "13\n", migrated_output
    llvm_output = _compile_and_run_llvm(emit_legalized_llvm(scalar))
    assert llvm_output == migrated_output, llvm_output
    assert "\n13\n" in "\n" + _run_legacy_cpp(), "legacy C++ oracle did not print 13"

    numeric = _lower_source(
        "fn compute(x: float, y: float) -> float { return (x * y) + 1.25 }\n"
        "fn main() {\n"
        "  let min: int = -9223372036854775808\n"
        "  print(9223372036854775807 + 1)\n"
        "  print(-7 / 3, -7 % 3)\n"
        "  print(\"min-divmod\", min / -1, min % -1)\n"
        "  print(\"bits\", 1 << 64, -1 >> 65)\n"
        "  print(\"answer\", compute(2.5, 4.0), true)\n"
        "}\n",
        "m5-numeric.nyx",
    )
    expected_numeric = "\n".join(MIRInterpreter(numeric).run().output) + "\n"
    assert expected_numeric == (
        "-9223372036854775808\n-2 -1\n"
        "min-divmod -9223372036854775808 0\n"
        "bits 1 -1\nanswer 11.25 true\n"
    )
    assert _compile_and_run_cpp(emit_legalized_cpp(numeric)) == expected_numeric
    assert _compile_and_run_llvm(emit_legalized_llvm(numeric)) == expected_numeric
    assert _compile_and_run_rust(emit_legalized_rust(numeric)) == expected_numeric
    assert _run_javascript(emit_legalized_javascript(numeric)) == expected_numeric
    assert _run_python(emit_legalized_python(numeric)) == expected_numeric
    assert _compile_and_run_c17(emit_legalized_c17(numeric)) == expected_numeric

    floating = _lower_source(
        "fn main() { print(1.0 / 0.0, 0.0 / 0.0, -7.5 % 2.0) }\n",
        "m5-floating.nyx",
    )
    expected_floating = "inf nan -1.5\n"
    assert "\n".join(MIRInterpreter(floating).run().output) + "\n" == expected_floating
    assert _compile_and_run_cpp(emit_legalized_cpp(floating)) == expected_floating
    assert _compile_and_run_llvm(emit_legalized_llvm(floating)) == expected_floating
    assert _compile_and_run_rust(emit_legalized_rust(floating)) == expected_floating
    assert _run_javascript(emit_legalized_javascript(floating)) == expected_floating
    assert _run_python(emit_legalized_python(floating)) == expected_floating
    assert _compile_and_run_c17(emit_legalized_c17(floating)) == expected_floating

    unknown = collect_legalization_issues(scalar, "moonvm")
    assert {issue.code for issue in unknown} == {"MIRG1000"}, unknown

    unprofiled = collect_legalization_issues(scalar, "asm")
    assert {issue.code for issue in unprofiled} == {"MIRG1001"}, unprofiled

    wasm = _lower_source(
        "fn sum_without_two(limit: int) -> int {\n"
        "  var total: int = 0\n"
        "  var i: int = 0\n"
        "  while i < limit {\n"
        "    if i != 2 { set total = total + i }\n"
        "    set i = i + 1\n"
        "  }\n"
        "  return total\n"
        "}\n"
        "fn safe_div(left: int, right: int) -> int { return left / right }\n"
        "fn safe_rem(left: int, right: int) -> int { return left % right }\n",
        "m5-wasm.nyx",
    )
    assert not collect_legalization_issues(wasm, "wasm", require_emitter=True)
    assert MIRInterpreter(wasm).run("sum_without_two", (6,)).value == 13
    assert "loop $dispatch" in emit_legalized_wat(wasm)
    wasm_bytes = emit_legalized_wasm(wasm)
    assert _run_wasm_export(wasm_bytes, "sum_without_two", 6) == "13\n"
    minimum = -(1 << 63)
    assert MIRInterpreter(wasm).run("safe_div", (minimum, -1)).value == minimum
    assert _run_wasm_export(wasm_bytes, "safe_div", minimum, -1) == f"{minimum}\n"
    assert _run_wasm_export(wasm_bytes, "safe_rem", minimum, -1) == "0\n"
    _run_wasm_export(wasm_bytes, "safe_div", 1, 0, expect_trap=True)
    shifted = _lower_source("fn shifted(x: int) -> int { return x << 64 }\n", "m5-shift.nyx")
    assert "MIRG1010" in {issue.code for issue in collect_legalization_issues(shifted, "wasm")}
    rejected_wasm = {issue.code for issue in collect_legalization_issues(scalar, "wasm")}
    assert "MIRG1007" in rejected_wasm, rejected_wasm

    aggregate = _lower(AGGREGATE_FIXTURE)
    assert not collect_legalization_issues(aggregate, "cpp", require_emitter=True)
    expected_aggregate = "\n".join(MIRInterpreter(aggregate).run().output) + "\n"
    assert _compile_and_run_cpp(emit_legalized_cpp(aggregate)) == expected_aggregate

    payload = _lower(PAYLOAD_FIXTURE)
    assert not collect_legalization_issues(payload, "cpp", require_emitter=True)
    expected_payload = "\n".join(MIRInterpreter(payload).run().output) + "\n"
    assert expected_payload == "hello\n"
    assert _compile_and_run_cpp(emit_legalized_cpp(payload)) == expected_payload

    control = _lower(CONTROL_FIXTURE)
    assert not collect_legalization_issues(control, "cpp", require_emitter=True)
    expected_control = "\n".join(MIRInterpreter(control).run().output) + "\n"
    assert _compile_and_run_cpp(emit_legalized_cpp(control)) == expected_control

    assert not collect_legalization_issues(scalar, "rust", require_emitter=True)
    assert _compile_and_run_rust(emit_legalized_rust(scalar)) == "13\n"
    assert not collect_legalization_issues(scalar, "js", require_emitter=True)
    assert _run_javascript(emit_legalized_javascript(scalar)) == "13\n"
    assert not collect_legalization_issues(scalar, "python", require_emitter=True)
    assert _run_python(emit_legalized_python(scalar)) == "13\n"
    assert not collect_legalization_issues(scalar, "c", require_emitter=True)
    assert _compile_and_run_c17(emit_legalized_c17(scalar)) == "13\n"

    ownership = _ownership_module()
    assert not collect_legalization_issues(ownership, "cpp", require_emitter=True)
    expected_ownership = "\n".join(MIRInterpreter(ownership).run().output) + "\n"
    assert expected_ownership == "42\n"
    generated_ownership = emit_legalized_cpp(ownership)
    assert "std::move" in generated_ownership
    assert "int64_t*" in generated_ownership
    assert _compile_and_run_cpp(generated_ownership) == expected_ownership

    aggregate_codes = {issue.code for issue in collect_legalization_issues(aggregate, "llvm")}
    assert "MIRG1002" in aggregate_codes, aggregate_codes
    assert "MIRG1004" in aggregate_codes, aggregate_codes
    assert "MIRG1005" in aggregate_codes, aggregate_codes
    assert "MIRG1007" in aggregate_codes, aggregate_codes
    try:
        emit_legalized_llvm(aggregate)
        raise AssertionError("aggregate MIR bypassed the LLVM legalization gate")
    except MIRLegalizationError as error:
        assert {issue.code for issue in error.issues} == aggregate_codes

    print(
        "[PASS] 7 target profiles, stable negative diagnostics, no-fallback gate, "
        "scalar/aggregate/payload/ownership MIR interpreter parity, C++/LLVM pilots, "
        "executable Wasm/Rust/JavaScript/Python/C17 CFG pilots, and legacy C++ oracle"
    )
    return True


if __name__ == "__main__":
    raise SystemExit(0 if run_mir_legalization_suite() else 1)
