# M0 compiler identity contract

Status: design contract. No runtime representation or public HIR schema changes
are introduced by M0.

Nyx currently carries many names as strings. That is sufficient for the v5
compiler, but it cannot safely support incremental compilation, multiple
frontends, package-scale semantic queries, or a new MIR. M0 therefore reserves
the following identity roles before any new IR is implemented.

## Identity roles

| Identity | Names | Stable within | Meaning |
| --- | --- | --- | --- |
| `SourceId` | source revision | one compiler database | Content-addressed source plus revision identity |
| `ModuleId` | source module | one dependency graph | Canonical module after path and package resolution |
| `NodeId` | syntax node | one parsed source revision | Concrete syntax occurrence; never reused after reparsing |
| `DefId` | declaration | one resolved package graph | `(package, module, local definition index)` |
| `SymbolId` | bound name | one semantic session | A binding or reference resolved to a `DefId` or local slot |
| `TypeId` | interned type | one compiler session | Canonical structural type identity |
| `InstanceId` | monomorphized definition | one compilation graph | A `DefId` plus canonical generic arguments and target-independent substitutions |
| `FeatureId` | language/backend capability | registry schema | Stable string key declared by `compiler/features.toml` |

Public serialization must use a versioned structural representation, not a
process-local integer. Dense integer forms are permitted only inside a compiler
session and must never be persisted as if they were stable across revisions.

## Allocation rules

1. `SourceId` changes whenever source bytes change and is the parent identity
   for spans and syntax nodes.
2. `NodeId` is allocated by the parser in source order and is invalidated when
   that source file is reparsed.
3. `DefId` is allocated after module resolution. Its public form includes the
   package and module identity; its local index is deterministic for an
   unchanged declaration order.
4. `SymbolId` is not derived from spelling. Shadowed names receive different
   identities, and every reference records the identity it resolved to.
5. `TypeId` is produced by interning canonical type structure. Aliases retain a
   `DefId`, while their resolved representation receives the same `TypeId` as
   the underlying type.
6. `InstanceId` is deterministic for one `DefId`, normalized type arguments,
   and target-independent substitution set. Target legalization is not part of
   this identity.
7. Synthetic compiler nodes use a reserved origin plus the identity of the
   source construct that caused their creation. They cannot impersonate source
   nodes.
8. IDs from different compiler sessions are never compared without first
   translating through a serialized stable key.

## Compatibility boundary

Typed HIR remains schema version 1. The present `symbol: string` fields remain
authoritative until an explicitly versioned HIR migration exists. Adding an
internal identity table is allowed, but changing serialized symbol meaning,
Bundle ABI v1, lockfile v1, or stable backend output is outside M0.

MIR may consume these identities only after it can prove that lowering keeps
source spans, symbol resolution, evaluation order, effects, and diagnostics.
Until then, `mir` remains `planned` in `compiler/features.toml` and cannot become
the default compilation path.

## Required proof before implementation

- identical definitions in separate modules do not collide;
- shadowed locals resolve to distinct symbols;
- an unchanged module produces deterministic public `DefId` keys;
- reparsing invalidates stale `NodeId` values;
- equivalent structural types intern to one `TypeId`;
- serialized HIR v1 remains byte-for-byte unchanged when identity tracking is
  enabled internally.
