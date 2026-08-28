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
from src.core.ast_nodes import (
    ProgramNode, VarDeclNode, AssignNode, NumberNode, StringNode, BooleanNode,
    NullNode, IdentifierNode, BinaryOpNode, UnaryOpNode, FunctionCallNode,
    FunctionDefNode, StructDefNode, ImplBlockNode, IfNode, ReturnNode,
    NativeIncludeNode, NativeLinkNode, NativeUseNode, NativeRawNode
)
from src.codegen.codegen import UniversalCodeGen
from src.codegen.cpp_toolchain import CppToolchain

def py_ast_to_canonical(node) -> str:
    if isinstance(node, ProgramNode):
        stmts = " ".join(py_ast_to_canonical(s) for s in node.statements)
        return f"(Program name='main' body=[{stmts}])"
    if isinstance(node, VarDeclNode):
        t = node.type_annot.name if node.type_annot else ""
        const_s = " const=true" if node.is_const else ""
        type_s = f" type='{t}'" if t else ""
        return f"(VarDecl name='{node.name}'{type_s}{const_s} body=[{py_ast_to_canonical(node.expr)}])"
    if isinstance(node, AssignNode):
        return f"(Assign op='=' body=[{py_ast_to_canonical(node.target)} {py_ast_to_canonical(node.expr)}])"
    if isinstance(node, NumberNode):
        return f"(Number val='{node.value}' type='int')"
    if isinstance(node, StringNode):
        return f"(String val='{node.value}' type='string')"
    if isinstance(node, BooleanNode):
        return f"(Boolean val='{str(node.value).lower()}' type='bool')"
    if isinstance(node, NullNode):
        return f"(Null val='null' type='null')"
    if isinstance(node, IdentifierNode):
        return f"(Identifier name='{node.name}')"
    if isinstance(node, BinaryOpNode):
        return f"(BinaryOp op='{node.op}' body=[{py_ast_to_canonical(node.left)} {py_ast_to_canonical(node.right)}])"
    if isinstance(node, UnaryOpNode):
        return f"(UnaryOp op='{node.op}' body=[{py_ast_to_canonical(node.expr)}])"
    if isinstance(node, FunctionCallNode):
        args = " ".join(py_ast_to_canonical(a) for a in node.args)
        body_s = f" body=[{args}]" if args else ""
        return f"(FunctionCall name='{node.callee}'{body_s})"
    if isinstance(node, FunctionDefNode):
        params_s = ", ".join(f"{p.name}: {p.type_annot.name if p.type_annot else ''}" for p in node.params)
        ret = node.return_type.name if node.return_type else "void"
        body = " ".join(py_ast_to_canonical(s) for s in node.body)
        params_attr = f" params=[{params_s}]" if params_s else ""
        return f"(FunctionDef name='{node.name}' type='{ret}'{params_attr} body=[{body}])"
    if isinstance(node, StructDefNode):
        params_s = ", ".join(f"{p.name}: {p.type_annot.name if p.type_annot else ''}" for p in node.fields)
        return f"(StructDef name='{node.name}' params=[{params_s}])"
    if isinstance(node, ImplBlockNode):
        methods = " ".join(py_ast_to_canonical(m) for m in node.methods)
        return f"(ImplBlock name='{node.target_type}' body=[{methods}])"
    if isinstance(node, IfNode):
        then_b = " ".join(py_ast_to_canonical(s) for s in node.then_branch)
        return f"(If body=[{py_ast_to_canonical(node.condition)} {then_b}])"
    if isinstance(node, ReturnNode):
        expr = py_ast_to_canonical(node.expr) if node.expr else "(Null val='null' type='null')"
        return f"(Return body=[{expr}])"
    if isinstance(node, NativeIncludeNode):
        return f"(Directive name='native_include' val='{node.header}')"
    if isinstance(node, NativeLinkNode):
        return f"(Directive name='native_link' val='{node.library}')"
    if isinstance(node, NativeUseNode):
        return f"(Directive name='native_use' val='{node.target}')"
    if isinstance(node, NativeRawNode):
        return f"(Directive name='native_raw' val='{node.raw}')"
    return f"({type(node).__name__})"

def run_bootstrap_parser_test() -> bool:
    print("=" * 70)
    print("⚡ NYX PHASE 4.0.4 - 4.0.5 BOOTSTRAP PARSER PARITY HARNESS")
    print("=" * 70)

    with open(os.path.join(_root_dir, "compiler", "parser.nyx"), "r", encoding="utf-8") as f:
        parser_content = f.read()

    # Strip top directives from parser_content
    parser_lines = [l for l in parser_content.split("\n") if not (l.startswith("#target") or l.startswith("#native"))]
    parser_body = "\n".join(parser_lines)

    with open(os.path.join(_root_dir, "compiler", "lexer.nyx"), "r", encoding="utf-8") as f:
        lexer_content = f.read()

    # Extract clean Lexer struct and its impl
    lexer_impl_start = lexer_content.index("struct Lexer")
    lexer_impl_end = lexer_content.index("fn main()") if "fn main()" in lexer_content else len(lexer_content)
    lexer_code = lexer_content[lexer_impl_start:lexer_impl_end].strip()

    combined_base = f"""#target hecpp
#native include <string>
#native include <vector>

{parser_body}

{lexer_code}
"""

    test_cases = [
        ("simple_var_and_math", "var x: int = 10 + 20 * 30;"),
        ("function_definition", "fn add(a: int, b: int) -> int { return a + b; }"),
        ("struct_definition", "struct Point { x: int, y: int }"),
        ("if_control_flow", "if a > 10 { print(\"Large\"); }"),
        ("native_directives", "#native include <vector>\n#native link \"user32.lib\"\n#native use std::vector;")
    ]

    all_passed = True
    for name, src in test_cases:
        print(f"[*] Verifying AST Parity: {name} ...", end=" ")

        # A. Python Reference Parser
        py_tokens = PyLexer(src, f"{name}.nyx").tokenize()
        py_ast = PyParser(py_tokens, src, f"{name}.nyx").parse()
        py_canon = py_ast_to_canonical(py_ast)

        # B. Nyx Compiled Native Parser
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

        temp_dir = tempfile.mkdtemp(prefix="nyx_test_parser_")
        exe_file = os.path.join(temp_dir, "nyx_parser.exe")
        cpp_file = os.path.join(temp_dir, "nyx_parser.cpp")

        try:
            with open(cpp_file, "w", encoding="utf-8") as f:
                f.write(cpp_code)

            ok, msg = CppToolchain.compile_cpp(cpp_file, exe_file)
            if not ok:
                print(f"FAILED (Compile error: {msg})")
                all_passed = False
                continue

            code, output = CppToolchain.run_executable(exe_file)
            nyx_canon = output.strip()

            if py_canon == nyx_canon:
                print("PASS (Exact Canonical AST Match)")
            else:
                print(f"FAILED (AST mismatch)")
                print(f"  Py:  {py_canon}")
                print(f"  Nyx: {nyx_canon}")
                all_passed = False
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    print("=" * 70)
    print(f"Bootstrap Parser Parity Result: {'SUCCESS' if all_passed else 'FAILURE'}")
    print("=" * 70)
    return all_passed

if __name__ == "__main__":
    success = run_bootstrap_parser_test()
    sys.exit(0 if success else 1)