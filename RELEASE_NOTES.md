# Nyx v4.0.0 — Nirvana

Nyx v4.0.0 establishes the stable language and toolchain contract for the
compiler-focused v4 line. It incorporates the unpublished RC3 work into Nirvana.
The stable semantic set is C++20/native, JavaScript, and Python. Rust,
WebAssembly, React, and assembly remain available under their explicit beta
capability contracts; this release does not promote those backends to stable.

These notes are prepared for publication. The exact release revision, platform
validation, and artifact evidence are tracked in the
[Nirvana release checklist](docs/internals/RELEASE_AUDIT_v4.0.0.md).

## Highlights

- Self-host lexing decodes the source into code points once, avoiding repeated
  whole-source scans. Generated C++ string literals retain their full UTF-8
  byte length, including combining characters and embedded NULs.
- Stable backends agree on empty/out-of-range string indexing and code-point
  length methods, backed by focused runtime regressions.
- Nyx-authored lexer, parser, type checker, typed-HIR lowerer, and C++ emitter
  remain reproducible through the native stage-1 -> stage-2 -> stage-3 chain.
- Rust 2021 now lowers postfix `?` through typed HIR and runs active `defer`
  expressions in LIFO order before an early `Err` return.
- JavaScript builds support import-safe ES2022 `.mjs` output with explicit
  exports and no implicit `main()` side effect.
- WebAssembly adds deterministic borrowed scalar-struct parameters, typed JS
  object marshalling, generated TypeScript interfaces, and explicit
  array/struct ABI capability metadata.
- `nyx build --target wasm --wasi` emits WASI preview1 executables with
  `fd_write`, `_start`, and UTF-8 string stdout support.
- Unsupported advanced semantics are rejected through capability-derived
  `E3001` diagnostics instead of target-specific silent approximations.
- Tour of Nyx grows from 67 to 81 verified exercises across 21 modules, adding
  payload enums, Result propagation, collection transforms, async task
  semantics, Unicode expressions, and real standard-library boundaries.
- The browser example suite expands the typed `std/web` Canvas surface while
  keeping generated adapters as the host bridge.
- The stable HIR runtime trio (`cpp`, `js`, `python`) retains shared typed-HIR
  semantics, including independent Array/Struct value copies and code-point
  based Unicode string length, indexing, and iteration. Rust, WASM, React, and
  assembly remain governed by their explicit capability contracts.
- The release includes native-first installers, a local VS Code `.vsix`,
  deterministic source archives, checksums, an SPDX SBOM, and GitHub provenance
  attestations once the tagged workflow completes.

## Scope

The Maya scope reset remains in force. Microcontroller/freestanding firmware,
board profiles, flashing, and physical HAL modules are not part of Nyx v4.
The active scope is compiler correctness, HIR parity, self-hosting, native and
WebAssembly output, readable syntax, diagnostics, and deterministic tooling.

## Install Nirvana

The following pinned commands become available when the `v4.0.0` tag and
matching release assets are published.

### Windows PowerShell

```powershell
$env:NYX_RELEASE_TAG = 'v4.0.0'; irm https://raw.githubusercontent.com/justsomeone-e/nyx/v4.0.0/install.ps1 | iex
```

### Linux / macOS

```bash
curl -fsSL https://raw.githubusercontent.com/justsomeone-e/nyx/v4.0.0/install.sh | NYX_RELEASE_TAG=v4.0.0 bash
```

For a reviewed installation path, download the matching release archive, inspect
the installer, verify `SHA256SUMS`, then run it locally.

## Validation

- The maintainer reported 48/48 suites and the 138/138 regression battery
  passing after the self-host UTF-8 fixes. Later string boundary and length
  method fixes passed targeted C++/JavaScript/Python runtime tests. The full
  suite must be rerun on the final release revision; these are separate results.
- Release gates include the 138-point regression battery, 530-case fuzz corpus,
  Python/Nyx HIR byte parity, Rust/JS/WASM backend conformance, Bundle/host ABI
  runtime conformance, all 81 Tour exercises, deterministic package locks, and
  native self-host reproducibility.
- The tagged GitHub Actions workflow validates the release on Windows, Linux,
  Intel macOS, and ARM macOS and
  produces the platform artifacts. Treat published checksums and attestations
  from that workflow as the release evidence.

## After Nirvana

v4.0.x carries compatible fixes. v4.5.0 prepares tooling, libraries, measured
performance improvements, and v5 migration guidance while preserving the v4
source, HIR, and ABI contracts. New backend experiments and breaking designs
are tracked separately from the stable v4 promise.
