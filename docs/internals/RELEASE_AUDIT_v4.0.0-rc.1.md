# Nyx v4.0.0-rc.1 Local Candidate Audit

Date: 2026-08-30
Current version: `4.0.0-dev.1`
Intended next tag: `v4.0.0-rc.1`

## Decision

The current Windows working-tree candidate passes the targeted compiler, HIR,
bundle, self-host, installer, VS Code, and embedded contract checks. The full
unified harness is not green yet: its native-library capability contract
currently stops at the `native/gpio` expectation. This is a WIP review
candidate, not an RC1 sign-off. Publication remains on hold until the same
commit passes the retained Windows, Linux x64, macOS x64, and macOS arm64
matrix and two clean-checkout release audits.

## Verified local evidence

| Gate | Result | Evidence |
| :-- | :--: | :-- |
| Unified framework | WIP | Full harness stops at the `native/gpio` capability expectation; targeted gates remain passing |
| Regression battery | REVIEWED | Prior retained evidence: 138/138; current unified harness is not green |
| Native self-host | PASS | Nyx-authored frontend, native stage 2, and byte-identical stage-3 C++ |
| Typed HIR | PASS | 162 programs, 21 stdlib modules, 182-case Nyx/Python HIR byte parity |
| `cpp` HIR runtime | PASS | 162 emitted and 138 native runtime cases |
| `js` HIR runtime | PASS | 162 executed, 138 runtime cases, 10 deterministic fixtures |
| `python` HIR runtime | PASS | 162 compiled, 138 runtime cases, 10 deterministic fixtures |
| `rust` HIR emission | PASS | 159 supported corpus programs passed Rust 2021 metadata/borrow checking; exception, spawn, and channel fixtures rejected with E3001; 8/8 focused Rust cases |
| Language freeze | PASS | 46 keywords, editor parity, embedded controls, traits, Task, exception, i64, and strict-bool contracts |
| Numeric semantics | PASS | Signed i64, IEEE binary64, and canonical scalar text on three stable backends |
| Bundle ABI v1 | PASS | Typed lowering, UTF-8, isolated instances, and 100,000-allocation stress |
| Capability model | PASS | Target aliases, target rejection, stdlib gates, and six-module parity |
| LSP | PASS | Completion, hover, definition, and CLI JSON-RPC framing: 4/4 |
| Native interoperability | PASS | C callback declarators, RAII, Result bridge, and generic Result context: 5/5 |
| Compiler robustness | PASS | 530 fuzz cases, zero unhandled crashes; 10/10 structured negative cases |
| Release archives | PASS | Byte-reproducible ZIP/TAR, canonical paths, modes, owners, and timestamps |
| Native-first installers | PASS | Exact native version signature, portable runtime allowlist, installed-wrapper LSP smoke, and Python fallback |
| Version contract | PASS | `VERSION`, CLI, native compiler, VS Code, README, and preserved animations agree |
| VS Code package | PASS | Contract test, VSIX packaging, local force install, canonical CLI resolution, persistent terminal commands, and project links |
| CLI toolchain behavior | PASS | Formatter idempotence and source preservation; real profile execution; honest source inspection; doc output; manifest/lock add/remove/install/pkg effects; negative exit codes |
| README | PASS | Language example parses/type-checks/lowers/verifies; local links and image assets resolve |

## Release engineering state

The release workflow defines four native platform artifacts, deterministic
source archives, the local-install VSIX, SHA-256 manifests, an SPDX 2.3 SBOM,
and signed provenance/SBOM attestations. The local contract verifies the
workflow and package layout; hosted attestations are evidence only after the
tagged workflow itself completes.

## Findings closed during this audit

- Canonical Boolean output fixtures now compare lowercase `true`/`false` on
  all three HIR-authoritative backends.
- C FFI callback parameters emit valid function-pointer declarators.
- Contextual `Result<T, E>` construction and Nyx i64 literals preserve their
  exact host-language types.
- Native HIR type parsing trims generic component whitespace deterministically.
- The Rust 2021 backend now emits exclusively from canonical typed HIR; its
  beta contract passed the supported corpus and keeps Task, exception, spawn,
  and channel behavior as explicit capability rejections rather than approximations.
- Installers no longer copy VS Code development `node_modules` into the Nyx
  runtime payload.
- Installers reject stale native executables that exit successfully without the
  exact `nyxc <version> (native self-host)` signature, and the installed wrapper
  now passes an LSP initialize/shutdown protocol smoke test.
- The VS Code extension now runs native executables in a persistent terminal,
  diagnoses missing C++20 toolchains, prefers the canonical Nyx installation,
  exposes repository/documentation/release/roadmap/issue links, and ships as a
  local VSIX.
- CLI quality/package commands no longer report success on missing files;
  profiling executes the selected backend, debug mode no longer fabricates
  runtime state, and manifest/lock mutations have a dedicated regression suite.
- README architecture and release claims now match the typed-HIR and native
  self-host implementation without removing the animated assets.

## Remaining RC1 blockers

- [ ] Complete the canonical `cpp/js/python/rust/wasm/react/asm` target-ID
      migration, remove the pre-Nyx compatibility surface, and pass the unified
      regression suite with no stale-brand tokens.
- [ ] Freeze one reviewed commit and run the clean Windows/Linux/macOS matrix.
- [ ] Complete the release audit twice from clean checkouts of that commit.
- [ ] Change the single version source and all generated package surfaces to
      exactly `4.0.0-rc.1` only after the matrix is green.
- [ ] Produce and retain checksums, SPDX SBOM, and provenance from the tagged
      hosted workflow.
- [ ] Approve the RC1 tag and publish the candidate artifacts.
- [x] Normalize official CubeIDE linker scripts for LLVM LLD and validate the
      official STM32Cube/CMSIS provider matrix across all 21 registered pack
      boards (25/25 total Nucleo profiles emit ELF/HEX/BIN).

## Stable blockers after RC1

- [ ] Complete the RC soak without an unresolved release-blocking defect.
- [ ] Publish HIR, compiler API, plugin API, Bundle ABI, and lockfile
      compatibility policies.
- [ ] Test and publish the rollback procedure.
- [ ] Re-run all eight gates for every backend advertised as stable.
