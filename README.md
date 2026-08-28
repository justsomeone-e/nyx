<div align="center">

  <a href="https://github.com/justsomeone-e/nyx">
    <img src="assets/logo.svg" width="420" alt="nyx logotype"/>
  </a>
  <br/><br/>

  <p align="center">
    <a href="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=20&duration=3000&pause=1200&color=00F0FF&center=true&vCenter=true&width=700&lines=High-Performance+Multi-Target+Systems+Toolchain.;C%2B%2B20+Native+Binaries+%7C+Node.js+ES2022+%7C+Rust+2021+%7C+Python+3.;Deterministic+AST+Pipeline+with+Topological+Deduplication.;Diagnostics+v2+with+Sub-Character+Span+Precision.">
      <img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=20&duration=3000&pause=1200&color=00F0FF&center=true&vCenter=true&width=700&lines=High-Performance+Multi-Target+Systems+Toolchain.;C%2B%2B20+Native+Binaries+%7C+Node.js+ES2022+%7C+Rust+2021+%7C+Python+3.;Deterministic+AST+Pipeline+with+Topological+Deduplication.;Diagnostics+v2+with+Sub-Character+Span+Precision." alt="Typing SVG" />
    </a>
  </p>

  <p align="center">
    <a href="https://github.com/justsomeone-e/nyx/releases"><img src="https://img.shields.io/badge/RELEASE-v3.0.0--beta.1-0E1318?style=for-the-badge&logoColor=00F0FF&labelColor=05070A" alt="Version"></a>
    <a href="https://github.com/justsomeone-e/nyx/actions"><img src="https://img.shields.io/badge/CI%20BUILD-PASSING-0E1318?style=for-the-badge&logoColor=00F0FF&labelColor=05070A" alt="CI"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/LICENSE-MIT-0E1318?style=for-the-badge&labelColor=05070A" alt="License"></a>
    <a href="#"><img src="https://img.shields.io/badge/PLATFORMS-LINUX%20%7C%20WIN%20%7C%20MACOS-0E1318?style=for-the-badge&labelColor=05070A" alt="Platforms"></a>
  </p>

  <p align="center">
    <a href="#overview">OVERVIEW</a> •
    <a href="#key-features">FEATURES</a> •
    <a href="#architecture">ARCHITECTURE</a> •
    <a href="#toolchain">TOOLCHAIN</a> •
    <a href="#language">LANGUAGE</a> •
    <a href="#installation">INSTALLATION</a> •
    <a href="#usage">USAGE</a> •
    <a href="#contributing">CONTRIBUTING</a>
  </p>

</div>

---

## `01` — Overview

**Nyx** is a compiled, statically typed systems programming language built around a deterministic multi-target compiler pipeline.

Instead of tying the language to a single runtime or execution environment, Nyx validates source code once, produces a canonical typed AST, and uses that representation to generate code for multiple targets.

The result is a toolchain designed to combine **native performance, predictable semantics, and backend flexibility** without requiring separate language frontends for every target.

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                                  NYX                                         │
│                     Multi-Target Systems Toolchain                           │
└──────────────────────────────────────────────────────────────────────────────┘

        SOURCE
          │
          ▼
┌───────────────────┐
│  UTF-8 LEXER      │
│  Token Stream     │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  PARSER           │
│  Syntax AST       │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  MODULE GRAPH     │
│  Topological DAG  │
│  + Deduplication  │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  TYPECHECKER      │
│  Inference        │
│  Scopes / Bounds  │
└─────────┬─────────┘
          │
          ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║                         CANONICAL TYPED AST                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
          │
    ┌─────┼─────────────┬─────────────┐
    │     │             │             │
    ▼     ▼             ▼             ▼
┌──────┐ ┌──────┐    ┌──────┐    ┌──────┐
│hecpp │ │ hejs │    │ hers │    │ hepy │
│C++20 │ │Node.js│   │Rust21│    │Python│
└──┬───┘ └──┬───┘    └──┬───┘    └──┬───┘
   │         │           │            │
   ▼         ▼           ▼            ▼
Native     ES2022       rustc       Reference
Binary     Module       Object      Semantics
```

Nyx's architecture keeps **language semantics separate from backend generation**, allowing each target to consume the same validated program representation.

---

## `02` — Key Features

<table>
<tr>
<td width="50%">

### ⚡ Multi-Target Compilation

Compile the same Nyx program toward:

* **C++20**
* **Node.js ES2022**
* **Rust 2021**
* **Python 3**

Each backend operates on the canonical typed AST.

</td>
<td width="50%">

### 🧠 Deterministic AST Pipeline

Nyx uses a predictable compilation pipeline:

```text
Source
  ↓
Lexer
  ↓
Parser
  ↓
Graph Loader
  ↓
TypeChecker
  ↓
Canonical AST
  ↓
Backend
```

</td>
</tr>

<tr>
<td>

### ◇ Topological Module Graph

Dependencies are represented as a directed graph with:

* Topological ordering
* Diamond dependency deduplication
* Cycle detection
* Symbol collision detection
* Deterministic resolution

</td>
<td>

### ⌁ Diagnostics v2

Compiler diagnostics provide precise source spans and structured error codes.

```text
error[E1302]

14 | use value
   |     ^^^^^
   |
   └─ ambiguous symbol collision
```

</td>
</tr>

<tr>
<td>

### ◈ Native Code Generation

The `hecpp` backend targets **C++20**, allowing generated programs to be compiled into native executables through Clang or GCC.

</td>
<td>

### ◌ Built-In Developer Protocol

Nyx includes a built-in **Language Server Protocol v2 JSON-RPC** implementation for editor and tooling integration.

</td>
</tr>
</table>

---

## `03` — Architecture

The compiler is divided into explicit stages. Each stage has a well-defined responsibility and passes validated data to the next stage.

```text
                              ┌─────────────────────┐
                              │   Nyx Source Code   │
                              │      .nyx / .he     │
                              └──────────┬──────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │   Lexical Engine    │
                              │                     │
                              │ UTF-8 Tokenization  │
                              └──────────┬──────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │   Parser / AST      │
                              │                     │
                              │ Syntax Construction │
                              └──────────┬──────────┘
                                         │
                                         ▼
                    ┌──────────────────────────────────────┐
                    │         Module Graph Loader          │
                    │                                      │
                    │  DAG → Topological Ordering          │
                    │  Diamond Deduplication                │
                    │  Cycle Detection                     │
                    │  Symbol Collision Detection          │
                    └──────────────────┬───────────────────┘
                                       │
                                       ▼
                              ┌─────────────────────┐
                              │     TypeChecker     │
                              │                     │
                              │ Inference           │
                              │ Scopes              │
                              │ Bounds              │
                              └──────────┬──────────┘
                                         │
                                         ▼
                         ╔════════════════════════════╗
                         ║    CANONICAL TYPED AST    ║
                         ╚════════════╤═══════════════╝
                                      │
             ┌────────────────────────┼────────────────────────┐
             │                        │                        │
             ▼                        ▼                        ▼
      ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
      │    hecpp     │        │    hejs      │        │    hers      │
      │    C++20     │        │ Node.js      │        │  Rust 2021   │
      │              │        │  ES2022      │        │              │
      └──────┬───────┘        └──────┬───────┘        └──────┬───────┘
             │                       │                       │
             ▼                       ▼                       ▼
        Native .exe              ES Module              rustc Object

                              ┌──────────────┐
                              │     hepy     │
                              │   Python 3   │
                              │  Reference   │
                              └──────┬───────┘
                                     │
                                     ▼
                              Canonical Semantics
```

### Backend Philosophy

The backend layer is intentionally separated from parsing and semantic validation.

```text
              ┌───────────────────────────┐
              │      Language Frontend    │
              │                           │
              │ Lexer → Parser → Types    │
              └─────────────┬─────────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │  Canonical Typed AST│
                 └──────────┬──────────┘
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
          C++20          Node.js          Rust
          hecpp           hejs            hers
             │              │              │
             └──────────────┼──────────────┘
                            │
                            ▼
                       Python / hepy
                       Reference Layer
```

This architecture makes backend behavior easier to test against a shared semantic source of truth.

---

## `04` — Toolchain

Nyx currently exposes four target backends.

| Backend     | Target         | Purpose                       | Status       |
| :---------- | :------------- | :---------------------------- | :----------- |
| **`hecpp`** | C++20          | Native executable generation  | 🔒 Stable    |
| **`hejs`**  | Node.js ES2022 | JavaScript execution          | 🔒 Stable    |
| **`hers`**  | Rust 2021      | Rust compilation pipeline     | 🟡 Active    |
| **`hepy`**  | Python 3       | Canonical reference semantics | 📐 Reference |

### `hecpp`

```text
Nyx
 │
 ▼
Canonical AST
 │
 ▼
C++20
 │
 ├── Clang
 └── GCC
      │
      ▼
 Native Executable
```

### `hejs`

```text
Nyx
 │
 ▼
Canonical AST
 │
 ▼
Node.js ES2022
 │
 ▼
ES Module
```

### `hers`

```text
Nyx
 │
 ▼
Canonical AST
 │
 ▼
Rust 2021
 │
 ▼
rustc
 │
 ▼
Rust Object
```

### `hepy`

The Python backend serves as a canonical semantic reference for validating behavior across targets.

---

## `05` — Language

Nyx source files can select a backend explicitly using a target directive.

```nyx
#target hecpp

import "std/math"
import "std/io"

struct ClusterNode {
    address: string,
    port: int,
    is_master: bool
}

fn compute_shard_capacity(nodes: int, factor: int) -> int {
    return power(nodes, 2) * factor
}

var node = ClusterNode("10.0.0.1", 9000, true)

if node.is_master {
    var total_capacity = compute_shard_capacity(8, 4)

    println_str(
        "Cluster Node [" +
        node.address +
        "] Online -> Capacity: " +
        to_string(total_capacity)
    )
}

test "shard capacity verification" {
    assert(
        compute_shard_capacity(2, 3) == 12,
        "Mathematical invariant failure"
    )
}
```

The example demonstrates several core language concepts:

* Explicit target selection
* Imports
* Structures
* Static type annotations
* Functions
* Return types
* Variables
* Conditionals
* Function calls
* Built-in testing
* Assertions

---

## `06` — Installation

### Windows

Nyx provides a PowerShell installer:

```powershell
irm https://raw.githubusercontent.com/justsomeone-e/nyx/main/install.ps1 | iex
```

Verify the installation:

```powershell
nyx doctor
```

### Linux / macOS

Use the provided POSIX installer:

```bash
curl -fsSL https://raw.githubusercontent.com/justsomeone-e/nyx/main/install.sh | bash
```

Then verify the environment:

```bash
nyx doctor
```

### Environment Verification

The `doctor` command is intended to verify the host environment, compiler availability, paths, and required tooling.

```bash
nyx doctor
```

---

## `07` — Usage

### Create a Workspace

```bash
nyx new core_engine
cd core_engine
```

### Validate

Run semantic and type validation:

```bash
nyx check
```

### Run Native C++20

The default execution target is the native C++20 backend:

```bash
nyx run
```

### Run Node.js

```bash
nyx run --target hejs
```

### Run Python Reference

```bash
nyx run --target hepy
```

### Build Rust

```bash
nyx build --target hers
```

### Command Overview

```text
nyx
 │
 ├── doctor
 │     └── Verify environment
 │
 ├── new <name>
 │     └── Create workspace
 │
 ├── check
 │     └── Validate source
 │
 ├── run
 │     ├── Default → hecpp
 │     ├── --target hejs
 │     └── --target hepy
 │
 └── build
       └── --target hers
```

---

## `08` — Verification & Conformance

Nyx maintains an automated verification battery covering the compiler pipeline and backend behavior.

```text
╔══════════════════════════════════════════════════════════════════════════════╗
║                         NYX VERIFICATION MATRIX                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  UTF-8 / Lexical Analysis                         ──► 100% PASS             ║
║  Syntactic AST Construction                       ──► 100% PASS             ║
║  Static Type Invariants                           ──► 100% PASS             ║
║  Topological Graph Deduplication                  ──► 100% PASS             ║
║  Symbol Collision Detection E1302                ──► 100% PASS             ║
║  LSP v2 JSON-RPC                                  ──► 100% PASS (3/3)      ║
║  Sandbox Isolation                                ──► 100% PASS (5/5)      ║
║  Negative Syntax / Semantic Cases                ──► 100% PASS (10/10)    ║
║  Deterministic Fuzzing                            ──► 100% PASS (530/530)  ║
║  Differential Backend Parity                     ──► 100% PASS (10/10)    ║
║  Node.js ES2022 Conformance                       ──► 100% PASS (8/8)      ║
║  Rust 2021 Borrow-Check                           ──► 100% PASS (8/8)      ║
║  C++20 Native Conformance                         ──► 100% PASS (8/8)      ║
║  Edge-Case Regression                             ──► 100% PASS (138/138)  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### Conformance Matrix

| Pipeline | Target         |    Gate    | Conformance            |
| :------- | :------------- | :--------: | :--------------------- |
| `hecpp`  | C++20          | **Gate 8** | 🔒 Frozen / Production |
| `hejs`   | Node.js ES2022 | **Gate 8** | 🔒 Frozen / Production |
| `hepy`   | Python 3       | **Gate 8** | 📐 Reference Semantics |
| `hers`   | Rust 2021      | **Gate 6** | 🟡 Conformance Probe   |

---

## `09` — Diagnostics

Nyx's diagnostic subsystem is designed around precise source spans and stable error identifiers.

```text
error[E1302]: ambiguous symbol collision

  --> src/example.nyx:14:9
   |
14 |     use value
   |         ^^^^^
   |
   = multiple symbols resolve to the same identifier
```

Diagnostic codes allow tooling and developers to reason about compiler failures without relying exclusively on human-readable messages.

The documented diagnostic catalog spans:

```text
E1000 ─────────────────────────────── E2006
```

See [`ERROR_REFERENCE.md`](ERROR_REFERENCE.md) for the complete catalog.

---

## `10` — Project Structure

```text
nyx/
│
├── assets/
│   └── logo.svg
│
├── install.ps1
├── install.sh
│
├── GETTING_STARTED.md
├── INSTALLATION.md
├── LANGUAGE_REFERENCE.md
├── CLI_REFERENCE.md
├── ERROR_REFERENCE.md
├── CHANGELOG.md
├── LICENSE
└── README.md
```

The structure shown here is limited to files explicitly established by the project documentation rather than guessing undocumented internal directories.

---

## `11` — Documentation

| Document                                         | Description                       |
| :----------------------------------------------- | :-------------------------------- |
| [`GETTING_STARTED.md`](GETTING_STARTED.md)       | Architecture and initial workflow |
| [`INSTALLATION.md`](INSTALLATION.md)             | Toolchain installation and setup  |
| [`LANGUAGE_REFERENCE.md`](LANGUAGE_REFERENCE.md) | Language reference and grammar    |
| [`CLI_REFERENCE.md`](CLI_REFERENCE.md)           | CLI commands and diagnostics      |
| [`ERROR_REFERENCE.md`](ERROR_REFERENCE.md)       | Diagnostic error catalog          |
| [`CHANGELOG.md`](CHANGELOG.md)                   | Release history                   |

---

## `12` — Contributing

Contributions are welcome.

When contributing to Nyx:

1. Keep changes focused and easy to review.
2. Preserve deterministic compiler behavior.
3. Add regression coverage for language or compiler changes.
4. Validate affected backends before submitting a pull request.
5. Keep diagnostics precise and consistent.
6. Update relevant documentation for user-facing changes.
7. Avoid introducing dependencies or architecture changes without a clear reason.

For larger architectural changes, discuss the design before implementing a substantial change.

### Pull Request Checklist

```text
[ ] Change is focused
[ ] Existing behavior is preserved where intended
[ ] Relevant verification suites pass
[ ] Backend-specific behavior has been checked
[ ] Documentation has been updated
[ ] No unnecessary dependencies were introduced
```

---

## `13` — License

Nyx is distributed under the **MIT License**.

See [`LICENSE`](LICENSE) for the complete license text.

---

<div align="center">

  <br/>

  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:05070A,50:0E1318,100:00F0FF&height=100&section=footer" width="100%" alt="Nyx footer"/>

  <br/>

  <sub>
    Maintained by <b>Nyx Systems Core</b>
  </sub>

<br/><br/>

  <sub>
    Deterministic compilation. Multiple targets. One language.
  </sub>

</div>
