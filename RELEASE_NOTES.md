# Nyx v5.0.1 — Daydream

Nyx v5.0.1 is a Windows and native self-host reliability patch for the stable
Daydream compiler line. It fixes the failures reported in issue #6 without
changing the v5 language, Typed HIR v1, Bundle ABI v1, or backend maturity
contracts.

## Fixed

- The Nyx-authored type checker now registers C++ foreign-import aliases before
  checking function bodies, so `examples/07_foreign_cpp.nyx` recognizes `fs`.
- Optional `null` values now lower to `std::nullopt` instead of `nullptr` in the
  self-hosted C++ emitter.
- Generated C++ defines `_CRT_SECURE_NO_WARNINGS` before CRT headers, avoiding
  MSVC and clang-cl `getenv` deprecation diagnostics.
- `examples/04_in_file_tests.nyx` now checks the actual `"Holy Easy"`
  concatenation result, allowing all three in-file tests to run.
- The Windows installer prefers `npm.cmd` or `npm.exe` when PowerShell blocks
  `npm.ps1`, and an optional VS Code extension failure no longer aborts the core
  compiler installation.
- Installation docs now distinguish the release compiler `nyxc.exe` from the
  installer-created unified command `nyx.cmd`; no separate `nyx.exe` asset is
  expected.

## Install

### Windows PowerShell

    $env:NYX_RELEASE_TAG = 'v5.0.1'; irm https://raw.githubusercontent.com/justsomeone-e/nyx/v5.0.1/install.ps1 | iex

### Linux / macOS

    curl -fsSL https://raw.githubusercontent.com/justsomeone-e/nyx/v5.0.1/install.sh | NYX_RELEASE_TAG=v5.0.1 bash

## Verification

A freshly built standalone native compiler compiled and executed all three
reported examples successfully on Windows. The tagged GitHub Actions workflow
is authoritative for the complete regression battery, Stage1 → Stage2 → Stage3
reproducibility, Python/Nyx canonical Typed HIR parity, four-platform native
binaries, VSIX, checksums, SBOM, and provenance.

C++20, JavaScript, and Python remain stable backends. LLVM and C17 remain
explicitly experimental.
