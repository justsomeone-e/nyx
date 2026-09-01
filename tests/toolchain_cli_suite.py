import os
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI_PATH = os.path.join(ROOT_DIR, "src", "cli.py")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.toolchain.manifest import NyxManifest


def _run(cwd: str, *arguments: str, input_text: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, CLI_PATH, *arguments],
        cwd=cwd,
        input=input_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )


def _output(process: subprocess.CompletedProcess) -> str:
    return (process.stdout + process.stderr).replace("\r\n", "\n")


def run_toolchain_cli_suite() -> bool:
    print("=" * 70)
    print("NYX TOOLCHAIN CLI REAL-BEHAVIOR CONTRACT")
    print("=" * 70)

    with tempfile.TemporaryDirectory(prefix="nyx_toolchain_cli_") as directory:
        root = Path(directory)

        assert _run(directory, "pkg").returncode == 1
        assert _run(directory, "add", "telemetry", "@2.3.4").returncode == 1

        initialized = _run(directory, "init", "cli-contract")
        assert initialized.returncode == 0, _output(initialized)
        assert (root / "nyx.toml").is_file() and (root / "nyx.lock").is_file()
        assert _run(directory, "init", "overwrite-attempt").returncode == 1

        added = _run(directory, "add", "telemetry", "@2.3.4")
        assert added.returncode == 0, _output(added)
        manifest = NyxManifest(str(root / "nyx.toml"))
        assert manifest.dependencies == {"telemetry": "2.3.4"}
        assert 'telemetry = "2.3.4"' in (root / "nyx.lock").read_text(encoding="utf-8")

        listed = _run(directory, "pkg")
        assert listed.returncode == 0, _output(listed)
        assert "telemetry: 2.3.4" in _output(listed)

        installed = _run(directory, "install")
        assert installed.returncode == 0, _output(installed)
        assert "Validated and locked 1 dependencies" in _output(installed)
        assert "Remote registry download is not part" in _output(installed)

        removed = _run(directory, "remove", "telemetry")
        assert removed.returncode == 0, _output(removed)
        assert NyxManifest(str(root / "nyx.toml")).dependencies == {}
        assert _run(directory, "remove", "telemetry").returncode == 1

        source_path = root / "format_contract.nyx"
        source_path.write_text(
            'import cpp "std::filesystem" from "<filesystem>" as fs\n'
            'fn main(){\n'
            'var url="https://nyx.dev/a?x=1"// preserve a=b and { braces }\n'
            'if true{\n'
            'print(url)\n'
            'print(fs.current_path().string())\n'
            '}\n'
            '}\n',
            encoding="utf-8",
        )
        original = source_path.read_text(encoding="utf-8")
        formatted = _run(directory, "fmt", str(source_path))
        assert formatted.returncode == 0, _output(formatted)
        first_format = source_path.read_text(encoding="utf-8")
        assert first_format != original
        assert '"https://nyx.dev/a?x=1"' in first_format
        assert 'import cpp "std::filesystem" from "<filesystem>" as fs' in first_format
        assert "// preserve a=b and { braces }" in first_format
        assert "    var url = " in first_format and "        print(url)" in first_format
        second_format = _run(directory, "fmt", str(source_path))
        assert second_format.returncode == 0, _output(second_format)
        assert source_path.read_text(encoding="utf-8") == first_format
        checked = _run(directory, "check", str(source_path))
        assert checked.returncode == 0, _output(checked)

        lint_path = root / "lint_contract.nyx"
        lint_path.write_text(
            "var value = 1\n"
            "unsafe {\n"
            "    var address = addr(value)\n"
            "    print(peek(address))\n"
            "}\n",
            encoding="utf-8",
        )
        linted = _run(directory, "lint", str(lint_path))
        assert linted.returncode == 0, _output(linted)
        assert "warning[W010]" in _output(linted)
        assert "warning[W002]" not in _output(linted)

        doc_path = root / "documented.nyx"
        doc_path.write_text(
            "/// Return <value> & keep it safe.\n"
            "fn documented(value: int) -> int { return value }\n",
            encoding="utf-8",
        )
        documented = _run(directory, "doc", str(doc_path))
        assert documented.returncode == 0, _output(documented)
        html = (root / "docs" / "index.html").read_text(encoding="utf-8")
        assert "Return &lt;value&gt; &amp; keep it safe." in html

        profile_path = root / "profile_contract.nyx"
        profile_path.write_text('print("PROFILE_REAL_OUTPUT")\n', encoding="utf-8")
        profiled = _run(directory, "profile", str(profile_path), "--target", "python")
        assert profiled.returncode == 0, _output(profiled)
        profile_output = _output(profiled)
        assert "PROFILE_REAL_OUTPUT" in profile_output
        assert "Total compile + run wall time:" in profile_output
        assert "radar_dsp_scan" not in profile_output

        inspected = _run(directory, "debug", str(profile_path), input_text="q\n")
        assert inspected.returncode == 0, _output(inspected)
        inspect_output = _output(inspected)
        assert "source inspector" in inspect_output
        assert "no runtime state" in inspect_output
        assert "Umut" not in inspect_output and "0x00007FFD" not in inspect_output

        for command in ("fmt", "lint", "doc", "profile", "debug"):
            missing = _run(directory, command, str(root / "missing.nyx"))
            assert missing.returncode == 1, (command, _output(missing))

        build_dir = root / "build"
        build_dir.mkdir(exist_ok=True)
        (build_dir / "artifact.tmp").write_text("temporary", encoding="utf-8")
        cleaned = _run(directory, "clean")
        assert cleaned.returncode == 0, _output(cleaned)
        assert not build_dir.exists()

    print(
        "[PASS] fmt/lint/debug/profile/doc and manifest/lock package commands "
        "have real effects, honest output, idempotence, and failure exit codes"
    )
    return True


if __name__ == "__main__":
    sys.exit(0 if run_toolchain_cli_suite() else 1)
