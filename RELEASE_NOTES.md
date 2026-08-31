# Nyx v4.0.0-dev.2 — Maya Scope Reset

This development release removes the microcontroller and freestanding firmware
platform from the active Nyx v4 codebase. Historical releases and Git history
still preserve the deleted implementation.

## What was removed

- STM32F1/F4, Nucleo, RP2040, AVR, generic embedded, and freestanding targets.
- Board profiles and custom board manifests.
- STM32Cube/CMSIS discovery and integration.
- Startup, linker, CRT, and HAL assets used to produce ELF/HEX/BIN firmware.
- Firmware flashing through STM32CubeProgrammer and OpenOCD.
- Physical hardware modules for board, GPIO, ADC, PWM, SPI, I2C, serial, timer,
  interrupts, and MMIO.
- Embedded-only syntax and APIs: `volatile`, `interrupt`, `critical`,
  `Buffer<T, N>`, and `buffer_ptr`.
- Hardware-specific fixtures, regression suites, VS Code snippets, completions,
  and documentation.

## Why it was removed

Nyx was attempting to maintain the language, seven application backends,
self-hosting, IDE tooling, a standard library, and a broad physical-board
platform simultaneously. The firmware layer had become too large to maintain
without weakening work on compiler correctness.

Dev.2 intentionally narrows v4 toward typed HIR, native and WebAssembly output,
self-hosting, readable Nim/Haxe-inspired syntax, diagnostics, package tooling,
and deterministic cross-backend behavior. Fixed-size collections can return in
the future only as a target-neutral language feature with a dedicated RFC.

## What remains

- Seven targets: C++20, JavaScript, Python, Rust, WebAssembly, React, and x86_64 assembly.
- Nyx-authored lexer, parser, type checker, HIR lowerer, and C++ emitter.
- Reproducible native stage-1 to stage-2 self-hosting.
- Bundle ABI v1, compiler/plugin APIs, LSP, VS Code integration, and native-first installers.
- A canonical 43-keyword language surface shared by the compiler and editor.

## Validation

- Exact Python/Nyx frontend parity and 184-case canonical HIR byte parity.
- 530 fuzz cases with zero unhandled compiler crashes.
- Python, JavaScript, C++20, and Rust backend conformance.
- Clean-environment smoke, installer, LSP, FFI, SDK, interop, and packaging suites.
- 138/138 exhaustive regression tests passed.

Nyx v4 has not reached beta, RC1, or the Nirvana stable release. This is the
latest active development snapshot.

