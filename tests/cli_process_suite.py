import os
import subprocess
import sys
import tempfile
from unittest import mock


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI_PATH = os.path.join(ROOT_DIR, "src", "cli.py")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.codegen.cpp_toolchain import CppToolchain


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, CLI_PATH, *args],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def run_cli_process_suite() -> bool:
    print("[*] Running CLI Process Exit-Code Tests...")
    with tempfile.TemporaryDirectory(prefix="nyx_cli_exit_") as temp_dir:
        source_path = os.path.join(temp_dir, "runtime_failure.nyx")
        with open(source_path, "w", encoding="utf-8") as source_file:
            source_file.write(
                "fn main() {\n"
                "    var values = [1]\n"
                "    print(values[5])\n"
                "}\n"
            )

        run_result = _run_cli("run", source_path, "--target", "hepy")
        assert run_result.returncode != 0, "nyx run swallowed the child runtime failure"

        test_result = _run_cli("test", source_path)
        assert test_result.returncode != 0, "nyx test swallowed the child runtime failure"
        assert "Execution finished successfully" not in test_result.stdout

        invalid_path = os.path.join(temp_dir, "invalid.nyx")
        with open(invalid_path, "w", encoding="utf-8") as source_file:
            source_file.write('var count: int = "wrong"\n')
        check_result = _run_cli("check", invalid_path)
        assert check_result.returncode != 0, "nyx check returned success for invalid source"
        assert "error[E2001]" in check_result.stdout

    with mock.patch.object(CppToolchain, "find_compiler", return_value=None):
        compiled, message = CppToolchain.compile_cpp("unused.cpp")
    assert not compiled
    assert "Clang++" in message and "GCC/G++" in message and "MSVC cl" in message
    assert "NYX_CXX" in message and "nyx doctor" in message

    print("  [PASS] child failures, diagnostics, and native toolchain guidance propagate")
    return True


if __name__ == "__main__":
    sys.exit(0 if run_cli_process_suite() else 1)
