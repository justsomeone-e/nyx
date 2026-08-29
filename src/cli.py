import sys
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass
import sys
import os
import shutil
import subprocess

_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

from src.core import Lexer, Parser, TypeChecker
from src.codegen import UniversalCodeGen
from src.codegen.cpp_toolchain import CppToolchain
from src.toolchain import (
    Formatter, Linter, Debugger, Profiler,
    DocGenerator, PackageManager, StandalonePackager
)

VERSION = "3.0.0-beta.1"

def print_banner():
    print("===================================================================")
    print(f"nyx core v{VERSION} (beta 1) — systems toolchain")
    print("===================================================================")

def print_help():
    print_banner()
    print("""Usage: nyx <command> [arguments] [options]

Project & Development Commands:
  nyx new <project_name>             Create a new nyx project in a directory
  nyx init [name]                    Initialize a nyx.toml project in current directory
  nyx check [file.nyx]               Fast type-check and semantic validation
  nyx build [file.nyx] [--target t]  Build executable or transpile project into build/
  nyx run [file.nyx] [--target t]    Compile and run project / file immediately
  nyx test [file.nyx | all]          Execute in-file unit tests or test framework
  nyx clean                          Remove build artifacts and temporary files

Toolchain & Quality:
  nyx fmt <file.nyx>                 Auto-format and beautify source code
  nyx lint <file.nyx>                Static analysis and unsafe boundary checks
  nyx lsp                            Launch Language Server Protocol (LSP) daemon
  nyx debug <file.nyx>               Interactive step-by-step debugger
  nyx profile <file.nyx>             Runtime bottleneck and profiling report
  nyx doc <file.nyx>                 Generate HTML API documentation from /// comments

Package Management:
  nyx add <pkg> [@version]           Add a dependency into nyx.toml and lock in nyx.lock
  nyx remove <pkg>                   Remove a dependency from nyx.toml and nyx.lock
  nyx install                        Install / verify dependencies from nyx.toml
  nyx pkg                            Inspect current project manifest and dependencies

System & Diagnostics:
  nyx doctor                         Inspect compiler toolchains & environment health
  nyx version                        Show compiler core and detected native toolchains
  nyx help                           Display this help message

Target Backends (--target):
  hecpp (C++20 Native) | hepy (Python) | hejs (Node.js) | hers (Rust 2021)
===================================================================""")

def parse_nyx_toml():
    """Reads nyx.toml or he.toml in current directory if available."""
    config = {
        "name": "nyx_app",
        "version": "0.1.0",
        "target": "hecpp",
        "entry": "src/main.nyx",
        "output_type": "exe"
    }
    manifest_path = "nyx.toml" if os.path.exists("nyx.toml") else ("he.toml" if os.path.exists("he.toml") else None)
    if manifest_path:
        try:
            from src.toolchain.manifest import NyxManifest
            mf = NyxManifest.load_from_file(manifest_path)
            config["name"] = mf.package.name
            config["version"] = mf.package.version
            config["target"] = mf.package.target or mf.build.target
            config["entry"] = mf.package.entry or mf.build.entry
            config["output_type"] = mf.build.output_type
        except Exception:
            with open(manifest_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("name ="):
                        config["name"] = line.split("=")[1].strip().strip('"').strip("'")
                    elif line.startswith("version ="):
                        config["version"] = line.split("=")[1].strip().strip('"').strip("'")
                    elif line.startswith("default =") or line.startswith("target ="):
                        config["target"] = line.split("=")[1].strip().strip('"').strip("'")
                    elif line.startswith("entry ="):
                        config["entry"] = line.split("=")[1].strip().strip('"').strip("'")
                    elif line.startswith("output_type ="):
                        config["output_type"] = line.split("=")[1].strip().strip('"').strip("'")
    return config

def get_target_from_args(default_target="hecpp", entry_file=None):
    # 1. Check CLI flag
    if "--target" in sys.argv:
        idx = sys.argv.index("--target")
        if idx + 1 < len(sys.argv):
            t_raw = sys.argv[idx + 1].lower()
            t_map = {
                "cpp": "hecpp", "hecpp": "hecpp",
                "asm": "heasm", "heasm": "heasm", "assembly": "heasm",
                "py": "hepy", "python": "hepy", "hepy": "hepy",
                "js": "hejs", "node": "hejs", "hejs": "hejs",
                "rs": "hers", "rust": "hers", "hers": "hers"
            }
            return t_map.get(t_raw, t_raw)
            
    # 2. Check in-file #target directive
    if entry_file and os.path.exists(entry_file):
        try:
            with open(entry_file, "r", encoding="utf-8") as f:
                for _ in range(15):
                    line = f.readline()
                    if not line: break
                    line = line.strip()
                    if line.startswith("#target"):
                        parts = line.split()
                        if len(parts) >= 2:
                            t_raw = parts[1].strip().lower()
                            t_map = {
                                "cpp": "hecpp", "hecpp": "hecpp",
                                "asm": "heasm", "heasm": "heasm", "assembly": "heasm",
                                "py": "hepy", "python": "hepy", "hepy": "hepy",
                                "js": "hejs", "node": "hejs", "hejs": "hejs",
                                "rs": "hers", "rust": "hers", "hers": "hers"
                            }
                            return t_map.get(t_raw, t_raw)
        except Exception:
            pass

    return default_target

def get_entry_file(default_entry="src/main.nyx"):
    args = [a for a in sys.argv[2:] if not a.startswith("--") and a not in ("cpp", "hecpp", "asm", "heasm", "py", "hepy", "js", "hejs", "rs", "hers")]
    if args and (args[0].endswith(".nyx") or args[0].endswith(".he")):
        return args[0]
    if os.path.exists(default_entry):
        return default_entry
    if os.path.exists("src/lib.nyx"):
        return "src/lib.nyx"
    if os.path.exists("src/main.he"):
        return "src/main.he"
    if os.path.exists("src/main.nyx"):
        return "src/main.nyx"
    if os.path.exists("main.nyx"):
        return "main.nyx"
    if os.path.exists("main.he"):
        return "main.he"
    return None

def cmd_check(entry_file):
    if not entry_file or not os.path.exists(entry_file):
        print(f"\033[91m[!] Error: File not found '{entry_file}'\033[0m")
        sys.exit(1)
    print(f"\033[96m[*] Checking semantics & types for:\033[0m {entry_file}")
    with open(entry_file, "r", encoding="utf-8") as f:
        code = f.read()
    from src.core.module_loader import ModuleLoader
    loader = ModuleLoader(base_dir=os.path.dirname(os.path.abspath(entry_file)))
    ast = loader.load_program(entry_file, code)
    TypeChecker(ast, entry_file, code).check()
    print("\033[92m[OK] Check Passed: 0 syntax or semantic errors found.\033[0m")

def cmd_build(entry_file, target, is_release=False, output_type="exe"):
    if not entry_file or not os.path.exists(entry_file):
        print(f"\033[91m[!] Error: Source file not found '{entry_file}'.\033[0m")
        sys.exit(1)

    build_dir = os.path.join("build", target)
    os.makedirs(build_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(entry_file))[0]
    
    print(f"\033[96m[*] Building [{target}] ({output_type}):\033[0m {entry_file} -> {build_dir}")
    with open(entry_file, "r", encoding="utf-8") as f:
        code = f.read()

    from src.core.module_loader import ModuleLoader
    loader = ModuleLoader(base_dir=os.path.dirname(os.path.abspath(entry_file)))
    ast = loader.load_program(entry_file, code)
    TypeChecker(ast, entry_file, code).check()
    
    codegen = UniversalCodeGen(ast)
    
    if target == "hecpp":
        cpp_code = codegen.gen_cpp()
        out_cpp = os.path.join(build_dir, f"{base_name}.cpp")
        with open(out_cpp, "w", encoding="utf-8") as f:
            f.write(cpp_code)

        if output_type == "lib":
            out_target = os.path.join(build_dir, f"lib{base_name}.a")
            ok, msg = CppToolchain.compile_cpp(out_cpp, out_target, codegen.get_link_libraries(), output_type="lib")
            if ok:
                print(f"\033[92m[OK] Compiled Static Library:\033[0m {out_target}")
            else:
                print(f"\033[93m[!] Static library generation failed:\033[0m {msg}")
        elif output_type == "shared":
            ext = ".dll" if sys.platform == "win32" else ".so"
            out_target = os.path.join(build_dir, f"{base_name}{ext}")
            ok, msg = CppToolchain.compile_cpp(out_cpp, out_target, codegen.get_link_libraries(), output_type="shared")
            if ok:
                print(f"\033[92m[OK] Compiled Shared Library:\033[0m {out_target}")
            else:
                print(f"\033[93m[!] Shared library generation failed:\033[0m {msg}")
        else:
            out_exe = os.path.join(build_dir, f"{base_name}.exe")
            ok, msg = CppToolchain.compile_cpp(out_cpp, out_exe, codegen.get_link_libraries(), output_type="exe")
            if ok:
                print(f"\033[92m[OK] Compiled Native Executable:\033[0m {out_exe}")
            else:
                print(f"\033[93m[!] Transpiled C++ source generated at:\033[0m {out_cpp}")
                print(f"    ({msg})")
            
    elif target in ("heasm", "asm"):
        cpp_code = codegen.gen_cpp()
        temp_cpp = os.path.join(build_dir, f"{base_name}_temp.cpp")
        with open(temp_cpp, "w", encoding="utf-8") as f:
            f.write(cpp_code)
        out_s = os.path.join(build_dir, f"{base_name}.s")
        ok, msg = CppToolchain.compile_cpp(temp_cpp, out_s, codegen.get_link_libraries(), output_type="asm")
        if ok and os.path.exists(out_s):
            out_exe = os.path.join(build_dir, f"{base_name}.exe")
            CppToolchain.compile_cpp(temp_cpp, out_exe, codegen.get_link_libraries(), output_type="exe")
            print(f"\033[96m[*] Generated Assembly (Intel x86_64):\033[0m {out_s}")
            if os.path.exists(out_exe):
                print(f"\033[92m[OK] Compiled Native Binary:\033[0m {out_exe}")
            if os.path.exists(temp_cpp):
                try: os.remove(temp_cpp)
                except: pass
        else:
            print(f"\033[91m[!] Assembly generation failed:\033[0m {msg}")

    elif target == "hejs":
        js_code = codegen.gen_js()
        out_js = os.path.join(build_dir, f"{base_name}.js")
        with open(out_js, "w", encoding="utf-8") as f:
            f.write(js_code)
        print(f"\033[92m[OK] Generated Node.js ES2022 Module:\033[0m {out_js}")

    elif target == "hers":
        rs_code = codegen.gen_rust()
        out_rs = os.path.join(build_dir, f"{base_name}.rs")
        with open(out_rs, "w", encoding="utf-8") as f:
            f.write(rs_code)
        print(f"\033[92m[OK] Generated Rust 2021 Source:\033[0m {out_rs}")

    elif target == "hepy":
        py_code = codegen.gen_python()
        out_py = os.path.join(build_dir, f"{base_name}.py")
        with open(out_py, "w", encoding="utf-8") as f:
            f.write(py_code)
        print(f"\033[92m[OK] Generated Python 3 Module:\033[0m {out_py}")

    else:
        print(f"\033[91m[!] Unknown target '{target}'\033[0m")

def cmd_run(entry_file, target):
    if not entry_file or not os.path.exists(entry_file):
        print(f"\033[91m[!] Error: Source file not found '{entry_file}'.\033[0m")
        sys.exit(1)
        
    build_dir = os.path.join("build", target)
    os.makedirs(build_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(entry_file))[0]

    with open(entry_file, "r", encoding="utf-8") as f:
        code = f.read()

    from src.core.module_loader import ModuleLoader
    loader = ModuleLoader(base_dir=os.path.dirname(os.path.abspath(entry_file)))
    ast = loader.load_program(entry_file, code)
    TypeChecker(ast, entry_file, code).check()
    codegen = UniversalCodeGen(ast)

    if target in ("heasm", "asm"):
        cpp_code = codegen.gen_cpp()
        temp_cpp = os.path.join(build_dir, f"{base_name}_temp.cpp")
        with open(temp_cpp, "w", encoding="utf-8") as f:
            f.write(cpp_code)
        out_s = os.path.join(build_dir, f"{base_name}.s")
        out_exe = os.path.join(build_dir, f"{base_name}.exe")
        CppToolchain.compile_cpp(temp_cpp, out_s, codegen.get_link_libraries(), output_type="asm")
        ok, msg = CppToolchain.compile_cpp(temp_cpp, out_exe, codegen.get_link_libraries(), output_type="exe")
        if ok and os.path.exists(out_exe):
            print(f"\033[96m[*] Generated Assembly (Intel x86_64):\033[0m {out_s}")
            print(f"\033[92m[OK] Compiled Native Binary:\033[0m {out_exe}")
            print("\033[90m--------------------------------------------------\033[0m")
            ret_code, out_str = CppToolchain.run_executable(out_exe)
            if out_str:
                print(out_str.rstrip())
            print("\033[90m--------------------------------------------------\033[0m")
            if os.path.exists(temp_cpp):
                try: os.remove(temp_cpp)
                except: pass
        else:
            print(f"\033[91m[!] Assembly Execution failed:\033[0m\n{msg}")
    elif target == "hepy":
        out_py = os.path.join(build_dir, f"{base_name}.py")
        py_code = codegen.gen_python()
        with open(out_py, "w", encoding="utf-8") as f:
            f.write(py_code)
        print(f"\033[96m[*] Target [Python 3]:\033[0m {out_py}")
        print("\033[90m--------------------------------------------------\033[0m")
        subprocess.run([sys.executable, out_py])
        print("\033[90m--------------------------------------------------\033[0m")
    elif target == "hejs":
        out_js = os.path.join(build_dir, f"{base_name}.js")
        js_code = codegen.gen_js()
        with open(out_js, "w", encoding="utf-8") as f:
            f.write(js_code)
        node_path = shutil.which("node")
        if not node_path:
            print("\033[91m[!] Node.js not found on system PATH.\033[0m")
            return
        print(f"\033[96m[*] Target [Node.js ES2022]:\033[0m {out_js}")
        print("\033[90m--------------------------------------------------\033[0m")
        subprocess.run([node_path, out_js])
        print("\033[90m--------------------------------------------------\033[0m")
    elif target == "hecpp":
        out_cpp = os.path.join(build_dir, f"{base_name}.cpp")
        out_exe = os.path.join(build_dir, f"{base_name}.exe")
        with open(out_cpp, "w", encoding="utf-8") as f:
            f.write(codegen.gen_cpp())
        ok, msg = CppToolchain.compile_cpp(out_cpp, out_exe, codegen.get_link_libraries(), output_type="exe")
        if ok and os.path.exists(out_exe):
            print(f"\033[96m[*] Transpiled C++20 Source:\033[0m {out_cpp}")
            print(f"\033[92m[OK] Compiled Native Binary:\033[0m {out_exe}")
            print("\033[90m--------------------------------------------------\033[0m")
            ret_code, out_str = CppToolchain.run_executable(out_exe)
            if out_str:
                print(out_str.rstrip())
            print("\033[90m--------------------------------------------------\033[0m")
        else:
            print(f"\033[91m[!] C++ Compilation failed:\033[0m\n{msg}")
    elif target == "hers":
        out_rs = os.path.join(build_dir, f"{base_name}.rs")
        with open(out_rs, "w", encoding="utf-8") as f:
            f.write(codegen.gen_rust())
        print(f"\033[96m[*] Transpiled Rust 2021 Source:\033[0m {out_rs}")
        rustc = r"C:\Program Files\Rust stable MSVC 1.98\bin\rustc.exe"
        if not os.path.exists(rustc):
            rustc = shutil.which("rustc")
        if rustc:
            out_exe = os.path.join(build_dir, f"{base_name}.exe")
            res = subprocess.run([rustc, "--edition=2021", out_rs, "-o", out_exe], capture_output=True, text=True)
            if res.returncode == 0 and os.path.exists(out_exe):
                print(f"\033[92m[OK] Compiled Native Binary:\033[0m {out_exe}")
                print("\033[90m--------------------------------------------------\033[0m")
                subprocess.run([out_exe])
                print("\033[90m--------------------------------------------------\033[0m")
            else:
                print(res.stderr or res.stdout)

def cmd_new(project_name, is_lib=False):
    if os.path.exists(project_name):
        print(f"\033[91m[!] Error: Directory '{project_name}' already exists.\033[0m")
        return
    os.makedirs(os.path.join(project_name, "src"), exist_ok=True)
    
    if is_lib:
        os.makedirs(os.path.join(project_name, "examples"), exist_ok=True)
        manifest_content = f"""[package]
name = "{project_name}"
version = "0.1.0"
edition = "2026"
target = "hecpp"
entry = "src/lib.nyx"

[dependencies]
# std = "2.0.0"

[build]
target = "hecpp"
output_type = "lib"
entry = "src/lib.nyx"
opt_level = 2
"""
        with open(os.path.join(project_name, "nyx.toml"), "w", encoding="utf-8") as f:
            f.write(manifest_content)

        gitignore_content = """build/
target/
*.a
*.lib
*.dll
*.so
*.o
*.lock
.system_generated/
"""
        with open(os.path.join(project_name, ".gitignore"), "w", encoding="utf-8") as f:
            f.write(gitignore_content)

        lib_nyx_content = f"""// nyx native library: {project_name}
#target hecpp

fn add(a: int, b: int) -> int {{
    return a + b
}}

test "library add test" {{
    assert(add(10, 20) == 30, "add must sum correctly")
}}
"""
        with open(os.path.join(project_name, "src", "lib.nyx"), "w", encoding="utf-8") as f:
            f.write(lib_nyx_content)

        example_nyx_content = f"""// Example usage of {project_name}
#target hecpp
import "../src/lib.nyx"

var res = add(5, 7)
print("Add result:", res)
"""
        with open(os.path.join(project_name, "examples", "basic.nyx"), "w", encoding="utf-8") as f:
            f.write(example_nyx_content)

        readme_content = f"""# {project_name}

Native library for nyx.

## Building
```bash
nyx build
```

## Testing
```bash
nyx test
```
"""
        with open(os.path.join(project_name, "README.md"), "w", encoding="utf-8") as f:
            f.write(readme_content)

        print(f"\033[92m[OK] Created nyx library project in ./{project_name}\033[0m")
        print(f"     - Manifest:   ./{project_name}/nyx.toml (output_type = 'lib')")
        print(f"     - Entrypoint: ./{project_name}/src/lib.nyx")
        print(f"     - Example:    ./{project_name}/examples/basic.nyx")
        print(f"\nTo get started:\n  cd {project_name}\n  nyx build\n")
        return

    manifest_content = f"""[package]
name = "{project_name}"
version = "0.1.0"
edition = "2026"
target = "hecpp"
entry = "src/main.nyx"

[dependencies]
# std = "2.0.0"

[build]
target = "hecpp"
output_type = "exe"
opt_level = 2
"""
    with open(os.path.join(project_name, "nyx.toml"), "w", encoding="utf-8") as f:
        f.write(manifest_content)
        
    gitignore_content = """build/
target/
*.exe
*.o
*.lock
.system_generated/
"""
    with open(os.path.join(project_name, ".gitignore"), "w", encoding="utf-8") as f:
        f.write(gitignore_content)
        
    main_nyx_content = f"""#target hecpp

fn greet(name: string) -> string {{
    return "Hello, " + name + " from nyx!"
}}

var message = greet("{project_name}")
print(message)

test "greeting test" {{
    assert(greet("User") == "Hello, User from nyx!", "Greeting must match")
}}
"""
    with open(os.path.join(project_name, "src", "main.nyx"), "w", encoding="utf-8") as f:
        f.write(main_nyx_content)
        
    vscode_dir = os.path.join(project_name, ".vscode")
    os.makedirs(vscode_dir, exist_ok=True)
    tasks_json_content = """{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "nyx: Build Active File",
      "type": "shell",
      "command": "nyx",
      "args": ["build", "${file}"],
      "group": {
        "kind": "build",
        "isDefault": true
      },
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      }
    },
    {
      "label": "nyx: Run Active File",
      "type": "shell",
      "command": "nyx",
      "args": ["run", "${file}"],
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": true,
        "panel": "shared"
      }
    },
    {
      "label": "nyx: Run Full Test Suite",
      "type": "shell",
      "command": "nyx",
      "args": ["test"],
      "group": {
        "kind": "test",
        "isDefault": true
      },
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      }
    }
  ]
}
"""
    with open(os.path.join(vscode_dir, "tasks.json"), "w", encoding="utf-8") as f:
        f.write(tasks_json_content)

    c_cpp_props = """{
  "configurations": [
    {
      "name": "nyx-MinGW",
      "includePath": ["${workspaceFolder}/**"],
      "defines": ["_DEBUG", "UNICODE", "_UNICODE"],
      "compilerPath": "C:/Users/USER/AppData/Local/Microsoft/WinGet/Packages/MartinStorsjo.LLVM-MinGW.UCRT_Microsoft.Winget.Source_8wekyb3d8bbwe/llvm-mingw-20260616-ucrt-x86_64/bin/clang++.exe",
      "cStandard": "c17",
      "cppStandard": "c++20",
      "intelliSenseMode": "windows-clang-x64"
    }
  ],
  "version": 4
}
"""
    with open(os.path.join(vscode_dir, "c_cpp_properties.json"), "w", encoding="utf-8") as f:
        f.write(c_cpp_props)

    print(f"\033[92m[OK] Created nyx project in ./{project_name}\033[0m")
    print(f"     - Manifest:   ./{project_name}/nyx.toml")
    print(f"     - Entrypoint: ./{project_name}/src/main.nyx")
    print(f"     - VS Code:    ./{project_name}/.vscode/ (tasks.json & IntelliSense ready)")
    print(f"\nTo get started:\n  cd {project_name}\n  nyx run\n")

def cmd_clean():
    cleaned = 0
    for target in ("build", "target", "__pycache__"):
        if os.path.exists(target):
            shutil.rmtree(target, ignore_errors=True)
            cleaned += 1
    print(f"\033[92m[OK] Cleaned {cleaned} build artifact directory/directories.\033[0m")

def cmd_doctor():
    print_banner()
    print("Environment & Toolchain Diagnostics:")
    
    # 1. Python runtime
    print(f"\n  [1] Core Python Runtime (hepy Reference):")
    print(f"      • Status:    \033[92m[OK] Available\033[0m")
    print(f"      • Path:      {sys.executable}")
    print(f"      • Version:   Python {sys.version.split()[0]}")

    # 2. C++ Compiler (hecpp Native)
    print(f"\n  [2] C++20 Compiler (hecpp Native Executables):")
    clang = CppToolchain.find_compiler()
    if clang:
        print(f"      • Status:    \033[92m[OK] Available\033[0m")
        print(f"      • Compiler:  {clang}")
        print(f"      • Capability: Native .exe compilation supported")
    else:
        print(f"      • Status:    \033[93m[!] NOT FOUND (Transpile Mode Only)\033[0m")
        print(f"      • Note:      To compile native .exe binaries, install LLVM Clang or MinGW-w64:")
        print(f"                   - Windows: winget install LLVM.LLVM")
        print(f"                   - Ubuntu/Debian: sudo apt install clang")
        print(f"                   - macOS: brew install llvm")

    # 3. Node.js (hejs Target)
    print(f"\n  [3] JavaScript Runtime (hejs Target):")
    node = shutil.which("node")
    if node:
        print(f"      • Status:    \033[92m[OK] Available\033[0m")
        print(f"      • Node Path: {node}")
    else:
        print(f"      • Status:    \033[93m[!] NOT FOUND\033[0m")
        print(f"      • Note:      Install Node.js to execute ES2022 output: winget install OpenJS.NodeJS")

    # 4. Rust Compiler (hers Target)
    print(f"\n  [4] Rust Toolchain (hers Conformance Target):")
    rustc = r"C:\Program Files\Rust stable MSVC 1.98\bin\rustc.exe"
    if not os.path.exists(rustc):
        rustc = shutil.which("rustc")
    if rustc:
        print(f"      • Status:    \033[92m[OK] Gate 6 Conformance\033[0m")
        print(f"      • Path:      {rustc}")
    else:
        print(f"      • Status:    \033[93m[!] NOT FOUND\033[0m")
        print(f"      • Note:      Install Rust: https://rustup.rs")

    print("\n===================================================================")

def cmd_version():
    print_banner()
    print("Detected Host Toolchains & Execution Engines:")
    clang = CppToolchain.find_compiler()
    print(f"  • C++20 Toolchain:      {clang or 'Not Found (Using Transpile Mode)'}")
    node = shutil.which("node")
    print(f"  • JavaScript Engine:    {node or 'Not Found'}")
    rustc = r"C:\Program Files\Rust stable MSVC 1.98\bin\rustc.exe"
    if not os.path.exists(rustc):
        rustc = shutil.which("rustc")
    print(f"  • Rust Compiler:        {rustc or 'Not Found'}")
    print(f"  • Python Reference:     {sys.executable} (v{sys.version.split()[0]})")
    print("===================================================================")

def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)

    cmd = sys.argv[1].lower()
    config = parse_nyx_toml()

    if cmd in ("--help", "-h", "help"):
        print_help()
    elif cmd in ("--version", "-v", "version"):
        cmd_version()
    elif cmd == "doctor":
        cmd_doctor()
    elif cmd == "new":
        raw_args = [a for a in sys.argv[2:] if not a.startswith("--")]
        name = raw_args[0] if raw_args else "nyx_project"
        is_lib = "--lib" in sys.argv
        cmd_new(name, is_lib=is_lib)
    elif cmd == "init":
        PackageManager.init(sys.argv[2] if len(sys.argv) > 2 else config.get("name", "nyx_project"))
    elif cmd == "check":
        entry = get_entry_file(config.get("entry", "src/main.nyx"))
        cmd_check(entry)
    elif cmd == "build":
        entry = get_entry_file(config.get("entry", "src/main.nyx"))
        target = get_target_from_args(config.get("target", "hecpp"), entry_file=entry)
        is_release = "--release" in sys.argv
        output_type = config.get("output_type", "exe")
        cmd_build(entry, target, is_release, output_type=output_type)
    elif cmd == "run":
        entry = get_entry_file(config.get("entry", "src/main.nyx"))
        target = get_target_from_args(config.get("target", "hecpp"), entry_file=entry)
        cmd_run(entry, target)
    elif cmd == "test":
        if len(sys.argv) > 2 and (sys.argv[2].endswith(".nyx") or sys.argv[2].endswith(".he")):
            target_file = sys.argv[2]
            if not os.path.exists(target_file):
                print(f"\033[91m[!] Error: Test file '{target_file}' not found.\033[0m")
                sys.exit(1)
            print(f"\033[96m[*] Running nyx In-File Unit Tests in '{target_file}'...\033[0m")
            cmd_run(target_file, "hepy")
            print("\033[92m[OK] Execution finished successfully.\033[0m")
        elif os.path.exists("src/lib.nyx"):
            print("\033[96m[*] Running nyx In-File Unit Tests in 'src/lib.nyx'...\033[0m")
            cmd_run("src/lib.nyx", "hepy")
            print("\033[92m[OK] Execution finished successfully.\033[0m")
        elif os.path.exists("src/main.nyx"):
            print("\033[96m[*] Running nyx In-File Unit Tests in 'src/main.nyx'...\033[0m")
            cmd_run("src/main.nyx", "hepy")
            print("\033[92m[OK] Execution finished successfully.\033[0m")
        else:
            test_suite = os.path.join(os.path.dirname(__file__), "..", "tests", "run_all_tests.py")
            if not os.path.exists(test_suite):
                test_suite = os.path.join(os.getcwd(), "tests", "run_all_tests.py")
            subprocess.run([sys.executable, test_suite])
    elif cmd == "clean":
        cmd_clean()
    elif cmd == "fmt":
        if len(sys.argv) < 3: print("Usage: nyx fmt <file.nyx>"); sys.exit(1)
        Formatter.format_file(sys.argv[2])
    elif cmd == "lint":
        if len(sys.argv) < 3: print("Usage: nyx lint <file.nyx>"); sys.exit(1)
        Linter.lint_file(sys.argv[2])
    elif cmd == "lsp":
        from src.toolchain.lsp_server import LanguageServer
        LanguageServer().run()
    elif cmd == "debug":
        if len(sys.argv) < 3: print("Usage: nyx debug <file.nyx>"); sys.exit(1)
        Debugger(sys.argv[2]).start()
    elif cmd == "profile":
        if len(sys.argv) < 3: print("Usage: nyx profile <file.nyx>"); sys.exit(1)
        Profiler.profile_file(sys.argv[2])
    elif cmd == "doc":
        if len(sys.argv) < 3: print("Usage: nyx doc <file.nyx>"); sys.exit(1)
        DocGenerator.generate_docs(sys.argv[2])
    elif cmd == "add":
        if len(sys.argv) < 3: print("Usage: nyx add <package_name>"); sys.exit(1)
        PackageManager.add(sys.argv[2])
    elif cmd == "remove":
        if len(sys.argv) < 3: print("Usage: nyx remove <package_name>"); sys.exit(1)
        PackageManager.remove(sys.argv[2])
    elif cmd == "install":
        PackageManager.install()
    elif cmd == "pkg":
        PackageManager.list_installed()
    else:
        print(f"\033[91m[!] Unknown command: '{cmd}'. Run 'nyx help' for available commands.\033[0m")
        sys.exit(1)

if __name__ == "__main__":
    main()
