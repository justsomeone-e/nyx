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
    MIR_BACKEND_MIGRATION_ORDER,
    MIR_BACKEND_PROFILES,
    MIRInterpreter,
    MIRLegalizationError,
    collect_legalization_issues,
    emit_legalized_cpp,
    emit_legalized_llvm,
    legalize_mir,
    lower_hir_to_mir,
    mir_backend_manifest,
)


SCALAR_FIXTURE = ROOT / "tests" / "fixtures" / "mir" / "m2_scalar.nyx"
AGGREGATE_FIXTURE = ROOT / "tests" / "fixtures" / "mir" / "m4_aggregates.nyx"


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


def run_mir_legalization_suite() -> bool:
    print("=" * 70)
    print("NYX M5 MIR LEGALIZATION / C++ MIGRATION PILOT")
    print("=" * 70)

    manifest = mir_backend_manifest()
    assert json.loads(json.dumps(manifest)) == manifest
    assert tuple(manifest["migration_order"]) == MIR_BACKEND_MIGRATION_ORDER
    assert tuple(profile["target"] for profile in manifest["profiles"]) == MIR_BACKEND_MIGRATION_ORDER
    assert MIR_BACKEND_PROFILES["cpp"].migration_status == "pilot"
    assert MIR_BACKEND_PROFILES["llvm"].migration_status == "pilot"
    assert all(
        MIR_BACKEND_PROFILES[target].migration_status == "profile-only"
        for target in MIR_BACKEND_MIGRATION_ORDER[2:]
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
        "  print(9223372036854775807 + 1)\n"
        "  print(-7 / 3, -7 % 3)\n"
        "  print(\"answer\", compute(2.5, 4.0), true)\n"
        "}\n",
        "m5-numeric.nyx",
    )
    expected_numeric = "\n".join(MIRInterpreter(numeric).run().output) + "\n"
    assert expected_numeric == "-9223372036854775808\n-2 -1\nanswer 11.25 true\n"
    assert _compile_and_run_cpp(emit_legalized_cpp(numeric)) == expected_numeric
    assert _compile_and_run_llvm(emit_legalized_llvm(numeric)) == expected_numeric

    unknown = collect_legalization_issues(scalar, "moonvm")
    assert {issue.code for issue in unknown} == {"MIRG1000"}, unknown

    unprofiled = collect_legalization_issues(scalar, "asm")
    assert {issue.code for issue in unprofiled} == {"MIRG1001"}, unprofiled

    pending = collect_legalization_issues(scalar, "wasm", require_emitter=True)
    assert {issue.code for issue in pending} == {"MIRG1009"}, pending

    aggregate = _lower(AGGREGATE_FIXTURE)
    aggregate_codes = {issue.code for issue in collect_legalization_issues(aggregate, "cpp")}
    assert "MIRG1002" in aggregate_codes, aggregate_codes
    assert "MIRG1004" in aggregate_codes, aggregate_codes
    assert "MIRG1005" in aggregate_codes, aggregate_codes
    assert "MIRG1007" in aggregate_codes, aggregate_codes
    try:
        emit_legalized_cpp(aggregate)
        raise AssertionError("aggregate MIR bypassed the C++ legalization gate")
    except MIRLegalizationError as error:
        assert {issue.code for issue in error.issues} == aggregate_codes

    print(
        "[PASS] 7 target profiles, stable negative diagnostics, no-fallback gate, "
        "MIR interpreter/C++/LLVM pilots and legacy C++ runtime parity"
    )
    return True


if __name__ == "__main__":
    raise SystemExit(0 if run_mir_legalization_suite() else 1)
