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
import json
from typing import Optional

_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

from src.core import Lexer, Parser, TypeChecker
from src.core.target_model import resolve_target, TARGET_REGISTRY
from src.core.board_model import (
    BOARD_REGISTRY,
    BoardProfileError,
    board_manifest,
    resolve_board,
    write_board_template,
)
from src.core.backend_capabilities import (
    BACKENDS,
    capability_manifest,
    normalize_backend_name,
    resolve_backend,
)
from src.core.embedded_builder import EmbeddedBuilder
from src.core.firmware_flasher import FirmwareFlashError, FirmwareFlasher
from src.core.stm32cube_provider import cube_board_report, install_cube_package
from src.codegen import UniversalCodeGen
from src.codegen.cpp_toolchain import CppToolchain
from src.toolchain import (
    Formatter, Linter, Debugger, Profiler,
    DocGenerator, PackageManager, StandalonePackager
)
from src.version import VERSION

def print_banner():
    print("===================================================================")
    print(f"nyx core v{VERSION} — systems toolchain")
    print("===================================================================")

def print_help():
    print_banner()
    print("""Usage: nyx <command> [arguments] [options]

Project & Development Commands:
  nyx new <project_name>             Create a new nyx project in a directory
  nyx init [name]                    Initialize a nyx.toml project in current directory
  nyx check [file.nyx] [--board b]   Fast type-check and semantic validation
  nyx build [file.nyx] [--target t]  Build executable or transpile project into build/
  nyx bundle [file.nyx] [-o dir]     Bundle Polyglot Web/WASM package (.wasm, .mjs, .d.ts, .tsx)
  nyx self-host verify               Verify the native stage-1 -> stage-2 bootstrap
  nyx self-host compile <file.nyx>   Emit C++ through the stage-1 compiler
  nyx self-host build                Build the standalone native nyxc frontend
  nyx targets [--json]               Inspect backend and stdlib capability contracts
  nyx boards [--json]                List Nucleo/custom-board support profiles
  nyx boards --init [board.toml]      Create a custom circuit/board profile template
  nyx boards --probe [--cube-root p]  Inspect installed STM32Cube/CMSIS packages
  nyx boards --install F1             Install official CMSIS/Nucleo assets sparsely
  nyx flash <firmware> --board NAME  Program an STM32 through on-board ST-LINK
  nyx run [file.nyx] [--target t]    Compile and run project / file immediately
  nyx test [file.nyx | all]          Execute in-file unit tests or test framework
  nyx clean                          Remove build artifacts and temporary files

Toolchain & Quality:
  nyx fmt <file.nyx>                 Auto-format and beautify source code
  nyx lint <file.nyx>                Static analysis and unsafe boundary checks
  nyx lsp                            Launch Language Server Protocol (LSP) daemon
  nyx debug <file.nyx>               Interactive validated source-line inspector
  nyx profile <file.nyx>             Measure real compile + run wall-clock time
  nyx doc <file.nyx>                 Generate HTML API documentation from /// comments

Package Management:
  nyx add <pkg> [@version]           Add a dependency into nyx.toml and lock in nyx.lock
  nyx remove <pkg>                   Remove a dependency from nyx.toml and nyx.lock
  nyx install                        Validate dependencies and regenerate nyx.lock
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
        "board": "",
        "entry": "src/main.nyx",
        "output_type": "exe"
    }
    manifest_path = "nyx.toml" if os.path.exists("nyx.toml") else ("he.toml" if os.path.exists("he.toml") else None)
    if manifest_path:
        try:
            from src.toolchain.manifest import NyxManifest
            mf = NyxManifest(manifest_path)
            config["name"] = mf.package.get("name", config["name"])
            config["version"] = mf.package.get("version", config["version"])
            config["target"] = mf.package.get("target") or mf.build.get("target") or config["target"]
            config["board"] = mf.build.get("board", config["board"])
            config["entry"] = mf.package.get("entry") or mf.build.get("entry") or config["entry"]
            config["output_type"] = mf.build.get("output_type", config["output_type"])
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
                    elif line.startswith("board ="):
                        config["board"] = line.split("=")[1].strip().strip('"').strip("'")
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
            return normalize_backend_name(sys.argv[idx + 1])
            
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
                            return normalize_backend_name(parts[1])
        except Exception:
            pass

    return normalize_backend_name(default_target)

def get_entry_file(default_entry="src/main.nyx"):
    args = [a for a in sys.argv[2:] if not a.startswith("--") and a not in ("cpp", "hecpp", "asm", "heasm", "wasm", "hewasm", "py", "hepy", "js", "hejs", "rs", "hers", "react")]
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


def parse_package_spec(arguments):
    if not arguments:
        raise ValueError("missing package name")
    if len(arguments) > 2:
        raise ValueError("too many package arguments")
    package_name = arguments[0]
    version = "1.0.0"
    if len(arguments) == 2:
        version = arguments[1][1:] if arguments[1].startswith("@") else arguments[1]
    elif "@" in package_name and not package_name.startswith("@"):
        package_name, version = package_name.rsplit("@", 1)
    if not package_name or not version:
        raise ValueError("package name and version must be non-empty")
    return package_name, version


def get_option_value(*names, default=None):
    for index, argument in enumerate(sys.argv):
        if argument in names and index + 1 < len(sys.argv):
            return sys.argv[index + 1]
    return default

def cmd_check(entry_file, target=None, board_name="", cube_root="") -> int:
    if not entry_file or not os.path.exists(entry_file):
        print(f"\033[91m[!] Error: File not found '{entry_file}'\033[0m")
        return 1
    board = None
    if board_name:
        try:
            board = resolve_board(board_name, cube_root=cube_root or None)
        except BoardProfileError as exc:
            print(f"\033[91m[!] Invalid board profile:\033[0m {exc}")
            return 1
        if board is None:
            print(f"\033[91m[!] Unknown board '{board_name}'. Run 'nyx boards'.\033[0m")
            return 1
        target = board.compiler_target
    print(f"\033[96m[*] Checking semantics & types for:\033[0m {entry_file}")
    from src.api import NyxCompiler
    result = NyxCompiler(
        os.path.dirname(os.path.abspath(entry_file)),
        board=board,
    ).check_file(entry_file, target=target)
    if not result.success:
        for diagnostic in result.diagnostics:
            print(diagnostic.rendered)
        return 1
    print("\033[92m[OK] Check Passed: 0 syntax or semantic errors found.\033[0m")
    return 0

def cmd_build(entry_file, target, is_release=False, output_type="exe", board_name="", cube_root="") -> int:
    if not entry_file or not os.path.exists(entry_file):
        print(f"\033[91m[!] Error: Source file not found '{entry_file}'.\033[0m")
        return 1

    board = None
    if board_name:
        try:
            board = resolve_board(board_name, cube_root=cube_root or None)
        except BoardProfileError as exc:
            print(f"\033[91m[!] Invalid board profile:\033[0m {exc}")
            return 1
        if board is None:
            print(f"\033[91m[!] Unknown board '{board_name}'. Run 'nyx boards'.\033[0m")
            return 1
        target = board.compiler_target

    backend = resolve_backend(target)
    if backend is None:
        print(f"\033[91m[!] Unknown target '{target}'. Run 'nyx targets'.\033[0m")
        return 1
    target = backend.name

    build_dir = os.path.join("build", board.name if board else target)
    os.makedirs(build_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(entry_file))[0]
    
    print(f"\033[96m[*] Building [{target}] ({output_type}):\033[0m {entry_file} -> {build_dir}")
    with open(entry_file, "r", encoding="utf-8") as f:
        code = f.read()

    from src.core.module_loader import ModuleLoader
    loader = ModuleLoader(
        base_dir=os.path.dirname(os.path.abspath(entry_file)),
        target=target,
        board=board,
    )
    ast = loader.load_program(entry_file, code)
    if target:
        ast.target = target
    TypeChecker(ast, entry_file, code).check()
    
    codegen = UniversalCodeGen(ast)
    
    target_spec = resolve_target(target)
    if target_spec and target_spec.is_freestanding:
        cpp_code = codegen.gen_cpp()
        target_build_dir = os.path.join("build", board.name if board else target_spec.name)
        os.makedirs(target_build_dir, exist_ok=True)
        out_cpp = os.path.join(target_build_dir, f"{base_name}.cpp")
        with open(out_cpp, "w", encoding="utf-8") as f:
            f.write(cpp_code)
        print(f"\033[96m[*] Transpiled Freestanding C++20:\033[0m {out_cpp}")
        
        builder = EmbeddedBuilder(target_spec, os.getcwd(), board=board)
        res = builder.build_firmware(out_cpp, base_name)
        if res.get("success"):
            architecture = f"{board.display_name} / {board.mcu}" if board else target_spec.description
            print(f"\033[92m[OK] Target Architecture:\033[0m {architecture}")
            if res.get("elf"): print(f"\033[92m[OK] Linked Embedded ELF Binary:\033[0m {res['elf']}")
            if res.get("hex"): print(f"\033[92m[OK] Generated Intel HEX Firmware:\033[0m {res['hex']}")
            if res.get("bin"): print(f"\033[92m[OK] Generated Raw BIN Firmware:\033[0m {res['bin']}")
            if res.get("size"):
                print(f"\n--- Flash / RAM Memory Footprint ---\n{res['size']}\n")
            for warning in res.get("warnings", []):
                print(f"\033[93m[!] Artifact conversion warning:\033[0m {warning}")
            return 0
        else:
            print(f"\033[93m[!] Embedded Cross-Build Diagnostic:\033[0m\n{res.get('error')}\n")
            return 1

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
                return 0
            else:
                print(f"\033[93m[!] Static library generation failed:\033[0m {msg}")
                return 1
        elif output_type == "shared":
            ext = ".dll" if sys.platform == "win32" else ".so"
            out_target = os.path.join(build_dir, f"{base_name}{ext}")
            ok, msg = CppToolchain.compile_cpp(out_cpp, out_target, codegen.get_link_libraries(), output_type="shared")
            if ok:
                print(f"\033[92m[OK] Compiled Shared Library:\033[0m {out_target}")
                return 0
            else:
                print(f"\033[93m[!] Shared library generation failed:\033[0m {msg}")
                return 1
        else:
            out_exe = os.path.join(build_dir, f"{base_name}.exe")
            ok, msg = CppToolchain.compile_cpp(out_cpp, out_exe, codegen.get_link_libraries(), output_type="exe")
            if ok:
                print(f"\033[92m[OK] Compiled Native Executable:\033[0m {out_exe}")
                print(
                    "\033[96m[>] Run in a persistent terminal:\033[0m "
                    f'nyx run "{entry_file}" --target hecpp'
                )
                print("\033[90m    (A console EXE closes normally as soon as main finishes.)\033[0m")
                return 0
            else:
                print(f"\033[93m[!] Transpiled C++ source generated at:\033[0m {out_cpp}")
                print(f"    ({msg})")
                return 1
            
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
                print(
                    "\033[96m[>] Run in a persistent terminal:\033[0m "
                    f'nyx run "{entry_file}" --target heasm'
                )
            if os.path.exists(temp_cpp):
                try: os.remove(temp_cpp)
                except: pass
            return 0
        else:
            print(f"\033[91m[!] Assembly generation failed:\033[0m {msg}")
            return 1

    elif target == "hejs":
        js_code = codegen.gen_js()
        out_js = os.path.join(build_dir, f"{base_name}.js")
        with open(out_js, "w", encoding="utf-8") as f:
            f.write(js_code)
        print(f"\033[92m[OK] Generated Node.js ES2022 Module:\033[0m {out_js}")
        return 0

    elif target == "hers":
        rs_code = codegen.gen_rust()
        out_rs = os.path.join(build_dir, f"{base_name}.rs")
        with open(out_rs, "w", encoding="utf-8") as f:
            f.write(rs_code)
        print(f"\033[92m[OK] Generated Rust 2021 Source:\033[0m {out_rs}")
        return 0

    elif target == "hepy":
        py_code = codegen.gen_python()
        out_py = os.path.join(build_dir, f"{base_name}.py")
        with open(out_py, "w", encoding="utf-8") as f:
            f.write(py_code)
        print(f"\033[92m[OK] Generated Python 3 Module:\033[0m {out_py}")
        return 0

    elif target in ("hereact", "react"):
        react_code = codegen.gen_react()
        out_tsx = os.path.join(build_dir, f"{base_name}.tsx")
        with open(out_tsx, "w", encoding="utf-8") as f:
            f.write(react_code)
        print(f"\033[92m[OK] Generated React 19 TSX Component:\033[0m {out_tsx}")
        return 0

    elif target in ("hewasm", "wasm"):
        wasm_code = codegen.gen_wasm()
        out_wat = os.path.join(build_dir, f"{base_name}.wat")
        with open(out_wat, "w", encoding="utf-8") as f:
            f.write(wasm_code)
        print(f"\033[92m[OK] Generated WebAssembly Module:\033[0m {out_wat}")
        return 0

    else:
        print(f"\033[91m[!] Unknown target '{target}'\033[0m")
        return 1

def cmd_run(entry_file, target) -> int:
    if not entry_file or not os.path.exists(entry_file):
        print(f"\033[91m[!] Error: Source file not found '{entry_file}'.\033[0m")
        return 1

    backend = resolve_backend(target)
    if backend is None:
        print(f"\033[91m[!] Unknown target '{target}'. Run 'nyx targets'.\033[0m")
        return 1
    if backend.family == "embedded":
        print(f"\033[91m[!] Target '{backend.name}' is freestanding and cannot run on the host. Use 'nyx build'.\033[0m")
        return 1
    target = backend.name

    build_dir = os.path.join("build", target)
    os.makedirs(build_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(entry_file))[0]

    with open(entry_file, "r", encoding="utf-8") as f:
        code = f.read()

    from src.core.module_loader import ModuleLoader
    loader = ModuleLoader(base_dir=os.path.dirname(os.path.abspath(entry_file)), target=target)
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
            return ret_code
        else:
            print(f"\033[91m[!] Assembly Execution failed:\033[0m\n{msg}")
            return 1
    elif target == "hepy":
        out_py = os.path.join(build_dir, f"{base_name}.py")
        py_code = codegen.gen_python()
        with open(out_py, "w", encoding="utf-8") as f:
            f.write(py_code)
        print(f"\033[96m[*] Target [Python 3]:\033[0m {out_py}")
        print("\033[90m--------------------------------------------------\033[0m")
        result = subprocess.run([sys.executable, out_py])
        print("\033[90m--------------------------------------------------\033[0m")
        return result.returncode
    elif target == "hejs":
        out_js = os.path.join(build_dir, f"{base_name}.js")
        js_code = codegen.gen_js()
        with open(out_js, "w", encoding="utf-8") as f:
            f.write(js_code)
        node_path = shutil.which("node")
        if not node_path:
            print("\033[91m[!] Node.js not found on system PATH.\033[0m")
            return 1
        print(f"\033[96m[*] Target [Node.js ES2022]:\033[0m {out_js}")
        print("\033[90m--------------------------------------------------\033[0m")
        result = subprocess.run([node_path, out_js])
        print("\033[90m--------------------------------------------------\033[0m")
        return result.returncode
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
            return ret_code
        else:
            print(f"\033[91m[!] C++ Compilation failed:\033[0m\n{msg}")
            return 1
    elif target == "hers":
        out_rs = os.path.join(build_dir, f"{base_name}.rs")
        with open(out_rs, "w", encoding="utf-8") as f:
            f.write(codegen.gen_rust())
        print(f"\033[96m[*] Transpiled Rust 2021 Source:\033[0m {out_rs}")
        rustc = shutil.which("rustc")
        if rustc:
            out_exe = os.path.join(build_dir, f"{base_name}.exe")
            res = subprocess.run([rustc, "--edition=2021", out_rs, "-o", out_exe], capture_output=True, text=True)
            if res.returncode == 0 and os.path.exists(out_exe):
                print(f"\033[92m[OK] Compiled Native Binary:\033[0m {out_exe}")
                run_res = subprocess.run([out_exe])
                return run_res.returncode
            print(f"\033[91m[!] Rust compilation failed:\033[0m\n{res.stderr or res.stdout}")
            return res.returncode or 1
        print("\033[91m[!] Rust compiler not found on system PATH.\033[0m")
        return 1
    elif target in ("hereact", "react"):
        out_tsx = os.path.join(build_dir, f"{base_name}.tsx")
        react_code = codegen.gen_react()
        with open(out_tsx, "w", encoding="utf-8") as f:
            f.write(react_code)
        print(f"\033[96m[*] Target [React 19 TSX]:\033[0m {out_tsx}")
        print("\033[90m--------------------------------------------------\033[0m")
        print(react_code)
        print("\033[90m--------------------------------------------------\033[0m")
        print("\033[92m[OK] React component generated successfully.\033[0m")
        return 0
    elif target in ("hewasm", "wasm"):
        out_wat = os.path.join(build_dir, f"{base_name}.wat")
        wasm_code = codegen.gen_wasm()
        with open(out_wat, "w", encoding="utf-8") as f:
            f.write(wasm_code)
        print(f"\033[96m[*] Target [WebAssembly WAT]:\033[0m {out_wat}")
        print("\033[90m--------------------------------------------------\033[0m")
        print(wasm_code)
        print("\033[90m--------------------------------------------------\033[0m")
        print("\033[92m[OK] WebAssembly module generated successfully.\033[0m")
        return 0
    else:
        print(f"\033[91m[!] Unknown target '{target}'.\033[0m")
        return 1

def cmd_bundle(entry_file: str, out_dir: Optional[str] = None, emit_react: bool = False) -> int:
    if not os.path.exists(entry_file):
        print(f"\033[91m[!] Error: File '{entry_file}' not found.\033[0m")
        return 1

    base_name = os.path.splitext(os.path.basename(entry_file))[0]
    bundle_dir = out_dir or os.path.join(os.getcwd(), "dist", base_name)

    with open(entry_file, "r", encoding="utf-8") as f:
        code = f.read()

    from src.core.module_loader import ModuleLoader
    from src.codegen.bundle_emitter import BundleEmitter
    loader = ModuleLoader(base_dir=os.path.dirname(os.path.abspath(entry_file)), target="hewasm")
    ast = loader.load_program(entry_file, code)
    TypeChecker(ast, entry_file, code).check()

    emitter = BundleEmitter(ast, module_name=base_name, source_name=entry_file)

    # Lower and render every artifact before touching the output directory.
    # Unsupported constructs therefore fail without leaving a partial bundle.
    try:
        wat_code = emitter.emit_wat()
        wasm_bytes = emitter.emit_wasm_bytes()
        mjs_code = emitter.emit_mjs()
        dts_code = emitter.emit_dts()
        react_code = emitter.emit_react() if emit_react else None
    except Exception as exc:
        from src.codegen.wasm_ir import BundleCompileError
        if isinstance(exc, BundleCompileError):
            print(f"\033[91m[!] Bundle compilation failed: {exc}\033[0m")
            return 1
        raise

    os.makedirs(bundle_dir, exist_ok=True)

    # 1. Emit WebAssembly Text (.wat)
    wat_path = os.path.join(bundle_dir, f"{base_name}.wat")
    with open(wat_path, "w", encoding="utf-8") as f:
        f.write(wat_code)

    # 2. Emit WebAssembly Binary (.wasm)
    wasm_path = os.path.join(bundle_dir, f"{base_name}.wasm")
    with open(wasm_path, "wb") as f:
        f.write(wasm_bytes)

    # 3. Emit ES Module Wrapper (.mjs)
    mjs_path = os.path.join(bundle_dir, f"{base_name}.mjs")
    with open(mjs_path, "w", encoding="utf-8") as f:
        f.write(mjs_code)

    # 4. Emit TypeScript Type Declarations (.d.ts)
    dts_path = os.path.join(bundle_dir, f"{base_name}.d.ts")
    with open(dts_path, "w", encoding="utf-8") as f:
        f.write(dts_code)

    print(f"\033[96m[*] Bundling Polyglot Web/WASM Package:\033[0m {entry_file} -> {bundle_dir}")
    print(f"\033[92m  [+] WebAssembly Text:     {wat_path}\033[0m")
    print(f"\033[92m  [+] WebAssembly Binary:   {wasm_path}\033[0m")
    print(f"\033[92m  [+] ES Module Runtime:     {mjs_path}\033[0m")
    print(f"\033[92m  [+] TypeScript Types:      {dts_path}\033[0m")

    # 5. Conditionally Emit React 19 Custom Hook (.react.tsx)
    if emit_react:
        react_path = os.path.join(bundle_dir, f"{base_name}.react.tsx")
        with open(react_path, "w", encoding="utf-8") as f:
            f.write(react_code or "")
        print(f"\033[92m  [+] React 19 useNyxModule: {react_path}\033[0m")

    return 0

def cmd_self_host(args) -> int:
    from src.self_host.bootstrap import (
        SelfHostError,
        build_native_compiler,
        compile_source,
        verify,
    )

    try:
        action = args[0].lower() if args else "verify"
        if action == "verify":
            verify()
            print("\033[92m[OK] Nyx native stage-1 -> stage-2 bootstrap verified.\033[0m")
            return 0
        if action == "compile":
            if len(args) < 2:
                print("\033[91m[!] Usage: nyx self-host compile <file.nyx> [-o output.cpp]\033[0m")
                return 1
            source_path = args[1]
            output_path = None
            for index, value in enumerate(args):
                if value in ("-o", "--output") and index + 1 < len(args):
                    output_path = args[index + 1]
            if not output_path:
                output_path = os.path.join("build", "self_host", os.path.splitext(os.path.basename(source_path))[0] + ".cpp")
            compile_source(source_path, output_path)
            print(f"\033[92m[OK] Stage-1 self-host C++ emitted:\033[0m {output_path}")
            return 0
        if action == "build":
            output_path = None
            for index, value in enumerate(args):
                if value in ("-o", "--output") and index + 1 < len(args):
                    output_path = args[index + 1]
            if not output_path:
                executable_name = "nyxc.exe" if os.name == "nt" else "nyxc"
                output_path = os.path.join("build", "self_host", executable_name)
            build_native_compiler(output_path)
            print(f"\033[92m[OK] Standalone native Nyx frontend built:\033[0m {output_path}")
            return 0
        print(f"\033[91m[!] Unknown self-host action '{action}'. Use verify, compile, or build.\033[0m")
        return 1
    except SelfHostError as exc:
        print(f"\033[91m[!] Self-host failed: {exc}\033[0m")
        return 1

def cmd_new(project_name, is_lib=False):
    if os.path.exists(project_name):
        print(f"\033[91m[!] Error: Directory '{project_name}' already exists.\033[0m")
        return 1
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
        return 0

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

    cpp_configuration = {
        "name": "nyx",
        "includePath": ["${workspaceFolder}/**"],
        "defines": ["_DEBUG", "UNICODE", "_UNICODE"],
        "cStandard": "c17",
        "cppStandard": "c++20",
    }
    compiler_path = CppToolchain.find_compiler()
    if compiler_path:
        cpp_configuration["compilerPath"] = compiler_path
    c_cpp_props = json.dumps(
        {"configurations": [cpp_configuration], "version": 4},
        indent=2,
    ) + "\n"
    with open(os.path.join(vscode_dir, "c_cpp_properties.json"), "w", encoding="utf-8") as f:
        f.write(c_cpp_props)

    print(f"\033[92m[OK] Created nyx project in ./{project_name}\033[0m")
    print(f"     - Manifest:   ./{project_name}/nyx.toml")
    print(f"     - Entrypoint: ./{project_name}/src/main.nyx")
    print(f"     - VS Code:    ./{project_name}/.vscode/ (tasks.json & IntelliSense ready)")
    print(f"\nTo get started:\n  cd {project_name}\n  nyx run\n")
    return 0

def cmd_clean():
    cleaned = 0
    for target in ("build", "target", "__pycache__"):
        if os.path.exists(target):
            shutil.rmtree(target, ignore_errors=True)
            cleaned += 1
    print(f"\033[92m[OK] Cleaned {cleaned} build artifact directory/directories.\033[0m")
    return 0

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
        print("      • Requirement: hecpp needs Clang++, GCC/G++, or MSVC cl (C++20).")
        print("      • Configure:   Put the compiler on PATH or set NYX_CXX to its executable.")
        print(f"                     - Windows: winget install LLVM.LLVM")
        print(f"                     - Ubuntu/Debian: sudo apt install clang")
        print(f"                     - macOS: xcode-select --install (or brew install llvm)")

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
    rustc = shutil.which("rustc")
    print(f"  • Rust Compiler:        {rustc or 'Not Found'}")
    print(f"  • Python Reference:     {sys.executable} (v{sys.version.split()[0]})")
    print("===================================================================")

def cmd_targets(as_json: bool = False) -> int:
    manifest = capability_manifest()
    if as_json:
        print(json.dumps(manifest, ensure_ascii=False, sort_keys=True))
        return 0

    print_banner()
    print(f"Backend Capability Contract v{manifest['schema_version']}:")
    for name in sorted(BACKENDS):
        backend = BACKENDS[name]
        modules = backend.to_dict()["stdlib_modules"]
        aliases = ", ".join(backend.aliases) if backend.aliases else "-"
        module_text = ", ".join(modules) if modules else "none"
        print(f"\n  {backend.name:<11} {backend.display_name} [{backend.maturity}]")
        print(f"      family={backend.family} artifact={backend.artifact} aliases={aliases}")
        print(f"      stdlib={module_text}")
    print("\nUse 'nyx targets --json' for the machine-readable contract.")
    print("===================================================================")
    return 0


def cmd_boards(
    as_json: bool = False,
    init_path: str = "",
    cube_root: str = "",
    probe: bool = False,
    install_family: str = "",
    install_root: str = "",
    dry_run: bool = False,
) -> int:
    if init_path:
        try:
            write_board_template(init_path)
        except (BoardProfileError, OSError) as exc:
            print(f"\033[91m[!] Could not create board profile:\033[0m {exc}")
            return 1
        print(f"\033[92m[OK] Custom board template created:\033[0m {os.path.abspath(init_path)}")
        return 0
    if install_family:
        destination_root = install_root or os.path.join(os.getcwd(), ".toolchains", "stm32cube")
        try:
            result = install_cube_package(
                install_family,
                destination_root,
                dry_run=dry_run,
            )
        except BoardProfileError as exc:
            print(f"\033[91m[!] STM32Cube installation failed:\033[0m {exc}")
            return 1
        if dry_run:
            print("================== STM32CUBE INSTALL DRY RUN =====================")
            for command in result["commands"]:
                print(f"  {subprocess.list2cmdline(command)}")
            print("===================================================================")
            return 0
        state = "already installed" if result["already_present"] else "installed"
        print(f"\033[92m[OK] STM32Cube{result['family']} {state}:\033[0m {result['destination']}")
        print(f"     Build with --cube-root {os.path.abspath(destination_root)}")
        return 0
    if probe:
        reports = [
            cube_board_report(board, cube_root or None)
            for board in BOARD_REGISTRY.values()
            if board.support == "cmsis-pack"
        ]
        if as_json:
            print(json.dumps({"schema_version": 1, "providers": reports}, ensure_ascii=False, sort_keys=True))
            return 0
        print("=================== NYX STM32CUBE PROVIDER PROBE ==================")
        for report in reports:
            state = "READY" if report["build_ready"] else "MISSING"
            detail = report.get("package_root") or report.get("error", "")
            print(f"  {report['board']:<20} [{state}] {detail}")
        print("===================================================================")
        return 0
    if as_json:
        print(json.dumps(board_manifest(), ensure_ascii=False, sort_keys=True))
        return 0
    print("======================= NYX EMBEDDED BOARDS =======================")
    print("  support=standalone : built-in BSP can build now")
    print("  support=cmsis-pack : board is known; configure STM32Cube/CMSIS or board.toml")
    for name in sorted(BOARD_REGISTRY):
        board = BOARD_REGISTRY[name]
        peripherals = ",".join(board.peripherals) or "none"
        print(f"\n  {board.name:<20} {board.mcu:<18} [{board.support}]")
        print(f"      cpu={board.cpu} peripherals={peripherals}")
    print("\nUse 'nyx boards --init board.toml' for a custom circuit/BSP profile.")
    print("===================================================================")
    return 0


def cmd_flash(firmware, board_name, *, probe="auto", serial_number="", dry_run=False, cube_root="") -> int:
    if not board_name:
        print("\033[91m[!] --board is required for flashing. Run 'nyx boards'.\033[0m")
        return 1
    try:
        board = resolve_board(board_name, cube_root=cube_root or None)
    except BoardProfileError as exc:
        print(f"\033[91m[!] Invalid board profile:\033[0m {exc}")
        return 1
    if board is None:
        print(f"\033[91m[!] Unknown board '{board_name}'. Run 'nyx boards'.\033[0m")
        return 1
    if not firmware:
        print("\033[91m[!] Firmware path is required (.elf, .hex, .bin, or .nyx).\033[0m")
        return 1

    if firmware.endswith((".nyx", ".he")):
        status = cmd_build(
            firmware,
            board.compiler_target,
            board_name=board_name,
            cube_root=cube_root,
        )
        if status != 0:
            return status
        base_name = os.path.splitext(os.path.basename(firmware))[0]
        firmware = os.path.join("build", board.name, f"{base_name}.elf")

    flasher = FirmwareFlasher(board)
    try:
        options = {
            "probe": probe,
            "serial_number": serial_number,
            "connect_under_reset": "--connect-under-reset" in sys.argv,
        }
        if dry_run:
            selected = "cube" if probe == "auto" else probe
            placeholder = "STM32_Programmer_CLI" if selected in ("cube", "stlink", "stm32cubeprogrammer") else "openocd"
            command = flasher.build_command(firmware, tool_override=placeholder, **options)
            print("\033[96m[*] Flash command (dry run; hardware untouched):\033[0m")
            print(subprocess.list2cmdline(command))
            return 0
        result = flasher.flash(firmware, **options)
    except FirmwareFlashError as exc:
        print(f"\033[91m[!] Flash failed before programming:\033[0m {exc}")
        return 1

    if result["stdout"]:
        print(str(result["stdout"]).rstrip())
    if result["stderr"]:
        print(str(result["stderr"]).rstrip())
    if result["success"]:
        print(f"\033[92m[OK] Programmed and verified {board.display_name}.\033[0m")
        return 0
    print(f"\033[91m[!] Programmer exited with code {result['returncode']}.\033[0m")
    return int(result["returncode"] or 1)

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
    elif cmd == "targets":
        sys.exit(cmd_targets("--json" in sys.argv))
    elif cmd == "boards":
        init_path = ""
        if "--init" in sys.argv:
            init_index = sys.argv.index("--init")
            init_path = sys.argv[init_index + 1] if init_index + 1 < len(sys.argv) else "board.toml"
        cube_root = get_option_value("--cube-root", default="")
        install_family = get_option_value("--install", default="")
        install_root = get_option_value("--install-root", default="")
        sys.exit(cmd_boards(
            "--json" in sys.argv,
            init_path,
            cube_root,
            "--probe" in sys.argv,
            install_family,
            install_root,
            "--dry-run" in sys.argv,
        ))
    elif cmd == "new":
        raw_args = [a for a in sys.argv[2:] if not a.startswith("--")]
        name = raw_args[0] if raw_args else "nyx_project"
        is_lib = "--lib" in sys.argv
        sys.exit(cmd_new(name, is_lib=is_lib))
    elif cmd == "init":
        raw_args = [a for a in sys.argv[2:] if not a.startswith("--")]
        name = raw_args[0] if raw_args else config.get("name", "nyx_project")
        sys.exit(PackageManager.init(name, force="--force" in sys.argv))
    elif cmd == "check":
        entry = get_entry_file(config.get("entry", "src/main.nyx"))
        target = get_option_value("--target", "-t", default=config.get("target"))
        board_name = get_option_value("--board", default=config.get("board", ""))
        cube_root = get_option_value("--cube-root", default="")
        sys.exit(cmd_check(entry, target=target, board_name=board_name, cube_root=cube_root))
    elif cmd == "build":
        entry = get_entry_file(config.get("entry", "src/main.nyx"))
        target = get_target_from_args(config.get("target", "hecpp"), entry_file=entry)
        is_release = "--release" in sys.argv
        output_type = config.get("output_type", "exe")
        board_name = get_option_value("--board", default=config.get("board", ""))
        cube_root = get_option_value("--cube-root", default="")
        sys.exit(cmd_build(
            entry,
            target,
            is_release,
            output_type=output_type,
            board_name=board_name,
            cube_root=cube_root,
        ))
    elif cmd == "flash":
        firmware = next(
            (
                argument for argument in sys.argv[2:]
                if argument.lower().endswith((".elf", ".hex", ".bin", ".nyx", ".he"))
            ),
            None,
        )
        board_name = get_option_value("--board", default=config.get("board", ""))
        probe = get_option_value("--probe", default="auto")
        serial_number = get_option_value("--probe-serial", "--serial", default="")
        cube_root = get_option_value("--cube-root", default="")
        sys.exit(
            cmd_flash(
                firmware,
                board_name,
                probe=probe,
                serial_number=serial_number,
                dry_run="--dry-run" in sys.argv,
                cube_root=cube_root,
            )
        )
    elif cmd == "bundle":
        raw_args = [a for a in sys.argv[2:] if not a.startswith("--")]
        entry = get_entry_file(raw_args[0] if raw_args else config.get("entry", "src/main.nyx"))
        out_dir = None
        for i, a in enumerate(sys.argv):
            if a in ("-o", "--output") and i + 1 < len(sys.argv):
                out_dir = sys.argv[i + 1]
        emit_react = "--react" in sys.argv
        sys.exit(cmd_bundle(entry, out_dir=out_dir, emit_react=emit_react))
    elif cmd in ("self-host", "selfhost"):
        sys.exit(cmd_self_host(sys.argv[2:]))
    elif cmd == "run":
        entry = get_entry_file(config.get("entry", "src/main.nyx"))
        target = get_target_from_args(config.get("target", "hecpp"), entry_file=entry)
        sys.exit(cmd_run(entry, target))
    elif cmd == "test":
        if len(sys.argv) > 2 and (sys.argv[2].endswith(".nyx") or sys.argv[2].endswith(".he")):
            target_file = sys.argv[2]
            if not os.path.exists(target_file):
                print(f"\033[91m[!] Error: Test file '{target_file}' not found.\033[0m")
                sys.exit(1)
            print(f"\033[96m[*] Running nyx In-File Unit Tests in '{target_file}'...\033[0m")
            status = cmd_run(target_file, "hepy")
            if status != 0:
                print("\033[91m[!] Test execution failed.\033[0m")
                sys.exit(status)
            print("\033[92m[OK] Execution finished successfully.\033[0m")
        elif os.path.exists("src/lib.nyx"):
            print("\033[96m[*] Running nyx In-File Unit Tests in 'src/lib.nyx'...\033[0m")
            status = cmd_run("src/lib.nyx", "hepy")
            if status != 0:
                print("\033[91m[!] Test execution failed.\033[0m")
                sys.exit(status)
            print("\033[92m[OK] Execution finished successfully.\033[0m")
        elif os.path.exists("src/main.nyx"):
            print("\033[96m[*] Running nyx In-File Unit Tests in 'src/main.nyx'...\033[0m")
            status = cmd_run("src/main.nyx", "hepy")
            if status != 0:
                print("\033[91m[!] Test execution failed.\033[0m")
                sys.exit(status)
            print("\033[92m[OK] Execution finished successfully.\033[0m")
        else:
            test_suite = os.path.join(os.path.dirname(__file__), "..", "tests", "run_all_tests.py")
            if not os.path.exists(test_suite):
                test_suite = os.path.join(os.getcwd(), "tests", "run_all_tests.py")
            result = subprocess.run([sys.executable, test_suite])
            sys.exit(result.returncode)
    elif cmd == "clean":
        sys.exit(cmd_clean())
    elif cmd == "fmt":
        if len(sys.argv) < 3: print("Usage: nyx fmt <file.nyx>"); sys.exit(1)
        sys.exit(0 if Formatter.format_file(sys.argv[2]) else 1)
    elif cmd == "lint":
        if len(sys.argv) < 3: print("Usage: nyx lint <file.nyx>"); sys.exit(1)
        warnings = Linter.lint_file(sys.argv[2])
        sys.exit(1 if warnings < 0 else 0)
    elif cmd == "lsp":
        from src.toolchain.lsp_server import LanguageServer
        LanguageServer().run()
    elif cmd == "debug":
        if len(sys.argv) < 3: print("Usage: nyx debug <file.nyx>"); sys.exit(1)
        sys.exit(Debugger.debug_file(sys.argv[2]))
    elif cmd == "profile":
        entry = get_entry_file(config.get("entry", "src/main.nyx"))
        if not entry: print("Usage: nyx profile <file.nyx>"); sys.exit(1)
        target = get_target_from_args(config.get("target", "hecpp"), entry_file=entry)
        sys.exit(Profiler.profile_file(entry, lambda: cmd_run(entry, target)))
    elif cmd == "doc":
        if len(sys.argv) < 3: print("Usage: nyx doc <file.nyx>"); sys.exit(1)
        sys.exit(DocGenerator.generate_docs(sys.argv[2]))
    elif cmd == "add":
        if len(sys.argv) < 3: print("Usage: nyx add <package_name>"); sys.exit(1)
        try:
            package_name, version = parse_package_spec(sys.argv[2:])
        except ValueError as exc:
            print(f"[!] Invalid package specification: {exc}")
            sys.exit(1)
        sys.exit(PackageManager.add(package_name, version))
    elif cmd == "remove":
        if len(sys.argv) < 3: print("Usage: nyx remove <package_name>"); sys.exit(1)
        sys.exit(PackageManager.remove(sys.argv[2]))
    elif cmd == "install":
        sys.exit(PackageManager.install())
    elif cmd == "pkg":
        sys.exit(PackageManager.list_installed())
    else:
        print(f"\033[91m[!] Unknown command: '{cmd}'. Run 'nyx help' for available commands.\033[0m")
        sys.exit(1)

if __name__ == "__main__":
    main()
