import os
import sys
import tempfile
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

from src.core.module_loader import ModuleLoader
from src.core.diagnostics import DiagnosticEmitter, DiagnosticError

def run_module_suite():
    print("=" * 70)
    print("⚡ HOLYEASYLANG MODULE SYSTEM & RESOLUTION HARNESS")
    print("=" * 70)

    # Disable exit on error so we can test negative compiler diagnostics
    DiagnosticEmitter.EXIT_ON_ERROR = False
    temp_dir = tempfile.mkdtemp(prefix="he_mod_test_")
    passed = 0
    total = 3

    try:
        # Test 1: Diamond Dependency Resolution (A -> B, A -> C, B -> D, C -> D)
        print("[*] Testing Diamond Dependency Resolution (A -> B, A -> C, B -> D, C -> D)...")
        mod_d = os.path.join(temp_dir, "d.nyx")
        mod_b = os.path.join(temp_dir, "b.nyx")
        mod_c = os.path.join(temp_dir, "c.nyx")
        mod_a = os.path.join(temp_dir, "a.nyx")

        with open(mod_d, "w", encoding="utf-8") as f:
            f.write("fn shared_base() -> int { return 42 }\n")
        with open(mod_b, "w", encoding="utf-8") as f:
            f.write("import \"./d\"\nfn from_b() -> int { return shared_base() + 1 }\n")
        with open(mod_c, "w", encoding="utf-8") as f:
            f.write("import \"./d\"\nfn from_c() -> int { return shared_base() + 2 }\n")
        with open(mod_a, "w", encoding="utf-8") as f:
            f.write("import \"./b\"\nimport \"./c\"\nvar total = from_b() + from_c()\n")

        loader = ModuleLoader(base_dir=temp_dir)
        ast = loader.load_program(mod_a)
        func_names = [getattr(s, "name", None) for s in ast.statements]
        print("  DEBUG NAMES:", func_names)
        assert func_names.count("shared_base") == 1, "Diamond dependency node 'shared_base' must be deduplicated"
        assert "from_b" in func_names and "from_c" in func_names
        print("  [PASS] Diamond dependency successfully resolved and deduplicated (0 collisions)")
        passed += 1

        # Test 2: Ambiguous Symbol Collision Detection (E1302)
        print("[*] Testing Ambiguous Symbol Collision Detection (E1302)...")
        mod_x = os.path.join(temp_dir, "x.nyx")
        mod_y = os.path.join(temp_dir, "y.nyx")
        mod_main = os.path.join(temp_dir, "ambig_main.nyx")

        with open(mod_x, "w", encoding="utf-8") as f:
            f.write("fn calculate() -> int { return 10 }\n")
        with open(mod_y, "w", encoding="utf-8") as f:
            f.write("fn calculate() -> int { return 20 }\n")
        with open(mod_main, "w", encoding="utf-8") as f:
            f.write("import \"./x\"\nimport \"./y\"\nvar res = calculate()\n")

        try:
            loader = ModuleLoader(base_dir=temp_dir)
            loader.load_program(mod_main)
            print("  [FAIL] Expected E1302 Ambiguous Symbol Collision error")
        except DiagnosticError as de:
            assert de.code == "E1302"
            print(f"  [PASS] Successfully caught Ambiguous Symbol Collision (Code: {de.code})")
            passed += 1

        # Test 3: Module Not Found with candidate paths search (E1301)
        print("[*] Testing Module Not Found with Diagnostics v2 (E1301)...")
        mod_missing = os.path.join(temp_dir, "missing_main.nyx")
        with open(mod_missing, "w", encoding="utf-8") as f:
            f.write("import \"./non_existent_module\"\n")

        try:
            loader = ModuleLoader(base_dir=temp_dir)
            loader.load_program(mod_missing)
            print("  [FAIL] Expected E1301 Module Not Found error")
        except DiagnosticError as de:
            assert de.code == "E1301"
            print(f"  [PASS] Successfully caught Module Not Found (Code: {de.code})")
            passed += 1

    finally:
        DiagnosticEmitter.EXIT_ON_ERROR = True
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("=" * 70)
    print(f"[OK] Module System Harness: {passed}/{total} Passed")
    print("=" * 70)
    return passed == total

if __name__ == "__main__":
    ok = run_module_suite()
    sys.exit(0 if ok else 1)
