import json
import os
import shutil
import subprocess
import sys
import tempfile


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI_PATH = os.path.join(ROOT_DIR, "src", "cli.py")
SOURCE_PATH = os.path.join(ROOT_DIR, "tests", "test_bundle.nyx")


def run_bundle_suite() -> bool:
    print("=" * 70)
    print("NYX BUNDLE TYPED-IR / WASM ABI CONFORMANCE")
    print("=" * 70)
    node = shutil.which("node")
    if not node:
        print("[!] Node.js not found. Bundle runtime conformance cannot run.")
        return False

    with tempfile.TemporaryDirectory(prefix="nyx_bundle_ir_") as output_dir:
        bundle = subprocess.run(
            [sys.executable, CLI_PATH, "bundle", SOURCE_PATH, "--output", output_dir, "--react"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert bundle.returncode == 0, bundle.stderr or bundle.stdout

        module_path = os.path.join(output_dir, "test_bundle.mjs")
        wasm_path = os.path.join(output_dir, "test_bundle.wasm")
        wat_path = os.path.join(output_dir, "test_bundle.wat")
        assert os.path.exists(module_path) and os.path.exists(wasm_path) and os.path.exists(wat_path)

        alternate_source = os.path.join(output_dir, "alternate.nyx")
        alternate_output = os.path.join(output_dir, "alternate_bundle")
        with open(alternate_source, "w", encoding="utf-8") as source_file:
            source_file.write(
                "fn add_numbers(a: int, b: int) -> int { return a - b; }\n"
                "fn compute_power(base: int, exp: int) -> int { return base + exp; }\n"
                "fn greet_developer(name: string) -> string { return name; }\n"
            )
        alternate = subprocess.run(
            [sys.executable, CLI_PATH, "bundle", alternate_source, "--output", alternate_output],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert alternate.returncode == 0, alternate.stderr or alternate.stdout
        alternate_wasm_path = os.path.join(alternate_output, "alternate.wasm")

        partial_source = os.path.join(output_dir, "partial_return.nyx")
        partial_output = os.path.join(output_dir, "partial_return_bundle")
        with open(partial_source, "w", encoding="utf-8") as source_file:
            source_file.write(
                "fn partial(flag: int) -> int {\n"
                "    if flag > 0 { return 1; }\n"
                "}\n"
            )
        partial = subprocess.run(
            [sys.executable, CLI_PATH, "bundle", partial_source, "--output", partial_output],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert partial.returncode != 0, "bundle accepted a value function with a fall-through path"
        assert "can fall through" in (partial.stdout + partial.stderr)
        assert not os.path.exists(partial_output), "failed bundle left a partial output directory"

        runner_path = os.path.join(output_dir, "verify.mjs")
        with open(runner_path, "w", encoding="utf-8") as runner:
            runner.write(
                "import fs from 'node:fs';\n"
                "import { pathToFileURL } from 'node:url';\n"
                "const modulePath = process.argv[2];\n"
                "const wasmPath = process.argv[3];\n"
                "const alternateWasmPath = process.argv[4];\n"
                "const bytes = fs.readFileSync(wasmPath);\n"
                "if (!WebAssembly.validate(bytes)) throw new Error('invalid WebAssembly binary');\n"
                "const generated = await import(pathToFileURL(modulePath));\n"
                "const api = await generated.initNyxModule(wasmPath);\n"
                "const unicodeInput = 'İstanbul 🌙 çığ ğüşö\\u0000é';\n"
                "const expected = `Hello from Nyx WebAssembly, ${unicodeInput}!`;\n"
                "if (api.add_numbers(15, 27) !== 42) throw new Error('numeric lowering failed');\n"
                "if (api.compute_power(2, 10) !== 1024) throw new Error('loop/local lowering failed');\n"
                "if (api.greet_developer(unicodeInput) !== expected) throw new Error('UTF-8 string lowering failed');\n"
                "for (let i = 0; i < 100000; i++) {\n"
                "  if (api.greet_developer('x') !== 'Hello from Nyx WebAssembly, x!') {\n"
                "    throw new Error(`stress mismatch at ${i}`);\n"
                "  }\n"
                "}\n"
                "const alternateApi = await generated.initNyxModule(alternateWasmPath);\n"
                "if (alternateApi.add_numbers(10, 3) !== 7) throw new Error('alternate instance mismatch');\n"
                "if (api.add_numbers(10, 3) !== 13) throw new Error('module instances share mutable state');\n"
                "if (generated.add_numbers(10, 3) !== 7) throw new Error('default API did not select latest init');\n"
                "console.log(JSON.stringify({ add: 42, power: 1024, stress: 100000, unicode: true, isolated: true }));\n"
            )

        runtime = subprocess.run(
            [node, runner_path, module_path, wasm_path, alternate_wasm_path],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert runtime.returncode == 0, runtime.stderr or runtime.stdout
        result = json.loads(runtime.stdout.strip().splitlines()[-1])
        assert result == {"add": 42, "power": 1024, "stress": 100000, "unicode": True, "isolated": True}

        with open(wat_path, "r", encoding="utf-8") as wat_file:
            wat = wat_file.read()
        assert "loop $for_loop_" in wat
        assert "memory.copy" in wat
        assert "i32.mul" in wat

    print("[PASS] Typed lowering, definite returns, UTF-8 ABI, isolated instances, and 100k allocation stress")
    return True


if __name__ == "__main__":
    sys.exit(0 if run_bundle_suite() else 1)
