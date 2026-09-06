# Nyx v5.0.0-rc.1 — Daydream

Daydream is the first release candidate for the Nyx v5 compiler line. It keeps
the stable C++20, JavaScript, and Python contracts intact while moving direct
LLVM IR generation from an isolated scalar pilot into the canonical compiler
and CLI pipeline.

## Highlights

- The LLVM build command emits the exact .ll artifact passed to Clang and
  produces a native executable without a C++ source-code hop.
- The LLVM run command compiles and executes that LLVM IR through the host
  Clang toolchain.
- The experimental LLVM backend supports signed 64-bit wrapping arithmetic,
  IEEE binary64 values, booleans, functions, recursion, structured control
  flow, scalar-field structs, and stack-owned scalar arrays.
- Supported Arrays have checked indexing, independent local copies,
  function-boundary value copies through llvm.memcpy, length methods, and
  for iteration with break and continue.
- Multi-argument print lowers to valid LLVM IR with C++-backend output parity.
- Unsupported LLVM constructs fail through compiler diagnostics instead of
  silently falling back to C++.

## Maturity and limits

LLVM and C17 remain experimental backends. The default backend is still C++20.
The LLVM path does not yet cover escaping or returned Arrays, nested aggregates,
aggregate fields, exceptions, tasks, closures, complete standard-library
bindings, or the native self-hosted emitter. Python remains the stage-0
orchestration frontend for this experimental backend.

## Install

### Windows PowerShell

    $env:NYX_RELEASE_TAG = 'v5.0.0-rc.1'; irm https://raw.githubusercontent.com/justsomeone-e/nyx/v5.0.0-rc.1/install.ps1 | iex

### Linux / macOS

    curl -fsSL https://raw.githubusercontent.com/justsomeone-e/nyx/v5.0.0-rc.1/install.sh | NYX_RELEASE_TAG=v5.0.0-rc.1 bash

## Validation

The compiler API suite, direct LLVM suite, Python syntax checks, and real CLI
LLVM build/run smoke test passed locally. The tagged GitHub Actions workflow is
the authoritative source for the full regression battery, native self-host
reproducibility, four-platform binaries, VSIX, checksums, SBOM, and provenance.
Do not treat this release candidate as a stable LLVM backend.
