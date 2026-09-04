# 💻 Nyx CLI & Command Reference

The `nyx` toolchain provides project scaffolding, validation, multi-target
compilation, testing, formatting, language services, and deterministic
manifest/lockfile management.

---

## 🛠️ Commands Overview

```bash
nyx <command> [arguments] [options]
```

### 1. `nyx new <project_name>`
Creates a standard Nyx project structure:
```text
my_project/
├── nyx.toml
├── nyx.lock
├── .gitignore
└── src/
    └── main.nyx
```

### 2. `nyx init [name]`
Initializes `nyx.toml` and `nyx.lock`. Existing manifests require explicit `--force`.

### 3. `nyx check [file.nyx]`
Performs fast static semantic and type-checking across project source files without invoking backend compilers.

### 4. `nyx build [file.nyx] [--target <backend>] [--release]`
Transpiles and builds the program into the `build/<target>/` directory.
Supported targets:
* `--target cpp` (Default: C++20 / Native Executable)
* `--target js` (Node.js ES2022 Module)
* `--target python` (Python 3)
* `--target rust` (Rust 2021 Source)
* `--target wasm` (WAT, WebAssembly binary, ES2022 loader, and TypeScript declarations)
* `--target react` (React 19 TSX preview)
* `--target asm` (Intel-syntax x86_64 assembly through the native toolchain)

Native console executables finish when `main` returns; use `nyx run file.nyx` to keep their
output visible in the current terminal instead of double-clicking the EXE.

### 5. `nyx run [file.nyx] [--target <backend>]`
Builds and executes the entrypoint immediately on the specified host backend.

### 6. `nyx test [file.nyx | all]`
* If a file is specified: Runs in-file `test "..." { assert(...) }` blocks.
* If omitted or `all`: Runs the master regression test framework.

### 7. `nyx doctor`
Diagnoses host system dependencies (Python, LLVM Clang, Node.js, Rust, and Git) and outputs remediation instructions for missing compilers.

### 8. `nyx lsp`
Launches the JSON-RPC 2.0 Language Server Protocol daemon for editor integrations (VS Code, Neovim, Emacs).

### 9. `nyx fmt <file.nyx>`
Applies string/comment-safe, idempotent source formatting. Missing files return nonzero.

### 10. `nyx clean`
Removes temporary build artifacts and directories (`build/`, `target/`, `__pycache__`).

### 11. `nyx lint <file.nyx>`
Reports style and unsafe-boundary warnings without treating warnings as process failures.

### 12. `nyx debug <file.nyx>`
Opens the validated source-line inspector. Runtime values are not fabricated;
runtime source maps and variable inspection are not part of RC1.

### 13. `nyx profile <file.nyx> [--target <backend>]`
Runs the real compile+execute path and reports measured whole-program wall time.
It does not print synthetic function timings.

### 14. `nyx doc <file.nyx>`
Generates escaped HTML API documentation from `///` comments.

### 15. `nyx add <package> [@version] [--path <directory>]`
Adds an explicit dependency to `nyx.toml` and regenerates `nyx.lock`. Local
path dependencies are resolved recursively, cycle-checked, content-hashed, and
recorded with canonical relative paths.

### 16. `nyx remove <package>`
Removes a dependency from the manifest and lockfile. Missing dependencies return nonzero.

### 17. `nyx install`
Validates manifest dependencies and regenerates `nyx.lock`. The RC2 contract
supports deterministic local path dependencies; remote registry download is
not enabled.

### 18. `nyx pkg`
Displays project metadata, dependencies, native settings, and build configuration.

### 19. `nyx targets [--json]`
Displays the human-readable or machine-readable backend and standard-library
capability contract.

### 20. `nyx bundle <file.nyx> --output <dir> [--package] [--react] [--vue] [--svelte]`
Writes the WASM ABI v1 package to an explicit directory. `--package` adds an
npm manifest; framework flags add typed React 19, Vue 3, or Svelte 5 adapters.
Vue and Svelte adapters require `--package`.
