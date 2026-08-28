# Nyx — CLI & Enterprise Toolchain Manual

## 1. Toolchain Overview

Nyx provides a unified CLI driver (`he` / `he.bat`) covering the full developer lifecycle: project scaffolding, type-checking, native compilation, direct execution, in-file testing, formatting, and package management.

```text
                                 he CLI
                                   │
       ┌───────────┬───────────────┼───────────────┬───────────┐
       ↓           ↓               ↓               ↓           ↓
   [ he new ]  [ he check ]   [ he build ]    [ he run ]  [ he test ]
```

---

## 2. Project Conventions & Manifest (`he.toml`)

Every Nyx project contains a `he.toml` manifest file at its root:

```toml
[package]
name = "my_project"
version = "0.1.0"
edition = "2026"
target = "hecpp"          # Default target backend: hecpp, hepy, hejs, hers
entry = "src/main.he"     # Application entrypoint

[dependencies]
# std = "4.0.0"
# math = "1.0.0"

[build]
opt_level = 2
debug = false
```

### Standard Project Layout
```text
my_project/
├── he.toml               # Package manifest
├── he.lock               # Resolved dependency lockfile
├── .gitignore            # Standard git ignore rules
├── src/
│   └── main.he           # Main entrypoint
└── build/                # Output binaries and transpiled modules
    ├── hecpp/
    │   └── main.exe      # Native C++20 Executable
    ├── hejs/
    │   └── main.js       # Node.js / Browser ESM Module
    └── hers/
        └── main.rs       # Rust 2021 Source
```

---

## 3. Command Reference

### Project Scaffolding
* `he new <project_name>`: Scaffolds a new project directory with `he.toml`, `src/main.he`, and `.gitignore`.
* `he init [name]`: Initializes a `he.toml` manifest in the current directory.

### Build & Verification
* `he check [file.he]`: Performs rapid syntax and semantic validation through `Lexer -> Parser -> TypeChecker` without code generation.
* `he build [file.he] [--target <hecpp|hepy|hejs|hers>]`: Transpiles and compiles the project into the `build/<target>/` directory.
  * If targeting `hecpp`, compiles directly to a native `.exe` binary.
  * If targeting `hejs`, emits an ES2022 Node.js module.
  * If targeting `hers`, emits clean, borrow-checked Rust 2021 code.
* `he run [file.he] [--target <hecpp|hepy|hejs|hers>]`: Compiles and executes the project or file immediately with the selected backend.
* `he clean`: Removes all `build/`, `target/`, and temporary compiler cache artifacts.

### Testing & Quality Assurance
* `he test`: Runs the automated test suite across all 4 backends (Negative, Fuzz, Differential, E2E, and 138-Regression Battery).
* `he test <file.he>`: Runs native in-file unit test blocks (`test "name" { assert(...) }`).
* `he fmt <file.he>`: Auto-formats and beautifies source code.
* `he lint <file.he>`: Runs static analysis and unsafe memory boundary checks.
* `he debug <file.he>`: Launches the step-by-step interactive debugger.
* `he profile <file.he>`: Generates a routine execution and bottleneck profiling report.
* `he doc <file.he>`: Generates HTML API documentation from `///` doc comments.

### Package Management
* `he add <package_name>`: Adds a dependency into `he.toml` and locks in `he.lock`.
* `he remove <package_name>`: Removes a dependency from `he.toml` and `he.lock`.
* `he install`: Resolves and locks all dependencies from `he.toml`.
* `he pkg`: Displays the current project manifest and dependency status.

### Toolchain Diagnostics
* `he version`: Displays Core compiler version and detected host toolchains (`clang++`, `node`, `rustc`, `python`).
