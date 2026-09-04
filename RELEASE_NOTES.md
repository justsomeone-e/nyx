# Nyx v4.0.0-rc.2 — Bodhi

Nyx v4.0.0-rc.2 is the WebAssembly/browser release candidate for the
compiler-focused v4 line. It is intended for evaluation, compatibility testing, and feedback;
it is not the `v4.0.0 Nirvana` stable release and does not freeze every public
API.

## Highlights

- Nyx-authored lexer, parser, type checker, typed-HIR lowerer, and C++ emitter
  remain reproducible through the native stage-1 -> stage-2 -> stage-3 chain.
- `nyx build --target wasm` and `nyx bundle` emit valid WAT/WASM, a grow-safe
  ES2022 loader, pointer-free TypeScript declarations, and optional npm package
  metadata in one compiler pass.
- The versioned `nyx_host_v1` import contract powers typed `std/web` DOM,
  event, lifecycle, and Canvas operations with a checked host ABI.
- npm bundles can include React 19, Vue 3, and Svelte 5 adapters. The pure-Nyx
  browser Pong example exercises keyboard input and animation without handwritten
  application JavaScript.
- Local path dependencies resolve recursively into deterministic, content-hashed
  lock entries with cycle diagnostics.
- Transparent aliases now type-check identically in the Python and Nyx-authored
  frontends.
- The stable HIR runtime trio (`cpp`, `js`, `python`) retains shared typed-HIR
  semantics. Rust, WASM, React, and assembly remain governed by their explicit
  capability contracts.
- The release includes native-first installers, a local VS Code `.vsix`,
  deterministic source archives, checksums, an SPDX SBOM, and GitHub provenance
  attestations once the tagged workflow completes.

## Scope

The Maya scope reset remains in force. Microcontroller/freestanding firmware,
board profiles, flashing, and physical HAL modules are not part of Nyx v4 RC2.
The active scope is compiler correctness, HIR parity, self-hosting, native and
WebAssembly output, readable syntax, diagnostics, and deterministic tooling.

## Install RC2

### Windows PowerShell

```powershell
$env:NYX_RELEASE_TAG = 'v4.0.0-rc.2'; irm https://raw.githubusercontent.com/justsomeone-e/nyx/v4.0.0-rc.2/install.ps1 | iex
```

### Linux / macOS

```bash
curl -fsSL https://raw.githubusercontent.com/justsomeone-e/nyx/v4.0.0-rc.2/install.sh | NYX_RELEASE_TAG=v4.0.0-rc.2 bash
```

For a reviewed installation path, download the matching release archive, inspect
the installer, verify `SHA256SUMS`, then run it locally.

## Validation

- The unified local test framework passed completely.
- Release gates include the 138-point regression battery, 530-case fuzz corpus,
  Python/Nyx HIR byte parity, Bundle/host ABI runtime conformance, deterministic
  package locks, and native self-host reproducibility.
- The tagged GitHub Actions workflow validates the full release candidate and
  produces the platform artifacts. Treat published checksums and attestations
  from that workflow as the release evidence.
