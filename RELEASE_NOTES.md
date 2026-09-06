# Nyx v5.0.0 — Daydream

Nyx v5.0.0 is the stable release of the Daydream compiler line. It preserves
the established C++20, JavaScript, Python, Typed HIR v1, and Bundle ABI v1
contracts while bringing direct LLVM IR generation into the canonical compiler
and CLI pipeline as an explicitly experimental backend.

## Highlights

- `nyx build -t llvm` emits the exact `.ll` artifact passed to Clang and builds
  a native executable without a C++ source-code hop.
- `nyx run -t llvm` compiles and executes that LLVM IR through the host Clang
  toolchain.
- The experimental LLVM path supports signed 64-bit wrapping arithmetic, IEEE
  binary64 values, booleans, functions, recursion, structured control flow,
  scalar-field structs, and stack-owned scalar arrays.
- Supported arrays use checked indexing, independent local and
  function-boundary value copies, length methods, and `for` iteration with
  `break` and `continue`.
- Unsupported LLVM constructs produce compiler diagnostics instead of silently
  falling back to C++.
- C++20 remains the default native backend. JavaScript and Python retain their
  stable contracts; every other backend keeps its documented capability and
  maturity level.

## LLVM and C17 maturity

LLVM and C17 remain experimental backends in v5.0.0. LLVM does not yet cover
escaping or returned arrays, nested aggregates, aggregate fields, exceptions,
tasks, closures, complete standard-library bindings, or the native self-hosted
emitter. Python remains the stage-0 orchestration frontend for these
experimental paths.

## Install

### Windows PowerShell

    $env:NYX_RELEASE_TAG = 'v5.0.0'; irm https://raw.githubusercontent.com/justsomeone-e/nyx/v5.0.0/install.ps1 | iex

### Linux / macOS

    curl -fsSL https://raw.githubusercontent.com/justsomeone-e/nyx/v5.0.0/install.sh | NYX_RELEASE_TAG=v5.0.0 bash

## Verification

The tagged GitHub Actions workflow is authoritative for the complete regression
battery, Stage1 → Stage2 → Stage3 reproducibility, Python/Nyx canonical Typed
HIR parity, four-platform native binaries, VSIX, checksums, SBOM, and
provenance. Stable refers to the Nyx v5 language and toolchain release; it does
not promote LLVM or C17 beyond their experimental contracts.
