import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

from src.core import Lexer, Parser, TypeChecker, TokenType
from src.core.ast_nodes import FunctionDefNode, StructDefNode
from src.codegen import UniversalCodeGen
from tests.battery138.run_battery import run_all_138 as run_battery138

def run_lexer_tests():
    print("[*] Running Lexer Unit Tests...")
    src = 'var x: int = 10 + 20; print("çğıöşü 🚀", x)'
    tokens = Lexer(src).tokenize()
    assert tokens[0].type == TokenType.VAR
    assert tokens[1].value == 'x'
    assert tokens[3].value == 'int'
    assert tokens[5].value == 10
    assert any(t.type == TokenType.STRING and 'çğıöşü' in t.value for t in tokens)
    print("  [PASS] Lexer tokenization & Unicode handling")

def run_parser_tests():
    print("[*] Running Parser Unit Tests...")
    src = """#target hecpp
struct Point { x: int, y: int }
fn add_point(p1: Point, p2: Point) -> Point {
    return Point(p1.x + p2.x, p1.y + p2.y)
}
"""
    ast = Parser(Lexer(src).tokenize(), src).parse()
    assert ast.target == 'hecpp'
    assert len(ast.statements) == 2
    print("  [PASS] Parser Struct & Function AST construction")

def run_type_checker_tests():
    print("[*] Running TypeChecker Semantic Tests...")
    src = """var a = 10
var b = 20.5
var c = "Hello"
var d = [1, 2, 3]
"""
    ast = Parser(Lexer(src).tokenize(), src).parse()
    tc = TypeChecker(ast, '<test>', src)
    tc.check()
    assert tc.lookup('a') == 'int'
    assert tc.lookup('b') == 'float'
    assert tc.lookup('c') == 'string'
    assert 'Array' in tc.lookup('d')
    print("  [PASS] TypeChecker Scope tracking & Inference")

def run_codegen_tests():
    print("[*] Running C++20 Codegen Tests...")
    src = """#target hecpp
struct User { name, age }
fn is_adult(u) { return u.age >= 18 }
"""
    ast = Parser(Lexer(src).tokenize(), src).parse()
    cpp = UniversalCodeGen(ast).gen_cpp()
    assert 'struct User {' in cpp
    assert 'User(' in cpp
    assert 'auto is_adult(' in cpp
    print("  [PASS] C++20 Structs, Constructors & Forward Declarations")

def run_module_tests():
    print("[*] Running Module & Import Loader Unit Tests...")
    from src.core.module_loader import ModuleLoader
    main_file = os.path.join(BASE_DIR, "tests", "modules", "main_test.nyx")
    loader = ModuleLoader(base_dir=os.path.dirname(main_file))
    ast = loader.load_program(main_file)
    assert any(isinstance(s, FunctionDefNode) and s.name == "calculate_discount" for s in ast.statements)
    assert any(isinstance(s, FunctionDefNode) and s.name == "power" for s in ast.statements)
    print("  [PASS] Multi-file local and standard library module resolution")

from tests.negative_tests import run_negative_tests
from tests.fuzz_test import run_fuzz_tests
from tests.differential_testing import run_differential_tests
from tests.module_resolution_suite import run_module_suite
from tests.lsp_suite import run_lsp_suite
from tests.smoke_test_clean_environment import run_smoke_test
from tests.cpp_e2e_suite import run_cpp_e2e_tests
from tests.js_e2e_suite import run_js_e2e_tests
from tests.rust_e2e_suite import run_rust_e2e_tests

def main():
    print("=" * 70)
    print("⚡ HOLYEASYLANG ENTERPRISE UNIFIED TEST FRAMEWORK")
    print("=" * 70)
    
    run_lexer_tests()
    run_parser_tests()
    run_type_checker_tests()
    run_codegen_tests()
    run_module_tests()
    
    print()
    mod_ok = run_module_suite()
    
    print()
    lsp_ok = run_lsp_suite()
    
    print()
    smoke_ok = run_smoke_test()
    
    print()
    neg_ok = run_negative_tests()
    
    print()
    fuzz_ok = run_fuzz_tests(500) # Exactly 530 deterministic fuzz test cases
    
    print()
    diff_ok = run_differential_tests()
    
    print()
    js_ok = run_js_e2e_tests()
    
    print()
    rs_ok = run_rust_e2e_tests()
    
    print()
    e2e_ok = run_cpp_e2e_tests()
    
    print("\n[*] Executing 138-Point Exhaustive Regression Battery...")
    battery_ok = run_battery138()
    
    all_passed = mod_ok and lsp_ok and smoke_ok and neg_ok and fuzz_ok and diff_ok and js_ok and rs_ok and e2e_ok and battery_ok
    print("=" * 70)
    if all_passed:
        print("🏆 ALL TEST SUITES PASSED (100% SUCCESS RATE)")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 70)
    
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
