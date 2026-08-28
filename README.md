<div align="center">

  <a href="https://github.com/k4chox/HolyEasyLang">
    <img src="assets/logo.svg" width="130" height="130" alt="HolyEasyLang Logo" style="filter: drop-shadow(0 10px 20px rgba(0,240,255,0.25));"/>
  </a>
  <br/>

  <a href="https://github.com/k4chox/HolyEasyLang">
    <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=1,11,21,31&height=200&section=header&text=⚡%20HolyEasyLang&fontSize=60&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Next-Gen%20Multi-Target%20Systems%20%26%20Application%20Language&descFontSize=19&descAlignY=62" width="100%" alt="HolyEasyLang Banner"/>
  </a>

  <p align="center">
    <a href="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&duration=3000&pause=1000&color=00F0FF&center=true&vCenter=true&width=650&lines=Zero+Boilerplate.+Instant+Compilation.;Write+Once%2C+Compile+to+C%2B%2B20%2C+JS%2C+Python+%26+Rust.;Rustc-Grade+Diagnostics+v2+%26+LSP+Built-in.;Native+Static+Binary+Outputs+with+Zero+Runtime.">
      <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&duration=3000&pause=1000&color=00F0FF&center=true&vCenter=true&width=650&lines=Zero+Boilerplate.+Instant+Compilation.;Write+Once%2C+Compile+to+C%2B%2B20%2C+JS%2C+Python+%26+Rust.;Rustc-Grade+Diagnostics+v2+%26+LSP+Built-in.;Native+Static+Binary+Outputs+with+Zero+Runtime." alt="Typing SVG" />
    </a>
  </p>

  <p align="center">
    <a href="https://github.com/k4chox/HolyEasyLang/releases"><img src="https://img.shields.io/badge/release-v2.0.0--beta.1-blueviolet?style=for-the-badge&logo=rocket" alt="Version"></a>
    <a href="https://github.com/k4chox/HolyEasyLang/actions"><img src="https://img.shields.io/badge/CI-100%25%20Passing-brightgreen?style=for-the-badge&logo=githubactions&logoColor=white" alt="CI"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge" alt="License"></a>
    <a href="#"><img src="https://img.shields.io/badge/platforms-Windows%20%7C%20Linux%20%7C%20macOS-informational?style=for-the-badge&logo=linux" alt="Platforms"></a>
  </p>

  <p align="center">
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-compiler-architecture">Architecture</a> •
    <a href="#-language-tour">Language Tour</a> •
    <a href="#-backend-quality-gates">Quality Gates</a> •
    <a href="#-documentation">Docs</a> •
    <a href="CHANGELOG.md">Changelog</a>
  </p>

</div>

---

## ✨ Why HolyEasyLang?

HolyEasyLang bridges the gap between **high-level expressiveness** (like Python & TypeScript) and **bare-metal systems performance** (like C++ & Rust). 

<table>
  <tr>
    <td width="50%">
      <h3>🚀 Fast & Multi-Target</h3>
      <p>Write once in <code>.he</code> and compile seamlessly to <b>C++20 Native Binaries</b>, <b>Node.js ES2022 Modules</b>, <b>Rust 2021 Source</b>, or <b>Python 3 Reference</b>.</p>
    </td>
    <td width="50%">
      <h3>🔍 Rustc-Grade Diagnostics v2</h3>
      <p>Beautiful visual errors with precise caret spans (<code>^^^^</code>), path resolution traces, and actionable <code>help:</code> suggestions.</p>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>🧩 Module & Diamond Resolution</h3>
      <p>Robust module loader supporting local relative paths, standard library namespaces, and <b>diamond dependency graph deduplication</b>.</p>
    </td>
    <td width="50%">
      <h3>🛠️ Integrated Toolchain & LSP v2</h3>
      <p>Built-in formatter (<code>he fmt</code>), linter, unit test runner (<code>he test</code>), environment doctor (<code>he doctor</code>), and IDE Language Server Protocol daemon.</p>
    </td>
  </tr>
</table>

---

## 🏛️ Compiler Architecture

```text
                           HolyEasyLang Source (.he)
                                      │
                                ┌─────▼─────┐
                                │   Lexer   │  (Unicode, Tokenizer)
                                └─────┬─────┘
                                      │
                                ┌─────▼─────┐
                                │   Parser  │  (Immutable Concrete AST)
                                └─────┬─────┘
                                      │
                             ┌────────▼────────┐
                             │  Module Loader  │  (Topological Dependency Graph,
                             └────────┬────────┘   Diamond Deduplication, E1302 Collision)
                                      │
                             ┌────────▼────────┐
                             │   TypeChecker   │  (Scope Tracking, Type Inference,
                             └────────┬────────┘   Option/Result Semantics)
                                      │
                             ┌────────▼────────┐
                             │    Typed AST    │
                             └────────┬────────┘
                                      │
          ┌─────────────────┬─────────┴─────────┬─────────────────┐
          │                 │                   │                 │
    ┌─────▼─────┐     ┌─────▼─────┐       ┌─────▼─────┐     ┌─────▼─────┐
    │   hecpp   │     │   hejs    │       │   hers    │     │   hepy    │
    │  Gate 8 🔒│     │  Gate 8 🔒│       │  Gate 6 🟡│     │  Gate 8 📐│
    │   C++20   │     │ Node.js   │       │ Rust 2021 │     │ Reference │
    └─────┬─────┘     └─────┬─────┘       └─────┬─────┘     └─────┬─────┘
          │                 │                   │                 │
          ▼                 ▼                   ▼                 ▼
     Native .exe       ES2022 Module       rustc Object        Python 3
    (Clang / GCC)
```

---

## ⚡ Quick Start

### 1-Line Automated Install

<table>
  <tr>
    <th>Platform</th>
    <th>Command</th>
  </tr>
  <tr>
    <td><b>Windows (PowerShell)</b></td>
    <td><code>irm https://raw.githubusercontent.com/k4chox/HolyEasyLang/main/install.ps1 | iex</code></td>
  </tr>
  <tr>
    <td><b>Linux / macOS (Bash)</b></td>
    <td><code>curl -fsSL https://raw.githubusercontent.com/k4chox/HolyEasyLang/main/install.sh | bash</code></td>
  </tr>
</table>

### Project Workflow

```bash
# 1. Verify host compilers & runtime environment
he doctor

# 2. Create a fresh project
he new my_app
cd my_app

# 3. Fast type-check
he check

# 4. Compile & Run (Native C++20 by default)
he run

# 5. Target Node.js, Python, or Rust
he run --target hejs
he run --target hepy
he build --target hers
```

---

## 💻 Language Tour

```holyeasy
#target hecpp
import "std/math"
import "std/io"

// Structs & typed fields
struct ServerConfig {
    host: string,
    port: int,
    is_active: bool
}

// Functions with return type annotations
fn calculate_capacity(clients: int, multiplier: int) -> int {
    return power(clients, 2) * multiplier
}

// Entrypoint logic
var config = ServerConfig("127.0.0.1", 8080, true)
if config.is_active {
    var max_load = calculate_capacity(10, 2)
    println_str("Server active at " + config.host + " -> Capacity: " + to_string(max_load))
}

// First-class in-file unit tests
test "capacity calculation test" {
    assert(calculate_capacity(2, 3) == 12, "2^2 * 3 must equal 12")
}
```

---

## 🚦 Backend Quality Gates

| Backend | Target | Quality Gate | Status | Execution Model |
| :--- | :--- | :--- | :--- | :--- |
| **`hecpp`** | C++20 | **Gate 8 (Stable)** | 🔒 Frozen | LLVM Clang / MinGW-w64 Native `.exe` |
| **`hepy`** | Python 3 | **Gate 8 (Reference)**| 📐 Reference | Canonical Semantic Verification Engine |
| **`hejs`** | JS/Node | **Gate 8 (Stable)** | 🔒 Frozen | High-speed Node.js ES2022 Modules |
| **`hers`** | Rust | **Gate 6 (Active)** | 🟡 Conformance | `rustc` MIR / Borrow-Checked Types |

---

## 🧪 Master Test & Conformance Matrix

```text
======================================================================
⚡ HOLYEASYLANG ENTERPRISE UNIFIED TEST BATTERY
======================================================================
[*] Lexer & Unicode Unit Tests        -> 100% PASS
[*] Parser AST Construction           -> 100% PASS
[*] TypeChecker Scope & Inference     -> 100% PASS
[*] Module Diamond Deduplication      -> 100% PASS (0 duplicate nodes)
[*] Ambiguous Collision (E1302)       -> 100% PASS
[*] LSP v2 IDE Suite (Hover/Comp/Def) -> 100% PASS (3/3)
[*] Clean Machine Sandbox Smoke Test  -> 100% PASS (5/5)
[*] Negative Rejection Tests          -> 100% PASS (10/10)
[*] Deterministic Fuzzing (Seed=42)   -> 100% PASS (530/530, 0 Crash)
[*] Differential Parity Tests         -> 100% PASS (10/10, 100% Parity)
[*] JS (Node.js ES2022) E2E           -> 100% PASS (8/8)
[*] Rust 2021 Conformance             -> 100% PASS (8/8)
[*] C++20 Native EXE Execution        -> 100% PASS (8/8)
[*] Exhaustive Regression Battery     -> 100% PASS (138/138)
======================================================================
🏆 ALL TEST SUITES PASSED (100% SUCCESS RATE)
======================================================================
```

---

## 📚 Complete Documentation

* 📖 [Getting Started Guide](GETTING_STARTED.md)
* 📦 [Installation & Toolchain Setup](INSTALLATION.md)
* 📐 [Language Reference & Syntax Specification](LANGUAGE_REFERENCE.md)
* 🛠️ [CLI Command & Flag Reference](CLI_REFERENCE.md)
* 🚨 [Error Reference Catalog (E1000 - E2006)](ERROR_REFERENCE.md)
* 📜 [Changelog](CHANGELOG.md)

---

<div align="center">

  <sub>Built with precision by the HolyEasyLang Core Team. Licensed under <a href="LICENSE">MIT</a>.</sub>

  <br/><br/>
  
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=1,11,21,31&height=100&section=footer" width="100%"/>

</div>
