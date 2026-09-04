# 📝 Nyx Changelog

All notable changes to the Nyx compiler, toolchain, and standard library are documented in this file.

---

## [4.0.0-rc.2] - 2026-09-04

### Bodhi release candidate

* Added complete `.wat`/`.wasm`/`.mjs`/`.d.ts` output to ordinary WASM builds.
* Added versioned `nyx_host_v1` imports and the typed `std/web` DOM, event,
  lifecycle, and Canvas API.
* Added npm-ready bundle manifests and React 19, Vue 3, and Svelte 5 adapters.
* Added pure-Nyx browser Pong and host-simulated runtime conformance tests.
* Expanded WASM lowering for host/internal calls, booleans, mutable globals,
  numeric arrays, collection loops, built-in `len()` methods, and conditional
  UTF-8 string results.
* Added recursive deterministic local path dependencies with slash-normalized
  manifests, source checksums, and cycle diagnostics.
* Made aliases transparently compatible in both the Python and Nyx-authored
  type checkers.

### Validation

* Bundle ABI v1, host ABI v1, framework artifact syntax, local package locks,
  canonical language surface, HIR parity, and native bootstrap remain direct
  release gates.

## [4.0.0-rc.1] - 2026-09-02

### Release candidate

* Promoted the compiler-focused v4 line to its first public release candidate,
  **Samsara**. This is an evaluation and soak release; `v4.0.0 Nirvana` remains
  the future stable milestone.
* Completed default-argument lowering in both frontends and the Nyx-authored
  HIR path, including omitted trailing arguments and required-argument
  diagnostics.
* Added flat array and struct destructuring declarations with single RHS
  evaluation, checked cardinality diagnostics, const preservation, and exact
  Python/Nyx HIR parity.
* Hardened destructuring lowering against user-identifier collisions and made
  top-level bounds failures deterministic across C++, JavaScript, and Python.
* Expanded typed standard-library, collection, fallible-result, and foreign
  binding test coverage; unsupported target behavior remains behind explicit
  capability gates rather than silently approximated.
* Updated the native compiler banner, VS Code package, documentation, and
  pinned installer instructions to one version source: `4.0.0-rc.1`.

### Validation

* The unified local test framework passed completely: self-host, 194-case HIR
  parity, backend runtime/compile gates, installer/LSP/fuzz checks, and the
  138-point regression battery.
* The tagged GitHub workflow is the source of release-asset checksums, SBOM,
  provenance, platform-native binaries, and the packaged VS Code extension.

## [4.0.0-dev.2] - 2026-08-31

### Scope reset: microcontroller support removed

* Removed STM32F1/F4, Nucleo, RP2040, AVR, generic embedded, and freestanding
  firmware targets from the backend registry and CLI.
* Removed board profiles, custom board manifests, STM32Cube/CMSIS resolution,
  linker/startup/runtime assets, firmware flashing, and ELF/HEX/BIN build paths.
* Removed the physical hardware standard-library surface: `std/board`,
  `std/gpio`, `std/adc`, `std/pwm`, `std/spi`, `std/i2c`, `std/serial`,
  `std/timer`, `std/interrupt`, and `std/mmio`.
* Removed embedded-only language residue from both Python and Nyx-authored
  frontends: `volatile`, `interrupt`, `critical`, `Buffer<T, N>`, and
  `buffer_ptr`. The canonical surface is now 43 keywords.
* Removed obsolete hardware fixtures, editor snippets/completions, documentation,
  and regression suites. Historical releases and Git history retain the deleted
  implementation.

### Why

Nyx was trying to maintain a language, seven application backends, self-hosting,
IDE tooling, and a broad physical-board platform simultaneously. The firmware
layer was larger than the project could support without weakening compiler
correctness. Dev.2 deliberately narrows v4 toward the compiler itself: typed HIR,
native/WASM output, self-hosting, readable Nim/Haxe-inspired syntax, diagnostics,
and deterministic tooling. Fixed-size collections may return later only through
a target-neutral language RFC.

### Validation

* Python/Nyx frontend and 184-case canonical HIR byte parity passed.
* 530 fuzz cases completed with zero unhandled compiler crashes.
* Python, JavaScript, C++20, and Rust backend conformance passed.
* VS Code/LSP, installer, FFI, SDK, interop, and clean-environment smoke suites passed.
* The 138-point exhaustive regression battery passed 138/138.

## [4.0.0-dev.1] - 2026-08-29

### Compiler architecture

* Nyx-authored lexer, parser, type checker, typed-HIR lowerer, and HIR C++
  emitter now form a reproducible native stage1 -> stage2 bootstrap.
* `cpp`, `js`, `python`, `rust`, and `wasm` consume canonical verified HIR;
  non-HIR targets retain beta or experimental status.
* The Rust 2021 emitter now preserves Nyx value semantics, strict Boolean
  boundaries, Option/Result lowering, lexical `defer`, and wrapping i64 code
  directly from HIR. Unsupported Task, exception, spawn, and channel semantics
  fail with `E3001`; beta status remains until runtime and Gate 8 evidence.
* Native-first installers provide `nyxc check`, `emit-cpp`, and `compile`
  without a Python runtime.

### Frozen v4 semantics

* 46 canonical keywords with `fn` as the sole function declaration spelling;
  embedded targets add `volatile`, `interrupt`, and `critical`.
* Signed i64 wrapping arithmetic, IEEE binary64, canonical scalar text, and
  optimizer/backend parity.
* Strict Boolean conditions, including runtime type checks at dynamic `any`
  boundaries.
* Verified trait contracts, shallow immutable bindings, reusable `Task<T>`,
  and exception propagation across awaits.
* Fixed-width scalar spellings and a first-class embedded control surface
  replace routine `#native raw` use for shared state and interrupt handlers.
* Embedded-only `Buffer<T, N>` adds allocation-free fixed storage, checked
  capacities/indexes, and pointer-length bulk-I/O interop without native code.
* Maya adds expression-bodied functions plus value-producing `if` and
  exhaustive literal `match` expressions. The Python and Nyx-authored
  frontends produce byte-identical HIR, and declared backends share the same
  branch typing and lazy evaluation rules.

### Embedded systems

* Data-driven Nucleo profiles, custom `board.toml`, STM32CubeProgrammer/OpenOCD
  command generation, and board connector aliases.
* Register-level STM32F4 GPIO, UART, SPI, I2C, ADC, PWM, timers, NVIC, and
  volatile MMIO APIs with bounded error paths and buffer-based bulk transfers.
* F410 now uses its real TIM5/TIM6 and IRQ map and rejects unavailable
  TIM2-backed PWM; F401/F411/F446 retain their board-specific timer maps.
* Standalone ELF/HEX/BIN builds for NUCLEO-F401RE, F410RB, F411RE, and F446RE.
* Official STM32Cube sparse installer/provider resolves CMSIS device selectors,
  startup assembly, system C, IRQ maps, and Nucleo linker scripts for 21 more
  profiles. Mixed C/C++/ASM compilation and GNU-ld/LLD normalization are covered
  by a 25-board ARM ELF/HEX/BIN integration matrix.
* A minimal weak CMSIS freestanding CRT supplies constructor arrays and memory
  primitives without overriding a user-configured libc/compiler runtime.
* Removed desktop HAL simulations that previously printed success without
  touching hardware.

### Release engineering

* Deterministic ZIP/TAR source archives from canonical Git blobs.
* Four native platform artifacts, SHA-256 manifests, SPDX 2.3 SBOM output,
  and signed GitHub provenance/SBOM attestations.

### CLI toolchain integrity

* `fmt`, `lint`, `debug`, `profile`, `doc`, `add`, `remove`, `install`, and
  `pkg` now propagate failure exit codes and are covered by real filesystem and
  process-effect tests.
* Formatting is string/comment-safe and idempotent; profiling measures an
  actual compile+run instead of printing synthetic routines; the source
  inspector no longer invents runtime variables or memory.
* Package commands mutate and verify `nyx.toml`/`nyx.lock` with explicit
  versions. RC1 intentionally exposes no remote registry fetch and says so.

## [2.0.0-beta.1] - 2026-08-28 (Beta 1 Public Release)

### 🚀 Major Additions
* **Multi-Backend Architecture**:
  * `cpp`: ISO C++20 backend frozen at Gate 8 (Production Native `.exe` via LLVM Clang / MinGW-w64).
  * `python`: Canonical reference evaluation engine.
  * `js`: Node.js ES2022 backend frozen at Gate 8.
  * `rust`: Rust 2021 active conformance backend (Gate 6).
* **Module & Import Altyapısı (`src/core/module_loader.py`)**:
  * Local relative imports (`import "./utils"`).
  * Standard library module imports (`import "std/math"`).
  * Selective symbol imports (`import { abs_val, power } from "std/math"`).
  * Diamond dependency deduplication ($A \to B, A \to C, B \to D, C \to D$).
  * Ambiguous symbol collision detection (`error[E1302]`).
* **Diagnostics v2 Standard**:
  * Rustc-style visual errors with dynamic span carets (`^^^^`), error catalog codes (`E1000` to `E2006`), `searched paths:`, `note:`, and actionable `help:`.
* **Standard Library Expansion (`src/stdlib/`)**:
  * `std/math.nyx` (`abs_val`, `max_val`, `min_val`, `power`, `clamp`, `gcd`, `sign`).
  * `std/str.nyx` (`is_empty_str`, `concat_three`, `wrap_with`, `contains_substring`).
  * `std/io.nyx` (`println_str`, `println_int`, `println_bool`, `prompt_input`).
  * `std/fs.nyx` (`join_paths`, `file_extension`, `is_source_file`).
* **Toolchain & Release Engineering**:
  * `nyx new`, `nyx init`, `nyx check`, `nyx build`, `nyx run`, `nyx test`, `nyx clean`, `nyx doctor`, `nyx lsp`.
  * `nyx.toml` project manifest and deterministic `nyx.lock` SHA256 locking.
  * Language Server Protocol v2 with autocomplete, hover signatures, and go-to-definition.
* **Test Verification**:
  * 138/138 Regression Battery (100%).
  * 10/10 Differential Parity across backends.
  * 530/530 Deterministic Fuzz cases (0 unhandled crashes).
  * 8/8 Native C++20 EXE conformance tests.
