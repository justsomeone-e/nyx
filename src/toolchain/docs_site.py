"""Rebuild the static site's real WASM artifacts from their Nyx sources."""
from pathlib import Path
import hashlib
import json
import shutil

from src.cli import cmd_bundle

ROOT = Path(__file__).resolve().parents[2]


def build_site():
    docs = ROOT / "docs"
    artifacts = []
    for name, source in (
        ("metrics", ROOT / "examples/metrics/metrics.nyx"),
        ("pong", ROOT / "examples/web_pong/pong.nyx"),
    ):
        output = docs / "generated" / name
        if cmd_bundle(str(source), str(output), emit_package=True) != 0:
            raise RuntimeError(f"Failed to bundle {source.name}")
        shutil.copyfile(source, output / source.name)
        for path in sorted(output.iterdir()):
            if path.is_file():
                artifacts.append({"path": path.relative_to(docs).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    examples = docs / "examples/metrics"
    examples.mkdir(parents=True, exist_ok=True)
    for filename in ("README.md", "metrics.nyx", "cli.nyx", "use_metrics.mjs", "use_metrics.py"):
        shutil.copyfile(ROOT / "examples/metrics" / filename, examples / filename)
    (docs / "generated/manifest.json").write_text(json.dumps({
        "compilerVersion": (ROOT / "VERSION").read_text().strip(),
        "rebuild": "python -m src.toolchain.docs_site",
        "artifacts": artifacts,
    }, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    build_site()
