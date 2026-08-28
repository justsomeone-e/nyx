# ⚡ HolyEasyLang Core (v2.0.0 Beta 1)

**HolyEasyLang** is a multi-target, statically typed systems programming language with seamless interoperability, zero boilerplate, and robust multi-backend compilation.

```text
                    HolyEasyLang Core
                 Lexer → Parser → TC → AST
                         │
             ┌───────────┼───────────┐
             ↓           ↓           ↓
           hecpp        hepy        hejs        hers
          Gate 8 🔒    Gate 8 📐   Gate 8 🔒   Gate 6 🟡
          (C++20)     (Reference)   (Node.js)    (Rust)
```

---

## 🚀 Key Features

* **Multi-Target Architecture**: Transpile clean, idiomatic, high-performance output across C++20, Node.js (ES2022), Python 3, and Rust 2021.
* **Native Executable Compilation (`hecpp`)**: Automatic host toolchain discovery (LLVM Clang / MinGW-w64) for building self-contained native `.exe` binaries with zero runtime dependencies.
* **Module & Import System**: Local relative (`import "./utils"`), standard library (`import "std/math"`), selective symbols (`import { power } from "std/math"`), and diamond dependency deduplication.
* **Diagnostics v2**: Rustc-grade visual compiler error diagnostics with exact source spans, carets (`^^^^`), searched paths, and actionable resolution suggestions.
* **Integrated LSP v2**: Built-in Language Server Protocol daemon supporting intelligent autocomplete, hover type tooltips, and go-to-definition.
* **Zero-Setup Testing**: First-class in-file `test "..." { assert(...) }` blocks runnable directly via `he test`.

---

## 📊 Backend Conformance & Quality Gates

| Target | Quality Gate | Status | Output / Execution Model |
| :--- | :--- | :--- | :--- |
| **`hecpp`** | **Gate 8 (Stable/Frozen)** | 🔒 Production | C++20 ISO Standard $\to$ Native Executable (`clang++` / `g++`) |
| **`hepy`** | **Gate 8 (Reference)** | 📐 Semantic Ref | Canonical Reference Semantic Evaluation Engine |
| **`hejs`** | **Gate 8 (Stable/Frozen)** | 🔒 Production | Modern Node.js ES2022 Modules |
| **`hers`** | **Gate 6 (Conformance)**| 🟡 Active | Rust 2021 Source $\to$ `rustc` MIR / Borrow-Checked Object |

---

## 📦 Quick Start

### Installation

* **Windows (PowerShell)**:
  ```powershell
  irm https://raw.githubusercontent.com/holyeasy/holyeasylang/main/install.ps1 | iex
  ```
* **Linux / macOS**:
  ```bash
  curl -fsSL https://raw.githubusercontent.com/holyeasy/holyeasylang/main/install.sh | bash
  ```

### Verify Environment
```bash
he doctor
```

### Create and Run a Project
```bash
# 1. Create a new project
he new my_project
cd my_project

# 2. Type-check semantics
he check

# 3. Compile and run immediately (Native C++20 by default)
he run

# 4. Target other backends
he run --target hejs
he run --target hepy
he build --target hers
```

---

## 📖 Example Code

```holyeasy
#target hecpp
import "std/math"
import "std/io"

struct User {
    name: string,
    age: int
}

fn is_adult(u: User) -> bool {
    return u.age >= 18
}

var admin = User("Umut", 24)
if is_adult(admin) {
    var p = power(2, 4)
    println_str("Admin verified. Power level: " + to_string(p))
}

test "user verification test" {
    var u = User("Alice", 20)
    assert(is_adult(u) == true, "Alice must be an adult")
}
```

---

## 📚 Documentation

* [Installation Guide](INSTALLATION.md)
* [Getting Started Tutorial](GETTING_STARTED.md)
* [Language Reference & Syntax](LANGUAGE_REFERENCE.md)
* [CLI & Toolchain Manual](CLI_REFERENCE.md)
* [Error Reference Catalog](ERROR_REFERENCE.md)
* [Changelog](CHANGELOG.md)

---

## 📜 License

HolyEasyLang is licensed under the [MIT License](LICENSE).
