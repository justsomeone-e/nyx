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
            [sys.executable, CLI_PATH, "bundle", SOURCE_PATH, "--output", output_dir, "--react", "--vue", "--svelte", "--package"],
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
        package_path = os.path.join(output_dir, "package.json")
        with open(package_path, "r", encoding="utf-8") as package_file:
            package_manifest = json.load(package_file)
        assert package_manifest["type"] == "module"
        assert package_manifest["exports"]["."]["types"] == "./test_bundle.d.ts"
        assert package_manifest["exports"]["./react"]["import"] == "./test_bundle.react.mjs"
        assert package_manifest["exports"]["./vue"]["import"] == "./test_bundle.vue.mjs"
        assert package_manifest["exports"]["./svelte"]["import"] == "./test_bundle.svelte.mjs"
        assert package_manifest["peerDependencies"]["react"].startswith(">=19")
        react_module_path = os.path.join(output_dir, "test_bundle.react.mjs")
        assert os.path.isfile(react_module_path)
        react_syntax = subprocess.run(
            [node, "--check", react_module_path], capture_output=True, text=True, encoding="utf-8"
        )
        assert react_syntax.returncode == 0, react_syntax.stderr
        for adapter in ("vue", "svelte"):
            adapter_path = os.path.join(output_dir, f"test_bundle.{adapter}.mjs")
            syntax = subprocess.run([node, "--check", adapter_path], capture_output=True, text=True, encoding="utf-8")
            assert syntax.returncode == 0, syntax.stderr

        build_workspace = os.path.join(output_dir, "build_workspace")
        os.makedirs(build_workspace)
        build = subprocess.run(
            [sys.executable, CLI_PATH, "build", SOURCE_PATH, "--target", "wasm"],
            cwd=build_workspace,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert build.returncode == 0, build.stderr or build.stdout
        build_dir = os.path.join(build_workspace, "build", "wasm")
        for extension in (".wat", ".wasm", ".mjs", ".d.ts"):
            assert os.path.isfile(os.path.join(build_dir, "test_bundle" + extension)), (
                f"nyx build --target wasm did not emit {extension}"
            )
        assert not os.path.exists(os.path.join(build_dir, "test_bundle.react.tsx"))

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

        host_source = os.path.join(output_dir, "host_import.nyx")
        host_output = os.path.join(output_dir, "host_import_bundle")
        with open(host_source, "w", encoding="utf-8") as source_file:
            source_file.write(
                'extern "WASM:test_host" fn host_add(a: int, b: int) -> int\n'
                'extern "WASM:test_host" fn host_text_len(value: string) -> int\n'
                "fn add_via_host(a: int, b: int) -> int { return host_add(a, b); }\n"
                'fn text_len_via_host(value: string) -> int { return host_text_len(value); }\n'
            )
        host_bundle = subprocess.run(
            [sys.executable, CLI_PATH, "bundle", host_source, "--output", host_output],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert host_bundle.returncode == 0, host_bundle.stderr or host_bundle.stdout

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
                "const hostModulePath = process.argv[5];\n"
                "const hostWasmPath = process.argv[6];\n"
                "const bytes = fs.readFileSync(wasmPath);\n"
                "if (!WebAssembly.validate(bytes)) throw new Error('invalid WebAssembly binary');\n"
                "const generated = await import(pathToFileURL(modulePath));\n"
                "const api = await generated.initNyxModule(wasmPath);\n"
                "const unicodeInput = 'İstanbul 🌙 çığ ğüşö\\u0000é';\n"
                "const expected = `Hello from Nyx WebAssembly, ${unicodeInput}!`;\n"
                "if (api.add_numbers(15, 27) !== 42) throw new Error('numeric lowering failed');\n"
                "if (api.next_counter() !== 1 || api.next_counter() !== 2) throw new Error('WASM mutable global failed');\n"
                "if (api.is_positive(1) !== true || api.is_positive(0) !== false) throw new Error('boolean ABI failed');\n"
                "if (typeof api.is_positive(1) !== 'boolean') throw new Error('boolean ABI leaked i32');\n"
                "if (api.compute_power(2, 10) !== 1024) throw new Error('loop/local lowering failed');\n"
                "if (api.sum_values(new Int32Array([1, 0, 2, 3])) !== 6) throw new Error('i32 array iteration failed');\n"
                "if (api.sum_float_values([1.5, 2.25]) !== 3.75) throw new Error('f64 array iteration failed');\n"
                "if (api.array_length([3, 4, 5]) !== 3) throw new Error('array method lowering failed');\n"
                "if (api.string_length('İstanbul') !== 9) throw new Error('string method lowering failed');\n"
                "if (api.choose_label(true, 'Nyx') !== 'enabled: Nyx' || api.choose_label(false, 'Nyx') !== 'disabled: Nyx') throw new Error('string conditional lowering failed');\n"
                "if (api.greet_developer(unicodeInput) !== expected) throw new Error('UTF-8 string lowering failed');\n"
                "if (api.echo_via_call(unicodeInput) !== unicodeInput) throw new Error('internal string parameter call failed');\n"
                "if (api.literal_via_call() !== 'internal UTF-8: İstanbul 🌙') throw new Error('internal string literal call failed');\n"
                "for (let i = 0; i < 100000; i++) {\n"
                "  if (api.greet_developer('x') !== 'Hello from Nyx WebAssembly, x!') {\n"
                "    throw new Error(`stress mismatch at ${i}`);\n"
                "  }\n"
                "}\n"
                "const alternateApi = await generated.initNyxModule(alternateWasmPath);\n"
                "if (alternateApi.add_numbers(10, 3) !== 7) throw new Error('alternate instance mismatch');\n"
                "if (api.add_numbers(10, 3) !== 13) throw new Error('module instances share mutable state');\n"
                "if (generated.add_numbers(10, 3) !== 7) throw new Error('default API did not select latest init');\n"
                "const isolatedA = await generated.createNyxModule(wasmPath);\n"
                "const isolatedB = await generated.createNyxModule(wasmPath);\n"
                "if (isolatedA === isolatedB) throw new Error('createNyxModule reused a cached API');\n"
                "if (isolatedA.next_counter() !== 1 || isolatedB.next_counter() !== 1) throw new Error('WASM globals leaked across instances');\n"
                "const hostGenerated = await import(pathToFileURL(hostModulePath));\n"
                "let hostMemory;\n"
                "const hostApi = await hostGenerated.createNyxModule(hostWasmPath, { imports: { test_host: {\n"
                "  host_add: (a, b) => a + b,\n"
                "  host_text_len: (ptr, len) => { if (!hostMemory) return len; return new Uint8Array(hostMemory.buffer, ptr, len).length; },\n"
                "} } });\n"
                "if (hostApi.add_via_host(20, 22) !== 42) throw new Error('WASM numeric host import failed');\n"
                "if (hostApi.text_len_via_host('İstanbul') !== 9) throw new Error('WASM string host import failed');\n"
                "console.log(JSON.stringify({ add: 42, power: 1024, stress: 100000, unicode: true, isolated: true }));\n"
            )

        runtime = subprocess.run(
            [
                node,
                runner_path,
                module_path,
                wasm_path,
                alternate_wasm_path,
                os.path.join(host_output, "host_import.mjs"),
                os.path.join(host_output, "host_import.wasm"),
            ],
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
        assert "call $echo_inner" in wat

    print("[PASS] Typed lowering, build/bundle artifacts, definite returns, UTF-8 ABI, isolated instances, and 100k allocation stress")
    return True


if __name__ == "__main__":
    sys.exit(0 if run_bundle_suite() else 1)
