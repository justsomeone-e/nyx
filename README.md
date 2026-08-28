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
    <a href="#tech-stack">TECH STACK</a> •
    <a href="#project-structure">STRUCTURE</a> •
    <a href="#getting-started">INSTALLATION</a> •
    <a href="#usage">USAGE</a> •
    <a href="#contributing">CONTRIBUTING</a> •
    <a href="#license">LICENSE</a>
  </p>

</div>

---

## Overview

**Nyx** is a compiled, statically typed systems programming language and multi-target toolchain designed around a deterministic compiler pipeline.

A single Nyx source program is parsed into a validated Abstract Syntax Tree and can then be emitted to multiple target environments:

* **C++20** for native executables
* **Node.js ES2022** for JavaScript execution
* **Rust 2021** for Rust-based compilation
* **Python 3** as a canonical semantic reference

Nyx separates language semantics from backend implementation through a shared canonical AST. This allows different targets to consume the same validated program representation rather than implementing independent frontend logic.

```text
Nyx Source
    │
    ▼
┌───────────────┐
│ Lexer         │
│ UTF-8 Tokens  │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Parser        │
│ Syntax AST    │
└───────┬───────┘
        │
        ▼
┌─────────────────────┐
│ Module Graph Loader │
│ Topological Dedup   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ TypeChecker         │
│ Inference / Scopes  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Canonical Typed AST │
└──────────┬──────────┘
           │
     ┌─────┼─────┬─────┐
     ▼     ▼     ▼     ▼
  hecpp  hejs   hers   hepy
   │      │      │      │
   ▼      ▼      ▼      ▼
 C++20  Node.js  Rust  Python
```

---

## Key Features

### Multi-Target Compilation

Nyx provides a single language frontend with multiple compilation targets:

| Target  | Output                    | Status    |
| :------ | :------------------------ | :-------- |
| `hecpp` | C++20 / Native executable | Stable    |
| `hejs`  | Node.js ES2022            | Stable    |
| `hers`  | Rust 2021                 | Active    |
| `hepy`  | Python 3                  | Reference |

### Deterministic Compiler Pipeline

The compiler operates through a deterministic sequence of frontend and semantic stages:

```text
Source
  → Lexing
  → Parsing
  → Module Resolution
  → Topological Ordering
  → Type Checking
  → Canonical AST
  → Backend Code Generation
```

### Topological Module Resolution

Nyx models module dependencies as a directed acyclic graph.

The module loader includes support for:

* Dependency ordering
* Diamond dependency deduplication
* Cycle detection
* Symbol collision detection
* Deterministic module processing

Relevant diagnostic codes include:

* `E1300` — dependency cycle
* `E1302` — ambiguous symbol collision

### Static Typing

Nyx performs semantic validation before backend generation, including:

* Type checking
* Type inference
* Scope handling
* Bounds validation
* Static invariants

### Diagnostics v2

The diagnostic subsystem provides source-aware compiler errors with precise spans.

```text
error[E1302]: ambiguous symbol collision

  --> src/module.nyx:14:9
   |
14 |     use value
   |         ^^^^^
   |
   = multiple symbols resolve to the same identifier
```

Diagnostics are designed to identify both the source location and the semantic reason for failure.

### Language Server Protocol

Nyx includes a built-in Language Server Protocol v2 JSON-RPC implementation for tooling integration.

### Verification Infrastructure

The project includes automated validation covering:

* Lexical analysis
* AST construction
* Static type invariants
* Module graph resolution
* Diagnostic behavior
* LSP RPC behavior
* Sandbox isolation
* Negative syntax and semantic cases
* Deterministic fuzzing
* Backend parity
* Node.js conformance
* Rust borrow-check conformance
* C++20 native conformance
* Edge-case regression testing

---

## Tech Stack

| Component               | Technology              |
| :---------------------- | :---------------------- |
| Native backend          | **C++20**               |
| JavaScript backend      | **Node.js / ES2022**    |
| Rust backend            | **Rust 2021**           |
| Reference backend       | **Python 3**            |
| Native compilation      | **LLVM Clang / GCC**    |
| Rust compilation        | **`rustc`**             |
| Language protocol       | **LSP v2 / JSON-RPC**   |
| Source encoding         | **Unicode UTF-8**       |
| Compiler representation | **Typed Canonical AST** |

Nyx is intentionally structured around a shared compiler representation so that backend implementations operate on validated semantic data instead of raw source text.

---

## Project Structure

The repository is organized around the compiler, language specification, installation tooling, and developer documentation.

```text
nyx/
├── assets/
│   └── logo.svg
│
├── install.ps1
├── install.sh
├── LICENSE
├── README.md
│
├── GETTING_STARTED.md
├── INSTALLATION.md
├── LANGUAGE_REFERENCE.md
├── CLI_REFERENCE.md
├── ERROR_REFERENCE.md
└── CHANGELOG.md
```

> The tree above intentionally lists only repository components explicitly documented by the project. Internal source directories are not inferred here.

---

## Getting Started

### Prerequisites

Nyx targets the following environments:

* Windows
* Linux
* macOS

The generated targets may additionally require their corresponding toolchains:

* **C++20:** Clang or GCC
* **Rust:** `rustc`
* **Node.js:** Node.js with ES2022 support
* **Python:** Python 3.10+

### Windows

Install Nyx through PowerShell:

```powershell
irm https://raw.githubusercontent.com/justsomeone-e/nyx/main/install.ps1 | iex
```

After installation, verify the environment:

```powershell
nyx doctor
```

### Linux / macOS

Install Nyx through the provided POSIX installer:

```bash
curl -fsSL https://raw.githubusercontent.com/justsomeone-e/nyx/main/install.sh | bash
```

Then verify the installation:

```bash
nyx doctor
```

### Initialize a Project

Create a new Nyx workspace:

```bash
nyx new core_engine
cd core_engine
```

Validate the project without generating a final target:

```bash
nyx check
```

---

## Usage

### Check a Project

Run semantic and type verification:

```bash
nyx check
```

This validates the source through the compiler's frontend and type-checking pipeline.

### Run a Native Build

The default execution target is the C++20 native backend:

```bash
nyx run
```

The resulting program is compiled through the available native C++ toolchain.

### Run the Node.js Backend

Generate and execute the Node.js ES2022 target:

```bash
nyx run --target hejs
```

### Run the Python Reference Backend

Use the canonical Python representation:

```bash
nyx run --target hepy
```

### Build the Rust Backend

Generate the Rust 2021 target:

```bash
nyx build --target hers
```

---

### Example Nyx Program

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

The example demonstrates:

* Target selection
* Module imports
* Typed structures
* Function declarations
* Explicit return types
* Variables
* Conditional execution
* Function calls
* Built-in tests
* Assertions

---

### Verification Status

The current verification battery reports the following results:

```text
Lexical Analyzer & UTF-8 Stream Suite       100% PASS
Syntactic AST Construction                  100% PASS
Static Type Invariant Checks                100% PASS
Topological Graph Deduplication             100% PASS
Ambiguous Symbol Collision (E1302)          100% PASS
Language Server Protocol RPC                100% PASS (3/3)
Clean Sandbox Isolation                     100% PASS (5/5)
Negative Syntax & Semantic Rejections       100% PASS (10/10)
Deterministic Fuzz Engine                   100% PASS (530/530)
Differential Backend Parity                 100% PASS (10/10)
Node.js ES2022 End-to-End                   100% PASS (8/8)
Rust 2021 Borrow-Check                     100% PASS (8/8)
C++20 Native Machine Code                  100% PASS (8/8)
Edge-Case Regression Battery               100% PASS (138/138)
```

---

### Documentation

Additional documentation is available in the repository:

* [Architecture & Getting Started](GETTING_STARTED.md)
* [Installation & Toolchain Setup](INSTALLATION.md)
* [Language Reference & Grammar](LANGUAGE_REFERENCE.md)
* [CLI Reference](CLI_REFERENCE.md)
* [Diagnostic Error Catalog](ERROR_REFERENCE.md)
* [Release Changelog](CHANGELOG.md)

---

## Contributing

Contributions are welcome.

Before submitting a change:

1. Read the relevant documentation for the compiler subsystem you are modifying.
2. Keep changes focused and avoid unrelated refactors.
3. Preserve deterministic compiler behavior.
4. Add or update verification coverage when changing language or compiler behavior.
5. Verify affected targets before opening a pull request.
6. Keep diagnostic behavior precise and source-aware.
7. Update documentation when introducing user-facing functionality.

For larger changes, open an issue first so the design and implementation can be discussed before significant work begins.

### Pull Requests

A useful pull request should include:

* A clear description of the change
* The reason for the change
* Relevant tests or verification results
* Documentation updates when applicable
* Any known limitations or target-specific differences

---

## License

Nyx is licensed under the **MIT License**.

See [`LICENSE`](LICENSE) for the complete license text.

---

<div align="center">
  <sub>Maintained by Nyx Systems Core.</sub>
</div>
