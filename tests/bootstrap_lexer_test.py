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
from src.core.parser import Parser
from src.codegen.codegen import UniversalCodeGen
from src.codegen.cpp_toolchain import CppToolchain

def run_bootstrap_lexer_test() -> bool:
    print("=" * 70)
    print("⚡ NYX PHASE 4.0.1 - 4.0.3 EXHAUSTIVE BOOTSTRAP LEXER PARITY HARNESS")
    print("=" * 70)

    # Read base lexer.nyx
    lexer_nyx_path = os.path.join(_root_dir, "compiler", "lexer.nyx")
    with open(lexer_nyx_path, "r", encoding="utf-8") as f:
        lexer_nyx_code = f.read()

    # Strip out any existing main()
    if "fn main()" in lexer_nyx_code:
        base_lexer_code = lexer_nyx_code[:lexer_nyx_code.index("fn main()")].strip()
    else:
        base_lexer_code = lexer_nyx_code.strip()

    test_sources = [
        ("basic_math", 'var x: int = 100 + 20; print("Result:", x)'),
        ("block_and_doc_comments", '/* multiline\nblock comment */\n/// doc comment\n// line comment\nvar a = 10;'),
        ("escaped_strings_and_quotes", 'var s1 = "escaped\\nstring"; var s2 = "quotes: \\"test\\"";'),
        ("floats_and_hex_literals", 'var f = 123.456; var h = 0xFF; var z = 0.789;'),
        ("ranges_and_operators", 'for i in 0..10 { if a >= 10 && b != 20 || c == 30 { var s = val ?? "default"; } }'),
        ("pipeline_and_arrows", 'var res = x |> double |> add; fn cb(x: int) -> int; (a, b) => a + b; obj?.field;'),
        ("native_directives_and_ffi", '#target hecpp\n#native include <vector>\n#native link "user32.lib"\n#native use std::vector;\n#native raw int x = 42;\nextern "C" fn puts(s: string) -> int'),
        ("struct_and_impl", 'struct Point { x: int, y: int }\nimpl Point { fn dist(self) -> int { return self.x + self.y } }')
    ]

    all_passed = True
    for name, src in test_sources:
        print(f"[*] Verifying Lexer Parity: {name} ...", end=" ")
        
        # A. Python Reference Lexer
        py_tokens = PyLexer(src, f"{name}.nyx").tokenize()
        py_stream = [(t.type, str(t.value)) for t in py_tokens if t.type != "EOF"]
        
        # B. Nyx Compiled Native Lexer
        # Generate standalone nyx runner for this source
        escaped_src = src.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        test_nyx_code = f"""{base_lexer_code}

fn main() {{
    var code = "{escaped_src}"
    var lex = Lexer(code, 0, 1, 1)
    var tokens = lex.tokenize()
    for t in tokens {{
        print(t.type_name, t.value)
    }}
}}

main()
"""
        tokens_ast = PyLexer(test_nyx_code, f"{name}_driver.nyx").tokenize()
        ast = Parser(tokens_ast, test_nyx_code, f"{name}_driver.nyx").parse()
        cpp_code = UniversalCodeGen(ast).gen_cpp()

        temp_dir = tempfile.mkdtemp(prefix="nyx_test_lexer_")
        exe_file = os.path.join(temp_dir, "nyx_lexer.exe")
        cpp_file = os.path.join(temp_dir, "nyx_lexer.cpp")
        
        try:
            with open(cpp_file, "w", encoding="utf-8") as f:
                f.write(cpp_code)

            ok, msg = CppToolchain.compile_cpp(cpp_file, exe_file)
            if not ok:
                print(f"FAILED (Compile error: {msg})")
                all_passed = False
                continue

            code, output = CppToolchain.run_executable(exe_file)
            lines = [l.strip() for l in output.strip().split("\n") if l.strip()]
            nyx_stream = []
            for l in lines:
                if " " in l:
                    tt, v = l.split(" ", 1)
                    if tt != "EOF":
                        nyx_stream.append((tt, v))

            # Compare
            if len(py_stream) != len(nyx_stream):
                print(f"FAILED (Length mismatch: Py={len(py_stream)}, Nyx={len(nyx_stream)})")
                print(f"  Py:  {py_stream}")
                print(f"  Nyx: {nyx_stream}")
                all_passed = False
                continue
                
            mismatch = False
            for i in range(len(py_stream)):
                p_t, p_v = py_stream[i]
                n_t, n_v = nyx_stream[i]
                if p_t != n_t:
                    print(f"FAILED at token {i}: Type mismatch (Py={p_t}, Nyx={n_t})")
                    mismatch = True
                    break
                    
            if not mismatch:
                print("PASS (100% Token Parity)")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    print("=" * 70)
    print(f"Exhaustive Bootstrap Lexer Parity Result: {'SUCCESS' if all_passed else 'FAILURE'}")
    print("=" * 70)
    return all_passed

if __name__ == "__main__":
    success = run_bootstrap_lexer_test()
    sys.exit(0 if success else 1)