import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.codegen.hir_javascript import emit_javascript
from src.core import Lexer, Parser, TypeChecker
from src.ir import lower_to_hir, optimize_hir, verify_hir
from tests.battery138.run_battery import test_cases
from tests.differential_testing import TRIPLE_DIFF_CASES


NODE = shutil.which("node")


def _emit(source: str, filename: str) -> str:
    tree = Parser(Lexer(source, filename).tokenize(), source, filename).parse()
    TypeChecker(tree, filename, source).check()
    hir = optimize_hir(lower_to_hir(tree, filename)).module
    verify_hir(hir)
    return emit_javascript(hir)


def _run(generated: str, timeout: int = 5) -> subprocess.CompletedProcess:
    assert NODE is not None, "Node.js is required for the HIR JavaScript suite"
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".cjs",
        encoding="utf-8",
        delete=False,
    ) as handle:
        handle.write(generated)
        path = handle.name
    try:
        return subprocess.run(
            [NODE, path],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


def _canonical_battery_output(value: str) -> str:
    value = value.replace("\r\n", "\n").strip()
    return "\n".join(
        "true" if line == "True" else "false" if line == "False" else line
        for line in value.splitlines()
    )


def _run_corpus_compile() -> int:
    paths = []
    for relative in ("tests/battery138", "tests/bughunt"):
        paths.extend(sorted(Path(ROOT_DIR, relative).glob("*.nyx")))
    assert len(paths) >= 162
    for path in paths:
        source = path.read_text(encoding="utf-8-sig")
        generated = _emit(source, str(path))
        runtime = _run(generated)
        assert runtime.returncode == 0, (str(path), runtime.stderr or runtime.stdout)
    return len(paths)


def _run_battery_runtime() -> int:
    for name, source, expected_output in test_cases:
        runtime = _run(_emit(source, name + ".nyx"))
        assert runtime.returncode == 0, (name, runtime.stderr or runtime.stdout)
        actual = _canonical_battery_output(runtime.stdout)
        expected = _canonical_battery_output(expected_output or "")
        if name == "unsafe_05_memdump_call":
            assert actual.endswith(expected), (name, expected, actual)
        else:
            assert actual == expected, (name, expected, actual)
    return len(test_cases)


def _run_differential_fixtures() -> int:
    for name, source in TRIPLE_DIFF_CASES:
        generated = _emit(source, name + ".nyx")
        first = _run(generated)
        second = _run(generated)
        assert first.returncode == second.returncode == 0
        assert first.stdout == second.stdout
    return len(TRIPLE_DIFF_CASES)


def _run_semantic_repairs() -> None:
    source = """
var value = 1
if true {
    var value = 2
    print(value)
}
print(value)

fn lifecycle(skip: bool) {
    defer print("first")
    if skip { return }
    defer print("second")
    print("body")
}

lifecycle(false)
lifecycle(true)
print(-7 / 3, -7 % 3)
"""
    generated = _emit(source, "semantic_repairs.nyx")
    runtime = _run(generated)
    assert runtime.returncode == 0, runtime.stderr or runtime.stdout
    assert runtime.stdout.replace("\r\n", "\n").strip() == (
        "2\n"
        "1\n"
        "body\n"
        "second\n"
        "first\n"
        "first\n"
        "-2 -1"
    )
    assert ROOT_DIR.replace("\\", "/") not in generated.replace("\\", "/")


def run_hir_javascript_suite() -> bool:
    print("=" * 70)
    print("NYX HIR-AUTHORITATIVE JAVASCRIPT BACKEND")
    print("=" * 70)
    assert NODE is not None, "Node.js is required for the HIR JavaScript suite"
    corpus_count = _run_corpus_compile()
    runtime_count = _run_battery_runtime()
    differential_count = _run_differential_fixtures()
    _run_semantic_repairs()
    print(
        f"[PASS] {corpus_count} executed, {runtime_count} runtime cases, "
        f"{differential_count} deterministic fixtures, shadowing/defer/int semantics"
    )
    return True


if __name__ == "__main__":
    sys.exit(0 if run_hir_javascript_suite() else 1)
