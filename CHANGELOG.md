# 📝 HolyEasyLang Changelog

All notable changes to the HolyEasyLang compiler, toolchain, and standard library are documented in this file.

---

## [2.0.0-beta.1] - 2026-08-28 (Beta 1 Public Release)

### 🚀 Major Additions
* **Multi-Backend Architecture**:
  * `hecpp`: ISO C++20 backend frozen at Gate 8 (Production Native `.exe` via LLVM Clang / MinGW-w64).
  * `hepy`: Canonical reference evaluation engine.
  * `hejs`: Node.js ES2022 backend frozen at Gate 8.
  * `hers`: Rust 2021 active conformance backend (Gate 6).
* **Module & Import Altyapısı (`src/core/module_loader.py`)**:
  * Local relative imports (`import "./utils"`).
  * Standard library module imports (`import "std/math"`).
  * Selective symbol imports (`import { abs_val, power } from "std/math"`).
  * Diamond dependency deduplication ($A \to B, A \to C, B \to D, C \to D$).
  * Ambiguous symbol collision detection (`error[E1302]`).
* **Diagnostics v2 Standard**:
  * Rustc-style visual errors with dynamic span carets (`^^^^`), error catalog codes (`E1000` to `E2006`), `searched paths:`, `note:`, and actionable `help:`.
* **Standard Library Expansion (`src/stdlib/`)**:
  * `std/math.he` (`abs_val`, `max_val`, `min_val`, `power`, `clamp`, `gcd`, `sign`).
  * `std/str.he` (`is_empty_str`, `concat_three`, `wrap_with`, `contains_substring`).
  * `std/io.he` (`println_str`, `println_int`, `println_bool`, `prompt_input`).
  * `std/fs.he` (`join_paths`, `file_extension`, `is_source_file`).
* **Toolchain & Release Engineering**:
  * `he new`, `he init`, `he check`, `he build`, `he run`, `he test`, `he clean`, `he doctor`, `he lsp`.
  * `he.toml` project manifest and deterministic `he.lock` SHA256 locking.
  * Language Server Protocol v2 with autocomplete, hover signatures, and go-to-definition.
* **Test Verification**:
  * 138/138 Regression Battery (100%).
  * 10/10 Differential Parity across backends.
  * 530/530 Deterministic Fuzz cases (0 unhandled crashes).
  * 8/8 Native C++20 EXE conformance tests.
