"""Generate the checked-in compiler feature matrix."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.core.feature_manifest import load_feature_manifest, render_feature_matrix


def main() -> int:
    destination = ROOT / "docs" / "generated" / "FEATURE_MATRIX.md"
    destination.write_text(render_feature_matrix(load_feature_manifest()), encoding="utf-8")
    print(f"[OK] Generated feature matrix: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
