import json
import os
import shutil
import subprocess
import sys
import tempfile


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI_PATH = os.path.join(ROOT_DIR, "src", "cli.py")
PARITY_SOURCE = os.path.join(ROOT_DIR, "tests", "test_parity_matrix.nyx")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.core.backend_capabilities import (
    BACKENDS,
    CAPABILITY_SCHEMA_VERSION,
    normalize_backend_name,
    stdlib_modules_for_target,
)
from src.core.diagnostics import DiagnosticEmitter, DiagnosticError
from src.core.module_loader import ModuleLoader


def _write(path: str, source: str) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(source)


def run_capability_suite() -> bool:
    print("=" * 70)
    print("NYX BACKEND / STDLIB CAPABILITY CONTRACT")
    print("=" * 70)

    assert normalize_backend_name("python") == "python"
    assert normalize_backend_name("node") == "js"
    assert normalize_backend_name("stm32") == "stm32f4"
    assert normalize_backend_name("desktop") == "cpp"
    assert "fs" in stdlib_modules_for_target("js")
    assert "fs" not in stdlib_modules_for_target("rust")
    for target in ("cpp", "js", "python"):
        assert {"int64_wrap", "float64_ieee", "canonical_scalar_text"} <= BACKENDS[target].features
    for target in ("cpp", "js", "python", "rust", "wasm"):
        assert "typed_hir_v1" in BACKENDS[target].features
    for target in ("cpp", "js", "python"):
        assert {"channels", "spawn"} <= BACKENDS[target].features
    assert {"channels", "spawn"}.isdisjoint(BACKENDS["rust"].features)
    for target in ("asm", "react", "stm32f4"):
        assert "typed_hir_v1" not in BACKENDS[target].features
    assert "int64_wrap" not in BACKENDS["wasm"].features
    assert "wasm32" in BACKENDS["wasm"].features

    cli_manifest = subprocess.run(
        [sys.executable, CLI_PATH, "targets", "--json"],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert cli_manifest.returncode == 0, cli_manifest.stderr or cli_manifest.stdout
    manifest = json.loads(cli_manifest.stdout)
    assert manifest["schema_version"] == CAPABILITY_SCHEMA_VERSION
    assert {backend["name"] for backend in manifest["backends"]} >= {
        "cpp", "js", "python", "rust", "react", "wasm", "stm32f4"
    }

    previous_exit_mode = DiagnosticEmitter.EXIT_ON_ERROR
    DiagnosticEmitter.EXIT_ON_ERROR = False
    try:
        with tempfile.TemporaryDirectory(prefix="nyx_capability_") as temp_dir:
            js_source = os.path.join(temp_dir, "js_ok.nyx")
            _write(js_source, '#target js\nimport "std/fs"\nfn main() {}\n')
            js_ast = ModuleLoader(base_dir=temp_dir).load_program(js_source)
            assert js_ast.target == "js"

            embedded_source = os.path.join(temp_dir, "embedded_ok.nyx")
            _write(embedded_source, '#target stm32\nimport "native/gpio"\nfn main() {}\n')
            embedded_ast = ModuleLoader(base_dir=temp_dir).load_program(embedded_source)
            assert embedded_ast.target == "stm32f4"

            portable_str = os.path.join(temp_dir, "portable_str.nyx")
            _write(
                portable_str,
                'import "std/str"\n'
                'fn main() {\n'
                '    print(concat_three("a", "b", "c"))\n'
                '    print(wrap_with("x", "[", "]"))\n'
                '    print(contains_substring("nyx-platform", "platform"))\n'
                '}\n',
            )
            for target in ("cpp", "js", "python"):
                portable_run = subprocess.run(
                    [sys.executable, CLI_PATH, "run", portable_str, "--target", target],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
                assert portable_run.returncode == 0, portable_run.stderr or portable_run.stdout
                normalized = portable_run.stdout.replace("\r\n", "\n").lower()
                assert "abc\n[x]\ntrue" in normalized, f"std/str parity failed for {target}: {normalized}"

            rust_build = subprocess.run(
                [sys.executable, CLI_PATH, "build", portable_str, "--target", "rust"],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            assert rust_build.returncode == 0, rust_build.stderr or rust_build.stdout
            rust_source_path = os.path.join(temp_dir, "build", "rust", "portable_str.rs")
            rustc = shutil.which("rustc")
            assert rustc, "rustc is required for the rust capability contract"
            rust_check = subprocess.run(
                [rustc, "--edition=2021", "--emit=metadata", rust_source_path],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            assert rust_check.returncode == 0, rust_check.stderr or rust_check.stdout

            for target in ("cpp", "js", "python"):
                parity_run = subprocess.run(
                    [sys.executable, CLI_PATH, "run", PARITY_SOURCE, "--target", target],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
                parity_output = parity_run.stdout + parity_run.stderr
                assert parity_run.returncode == 0, parity_output
                assert "[FAIL]" not in parity_output, f"stdlib parity failed for {target}: {parity_output}"
                assert "[SUCCESS] All 6 Stdlib Modules" in parity_output

            rust_source = os.path.join(temp_dir, "rust_reject.nyx")
            _write(rust_source, '#target rust\nimport "std/fs"\nfn main() {}\n')
            try:
                ModuleLoader(base_dir=temp_dir).load_program(rust_source)
                raise AssertionError("rust accepted unsupported std/fs")
            except DiagnosticError as error:
                assert error.code == "E1400"

            unknown_source = os.path.join(temp_dir, "unknown_target.nyx")
            _write(unknown_source, '#target moonvm\nfn main() {}\n')
            try:
                ModuleLoader(base_dir=temp_dir).load_program(unknown_source)
                raise AssertionError("unknown target was accepted")
            except DiagnosticError as error:
                assert error.code == "E1401"

            unknown_build = subprocess.run(
                [sys.executable, CLI_PATH, "build", unknown_source, "--target", "moonvm"],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            assert unknown_build.returncode != 0
            assert "Unknown target" in (unknown_build.stdout + unknown_build.stderr)
    finally:
        DiagnosticEmitter.EXIT_ON_ERROR = previous_exit_mode

    print("[PASS] Aliases, HIR authority manifest, target gates, std/str, and 6-module parity")
    return True


if __name__ == "__main__":
    sys.exit(0 if run_capability_suite() else 1)
