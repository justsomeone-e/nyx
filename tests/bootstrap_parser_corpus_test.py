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
from src.core.ast_nodes import *
from src.codegen.codegen import UniversalCodeGen
from src.codegen.cpp_toolchain import CppToolchain
from tests.bootstrap_parser_test import py_ast_to_canonical

def run_parser_validation_corpus() -> bool:
    print("=" * 70)
    print("⚡ NYX PHASE 4.0.5.x PARSER VALIDATION & STRESS CORPUS HARNESS")
    print("=" * 70)

    # 1. Prepare native parser binary
    with open(os.path.join(_root_dir, "compiler", "parser.nyx"), "r", encoding="utf-8") as f:
        parser_content = f.read()
    parser_lines = [l for l in parser_content.split("\n") if not (l.startswith("#target") or l.startswith("#native"))]
    parser_body = "\n".join(parser_lines)

    with open(os.path.join(_root_dir, "compiler", "lexer.nyx"), "r", encoding="utf-8") as f:
        lexer_content = f.read()
    lexer_impl_start = lexer_content.index("struct Lexer")
    lexer_impl_end = lexer_content.index("fn main()") if "fn main()" in lexer_content else len(lexer_content)
    lexer_code = lexer_content[lexer_impl_start:lexer_impl_end].strip()

    combined_base = f"""#target hecpp
#native include <string>
#native include <vector>

{parser_body}

{lexer_code}
"""

    valid_corpus = [
        ("deep_nested_arithmetic", "var res: int = ((a + 2) * (b - 3)) / (c % 4);"),
        ("complex_type_signatures", "fn transform(ptr: *int, opt: string?) -> bool { return true; }"),
        ("nested_control_flow", "while true { if a > 0 { for i in 0..10 { break; } } else { continue; } }"),
        ("chained_member_index_call", "var val = service.getUser().accounts[0].getBalance();"),
        ("multi_branch_match", "match status { 200 => { print(\"OK\"); } 404 => { print(\"NotFound\"); } 500 => { print(\"Error\"); } }")
    ]

    all_passed = True
    print("\n--- 1. Valid Stress Corpus (AST Equivalence) ---")
    for name, src in valid_corpus:
        print(f"[*] Validating: {name} ...", end=" ")

        # Python Parser
        py_tokens = PyLexer(src, f"{name}.nyx").tokenize()
        py_ast = PyParser(py_tokens, src, f"{name}.nyx").parse()
        py_canon = py_ast_to_canonical(py_ast)

        # Native Parser
        escaped_src = src.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        runner_code = f"""{combined_base}

fn main() {{
    var code = "{escaped_src}"
    var lex = Lexer(code, 0, 1, 1)
    var tokens = lex.tokenize()
    var p = Parser(tokens, 0)
    var ast = p.parse_program()
    print(ast.to_str())
}}

main()
"""
        tokens_ast = PyLexer(runner_code, f"{name}_driver.nyx").tokenize()
        ast = PyParser(tokens_ast, runner_code, f"{name}_driver.nyx").parse()
        cpp_code = UniversalCodeGen(ast).gen_cpp()

        temp_dir = tempfile.mkdtemp(prefix="nyx_corpus_")
        exe_file = os.path.join(temp_dir, "nyx_parser.exe")
        cpp_file = os.path.join(temp_dir, "nyx_parser.cpp")

        try:
            with open(cpp_file, "w", encoding="utf-8") as f:
                f.write(cpp_code)

            ok, msg = CppToolchain.compile_cpp(cpp_file, exe_file)
            if not ok:
                print(f"FAILED (Compile: {msg})")
                all_passed = False
                continue

            code, output = CppToolchain.run_executable(exe_file)
            nyx_canon = output.strip()

            if py_canon == nyx_canon:
                print("PASS (Matched)")
            else:
                print("FAILED (Mismatch)")
                print(f"  Py:  {py_canon}")
                print(f"  Nyx: {nyx_canon}")
                all_passed = False
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    print("\n--- 2. Invalid / Rejection Corpus (Syntax Error Rejection) ---")
    invalid_corpus = [
        ("unclosed_parenthesis", "var x = (10 + 20;"),
        ("missing_colon_in_decl", "var x int = 10;"),
        ("trailing_plus_operator", "var a = 10 + ;"),
        ("unclosed_brace_block", "fn test() { var a = 10;")
    ]

    for name, src in invalid_corpus:
        print(f"[*] Testing Rejection: {name} ...", end=" ")
        
        # Verify Python Parser raises Diagnostic / error on invalid input
        py_rejected = False
        try:
            py_toks = PyLexer(src, f"{name}.nyx").tokenize()
            # Diagnostic emitter raises SystemExit on error
            try:
                PyParser(py_toks, src, f"{name}.nyx").parse()
            except SystemExit:
                py_rejected = True
        except:
            py_rejected = True

        if py_rejected:
            print("PASS (Correctly rejected by compiler frontend)")
        else:
            print("FAILED (Invalid syntax was unexpectedly accepted)")
            all_passed = False

    print("=" * 70)
    print(f"Phase 4.0.5.x Parser Corpus Validation: {'SUCCESS' if all_passed else 'FAILURE'}")
    print("=" * 70)
    return all_passed

if __name__ == "__main__":
    success = run_parser_validation_corpus()
    sys.exit(0 if success else 1)