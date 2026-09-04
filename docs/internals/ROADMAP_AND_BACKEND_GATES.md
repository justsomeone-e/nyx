# Nyx v4 RC2, Self-Hosting, and Backend Roadmap

This document is the release-planning source of truth for the v4 line. Backend
capabilities exposed by the compiler remain machine-readable through
`nyx targets --json`.

## Release decision

- Published release: `v4.0.0-rc.1`.
- Current candidate: `v4.0.0-rc.2`, focused on the WebAssembly, browser, and
  TypeScript ecosystem plus RC1 soak fixes.
- Do not publish `v4.0.0` stable before an observed RC soak period.
- Python remains a stage-0 bootstrap and optional orchestration tool, not a
  dependency of the distributed native compiler.
- `cpp`, `js`, and `python` are the stable semantic parity set. A backend with
  a narrower contract must reject unsupported behavior explicitly.

## Compiler architecture

```text
Nyx source
  -> frontend (lexer, parser, type checker)
  -> canonical typed HIR v1
  -> verified deterministic passes
  -> backend
  -> target artifact
```

Backends must consume verified HIR. Direct AST emitters are migration-only and
cannot receive a new `stable` designation. `rust` now consumes HIR directly;
its beta label remains because Task/exception/concurrency support, retained
runtime parity, and cross-platform Gate 8 evidence are intentionally incomplete.

## Current backend status

| Target | Artifact | Registry maturity | HIR authority | RC2 action |
|---|---|---:|---:|---|
| `cpp` | C++20 / native binary | stable | Yes | Keep native runtime and self-host parity green |
| `js` | ES2022 / Node.js | stable | Yes | Keep exact hosted semantics green |
| `python` | Python 3 | stable | Yes | Keep exact hosted semantics green |
| `wasm` | WAT / WASM ABI v1 | beta | Yes | Versioned host ABI, std/web, package adapters, and browser soak |
| `rust` | Rust 2021 | beta | Yes | Keep beta until runtime parity and cross-platform Gate 8 evidence |
| `react` | React 19 TSX | beta | No | Treat as web tooling, not semantic oracle |
| `asm` | x86_64 assembly via C++ | beta | No | Keep beta |

## Eight backend gates

1. Registered capability and artifact contract.
2. Complete HIR node coverage with no AST dependency.
3. Defined numeric, string, ownership, error, and control-flow semantics.
4. Valid target artifact produced by the official target toolchain.
5. Structured negative diagnostics with stable error codes.
6. Deterministic fuzzing with no compiler crash or invalid artifact.
7. Differential runtime parity against canonical semantic fixtures.
8. Windows, Linux, and macOS CI plus packaging and documentation audit.

## Self-hosting and the Python boundary

Completed:

1. The Nyx-authored lexer, parser, type checker, typed-HIR lowerer, and HIR C++
   emitter build into the standalone native `nyxc` compiler.
2. Python and Nyx frontends have exact accepted/rejected corpus and canonical
   HIR parity.
3. Stage 1 builds stage 2; stage 2 emits byte-identical stage-3 C++ from the
   same compiler sources and compiles a native fixture.
4. Native-first installers route `check`, `emit-cpp`, `compile`, `targets`, and
   version queries to `nyxc` without Python.

Python remains intentionally available for three roles: recreating stage 1
from zero, optional legacy/orchestration commands, and the `python` target runtime.
It is no longer the production compiler architecture.

## v4 language freeze

The RC1 candidate freezes:

- 44 canonical keywords shared exactly by the lexer, self-host frontend, LSP,
  grammar, and VS Code extension;
- `fn` as the only function declaration spelling (`def` is an identifier);
- shallow immutable `let`/`const` bindings and explicit `set` assignment;
- bodyless trait signatures with verified implementation contracts;
- `Task<T>`, `await`, exceptions, `guard`, `defer`, `match`, interpolation, and
  pipelines;
- fixed-width scalars and explicit unsafe/native interoperability boundaries;
- strict Boolean conditions;
- signed i64 wrap/division/shift semantics, IEEE binary64 semantics, canonical
  scalar text, and identical constant-folding behavior.

Expression-bodied functions, value-producing `if`/`match`, array/struct
destructuring, Result propagation, default arguments, collection iteration,
and `yield` syntax are implemented. The full iterator protocol, closures, rest
patterns, compile-time `when`, named arguments, and visibility syntax remain
RFC candidates. No grammar change lands after RC1 without a compatibility
proof.

## Release codenames

Release names do not create artificial releases; unused RC names are skipped.

| Release | Codename |
|---|---|
| `v4.0.0-dev.*` | Maya |
| `v4.0.0-beta.*` | Nocturne |
| `v4.0.0-rc.1` | Samsara |
| `v4.0.0-rc.2` | Bodhi |
| `v4.0.0-rc.3` | Moksha |
| `v4.0.0` | Nirvana |
| `v5.0.0` | Aether |
| `v6.0.0` | Eclipse |
| `v7.0.0` | Apotheosis |
| `v8.0.0` | Elysium |

## New target order after RC1

1. `c`: portable C17 source backend and a smaller bootstrap surface.
2. `llvm`: direct LLVM IR native backend; no C++ source hop.
3. `go`: Go service/concurrency backend with explicit channel mapping.
4. `jvm`: JVM backend with Java 21 class-file compatibility as its baseline.
5. `dotnet`: .NET 10 managed backend.
6. `lua`: Lua 5.4 embedding and game-scripting backend.

Every new target starts experimental and must pass all eight gates. `zig` is
deferred until its language/toolchain contract is stable enough to freeze a
backend against it.

## OCaml reference frontend

`nyx-ocaml` is a post-RC1 verification track, not a rewrite of the production
compiler. It will:

- parse the frozen Nyx grammar independently;
- emit canonical HIR JSON;
- compare HIR fingerprints and structured diagnostics with the primary
  frontend;
- contain no backend, package manager, or runtime implementation.

This gives Nyx a second implementation capable of detecting shared assumptions
without delaying the HIR migration or self-hosting chain.

## RC2 candidate gate

- Run the full battery from clean Windows, Linux x64, macOS x64, and macOS arm64
  environments; retain the CI evidence.
- Make release archives deterministic and reject machine-specific paths.
- Synchronize the CLI, native compiler, changelog, README, editor manifest, and
  tag to `4.0.0-rc.2` only after all other gates pass.
- Keep `nyx_host_v1`, Bundle ABI v1, generated TypeScript types, and npm exports
  under direct conformance tests.
- Keep the pure-Nyx browser Pong fixture free of handwritten application logic
  in JavaScript; the generated adapter is the only host bridge.
- Verify recursive local dependency locks are path-normalized, cycle-safe, and
  content-addressed.
- Publish archive and native-binary SHA-256 manifests plus provenance/SBOM.
- Run the release audit twice from clean checkouts and complete an RC soak.

## Stable gate

- The latest v4 release candidate has no unresolved release-blocking defect
  after its soak period.
- Stable backends pass all eight gates from clean environments.
- Compiler API, plugin API, HIR schema, Bundle ABI, and package lockfile formats
  have published compatibility rules.
- Release artifacts have checksums, provenance/SBOM, and a tested rollback.

## Primary references

- [LLVM Language Reference](https://llvm.org/docs/LangRef.html)
- [Go specification and compatibility promise](https://go.dev/ref/spec)
- [Java Virtual Machine Specification](https://docs.oracle.com/javase/specs/)
- [.NET support policy](https://dotnet.microsoft.com/en-us/platform/support/policy)
- [OCaml language documentation](https://ocaml.org/docs)
