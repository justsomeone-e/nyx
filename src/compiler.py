import os, sys
try:
    from src.core import Lexer, Parser, TypeChecker, DiagnosticEmitter
    from .codegen import UniversalCodeGen
    from .runtime import get_runtime_env
except (ImportError, ValueError):
    from src.core import Lexer, Parser, TypeChecker, DiagnosticEmitter
    from src.codegen import UniversalCodeGen
    from src.runtime import get_runtime_env
class Compiler:
    def __init__(self, filepath: str, target_override: str = None):
        self.filepath = filepath
        self.target_override = target_override

    def compile(self, run_immediately: bool = True):
        if not os.path.exists(self.filepath):
            print(f"Error: Source file '{self.filepath}' not found!")
            sys.exit(1)

        with open(self.filepath, 'r', encoding='utf-8') as f:
            source = f.read()

        # Step 1 & 2: Load program and resolve module imports
        from src.core.module_loader import ModuleLoader
        loader = ModuleLoader(base_dir=os.path.dirname(os.path.abspath(self.filepath)))
        ast = loader.load_program(self.filepath, source)

        # Step 3: Type Checking & Semantic Analysis
        type_checker = TypeChecker(ast, self.filepath, source)
        type_checker.check()

        # Target selection
        target = self.target_override or ast.target or "hecpp"
        codegen = UniversalCodeGen(ast)

        base_name = os.path.splitext(self.filepath)[0]

        if target == "hecpp":
            cpp_out = codegen.gen_cpp()
            out_file = base_name + ".cpp"
            with open(out_file, 'w', encoding='utf-8') as f:
                f.write(cpp_out)
            print(f"[*] Nyx Compiling: {self.filepath} -> [Target: hecpp]")
            print(f"[+] Output generated: {out_file}")

        elif target == "hereact":
            tsx_out = codegen.gen_react()
            out_file = base_name + ".tsx"
            with open(out_file, 'w', encoding='utf-8') as f:
                f.write(tsx_out)
            print(f"[*] Nyx Compiling: {self.filepath} -> [Target: hereact]")
            print(f"[+] Output generated: {out_file}")

        elif target == "hewasm":
            wat_out = codegen.gen_wasm()
            out_file = base_name + ".wat"
            with open(out_file, 'w', encoding='utf-8') as f:
                f.write(wat_out)
            print(f"[*] Nyx Compiling: {self.filepath} -> [Target: hewasm]")
            print(f"[+] Output generated: {out_file}")

        elif target == "hepy":
            py_out = codegen.gen_python()
            out_file = base_name + ".py"
            with open(out_file, 'w', encoding='utf-8') as f:
                f.write(py_out)
            print(f"[*] Nyx Compiling: {self.filepath} -> [Target: hepy]")
            print(f"[+] Output generated: {out_file}")

        elif target == "hejs":
            js_out = codegen.gen_js()
            out_file = base_name + ".js"
            with open(out_file, 'w', encoding='utf-8') as f:
                f.write(js_out)
            print(f"[*] Nyx Compiling: {self.filepath} -> [Target: hejs]")
            print(f"[+] Output generated: {out_file}")

        if run_immediately:
            print("\n" + "="*50)
            print("[+] Program Output:\n")
            py_runner_code = codegen.gen_python()
            env = get_runtime_env()
            try:
                exec(py_runner_code, env)
            except Exception as e:
                print(f"\nRuntime Execution Error: {e}")
            print("\n" + "="*50)
            print("[OK] Execution finished successfully.\n")
