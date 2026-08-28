# Nyx — Unified Architecture & Backend Quality Gates

## 1. Unified Versioning Standard

Nyx uses a **single, unified versioning model**. The language version applies to the entire compiler and standard ecosystem. Backends declare **Stability States**, not fragmented version numbers.

```text
Nyx Core v4.0 (Unified Language Specification)
├── Backend API Contract v4.0
│     ├── hepy  [ 📐 REFERENCE ] : Pure Python Canonical Semantic Engine (Gate 8)
│     ├── hecpp [ 🔒 STABLE    ] : Native C++20 Clang/G++ Pipeline (Gate 8)
│     ├── hejs  [ 🔒 STABLE    ] : JavaScript ES2022 / Node.js Engine (Gate 8)
│     └── hers  [ 🟡 GATE 4    ] : Rust 2021 Safe Ownership Engine (Active Conformance)
└── Unified Toolchain & Package Manager (`he.toml` & `he.lock`)
```

---

## 2. The 8-Stage Backend Quality Gate

To achieve `🔒 STABLE / FROZEN` status, every backend must pass all 8 gates sequentially:

| Stage | Gate Name | Verification Criteria | Status for `hers` |
|---|---|---|---|
| **Gate 1** | **Syntax & AST Mapping** | AST nodes map 1:1 to target constructs without syntactic distortion. | 🟢 **Passed** |
| **Gate 2** | **Semantic & Ownership Compatibility** | Value semantics, copy/clone, mutability, and scopes align with specification. | 🟢 **Passed** |
| **Gate 3** | **Target Codegen** | Emits clean, idiomatic, warning-free target source code. | 🟢 **Passed** |
| **Gate 4** | **Native Compiler / Object Verification** | Compiles via native host compiler (`rustc`) without type or borrow errors. | 🟢 **Passed** |
| **Gate 5** | **Negative Error Rejection** | Rejects invalid semantic programs at compiler frontend with exact error codes. | 🔴 **In Progress** |
| **Gate 6** | **Fuzzing Resilience** | Zero unhandled compiler panics or crashes across 500+ randomized inputs. | 🔴 **In Progress** |
| **Gate 7** | **Differential Runtime Parity** | Native executable stdout matches `hepy` reference output across edge cases. | 🔴 **Pending Linker** |
| **Gate 8** | **Conformance & Spec Freeze** | Passes full regression battery; backend transitions to maintenance mode. | 🔴 **Target** |

---

## 3. Quad-Backend Status & Verification Matrix

| Target Driver | Target Platform | Stability Status | Verification Method |
|---|---|---|---|
| **`hepy`** | Python 3.10+ | 📐 **REFERENCE (Gate 8)** | Semantic Baseline & Master Differential Oracle |
| **`hecpp`** | C++20 | 🔒 **STABLE / FROZEN (Gate 8)** | C++20 End-to-End Conformance Harness |
| **`hejs`** | JS ES2022 / Node.js | 🔒 **STABLE / FROZEN (Gate 8)** | Node.js v24 Runtime Output Parity (`hepy == hejs`) |
| **`hers`** | Rust 2021 Edition | 🟡 **GATE 4 (Active Conformance)** | `rustc` MIR, Typecheck & Borrow-Check Object Pipeline |
| **`hereact`** | React JSX | 📋 **TOOLING LAYER** | UI Component Code Generator |
| **`hewasm`** | WebAssembly (WAT) | 📋 **BACKLOG** | Low-level WASM Linear Memory Engine |
