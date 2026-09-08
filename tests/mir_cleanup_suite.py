from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.api import NyxCompiler
from src.mir import MIRInterpreter, lower_hir_to_mir, print_mir, verify_mir


FIXTURE = ROOT / "tests" / "fixtures" / "mir" / "m3_control.nyx"


def run_mir_cleanup_suite() -> bool:
    print("=" * 70)
    print("NYX M3 MIR CANONICAL CONTROL / CLEANUP")
    print("=" * 70)

    result = NyxCompiler(str(ROOT)).check_file(str(FIXTURE), target="cpp")
    assert result.success and result.hir is not None, result.diagnostics
    mir = lower_hir_to_mir(result.hir)
    verify_mir(mir)
    text = print_mir(mir)
    for forbidden in ("IRIf", "IRFor", "IRGuard", "IRDefer", "IRTryCatch", "IRResultPropagate"):
        assert forbidden not in text

    executed = MIRInterpreter(mir).run()
    assert executed.output == (
        "false",
        "true",
        "10",
        "two",
        "10",
        "caught boom",
        "checked-cleanup",
        "use-cleanup",
        "Ok(8)",
        "checked-cleanup",
        "use-cleanup",
        "Err(bad)",
    ), executed.output

    print("[PASS] short-circuit, value branches, match, range, guard, defer, Result ?, and unwind")
    return True


if __name__ == "__main__":
    raise SystemExit(0 if run_mir_cleanup_suite() else 1)
