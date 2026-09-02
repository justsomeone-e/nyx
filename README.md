> [!IMPORTANT]
> ## Nyx v4.0.0-rc.1 is available
>
> **Samsara** is the first public release candidate for Nyx v4. It validates
> compiler correctness, reproducible self-hosting, native/WASM backends,
> language ergonomics, installers, and editor tooling. Microcontroller firmware
> support is outside the v4 scope. This is an RC, not the final **Nirvana**
> stable release.

<div align="center">

  <a href="https://github.com/justsomeone-e/nyx">
    <img src="assets/nyx-mark-dark.png?v=4.0.0-rc1" width="240" alt="nyx bird emblem"/>
  </a>
  <br/>
  <a href="https://github.com/justsomeone-e/nyx">
    <img src="assets/logo.svg?v=4.0.0-rc1" width="600" alt="nyx logotype"/>
  </a>
  <p align="center">
    <a href="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=20&duration=3000&pause=1200&color=00F0FF&center=true&vCenter=true&width=760&lines=One+Language.+Verified+HIR.+Multiple+Targets.;Native+nyxc+%7C+C%2B%2B20+%7C+Node.js+%7C+Python+%7C+WASM.;Reproducible+Self-Hosting+Without+a+Python+Runtime.;Deterministic+i64%2C+binary64%2C+UTF-8%2C+and+Diagnostics.">
      <img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=20&duration=3000&pause=1200&color=00F0FF&center=true&vCenter=true&width=760&lines=One+Language.+Verified+HIR.+Multiple+Targets.;Native+nyxc+%7C+C%2B%2B20+%7C+Node.js+%7C+Python+%7C+WASM.;Reproducible+Self-Hosting+Without+a+Python+Runtime.;Deterministic+i64%2C+binary64%2C+UTF-8%2C+and+Diagnostics." alt="Typing SVG" />
    </a>
  </p>

<p align="center">
    <a href="https://github.com"><img src="https://shields.io" alt="Version"></a>
    <a href="https://github.com"><img src="https://shields.io" alt="Release candidate"></a>
    <a href="https://github.com"><img src="https://shields.io" alt="AGPL-3.0 with Nyx Output Exception"></a>
    <a href="https://github.com"><img src="https://shields.io_|_WIN_|_MACOS-0E1318?style=for-the-badge&labelColor=05070A" alt="Platforms"></a>
</p>

  <p><strong>v4 path: MAYA (DEV) → SAMSARA (RC1) → BODHI (RC2) → MOKSHA (FINAL RC) → NIRVANA (STABLE)</strong></p>

  <p align="center">
    <a href="#overview">OVERVIEW</a> •
    <a href="#features">FEATURES</a> •
    <a href="#backends">BACKENDS</a> •
    <a href="#installation">INSTALL</a> •
    <a href="#vscode">VS CODE</a> •
    <a href="#bundle">BUNDLE</a> •
    <a href="#verification">VERIFICATION</a> •
    <a href="#documentation">DOCS</a>
  </p>

</div>

---

<div align="center">
  <img src="assets/terminal_animated.svg?v=4.0.0-rc1" width="92%" alt="nyx interactive live execution"/>
</div>

---

<a id="overview"></a>

## `01` — Overview

**Nyx** is a compiled, statically typed systems language and multi-target toolchain built around one verified semantic boundary: canonical typed **HIR v1**.

A source file is lexed, parsed, type-checked, lowered, verified, optimized, and only then handed to a backend. Stable backends do not reinterpret the AST independently, so one language contract drives native C++20, Node.js ES2022, and Python 3 output.

<div align="center">
  <img src="assets/pipeline_animated.svg?v=4.0.0-rc1" width="98%" alt="nyx compiler architecture pipeline"/>
</div>

The compiler frontend and HIR-to-C++ emitter are also written in Nyx. A native stage-1 compiler produces stage 2; stage 2 reproduces byte-identical stage-3 C++ from the same compiler sources. Python remains useful for bootstrapping from zero, orchestration, and the `python` target, but it is not required by the distributed native `nyxc` path.

> **Release status:** `4.0.0-rc.1` / Samsara is the current public release
> candidate. It is suitable for evaluation and feedback, not a stable API
> compatibility promise.

---

<a id="release-line"></a>

## Release line

The names below describe the intended direction of the project. Their meanings
are metaphorical, not technical requirements, and a release is created only
after its compiler and compatibility gates pass.

| Version | Codename | Meaning | Intended focus | Status |
| :-- | :-- | :-- | :-- | :-- |
| `v2.x` | — | — | Initial multi-target compiler, standard library, and CLI foundation | Historical |
| `v3.x` | — | — | Bundle ABI, Unicode/byte correctness, parity testing, and native interop | Historical |
| `v4.0.0-dev.1`–`dev.2` | **Maya** | Illusion / appearance | Scope reset, firmware removal, compiler/HIR expansion, syntax ergonomics, native/WASM, self-hosting, and LSP work | Historical development line |
| `v4.0.0-rc.1` | **Samsara** | Cycle of existence | Cross-platform release-candidate validation and compatibility soak | **Current release candidate** |
| `v4.0.0-rc.2` | **Bodhi** | Awakening | Focused corrections discovered during RC1 testing | Only if required |
| `v4.0.0-rc.3` | **Moksha** | Liberation | Final release-gate verification without new feature work | Only if required |
| `v4.0.0` | **Nirvana** | Release from the cycle | Stable v4 language, compiler, tooling, and compatibility baseline | Planned after RC gates |
| `v5.0.0` | Aether | Upper sky / pure medium | New major language work, portable C/LLVM direction, and an independent reference frontend | Future target |
| `v6.0.0` | Eclipse | Obscuring and transition | Direct native code generation and broader optimization/tooling contracts | Future target |
| `v7.0.0` | Apotheosis | Highest development | Additional service and managed-runtime targets with explicit concurrency mappings | Future target |
| `v8.0.0` | Elysium | Ideal peaceful place | Mature multi-target ecosystem, long-term compatibility, and production release discipline | Future target |

### Why the scope changed

Nyx previously attempted compiler work, many backend toolchains, firmware and
board support, self-hosting, IDE integration, and a standard library at the same
time. The active v4 line removes the microcontroller platform layer so effort
can stay on the language itself: compiler correctness, clear semantics,
native/WASM output, readable syntax, diagnostics, and tooling.

---

<a id="features"></a>

## `02` — Key Features

<div align="center">
  <img src="assets/features_animated.svg?v=4.0.0-rc1" width="98%" alt="nyx key features pillars"/>
</div>

### ⚡ One frontend, capability-gated targets

Nyx exposes seven target families without pretending they all have the same maturity. `nyx targets --json` is the machine-readable source of truth.

```text
┌─────────────┬──────────────────────────────┬──────────────┬───────────────┐
│ Target      │ Artifact                     │ Maturity     │ HIR authority │
├─────────────┼──────────────────────────────┼──────────────┼───────────────┤
│ cpp         │ C++20 / native executable    │ stable       │ yes           │
│ js          │ ES2022 / Node.js module      │ stable       │ yes           │
│ python      │ Python 3 program             │ stable       │ yes           │
│ wasm        │ WAT + WASM ABI v1            │ beta         │ yes           │
│ rust        │ Rust 2021 source/object      │ beta         │ yes           │
│ react       │ React 19 TSX tooling         │ beta         │ tooling       │
│ asm         │ x86_64 assembly via C++      │ beta         │ migration     │
└─────────────┴──────────────────────────────┴──────────────┴───────────────┘
```

Unsupported syntax or standard-library modules fail with a capability diagnostic; a narrow backend may not silently change the program's meaning.

### ◇ Deterministic typed-HIR pipeline

Nyx uses a deterministic compilation flow:

```text
SOURCE
  │
  ├──► UTF-8 Lexer
  │
  ├──► Syntax Parser
  │
  ├──► Module Graph + Type Checker
  │
  ├──► Typed HIR v1 Lowering
  │
  ├──► Verification + Deterministic Passes
  │
  └──► Backend Code Generation
```

HIR has a deterministic serializer and verifier. The Python and Nyx-authored frontends are checked for byte-identical HIR across accepted and rejected corpora.

### ⟳ Reproducible native self-hosting

```text
stage 0 bootstrap
      │
      ▼
native nyxc stage 1 ──► stage-2 C++ ──► native stage 2
                               │
                               └──────► byte-identical stage-3 C++
```

The installed native compiler handles `check`, `emit-cpp`, `compile`, `targets`, and version queries without starting Python.

### ◆ Topological Module Resolution

Modules are represented as a dependency graph and processed topologically.

The graph system handles:

* Dependency ordering
* Diamond dependency deduplication
* Dependency cycles
* Ambiguous symbol collisions
* Deterministic graph traversal

```text
        A
       / \
      B   C
       \ /
        D

        ↓

   D is processed once.
   Shared dependencies are deduplicated.
```

### ⌁ Diagnostics v2

Nyx provides source-aware diagnostics with precise spans and stable error identifiers.

```text
error[E1302]: ambiguous symbol collision

  --> src/main.nyx:14:9
   |
14 |     use value
   |         ^^^^^
   |
   = multiple symbols resolve to the same identifier
```

The diagnostic system is designed for both human-readable compiler output and tooling integration.

### ◈ Native C++20 Backend

The `cpp` backend emits C++20 suitable for compilation through Clang or GCC.

```text
Nyx Source
    │
    ▼
Verified HIR
    │
    ▼
C++20
    │
    ├── Clang
    └── GCC
         │
         ▼
    Native Binary
```

### ⌘ Compiler-aware editor tooling

Nyx includes an LSP JSON-RPC server and a local VS Code package with diagnostics, hover, completion, go-to-definition, syntax highlighting, snippets, one-click Run/Build/Check, and a toolchain doctor. Native output runs in a persistent integrated terminal so a completed `.exe` does not disappear immediately.

---

<a id="backends"></a>

## `03` — Compiler & Backend Contract

| Layer | Contract |
| :-- | :-- |
| Source | UTF-8 `.nyx`, 46 canonical v4 keywords |
| Portable integer | Signed i64 with specified wrapping, division, remainder, and shift behavior |
| Portable float | IEEE-754 binary64 with canonical `nan`, `inf`, exponent, and negative-zero text |
| Strings | Unicode, embedded NUL, `\uXXXX`, interpolation; no implicit NFC/NFD normalization |
| Semantic boundary | Canonical typed HIR v1 + verifier + deterministic passes |
| Stable semantic set | `cpp`, `js`, `python` exact hosted parity |
| Web ABI | `wasm` beta `wasm32` + Bundle ABI v1 |
| Native linker path | Clang++, GCC/G++, or MSVC `cl` with C++20 support |
| Tooling | Native `nyxc`, `nyx` CLI, LSP JSON-RPC, local VS Code VSIX |

Every backend declares numeric, string, ownership, error, control-flow, artifact, and standard-library capabilities. New targets begin as experimental and must cross eight gates before they can be called stable: registration, HIR coverage, semantic definition, official-toolchain validation, negative diagnostics, fuzzing, differential parity, and cross-platform release evidence.

---

## `04` — Project Structure

```text
nyx/
├── compiler/          # Nyx-authored frontend, HIR lowerer, and HIR C++ emitter
├── src/
│   ├── core/          # Stage-0 lexer, parser, type checker, modules, diagnostics
│   ├── ir/            # Typed HIR v1, verifier, serializer, optimization passes
│   ├── codegen/       # HIR backends, Bundle ABI emitter, native toolchain bridge
│   ├── self_host/     # Bootstrap and reproducibility orchestration
│   ├── stdlib/        # Capability-gated standard library modules
│   └── cli.py         # Full nyx command surface
├── vscode-extension/ # Local VSIX, LSP client, commands, syntax, snippets, icons
├── tests/             # Runtime, parity, negative, fuzz, ABI, and release gates
├── tools/             # Deterministic packaging and release utilities
├── docs/              # Versioned specs, roadmaps, compatibility and internals
├── assets/            # Logos and preserved animated README visuals
├── install.ps1        # Native-first Windows installer
├── install.sh         # Native-first Linux/macOS installer
└── VERSION            # Single version source
```

The production architecture lives at the HIR boundary. Direct AST emitters are migration-only and cannot be promoted to stable.

---

<a id="installation"></a>

## `05` — Installation

Nyx ships native-first installers for Windows, Linux, and macOS. Release archives contain the standalone `nyxc` compiler; Python is only needed for stage-0 recreation, optional orchestration commands, or the `python` target.

### Windows

From a downloaded source/release directory:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\install.ps1
```

Or install this exact RC1 release directly:

```powershell
$env:NYX_RELEASE_TAG = 'v4.0.0-rc.1'; irm https://raw.githubusercontent.com/justsomeone-e/nyx/v4.0.0-rc.1/install.ps1 | iex
```

### Linux / macOS

From an extracted source/release directory:

```bash
chmod +x install.sh
./install.sh
```

Or install this exact RC1 release directly:

```bash
curl -fsSL https://raw.githubusercontent.com/justsomeone-e/nyx/v4.0.0-rc.1/install.sh | NYX_RELEASE_TAG=v4.0.0-rc.1 bash
```

### Toolchain requirements

| Target | Host requirement |
| :-- | :-- |
| `cpp` / native `nyxc compile` | C++20-capable Clang++, GCC/G++, or MSVC `cl` |
| `js` | Node.js with ES2022 support |
| `python` | Python 3 |
| `rust` | Rust toolchain / `rustc` |
| `wasm` bundle | Built-in WAT/WASM emitter; Node.js is used by live wrapper tests |

The C++ compiler must be on `PATH`, or its absolute executable path can be supplied with `NYX_CXX`.

Verify the complete environment after installation:

```text
nyx doctor
nyx version
nyx targets
```

<a id="vscode"></a>

### VS Code — local one-click package

Download or build `nyx-language-support-<version>.vsix`, then either double-click it and choose **Install**, use **Extensions: Install from VSIX...**, or run:

```text
code --install-extension nyx-language-support-<version>.vsix
```

No Marketplace account or repository checkout is required to install a local VSIX. The extension contributes:

- compiler-backed diagnostics, hover, completion, and go-to-definition;
- canonical v4 keyword completion, snippets, syntax highlighting, and Nyx file icons;
- **Nyx: Run Current File**, **Build**, **Check**, and **Toolchain Doctor** commands;
- an editor-title ▶ button and a persistent integrated terminal.

For native builds, install Clang++, GCC/G++, or MSVC first. If none is found, the extension explains the requirement and points to `NYX_CXX` / `nyx doctor` instead of failing silently.

---

<a id="usage"></a>

## `06` — Usage

### Create a Workspace

```bash
nyx new core_engine
cd core_engine
```

### Check Source

Run semantic and type validation:

```bash
nyx check src/main.nyx
```

### Run Native C++20

The default execution backend is `cpp`:

```bash
nyx run src/main.nyx --target cpp
nyx build src/main.nyx --target cpp --release
```

> **Why does a generated `.exe` close immediately?** When launched from Explorer, Windows owns the temporary console and closes it as soon as the process returns or crashes. Run it from a terminal, or use **Nyx: Run Current File** in VS Code; the integrated terminal remains open and preserves stdout, stderr, and the exit code.

### Inspect target capabilities

```bash
nyx targets
nyx targets --json
```

Use this before selecting a beta backend or importing a target-specific standard-library module.

### Emit & Run x86_64 Assembly (Intel Syntax)

Generate and execute optimized Intel-syntax x86_64 assembly (`.s`):

```bash
# Via CLI flag
nyx run --target asm

# Or build standalone .s file in build/asm/<name>.s
nyx build --target asm
```

You can also specify the target directly in source code:

```nyx
#target asm

fn main() {
    print("Direct x86_64 Assembly Output")
}
```

### Run Node.js

```bash
nyx run src/main.nyx --target js
```

### Run Python Reference

```bash
nyx run src/main.nyx --target python
```

### Build Rust

```bash
nyx build src/main.nyx --target rust
```

### Verify local tooling behavior

```bash
nyx fmt src/main.nyx
nyx lint src/main.nyx
nyx profile src/main.nyx --target python
nyx doc src/main.nyx
nyx add telemetry @2.3.4
nyx pkg
```

`fmt` is string/comment-safe and idempotent. `profile` reports measured
whole-program compile+run wall time rather than synthetic per-function data.
`debug` is currently a validated source-line inspector and does not fabricate
runtime values. The package contract mutates `nyx.toml`/`nyx.lock`; remote
registry download is not implemented and `nyx install` states that limit.

### Verify or invoke the native self-host compiler

```bash
nyx self-host verify
nyx self-host build
nyxc check src/main.nyx
nyxc emit-cpp src/main.nyx -o build/main.cpp
nyxc compile src/main.nyx -o build/main
```

---

## `07` — Language Surface

Nyx keeps familiar control flow, but adds explicit cleanup, early-exit, matching, pipelines, traits, strict booleans, and reusable tasks without requiring a wall of ceremony:

```nyx
#target cpp

struct Build {
    name: string,
    score: int
}

trait Show {
    fn show(self) -> string
}

impl Show for Build {
    fn show(self) -> string {
        return $"{self.name}: {self.score}"
    }
}

async fn double_score(value: int) -> int {
    guard value >= 0 else { throw "score cannot be negative" }
    return value |> doubled
}

fn doubled(value: int) -> int {
    return value * 2
}

async fn main() {
    let build = Build("native-self-host", 21)
    defer print("done")

    let task: Task<int> = double_score(build.score)
    let final_score: int = await task

    for pass in 1..3 {
        if pass == 2 { continue }
        print($"pass {pass}")
    }

    print(Build(build.name, final_score).show())
}
```

Core v4 includes `var`/`let`/`const`, explicit `set`, `if`/`elif`/`else`, `for`, `while`, `loop`, `break`, `continue`, `guard`, `defer`, `match`, `try`/`catch`/`throw`, `async`/`await`, interpolation, null-safe access, pipelines, structs, traits, implementations, tests, modules, and explicit `unsafe` boundaries. The RC1 grammar contract is specified in [`docs/SYNTAX_SPEC.md`](docs/SYNTAX_SPEC.md).

---

<a id="bundle"></a>

## `08` — Bundle ABI v1

One compilation pass can turn an exported Nyx module into a browser/Node/React package:

```bash
nyx bundle src/math.nyx --output dist/math
nyx bundle src/math.nyx --output dist/math --react
```

| Artifact | Purpose |
| :-- | :-- |
| `<module>.wat` | Inspectable WebAssembly text |
| `<module>.wasm` | Binary WebAssembly module |
| `<module>.mjs` | ES2022 loader, Promise cache, memory and string marshaling |
| `<module>.d.ts` | Pointer-free TypeScript API declarations |
| `<module>.react.tsx` | Optional React 19 client/Suspense hook |

ABI v1 requires `memory`, `__nyx_alloc(i32)`, `__nyx_free(i32, i32)`, and `__nyx_abi_version() -> 1`. Strings use UTF-8 and a packed i64 `(len << 32) | ptr`; JavaScript refreshes views after memory growth, validates bounds, frees input buffers in `finally`, and releases caller-owned returned buffers after decoding. Embedded NUL, Turkish text, emoji, empty strings, and distinct input/output allocation are covered by live runtime tests.

React clients can load a URL-keyed singleton module through the generated hook:

```tsx
'use client'

const { add, compute } = useNyxModule()
```

The generated Promise cache prevents duplicate WebAssembly instantiation during React Strict Mode's development double render.

---

## `09` — Native Self-Hosting Boundary

Nyx no longer depends on one Python compiler implementation for production compilation:

| Component | Authored in | Release role |
| :-- | :-- | :-- |
| Lexer, parser, type checker | Nyx | Native frontend inside `nyxc` |
| Typed-HIR lowerer | Nyx | Canonical semantic output |
| HIR-to-C++ emitter | Nyx | Native bootstrap/backend path |
| Stage-0 frontend | Python | Rebuild from zero and independent parity oracle |
| `python` backend | Python target code | Stable language target, not compiler dependency |

The release gate checks accepted/rejected corpus parity, byte-identical HIR, stage1→stage2→stage3 reproducibility, native fixture compilation, and the absence of machine-specific paths in generated output.

---

<a id="verification"></a>

## `10` — Verification & Conformance

Samsara RC1 is qualified by the unified verification framework rather than a
single happy-path build. The gates cover syntax, semantics, HIR, native
execution, hosted parity, Bundle ABI, self-hosting, LSP/editor contracts,
installers, packaging, fuzzing, and negative diagnostics.

```text
╔══════════════════════════════════════════════════════════════════════╗
║                    NYX VERIFICATION BATTERY                         ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  Edge-case regression                         ──► 138 / 138 PASS    ║
║  HIR corpus emission                          ──► 162 programs PASS ║
║  Nyx/Python canonical HIR byte parity         ──► 194 cases PASS    ║
║  Stable backend runtime parity                ──► 3 × 138 PASS      ║
║  Deterministic backend fixtures               ──► 3 × 10 PASS       ║
║  Standard-library HIR coverage                ──► 17 modules PASS   ║
║  Bundle ABI isolated + allocation stress      ──► 100,000 PASS      ║
║  Native self-host reproducibility             ──► stage 1/2/3 PASS ║
║  Deterministic fuzz engine                    ──► 530 / 530 PASS    ║
║  LSP JSON-RPC contract                        ──► 4 / 4 PASS        ║
║  C/C++ native interoperability                ──► 5 / 5 PASS        ║
║  Installer + VS Code extension contracts      ──► PASS             ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

### Backend maturity matrix

| Target | Language semantics | HIR | RC1 status |
| :-- | :--: | :--: | :-- |
| **`cpp`** | v4 RC contract | authoritative | native release candidate |
| **`js`** | v4 RC contract | authoritative | hosted release candidate |
| **`python`** | v4 RC contract | authoritative | parity/reference target |
| **`wasm`** | explicit `wasm32` subset | authoritative | ABI v1 candidate |
| **`rust`** | narrower Rust 2021 contract | authoritative | preview; additional runtime gates pending |
| **`react`** | wrapper/tooling contract | N/A | preview tooling |
| **`asm`** | native subset | via C++ | preview |

These results qualify Samsara as an RC1 candidate. Nirvana stable promotion
still requires the RC compatibility and release gates to remain green.

### Release integrity

The release workflow is configured to produce deterministic ZIP/TAR source archives, four native platform artifacts, the local-install VSIX, SHA-256 manifests, an SPDX 2.3 SBOM, and signed provenance/SBOM attestations. Version strings are checked against the root [`VERSION`](VERSION) file before packaging.

---

## `11` — Diagnostics

Nyx diagnostics are built around structured error codes and precise source spans.

```text
┌─────────────────────────────────────────────────────┐
│ error[E1302]: ambiguous symbol collision             │
├─────────────────────────────────────────────────────┤
│                                                     │
│  --> src/main.nyx:14:9                              │
│                                                     │
│ 14 │ use value                                      │
│    │     ^^^^^                                      │
│                                                     │
│ = multiple symbols resolve to the same identifier   │
└─────────────────────────────────────────────────────┘
```

The documented error catalog currently covers the `E1000` through `E2006` range.

See [`ERROR_REFERENCE.md`](ERROR_REFERENCE.md) for the diagnostic catalog.

---

<a id="documentation"></a>

## `12` — Documentation

| Documentation | Description |
| :-- | :-- |
| [`GETTING_STARTED.md`](GETTING_STARTED.md) | First project and compiler workflow |
| [`INSTALLATION.md`](INSTALLATION.md) | Host and native toolchain setup |
| [`LANGUAGE_REFERENCE.md`](LANGUAGE_REFERENCE.md) | Versioned v4 language semantics |
| [`docs/SYNTAX_SPEC.md`](docs/SYNTAX_SPEC.md) | Grammar, type, Task, exception, and HIR contract |
| [`CLI_REFERENCE.md`](CLI_REFERENCE.md) | CLI command reference |
| [`ERROR_REFERENCE.md`](ERROR_REFERENCE.md) | Structured diagnostic catalog |
| [`docs/internals/ROADMAP_AND_BACKEND_GATES.md`](docs/internals/ROADMAP_AND_BACKEND_GATES.md) | v4 decision record, backend gates, and future target order |
| [`docs/TODO.md`](docs/TODO.md) | Historical and maintenance checklist |
| [`CHANGELOG.md`](CHANGELOG.md) | Release history and version changes |

---

## `13` — Contributing

Nyx welcomes contributions that improve the compiler, language, tooling, documentation, and verification infrastructure.

Before opening a pull request:

1. Keep changes focused and reviewable.
2. Preserve deterministic compiler behavior.
3. Add regression coverage for behavior changes.
4. Verify affected compilation targets.
5. Keep diagnostics precise and consistent.
6. Update documentation for user-facing changes.
7. Avoid unnecessary dependencies or unrelated refactoring.

For larger architectural changes, discuss the intended design before implementing a substantial change.

### Pull Request Checklist

```text
[ ] Implementation is focused
[ ] Existing behavior is preserved where intended
[ ] Relevant verification suites pass
[ ] Affected backends were checked
[ ] Diagnostics remain deterministic
[ ] Documentation was updated
[ ] No unnecessary dependencies were introduced
```

---

## `14` — License

The Nyx compiler, toolchain, and standalone standard-library sources are
licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.
Redistributed or modified Nyx tooling must continue to satisfy the AGPL; it
cannot be relicensed as a closed-source product.

The separate **[Nyx Output and Standard Library Exception](NYX-OUTPUT-EXCEPTION)**
keeps applications built with Nyx independent: generated C++20, JavaScript,
WebAssembly, binaries, and other artifacts may be distributed under terms of
the developer's choice, including MIT or proprietary terms. The same
permission covers Nyx runtime or standard-library portions incorporated into
those generated artifacts. It does not cover standalone redistribution of the
compiler, runtime, or standard library.

See [`LICENSE`](LICENSE) for the complete AGPLv3 text and
[`NYX-OUTPUT-EXCEPTION`](NYX-OUTPUT-EXCEPTION) for the additional permission.

---

<div align="center">
  <img src="assets/footer_animated.svg?v=4.0.0-rc1" width="98%" alt="nyx systems footer banner"/>
</div>
