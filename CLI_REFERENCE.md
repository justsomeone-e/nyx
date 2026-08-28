# 💻 HolyEasyLang CLI & Command Reference

The HolyEasyLang toolchain binary (`he`) provides project scaffolding, validation, multi-target compilation, testing, formatting, and language services.

---

## 🛠️ Commands Overview

```bash
he <command> [arguments] [options]
```

### 1. `he new <project_name>`
Creates a standard HolyEasy project structure:
```text
my_project/
├── he.toml
├── .gitignore
└── src/
    └── main.he
```

### 2. `he init [name]`
Initializes a `he.toml` project manifest in the current directory.

### 3. `he check [file.he]`
Performs fast static semantic and type-checking across project source files without invoking backend compilers.

### 4. `he build [file.he] [--target <backend>] [--release]`
Transpiles and builds the program into the `build/<target>/` directory.
Supported targets:
* `--target hecpp` (Default: C++20 / Native Executable)
* `--target hejs` (Node.js ES2022 Module)
* `--target hepy` (Python 3)
* `--target hers` (Rust 2021 Source)

### 5. `he run [file.he] [--target <backend>]`
Builds and executes the entrypoint immediately on the specified host backend.

### 6. `he test [file.he | all]`
* If a file is specified: Runs in-file `test "..." { assert(...) }` blocks.
* If omitted or `all`: Runs the master regression test framework.

### 7. `he doctor`
Diagnoses host system dependencies (Python, LLVM Clang, Node.js, Rust, and Git) and outputs remediation instructions for missing compilers.

### 8. `he lsp`
Launches the JSON-RPC 2.0 Language Server Protocol daemon for editor integrations (VS Code, Neovim, Emacs).

### 9. `he fmt <file.he>`
Auto-formats and indents source code according to HolyEasyLang standards.

### 10. `he clean`
Removes temporary build artifacts and directories (`build/`, `target/`, `__pycache__`).
