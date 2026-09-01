# Nyx v4.0.0-rc.1 — Samsara

Nyx v4.0.0-rc.1 is the first public release candidate for the compiler-focused
v4 line. It is intended for evaluation, compatibility testing, and feedback;
it is not the `v4.0.0 Nirvana` stable release and does not freeze every public
API.

## Highlights

- Nyx-authored lexer, parser, type checker, typed-HIR lowerer, and C++ emitter
  remain reproducible through the native stage-1 -> stage-2 -> stage-3 chain.
- Default arguments now lower consistently through the Python and self-hosted
  paths, including calls that omit trailing defaulted parameters.
- Flat array and struct destructuring is available with single-evaluation
  semantics, checked bounds/arity failures, const bindings, and hygienic
  compiler temporaries.
- The stable HIR runtime trio (`cpp`, `js`, `python`) retains shared typed-HIR
  semantics. Rust, WASM, React, and assembly remain governed by their explicit
  capability contracts.
- The release includes native-first installers, a local VS Code `.vsix`,
  deterministic source archives, checksums, an SPDX SBOM, and GitHub provenance
  attestations once the tagged workflow completes.

## Scope

The Maya scope reset remains in force. Microcontroller/freestanding firmware,
board profiles, flashing, and physical HAL modules are not part of Nyx v4 RC1.
The active scope is compiler correctness, HIR parity, self-hosting, native and
WebAssembly output, readable syntax, diagnostics, and deterministic tooling.

## Install RC1

### Windows PowerShell

```powershell
$env:NYX_RELEASE_TAG = 'v4.0.0-rc.1'; irm https://raw.githubusercontent.com/justsomeone-e/nyx/v4.0.0-rc.1/install.ps1 | iex
```

### Linux / macOS

```bash
curl -fsSL https://raw.githubusercontent.com/justsomeone-e/nyx/v4.0.0-rc.1/install.sh | NYX_RELEASE_TAG=v4.0.0-rc.1 bash
```

For a reviewed installation path, download the matching release archive, inspect
the installer, verify `SHA256SUMS`, then run it locally.

## Validation

- The unified local test framework passed completely.
- 138/138 regression battery, 530-case fuzz corpus, 194-case Python/Nyx HIR
  byte parity, default arguments, destructuring, and native self-host
  reproducibility all passed.
- The tagged GitHub Actions workflow validates the full release candidate and
  produces the platform artifacts. Treat published checksums and attestations
  from that workflow as the release evidence.
