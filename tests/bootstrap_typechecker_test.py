import os
import sys
import tempfile
import shutil

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

from src.core.lexer import Lexer as PyLexer
from src.core.parser import Parser as PyParser
from src.core.type_checker import TypeChecker as PyTypeChecker
from src.codegen.codegen import UniversalCodeGen
from src.codegen.cpp_toolchain import CppToolchain

def run_bootstrap_typechecker_test() -> bool:
    print("=" * 70)
    print("⚡ NYX PHASE 4.0.6 SEMANTIC TYPECHECKER PARITY HARNESS")
    print("=" * 70)

    # 1. Read Lexer, Parser, and TypeChecker nyx files
    with open(os.path.join(_root_dir, "compiler", "parser.nyx"), "r", encoding="utf-8") as f:
        parser_content = f.read()
    parser_lines = [l for l in parser_content.split("\n") if not (l.startswith("#target") or l.startswith("#native"))]
    parser_body = "\n".join(parser_lines)

    with open(os.path.join(_root_dir, "compiler", "lexer.nyx"), "r", encoding="utf-8") as f:
        lexer_content = f.read()
    lexer_impl_start = lexer_content.index("struct Lexer")
    lexer_impl_end = lexer_content.index("fn main()") if "fn main()" in lexer_content else len(lexer_content)
    lexer_code = lexer_content[lexer_impl_start:lexer_impl_end].strip()

    with open(os.path.join(_root_dir, "compiler", "type_checker.nyx"), "r", encoding="utf-8") as f:
        tc_content = f.read()
    tc_lines = [l for l in tc_content.split("\n") if not (l.startswith("#target") or l.startswith("#native"))]
    tc_body = "\n".join(tc_lines)

    combined_base = f"""#target hecpp
#native include <string>
#native include <vector>

{parser_body}

{lexer_code}

{tc_body}
"""

    valid_cases = [
        ("valid_types_and_arithmetic", "var x: int = 10 + 20; var f: float = 10; var s: string = \"hello\";"),
        ("valid_function_return", "fn calc(a: int, b: int) -> int { return a + b; }"),
        ("valid_optional_types", "var opt1: string? = null; var opt2: string? = \"active\";"),
        ("valid_struct_field_access", "struct Point { x: int, y: int }\nvar p: Point = Point(10, 20); var px: int = p.x;")
    ]

    all_passed = True
    print("\n--- 1. Valid Semantic Cases (Acceptance Parity) ---")
    for name, src in valid_cases:
        print(f"[*] Validating: {name} ...", end=" ")

        # A. Python TypeChecker
        py_tokens = PyLexer(src, f"{name}.nyx").tokenize()
        py_ast = PyParser(py_tokens, src, f"{name}.nyx").parse()
        py_tc = PyTypeChecker(py_ast, f"{name}.nyx", src)
        py_accepted = True
        try:
            py_tc.check()
        except:
            py_accepted = False

        # B. Native Nyx TypeChecker
        escaped_src = src.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        runner_code = f"""{combined_base}

fn main() {{
    var code = "{escaped_src}"
    var lex = Lexer(code, 0, 1, 1)
    var tokens = lex.tokenize()
    var p = Parser(tokens, 0, false, "")
    var ast = p.parse_program()
    var tc = TypeChecker([], [], "", false, "")
    var ok = tc.check_program(ast)
    if ok {{
        print("SEMANTIC_OK")
    }} else {{
        print("SEMANTIC_ERROR:", tc.error_msg)
    }}
}}

main()
"""
        tokens_ast = PyLexer(runner_code, f"{name}_tc_driver.nyx").tokenize()
        ast = PyParser(tokens_ast, runner_code, f"{name}_tc_driver.nyx").parse()
        cpp_code = UniversalCodeGen(ast).gen_cpp()

        temp_dir = tempfile.mkdtemp(prefix="nyx_tc_")
        exe_file = os.path.join(temp_dir, "nyx_tc.exe")
        cpp_file = os.path.join(temp_dir, "nyx_tc.cpp")

        nyx_accepted = False
        try:
            with open(cpp_file, "w", encoding="utf-8") as f:
                f.write(cpp_code)

            ok, msg = CppToolchain.compile_cpp(cpp_file, exe_file)
            if ok:
                code, output = CppToolchain.run_executable(exe_file)
                if "SEMANTIC_OK" in output:
                    nyx_accepted = True
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        if py_accepted and nyx_accepted:
            print("PASS (Accepted by both Python & Native Nyx TypeCheckers)")
        else:
            print(f"FAILED (Py={py_accepted}, Nyx={nyx_accepted})")
            all_passed = False

    print("\n--- 2. Invalid Semantic Cases (Rejection Parity) ---")
    invalid_cases = [
        ("type_mismatch_var", "var x: int = \"string_val\";"),
        ("return_type_mismatch", "fn get_num() -> int { return \"not_a_num\"; }")
    ]

    for name, src in invalid_cases:
        print(f"[*] Testing Rejection: {name} ...", end=" ")

        # A. Python TypeChecker Rejection
        py_rejected = False
        try:
            py_tokens = PyLexer(src, f"{name}.nyx").tokenize()
            py_ast = PyParser(py_tokens, src, f"{name}.nyx").parse()
            py_tc = PyTypeChecker(py_ast, f"{name}.nyx", src)
            try:
                py_tc.check()
            except SystemExit:
                py_rejected = True
        except:
            py_rejected = True

        # B. Native Nyx TypeChecker Rejection
        escaped_src = src.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        runner_code = f"""{combined_base}

fn main() {{
    var code = "{escaped_src}"
    var lex = Lexer(code, 0, 1, 1)
    var tokens = lex.tokenize()
    var p = Parser(tokens, 0, false, "")
    var ast = p.parse_program()
    var tc = TypeChecker([], [], "", false, "")
    var ok = tc.check_program(ast)
    if ok {{
        print("SEMANTIC_OK")
    }} else {{
        print("SEMANTIC_REJECTED:", tc.error_msg)
    }}
}}

main()
"""
        tokens_ast = PyLexer(runner_code, f"{name}_tc_driver.nyx").tokenize()
        ast = PyParser(tokens_ast, runner_code, f"{name}_tc_driver.nyx").parse()
        cpp_code = UniversalCodeGen(ast).gen_cpp()

        temp_dir = tempfile.mkdtemp(prefix="nyx_tc_rej_")
        exe_file = os.path.join(temp_dir, "nyx_tc.exe")
        cpp_file = os.path.join(temp_dir, "nyx_tc.cpp")

        nyx_rejected = False
        try:
            with open(cpp_file, "w", encoding="utf-8") as f:
                f.write(cpp_code)

            ok, msg = CppToolchain.compile_cpp(cpp_file, exe_file)
            if ok:
                code, output = CppToolchain.run_executable(exe_file)
                if "SEMANTIC_REJECTED:" in output:
                    nyx_rejected = True
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        if py_rejected and nyx_rejected:
            print("PASS (Dual Semantic Rejection Parity - Both Python & Nyx Rejected)")
        else:
            print(f"FAILED (Py={py_rejected}, Nyx={nyx_rejected})")
            all_passed = False

    print("=" * 70)
    print(f"Phase 4.0.6 TypeChecker Parity Result: {'SUCCESS' if all_passed else 'FAILURE'}")
    print("=" * 70)
    return all_passed

if __name__ == "__main__":
    success = run_bootstrap_typechecker_test()
    sys.exit(0 if success else 1)