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
from src.cli import get_entry_file, get_target_from_args


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
        directive_path = os.path.join(temp_dir, "directive.nyx")
        with open(directive_path, "w", encoding="utf-8") as source_file:
            source_file.write(
                '#target js\nimport js "node:os" as os\nprint(os.platform())\n'
            )
        plain_path = os.path.join(temp_dir, "plain.nyx")
        with open(plain_path, "w", encoding="utf-8") as source_file:
            source_file.write(
                'import cpp "std::filesystem" from "<filesystem>" as fs\n'
                'print(fs.current_path().string())\n'
            )

        assert get_target_from_args("python", directive_path, []) == "js"
        assert get_target_from_args("python", directive_path, ["-t", "rust"]) == "rust"
        assert get_target_from_args("python", directive_path, ["--target=python"]) == "python"
        assert get_target_from_args("python", plain_path, []) == "python"
        assert get_target_from_args(None, plain_path, []) == "cpp"
        assert get_entry_file("missing.nyx", ["-t", "js", plain_path]) == plain_path
        assert get_entry_file("missing.nyx", ["--target=js", plain_path]) == plain_path

        directive_check = _run_cli("check", directive_path)
        assert directive_check.returncode == 0, directive_check.stdout + directive_check.stderr
        native_default_check = _run_cli("check", plain_path)
        assert native_default_check.returncode == 0, native_default_check.stdout + native_default_check.stderr

        source_path = os.path.join(temp_dir, "runtime_failure.nyx")
        with open(source_path, "w", encoding="utf-8") as source_file:
            source_file.write(
                "fn main() {\n"
                "    var values = [1]\n"
                "    print(values[5])\n"
                "}\n"
            )

        run_result = _run_cli("run", source_path, "--target", "python")
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
