from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from pathlib import Path
import sys
import tempfile


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.codegen.cpp_toolchain import CppToolchain
from src.codegen.hir_cpp import emit_cpp
from src.core import Lexer, Parser, TypeChecker
from src.ir import lower_to_hir, optimize_hir, verify_hir
from src.self_host.bootstrap import _driver_source
from tests.battery138.run_battery import test_cases


_NATIVE_EXPECTED_OVERRIDES = {
    # Native hecpp exposes actual address dereference semantics.  The legacy
    # Python battery oracle intentionally returned its fixed emulation value.
    "unsafe_01_basic_addr": "42",
}


def _emit(source: str, filename: str) -> str:
    tree = Parser(Lexer(source, filename).tokenize(), source, filename).parse()
    TypeChecker(tree, filename, source).check()
    hir = optimize_hir(lower_to_hir(tree, filename)).module
    verify_hir(hir)
    return emit_cpp(hir)


def _canonical_battery_output(value: str) -> str:
    value = value.replace("\r\n", "\n").strip()
    return "\n".join(
        "true" if line == "True" else "false" if line == "False" else line
        for line in value.splitlines()
    )


def _run_corpus_emission() -> int:
    paths = []
    for relative in ("tests/battery138", "tests/bughunt"):
        paths.extend(sorted(Path(ROOT_DIR, relative).glob("*.nyx")))
    assert len(paths) >= 162
    for path in paths:
        _emit(path.read_text(encoding="utf-8-sig"), str(path))
    return len(paths)


def _compile_and_run_case(
    directory: str,
    index: int,
    name: str,
    source: str,
    expected_output: str,
) -> str:
    generated = _emit(source, name + ".nyx")
    cpp_path = os.path.join(directory, f"{index:03d}_{name}.cpp")
    executable = os.path.join(directory, f"{index:03d}_{name}.exe")
    with open(cpp_path, "w", encoding="utf-8") as handle:
        handle.write(generated)
    compiled, message = CppToolchain.compile_cpp(cpp_path, executable)
    assert compiled, (name, message)
    return_code, output = CppToolchain.run_executable(executable)
    assert return_code == 0, (name, return_code, output)
    actual = _canonical_battery_output(output)
    expected = _canonical_battery_output(
        _NATIVE_EXPECTED_OVERRIDES.get(name, expected_output or "")
    )
    if name == "unsafe_05_memdump_call":
        assert actual.endswith(expected), (name, expected, actual)
    else:
        assert actual == expected, (name, expected, actual)
    return name


def _run_native_battery() -> int:
    workers = max(1, min(8, os.cpu_count() or 1))
    with tempfile.TemporaryDirectory(prefix="nyx_hir_cpp_battery_") as directory:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(
                    _compile_and_run_case,
                    directory,
                    index,
                    name,
                    source,
                    expected,
                ): name
                for index, (name, source, expected) in enumerate(test_cases)
            }
            failures = []
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as error:
                    details = str(error).replace("\r\n", "\n")
                    failures.append((futures[future], details[:1600]))
            assert not failures, "\n".join(f"{name}: {error}" for name, error in failures)
    return len(test_cases)


def _run_stage1_smoke() -> None:
    source = _driver_source("fn add(a: int, b: int) -> int { return a + b; }")
    generated = _emit(source, "<hir-stage1-smoke>")
    with tempfile.TemporaryDirectory(prefix="nyx_hir_cpp_stage1_") as directory:
        cpp_path = os.path.join(directory, "stage1.cpp")
        executable = os.path.join(directory, "stage1.exe")
        with open(cpp_path, "w", encoding="utf-8") as handle:
            handle.write(generated)
        compiled, message = CppToolchain.compile_cpp(cpp_path, executable)
        assert compiled, message
        return_code, output = CppToolchain.run_executable(executable)
        assert return_code == 0, output
        assert "SELF_HOST_OK" in output
        assert "int64_t add(int64_t a, int64_t b)" in output


def _run_cli_args_smoke() -> None:
    source = "fn main() { var values: Array<string> = args(); print(values[1]); }"
    generated = _emit(source, "<hir-cli-args-smoke>")
    with tempfile.TemporaryDirectory(prefix="nyx_hir_cpp_args_") as directory:
        cpp_path = os.path.join(directory, "args.cpp")
        executable = os.path.join(directory, "args.exe")
        with open(cpp_path, "w", encoding="utf-8") as handle:
            handle.write(generated)
        compiled, message = CppToolchain.compile_cpp(cpp_path, executable)
        assert compiled, message
        return_code, output = CppToolchain.run_executable(executable, ("nyx-arg",))
        assert return_code == 0, output
        assert output.strip() == "nyx-arg", output


def run_hir_cpp_suite() -> bool:
    print("=" * 70)
    print("NYX HIR-AUTHORITATIVE C++20 NATIVE BACKEND")
    print("=" * 70)
    compiler = CppToolchain.find_compiler()
    assert compiler is not None, "A working C++20 compiler is required for the HIR C++ suite"
    corpus_count = _run_corpus_emission()
    runtime_count = _run_native_battery()
    _run_stage1_smoke()
    _run_cli_args_smoke()
    print(
        f"[PASS] {corpus_count} emitted, {runtime_count} native runtime cases, "
        "Nyx-authored stage1 frontend and argv runtime compiled and executed"
    )
    return True


if __name__ == "__main__":
    sys.exit(0 if run_hir_cpp_suite() else 1)
