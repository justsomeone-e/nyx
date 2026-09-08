# Nyx Deep Compiler Architecture and Formal Roadmap

Status: research and design proposal. This document does not claim that the
described MIR, semantic model, proofs, ABI revisions, or backend migrations are
implemented.

Nyx should grow by strengthening a small target-independent semantic core, not
by adding keywords or duplicating lowering logic across emitters. The intended
long-term shape is a language platform whose source semantics, intermediate
representations, runtime contracts, target legalization, and observable
behavior are explicit and independently verifiable.

## 1. Current architectural pressure

Nyx already has a structured Typed HIR and multiple backend implementations.
The current HIR remains source-oriented and tree-shaped rather than a
control-flow or SSA representation. Backend emitters independently lower many
of the same constructs, including branching, loops, pattern matching, `defer`,
`guard`, `spawn`, `await`, exceptions, and Result propagation.

That repetition creates three risks:

1. A language feature can acquire different semantics in different emitters.
2. Every new feature multiplies implementation and regression work by the
   number of backends.
3. Backend capability errors may be discovered too late, after semantic
   lowering has already entered an emitter.

The required direction is:

```text
Source
  -> AST
  -> name and type resolution
  -> Typed HIR v1
  -> Nyx MIR
  -> target legalization
  -> emitter and runtime adapter
  -> target artifact
```

Typed HIR should remain the public, source-oriented compiler and plugin
contract until an explicitly versioned migration replaces it. MIR should begin
as an internal compiler representation.

## 2. Hidden foundations that must precede scale

### 2.1 Stable compiler identities

Large modules, incremental compilation, generics, and separate compilation
need identities that do not depend on display names or import order:

```text
SourceId
PackageId
ModuleId
DefId
TypeId
LocalId
BlockId
InstanceId
CodegenUnitId
```

Imported declarations should not be flattened into one root program as the
long-term module model. The compiler should preserve a module graph and expose
only a module's public interface to dependants.

### 2.2 Exact type identity

Type checking, assignment compatibility, ABI compatibility, and exact type
identity are different questions and should not share one permissive helper:

```text
is_exact_type(left, right)
is_assignable(expected, actual)
is_coercible(source, destination)
is_abi_compatible(left, right, target)
```

Canonical type identity must include generic arguments, optionality, pointer
kind, function parameters, return type, calling convention where relevant, and
resolved nominal identity.

### 2.3 A real module graph

The module graph should retain:

```text
module identity
source identity
public declarations
private declarations
imports and re-exports
initialization dependencies
foreign dependencies
interface fingerprint
implementation fingerprint
```

A private implementation change should not invalidate unrelated dependant
modules when the public interface fingerprint is unchanged.

### 2.4 Current repository evidence

The architectural pressure above is visible in the current implementation. The
following findings are an audit of the repository state, not claims that the
proposed replacements already exist.

#### Generics currently carry names rather than resolved instances

[`IRFunction`](../../src/ir/model.py#L263), `IRStruct`, and `IREnum` carry
`generic_params` as tuples of strings. The current model does not attach a
resolved generic parameter identity, constraint set, substitution map, concrete
instance identity, or monomorphization record.

Consequences include:

- `Box<int>` and `Box<string>` do not yet have a dedicated compiler instance
  identity at this layer;
- trait-bound resolution can leak into backend-specific logic;
- C++, Rust, LLVM, and Wasm can accidentally choose different generic
  representations or lowering behavior.

The required replacement concepts are:

```text
GenericParamId
GenericConstraint
SubstitutionMap
MonomorphInstance
CanonicalTypeId
```

#### Type compatibility is intentionally permissive

[`compatible()`](../../src/ir/types.py#L132) currently performs broad
compatibility checks, including generic-name compatibility when one side lacks
fully specified arguments. That behavior can support transitional HIR, but it
must not become the final definition of overload resolution, generic identity,
or ABI equality.

It should be decomposed into:

```text
is_exact_type(left, right)
is_assignable(expected, actual)
is_coercible(source, destination)
is_abi_compatible(left, right, target)
```

#### Async is represented but not yet modeled as a state machine

The HIR contains [`IRAwait`](../../src/ir/model.py#L57),
[`IRSpawn`](../../src/ir/model.py#L214), and the
[`IRFunction.is_async`](../../src/ir/model.py#L270) flag. It does not yet encode:

```text
suspend point identity
coroutine frame
locals live across await
start/resume/destroy paths
cancellation
async exception transfer
single-await versus multi-await Task policy
hot versus cold Task behavior
```

Those decisions belong in the Nyx Task contract and coroutine MIR lowering,
not in direct backend syntax generation.

#### Imports are flattened into the root AST

[`ModuleLoader.load_program()`](../../src/core/module_loader.py#L148) prepends
collected imported declarations to root statements. Parsed modules are cached,
but their declarations are ultimately combined into one root program.

This simplifies the current compiler but obstructs a long-term implementation
of:

```text
real module namespaces
public and private visibility
same-named private declarations
separate compilation units
interface-only invalidation
cyclic interface diagnostics
package initialization order
parallel compilation
```

The replacement should preserve module boundaries and make dependant modules
consume public interface fingerprints rather than flattened AST declarations.

#### Traits have declarations but no complete dispatch model

[`IRTrait`](../../src/ir/model.py#L284) and
[`IRImpl`](../../src/ir/model.py#L291) carry methods and target names. The model
does not yet distinguish:

```text
resolved TraitId and ImplId
associated types
generic bounds
static dispatch
dynamic dispatch
witness or vtable layout
object-safety rules
```

The first complete implementation should resolve static dispatch before MIR:

```text
trait call
  -> resolve implementation
  -> select concrete function
  -> apply substitutions
  -> monomorphize
  -> emit an ordinary MIR call
```

Dynamic trait objects should remain a separate capability and ABI project.

#### Existing pass fingerprints are a useful foundation

The HIR [`PassManager`](../../src/ir/passes.py#L545) already fingerprints input
and output around each pass and can verify every transformed module. This is a
useful seed for deterministic MIR pass records and later incremental query
keys, but it is not itself a complete incremental compiler.

## 3. Staged MIR architecture

Nyx should avoid one representation that accepts every high-level and
low-level construct at once. A staged representation provides explicit
invariants and smaller verifier surfaces.

```text
Typed HIR
   |
   v
Build MIR
   Structured source semantics may still be visible.
   |
   v
Cleanup MIR
   `defer`, `?`, destructuring, and unwind cleanup are explicit.
   |
   v
Canonical MIR
   Control flow is a CFG and expressions are unnested.
   |
   +--> Native SSA or LLVM-legal MIR
   +--> Wasm-legal MIR
   +--> Rust-legal MIR
   +--> source-backend legal MIR
```

The first MIR implementation should be non-SSA. SSA can be introduced as a
derived representation for optimization and native code generation after the
canonical CFG, ownership, and cleanup semantics are stable.

### 3.1 Core MIR vocabulary

```text
Storage:
  local
  temporary
  argument
  return_slot
  static
  coroutine_field

Place:
  local
  field
  index
  dereference
  downcast

RValue:
  use
  constant
  unary
  binary
  cast
  aggregate
  discriminant
  length
  reference

Statement:
  assign
  storage_live
  storage_dead
  retain
  release
  drop
  bounds_check
  assert
  intrinsic

Terminator:
  goto
  branch
  switch
  call
  return
  throw
  resume_unwind
  suspend
  spawn
  unreachable
  trap
```

`match`, `guard`, `defer`, postfix `?`, destructuring, safe navigation, null
coalescing, and structured loops should not survive into Canonical MIR. They
must lower into primitive control flow while preserving single evaluation and
source spans.

### 3.2 MIR invariants

Every MIR stage must have a verifier. Canonical MIR should require at least:

```text
- Every basic block has exactly one terminator.
- Every branch target exists.
- Block arguments agree with predecessor values and types.
- Every local and temporary has a unique typed identity.
- Values are initialized before use.
- Storage is not accessed after StorageDead.
- A moved value is not reused.
- A value is dropped at most once.
- Every expression with effects is evaluated exactly once.
- Result payloads are read only after discriminant refinement.
- Every source operation retains provenance to a source span.
```

### 3.3 Pass manager

Each pass should declare:

```text
name
accepted MIR stage
produced MIR stage
required analyses
invalidated analyses
operations it may introduce
preserved invariants
```

The verifier should run before and after each development/debug pass. The pass
pipeline should support textual dumps, timing, fingerprints, and minimal crash
reproducers.

## 4. Central semantic lowering

The following constructs should be lowered once before backend code generation:

```text
and/or                    -> short-circuit CFG
if expression             -> branch plus destination
match                     -> discriminant and switch CFG
guard                     -> branch plus early exit
postfix ?                 -> Result switch plus early return
defer                     -> cleanup chain
try/catch                 -> normal and unwind edges
for                       -> iterator protocol
destructuring             -> projections with one source evaluation
safe navigation           -> optional switch
null coalescing           -> optional switch
closure                   -> environment plus function
async/await               -> coroutine state machine
trait call                -> resolved static or dynamic dispatch
```

No emitter should independently decide the language meaning of these features.

## 5. Effects and capabilities

Functions and calls should carry an internal effect set:

```text
pure
may_allocate
may_throw
may_suspend
may_block
io
unsafe
host_call
```

The first implementation need not add user-facing effect syntax. Internal
effects allow the compiler to:

- reject suspension in a non-async context;
- reject filesystem operations in a browser-only profile;
- distinguish an ordinary Result from exceptional unwinding;
- preserve ordering around observable operations;
- prevent optimizations from moving effectful calls;
- calculate a program's required capability set.

Capabilities may later be declared by a package manifest:

```toml
[capabilities]
allow = ["fs.read", "stdout"]
deny = ["network", "process.spawn"]
```

## 6. Result, exception, panic, and trap

These must remain distinct:

```text
Result<T, E>  normal typed value and control flow
throw         catchable exceptional control flow
panic         runtime failure governed by a panic policy
trap          non-catchable target/runtime safety termination
```

Postfix `?` on `Result<T, E>` should become a discriminant branch and early
return, not an exception. Calls that may throw need explicit normal and unwind
successors. Cleanup elaboration must ensure all relevant `defer` and `drop`
operations run on return, break, continue, and unwind paths.

The MIR should retain abstract unwind semantics. LLVM's Windows and Itanium
exception representations differ, so platform-specific landing pads,
personalities, and tables belong in target legalization rather than source
semantics.

## 7. Generics and trait solving

### 7.1 Generic identities

The compiler needs:

```text
GenericParamId
GenericConstraint
SubstitutionMap
MonomorphInstance
CanonicalTypeId
```

HIR should retain generic declarations and constraints. The initial MIR path
should receive concrete monomorphized instances. A collector discovers all
reachable concrete functions, methods, statics, and layouts before codegen.

Monomorphization keys must include canonical type arguments and relevant
compile-time parameters. Collection requires recursion/cycle guards and a code
size budget.

Target-language templates must not become the source of Nyx generic semantics.
C++ and Rust emitters should receive already-resolved concrete instances. JS
and Python may erase representation details only after Nyx-level checking. JVM
or .NET reification can be introduced later through target legalization.

### 7.2 Trait solver

Trait solving should be independent from ordinary compatibility checks and
emitters:

```text
Goal: T implements Display

Result:
  Proven(ImplId, substitutions)
  Ambiguous
  NoSolution
  Overflow
```

Initial support should use static dispatch:

```text
trait call
  -> resolve ImplId
  -> select concrete method
  -> apply substitutions
  -> monomorphize
  -> ordinary MIR call
```

Dynamic trait objects, object safety, witness tables, and vtables should be a
later and separately gated feature.

### 7.3 Parametricity

Generic code should use only operations granted by its constraints. A function
such as `identity<T>(value: T) -> T` cannot inspect or change an unknown `T`.
This rule must come from the type system rather than incidental emitter
behavior.

## 8. Async, Task, spawn, and channels

`async` cannot remain a function flag plus direct target syntax. Lowering needs:

```text
coroutine analysis
live-across-suspend analysis
coroutine frame layout
suspend point identities
start/resume/complete/destroy paths
cancellation path
exception propagation
debug source mapping
```

The language contract must define:

- whether a Task is hot or cold;
- whether one Task can be awaited more than once;
- when execution begins;
- how cancellation is observed;
- whether cancellation runs `defer` and `drop`;
- how child failure reaches its parent;
- whether channels are FIFO;
- whether channel sends copy or move values;
- how channel closure is represented;
- how a single-thread Wasm profile preserves semantics.

Two explicit execution profiles are preferable to one ambiguous operation:

```text
task-local     deterministic cooperative scheduling
task-threaded  platform-backed parallel scheduling
```

Canonical async events can be represented as:

```text
Ready(task)
Poll(task)
Suspend(task, reason)
Wake(task)
Complete(task, value)
Cancel(task)
```

Small programs can be model-checked across possible schedules instead of
depending only on nondeterministic real-thread tests.

## 9. Memory, ownership, and layout

The language specification must distinguish:

```text
value identity
object identity
address
storage
lifetime
ownership
borrowing
aliasing
mutation
initialization
drop
pointer provenance
```

Questions that require explicit answers include:

- whether nested arrays and structs are deep-copied;
- how function arguments and returns transfer values;
- how closure capture copies or borrows values;
- what moves into a coroutine frame;
- how long an FFI borrow remains valid;
- whether self-referential values are representable;
- which actions are permitted inside `unsafe`;
- whether safe code can exhibit a data race or use-after-free.

### 9.1 Layout engine

Logical type, storage layout, and calling convention should be independent:

```text
LogicalType
  Array<int>
  Option<User>
  Result<T, E>

StorageLayout
  size
  alignment
  field offsets
  discriminant
  payload layout

CallingConvention
  direct
  indirect
  sret
  scalar pair
  borrowed pointer
  owned pointer
```

Suggested modules:

```text
src/layout/model.py
src/layout/target.py
src/layout/engine.py
src/layout/abi.py
src/layout/verify.py
```

Rust or C++ implementation layout must not become Nyx ABI by accident. A future
C-compatible representation should be an explicit ABI attribute backed by a
versioned RFC and conformance tests.

## 10. Backend legalization

Each backend should publish a machine-readable legal contract:

```yaml
backend: wasm
integer_width: 32
overflow: wrap
exceptions: false
threads: false
ownership: linear-memory-runtime
legal_mir:
  - scalar
  - structured-control
  - borrowed-array
reject:
  - unwind
  - native-pointer
  - threaded-spawn
```

Legalization must either:

1. convert an operation and its types to target-legal MIR; or
2. emit a stable capability diagnostic.

An illegal operation reaching an emitter is an internal compiler error. There
must be no silent fallback or approximate semantic mapping.

Recommended migration order:

```text
C++ -> LLVM -> Wasm -> Rust -> JavaScript -> Python -> C17
```

C++ first preserves the existing native oracle while exercising the full MIR
surface. LLVM and Wasm then force precise CFG, layout, and integer semantics.
Rust validates ownership mapping. JS and Python migrate after semantics no
longer depend on source-emitter shortcuts.

### 10.1 Backend portfolio beyond the current targets

Nyx should distinguish a semantic backend, an ecosystem adapter, and an
interoperability profile. Producing another file extension is not by itself a
new useful backend.

```text
Semantic backend
  Own legalization, runtime mapping, output contract, and parity corpus.

Ecosystem adapter
  Reuses an existing backend while exposing another ecosystem's packages or
  type declarations.

Interop profile
  Uses a stable ABI to call or be called by another language.
```

#### Tier A: high-value semantic backends

| Target | Primary value | Main semantic mismatch | Recommended first form |
| --- | --- | --- | --- |
| Go | Services, command-line tools, networking, and Go packages | Nyx lexical `defer`, Task behavior, exceptions, value copies, goroutines, and channels | Generated Go source |
| C#/.NET | .NET libraries, desktop/server applications, and a rich managed runtime | Value/reference distinction, generics, exception identity, Task cancellation, and disposal | Generated C# source |
| Java/JVM | Java/Kotlin libraries and the JVM deployment ecosystem | Boxing, erased/reified generic boundaries, class initialization, exceptions, and object identity | Generated Java source |

Go must not receive a direct syntax substitution for `defer`: Go executes
deferred calls when the surrounding function returns, while Nyx lexical defer
is defined at scope exit. Go goroutines and channels are useful implementation
mechanisms, but Nyx Task and Channel contracts remain authoritative.

C# Task exceptions, cancellation, value types, reference types, and disposal
require an explicit runtime adapter. A Nyx `Result<T, E>` remains an ordinary
sum value and must not silently become a .NET exception.

The first JVM backend should emit Java source. Kotlin libraries are accessed
through JVM bindings; Kotlin does not initially require a second semantic
backend. Direct JVM bytecode becomes worthwhile only after stack-map frames,
verification, object layout, generics, and exception tables are understood and
covered by target-specific tests.

#### Tier B: strategic optional backends

| Target | Add when | Main blocker | Initial strategy |
| --- | --- | --- | --- |
| Lua | Embedded scripting, games, or modding becomes a primary direction | Dynamic tables, number policy, GC identity, errors, and coroutine semantics | Lua source plus a small runtime |
| Zig | Nyx needs better C-library consumption or freestanding/native tooling | Error unions, comptime, allocation ownership, target ABI, and async differences | Zig source or C ABI adapter |
| Swift | Apple application and framework integration becomes important | ARC ownership, value semantics, async behavior, module resilience, and platform ABI scope | Swift source and generated C bridge |
| Ruby | Dynamic scripting and RubyGem integration has demonstrated users | Open classes, reflection, exceptions, block/closure semantics, and object identity | Ruby source or C-extension adapter |
| Dart | Flutter or Dart server consumers exist | Futures, isolates, GC values, null safety, and FFI ownership | Dart source plus `dart:ffi` bridge |
| BEAM | Actor/distributed systems become a product goal | Isolated processes, immutable messages, selective receive, supervision, and failure semantics | Erlang or Elixir source with a dedicated actor profile |

Lua is more valuable as an embedding target than as another general-purpose
source output. Its runtime contract must select an exact Lua version and define
integer, floating, table, coroutine, error, and garbage-collection boundaries.

Zig is attractive because it has explicit C ABI primitives and C translation
tooling. That makes it useful for Nyx native interoperability, but it does not
remove the need for exact target triples, flags, ownership, and ABI validation.

Swift should not be described as universally ABI-stable. Swift's published ABI
stability commitment is platform-specific, historically centered on Apple
platforms. Nyx should therefore prefer generated Swift source and a C boundary
before claiming portable binary interoperability.

BEAM deserves a separate actor-oriented target profile rather than pretending
that Nyx shared-memory `spawn` and Channel behavior naturally matches Erlang
processes and mailboxes. Erlang processes use isolated mailboxes and selective
receive; adopting that model would be a semantic feature, not an emitter trick.

#### Tier C: adapters rather than duplicate backends

| Surface | Decision | Reason |
| --- | --- | --- |
| TypeScript | Extend the JavaScript backend's typed output | TypeScript erases types and preserves JavaScript runtime behavior, so a separate runtime backend adds little |
| Kotlin | Build a JVM ecosystem adapter first | Kotlin and Java interoperate on the JVM; a separate Kotlin emitter would duplicate JVM legalization |
| React/Vue/Svelte | Keep as generated web adapters | These are consumer frameworks, not independent Nyx semantic targets |
| Objective-C | Reach through Swift/C adapters initially | A dedicated semantic backend provides limited new reach |

TypeScript declarations, source maps, ESM packaging, and typed host adapters
should therefore be features of the JavaScript/Wasm toolchain rather than a
second definition of Nyx semantics.

#### Tier D: reference languages, not immediate output targets

Haxe and Nim are valuable comparison projects for language ergonomics,
conditional compilation, portable libraries, and multi-target design. Emitting
Haxe or Nim from Nyx does not immediately unlock a unique runtime or package
ecosystem comparable to Go, .NET, or JVM, and would insert another compiler
between Nyx and the final target.

They should initially be used for comparative conformance research:

```text
feature ergonomics
portable versus target-specific standard-library structure
conditional compilation boundaries
generated-code debugging
package and build integration
runtime footprint
```

#### Backend admission rule

A proposed backend enters implementation only when it has:

```text
1. A real consumer application.
2. A target semantic-difference document.
3. A target legalization profile.
4. A runtime and ownership mapping.
5. A package or FFI integration story.
6. Positive and negative conformance fixtures.
7. A maintained official toolchain in CI.
8. A reason it cannot be served by an existing adapter.
```

The recommended portfolio order is therefore:

```text
Finish shared MIR and current backends
  -> Go
  -> C#/.NET
  -> Java/JVM plus Kotlin bindings
  -> choose one demand-driven specialist:
       Lua for embedding
       Zig for native/C interoperability
       Swift for Apple platforms
       Dart for Flutter
       BEAM for actor systems
  -> reconsider the remaining targets using real adoption evidence
```

## 11. ABI and interoperability

Bundle ABI v1 should remain stable. More expressive interoperability should use
separately versioned contracts:

```text
Bundle ABI v1       current compatibility contract
Bundle ABI v2       richer Nyx host ABI
WIT component mode  standardized Wasm component integration
```

FFI functions require machine-readable preconditions and postconditions:

```text
requires:
  pointer addresses `length` initialized bytes
  allocation remains live for the call duration

ensures:
  returned owned pointer belongs to the caller
  destroy may be called exactly once
```

C ABI should be the initial stable native boundary. Raw C++ or Rust ABI should
not be treated as cross-toolchain stable. Higher-level ecosystem imports should
use generated adapters, stable C shims, Wasm components, or explicitly pinned
same-toolchain profiles.

## 12. Standard library topology

The standard library should separate portable semantics from host adapters:

```text
std/core       available everywhere
std/portable   behaviorally equal implementations
std/sys        native/system targets
std/web        browser and Wasm hosts
std/node       Node.js host APIs
std/python     Python host APIs
std/jvm        future JVM adapters
std/dotnet     future .NET adapters
```

Target-specific code is acceptable inside controlled adapters. Target branches
should not spread through ordinary Nyx application code. The compiler should
resolve capabilities and select adapters before target emission.

## 13. Incremental compilation

The compiler should become a deterministic query graph:

```text
read_source(SourceId)
  -> tokenize(SourceId)
  -> parse(ModuleId)
  -> collect_interface(ModuleId)
  -> resolve_names(ModuleId)
  -> typecheck_item(DefId)
  -> lower_hir(DefId)
  -> instantiate(InstanceId)
  -> lower_mir(InstanceId)
  -> legalize(Target, InstanceId)
  -> emit(CodegenUnitId)
```

Cache keys must include:

```text
compiler version
HIR and MIR schema versions
target triple and profile
optimization level
feature flags
source fingerprint
dependency interface fingerprints
runtime ABI version
```

Incremental caching should begin only after stable identities, deterministic
serialization, module boundaries, pure queries, and public interface hashes
exist. Otherwise a fast cache can produce stale or semantically invalid builds.

## 14. Debug information and provenance

MIR must retain source information from its first implementation:

```text
SourceSpan
InlineOrigin
LexicalScopeId
VariableDebugName
GeneratedFromNodeId
```

Required tooling:

```text
nyx emit ast
nyx emit hir
nyx emit mir
nyx emit mir --after cleanup
nyx verify mir
nyx explain E3001
nyx explain-backend rust
nyx compile --save-temps
```

Generated target locations should map back to Nyx source ranges. Native LLVM
output should eventually emit DWARF or CodeView metadata. JavaScript should
emit source maps. Diagnostics from generated C++ or other source backends should
be translated back through a generated-range map.

## 15. Reference interpreter and observable behavior

Stable semantics should not use the C++ emitter as the sole oracle. Nyx needs a
small, deliberately slow MIR interpreter.

```text
Source
  -> Typed HIR
  -> MIR
  -> MIR interpreter
```

Every backend can then be checked against that interpreter.

Program behavior should be represented as an observable event trace rather
than only stdout:

```text
ReadFile(path, result)
WriteFile(path, bytes)
HostCall(namespace, function, arguments)
Print(text)
Spawn(task_id)
Suspend(task_id)
Resume(task_id)
Throw(type, value)
Return(value)
Trap(reason)
```

For deterministic sequential code, one program should have one trace. For I/O
or concurrency, the semantics may permit a set of traces.

## 16. Nyx semantic constitution

Every operation must be classified as:

```text
defined behavior
implementation-defined behavior
compile-time error
catchable runtime error
trap
unsafe-only behavior
```

At minimum, the specification must settle:

- signed and unsigned overflow;
- division by zero and signed minimum divided by minus one;
- floating NaN, infinity, comparison, and conversion behavior;
- evaluation order for arguments, operands, and initializers;
- negative and out-of-range indexing;
- Unicode code point versus grapheme behavior;
- shallow versus deep value copying;
- drop and defer order;
- multiple exceptions during cleanup;
- FFI exception boundaries;
- data races and atomics;
- pointer provenance and invalid addresses;
- global initialization and module ordering.

Safe Nyx should avoid undefined behavior. A valid safe program should produce a
defined value, structured error, defined trap, or compile-time rejection.

LLVM lowering must avoid unjustified `nsw`, `nuw`, `inbounds`, alias, lifetime,
and initialization assumptions. Otherwise an apparently safe Nyx operation can
become LLVM poison or undefined behavior after optimization.

## 17. Abstract machine and operational semantics

Nyx should have a target-independent abstract machine:

```text
MachineState {
  control: InstructionPointer
  stack: FrameStack
  heap: ObjectStore
  tasks: TaskSet
  scheduler: SchedulerState
  output: EventTrace
  exception: Optional<Exception>
}
```

Execution is a transition relation:

```text
State -> State'
```

A smaller formal core can be described with:

```text
Types:
tau ::= Unit | Bool | Int64 | Float64
      | Array tau
      | Struct S
      | Result tau tau
      | Task tau
      | tau -> tau

Expressions:
e ::= value
    | variable
    | let x = e in e
    | set place = e
    | if e then e else e
    | call e(e...)
    | return e
    | throw e
    | spawn e
    | await e

Runtime configuration:
<expression, environment, heap, continuation, scheduler>
```

High-level language features desugar into this core. The formal core, rather
than generated C++, defines Nyx program meaning.

```text
for        -> iterator plus while
match      -> discriminant plus switch
?          -> Result switch
defer      -> explicit cleanup continuation
closure    -> environment struct plus function
async      -> coroutine state machine
trait call -> resolved function or witness call
```

Keeping this calculus deliberately small means proofs target a compact semantic
core instead of every surface-language spelling independently.

## 18. Type-system judgments

Typing can be expressed as:

```text
Gamma |- expression : Type ! Effects
```

That judgment states that an expression has a type and may produce a defined
set of effects under an environment.

Bidirectional checking separates synthesis from checking:

```text
Gamma |- expression => Type
Gamma |- expression <= ExpectedType
```

This is especially useful for contextual lambdas, generic calls, enum
constructors, collection literals, and overload resolution.

The formal metatheory should establish:

```text
weakening
substitution
canonical forms
progress
preservation
sequential determinism
```

## 19. Logical relations, memory reasoning, and separation logic

### 19.1 Logical relations

Generics, representation independence, and higher-order functions cannot be
fully validated with example programs alone. A logical relation can classify
related values and expressions by type:

```text
V[[tau]] = values related at type tau
E[[tau]] = expressions whose executions produce related results at type tau
```

For example:

```nyx
fn identity<T>(x: T) -> T = x
```

A parametric logical relation expresses that this function cannot inspect an
unknown `T` except through capabilities granted by constraints. The same
technique can support reasoning about:

```text
generic parametricity
private representation hiding
optimizer equivalence
trait implementation equivalence
safe abstraction boundaries
```

### 19.2 Separation logic

Ownership can be modeled as exclusive resources rather than informal emitter
conventions. Separation logic expresses disjoint ownership with a separating
conjunction:

```text
owns(x, object_a) * owns(y, object_b)
```

A move transfers ownership:

```text
owns(x, object)
  -> owns(y, object)
```

After the transition, access through `x` can no longer be derived. A value copy
creates a distinct object with equal contents:

```text
owns(a, array_1)
  -> owns(a, array_1) * owns(b, array_2)
     and contents(array_1) = contents(array_2)
     and array_1 != array_2
```

Channel send can transfer ownership between tasks. Resource obligations can
ensure memory, locks, files, and foreign handles are released exactly once.

### 19.3 Step-indexed semantics

Recursive types, mutable references, closures, and asynchronous state may
require step-indexed logical relations:

```text
V[[tau]]_n
```

This means that a value behaves as type `tau` for at least `n` execution steps.
Induction proceeds over `n = 0, 1, 2, ...`, avoiding circular definitions for:

```text
recursive structs and enums
closures capturing closures
trait objects
mutable references
async tasks
higher-order FFI callbacks
```

### 19.4 Kripke worlds

Kripke worlds can track future-valid extensions of heap allocations, ownership
invariants, tasks, capabilities, and foreign resources.

```text
W = {
  allocated_locations,
  ownership_invariants,
  active_tasks,
  capability_tokens,
  foreign_resources
}

W <= W'
```

`W <= W'` states that execution has extended the world validly. It lets the
formal model ask whether a captured value remains valid when a closure is
called later, whether a suspended coroutine frame remains live, whether a
foreign handle survives between calls, and whether a capability was legally
transferred to another task.

## 20. Contextual equivalence and secure compilation

Two source programs are contextually equivalent when no valid Nyx context can
distinguish them:

```text
P ~= Q
iff
for every valid context C, C[P] and C[Q] have equivalent observations
```

Compiler correctness should preserve observable behavior. A stronger secure
compilation goal is full abstraction:

```text
P ~=Nyx Q
iff
compile(P) ~=Target compile(Q)
```

This prevents a target context from observing representation details that are
not observable in Nyx, such as hidden object identity, padding, generated
fields, or raw linear-memory layouts.

Concrete leakage risks include:

- JavaScript object identity exposing a distinction that Nyx value-copy
  semantics hide;
- Python reflection exposing generated storage fields;
- a C++ host reading padding or an internal discriminant;
- a Wasm host inspecting raw linear-memory representation;
- a Rust target exposing a target-specific drop order.

Complete full abstraction is a research-scale goal. Practical intermediate
steps are:

```text
representation hiding
capability isolation
checked FFI adapters
robust safety at component boundaries
versioned host contracts
```

## 21. Compiler simulation and semantic preservation

For each lowering stage, define a relation between source and target machine
states:

```text
HIR state H ~ MIR state M
```

If H takes a step, M should take zero or more corresponding steps and restore
the relation:

```text
H -> H'
M ->* M'
H' ~ M'
```

The complete compiler theorem should be composed from pass-local simulation or
refinement results:

```text
Typed HIR
  ~ Build MIR
  ~ Cleanup MIR
  ~ Canonical MIR
  ~ Target MIR
  ~ emitted target program
```

Depending on the transformation, the relation may be established with:

```text
forward simulation
backward simulation
bisimulation
trace refinement
```

For a representative HIR-to-MIR relation `H ~ M`, the expected local shape is:

```text
H -> H'
M ->* M'
H' ~ M'
```

One HIR step may therefore correspond to zero or more MIR steps while restoring
the relation afterward.

Important proof obligations include:

```text
type preservation
progress
ownership uniqueness
absence of use-after-free in safe code
race freedom under the safe concurrency model
cleanup exactly once
lowering simulation
backend behavioral refinement
```

## 22. Translation validation and proof-carrying passes

End-to-end formal verification of every optimizer is not required at the
beginning. A practical translation validator checks each concrete
transformation:

```text
before = MIR
after = optimize(before)

verify(after)
validate(after refines before)
```

Initial bounded validation can cover scalar values, finite heaps, bounded loop
iterations, and single-function transformations.

Passes may eventually produce certificates:

```text
transformed MIR
transformation certificate
```

A small checker validates the certificate. The optimizer may remain large and
untrusted while the checker becomes part of the trusted computing base.

## 23. Separate compilation and linking

Compiler correctness must eventually extend beyond a monolithic program:

```text
compile(A plus B)
  ~=
link(compile(A), compile(B))
```

The linker model must account for:

```text
symbol identity
duplicate definitions
visibility and re-exports
generic instance sharing
module initialization order
ABI agreement
runtime singleton state
foreign callbacks
dynamic loading
version skew
```

Correct modules must not become incorrect only because they were compiled
separately and linked later.

## 24. Trusted computing base

Formal claims are limited by the components that remain trusted:

```text
language specification
formal semantics
proof kernel
MIR verifier
certificate checker
backend validator
runtime
assembler and linker
operating system
hardware
```

The design goal is to move complexity outside the trusted core:

```text
large optimizer          untrusted
small certificate checker trusted

large backend            untrusted
small output validator   trusted
```

Proof-producing automation, tactics, and AI-generated proofs must be checked by
a small proof kernel. AI assistance then affects productivity but not the
validity criterion.

```text
large automatic prover
  -> produces proof term
  -> small kernel checks proof term

AI-generated proof            untrusted
optimization certificate      untrusted
small proof checker           trusted
Nyx formal specification      trusted
```

A faulty tactic, optimizer, or AI agent may fail to produce an accepted proof,
but it must not be able to convince the kernel of an invalid theorem.

## 25. Bootstrap and reproducibility

The self-host chain should retain:

```text
Stage0 -> Stage1 -> Stage2 -> Stage3
```

Stage equality is useful but does not alone prove compiler correctness. The
trust analysis must include:

- whether Stage0 can inject behavior;
- whether compiler source and binary correspond;
- whether absolute paths, locale, timestamps, and environment leak into output;
- which runtime and standard library sources were used;
- whether independent bootstrap implementations agree.

A future diverse double compilation experiment can compare compilers produced
through independent bootstrap paths.

## 26. Conformance corpus

Tests should be organized by semantic feature rather than backend:

```text
tests/conformance/
  arithmetic/
  control_flow/
  functions/
  modules/
  generics/
  traits/
  ownership/
  arrays/
  strings/
  result/
  exceptions/
  async/
  ffi/
  diagnostics/
```

Each fixture should carry metadata:

```yaml
feature: result-propagation
targets: [cpp, js, python, rust]
profiles: [hosted]
expect:
  stdout: "42\n"
  exit_code: 0
  diagnostic: null
  mir_contains: [switch, return]
```

CI layers:

```text
PR smoke
feature parity
nightly differential and fuzz
release platform and ABI gates
long-running soak
```

A feature is complete only when parser, checker, HIR, MIR, verifier, legalizer,
backend, runtime, positive tests, negative tests, parity tests, and
documentation agree.

## 27. Generated and metamorphic testing

A typed random generator should produce valid HIR programs:

```text
generate typed HIR
  -> verify HIR
  -> lower MIR
  -> interpret MIR
  -> compile supported targets
  -> compare observations
```

An invalid-MIR mutator should verify that malformed states are rejected:

```text
remove a terminator
use a value after move
corrupt a block argument
read the wrong enum payload
skip required cleanup
resume a completed coroutine
```

Metamorphic properties include:

```text
alpha-renaming does not change behavior
adding an unused declaration does not change behavior
splitting a basic block does not change behavior
constant folding preserves behavior
dead-code elimination preserves behavior
parentheses do not alter defined evaluation order
```

Found failures should be automatically minimized into permanent regression
fixtures.

## 28. Suggested implementation modules

```text
src/mir/model.py
src/mir/types.py
src/mir/builder.py
src/mir/lowering.py
src/mir/cleanup.py
src/mir/verifier.py
src/mir/serialization.py
src/mir/printer.py
src/mir/interpreter.py
src/mir/passes.py

src/layout/model.py
src/layout/target.py
src/layout/engine.py
src/layout/abi.py
src/layout/verify.py

src/semantics/events.py
src/semantics/effects.py
src/semantics/capabilities.py

src/incremental/keys.py
src/incremental/queries.py
src/incremental/cache.py
src/incremental/graph.py
```

Formal work may eventually live in:

```text
formal/
  CoreSyntax.v
  CoreTypes.v
  CoreSemantics.v
  MemoryModel.v
  Effects.v
  Ownership.v
  Concurrency.v
  HIRSemantics.v
  MIRSemantics.v

  Lowering/
    HIRToMIR.v
    CleanupElaboration.v
    ClosureConversion.v
    CoroutineLowering.v
    Monomorphization.v

  Proofs/
    Progress.v
    Preservation.v
    Determinism.v
    RaceFreedom.v
    MemorySafety.v
    SemanticPreservation.v

  Extraction/
    ReferenceInterpreter.v
    MIRVerifier.v
    CertificateChecker.v
```

The proof assistant and final file extension are not decided by this document.
Rocq is a strong candidate because CompCert and Iris demonstrate relevant
compiler, ownership, and concurrency verification techniques.

## 29. M0-M8 execution map

This milestone map turns the architecture into bounded implementation batches.
Milestones are ordered by dependency. A later milestone must not compensate for
an incomplete invariant or semantic contract in an earlier milestone.

### M0: inventory, contracts, and feature manifest

Implementation status (2026-09-08): complete. The canonical registry is
[`compiler/features.toml`](../../compiler/features.toml), its deterministic
output is [`docs/generated/FEATURE_MATRIX.md`](../generated/FEATURE_MATRIX.md),
and `tests/feature_manifest_suite.py` rejects drift from compiler registries.
Stable identity rules are frozen in
[`M0_COMPILER_IDENTITIES.md`](M0_COMPILER_IDENTITIES.md). This milestone adds
no MIR implementation and does not alter the default compilation path.

Purpose: freeze the current observable surface before introducing another IR.

Work:

- inventory every AST and HIR node, type form, builtin, intrinsic, effectful
  operation, diagnostic, standard-library capability, and backend;
- introduce stable `SourceId`, `ModuleId`, `DefId`, `TypeId`, and `InstanceId`
  designs;
- create `compiler/features.toml` as the canonical machine-readable feature
  registry;
- record each feature's parser, checker, HIR, runtime, and backend status;
- preserve HIR schema v1, Bundle ABI v1, lockfile contracts, and stable backend
  behavior;
- classify existing behavior as defined, implementation-defined, rejected,
  trapped, or unsafe-only.

Exit gate:

```text
The feature matrix is generated from one canonical manifest.
Every existing stable behavior has a named conformance fixture.
No MIR implementation has changed default compiler output.
```

### M1: MIR skeleton and tooling

Purpose: create the representation without migrating production codegen.

Work:

```text
src/mir/model.py
src/mir/types.py
src/mir/builder.py
src/mir/lowering.py
src/mir/verifier.py
src/mir/serialization.py
src/mir/printer.py
src/mir/passes.py
```

- define functions, locals, places, blocks, statements, and terminators;
- require typed values, unique block identities, valid branch targets, one
  terminator per block, and retained source spans;
- provide deterministic textual and canonical serialized forms;
- add `nyx emit mir` and `nyx verify mir` behind an experimental path;
- fingerprint every pass input and output;
- keep all current emitters on the existing verified HIR route.

Exit gate:

```text
MIR round-trips deterministically.
The verifier rejects intentionally malformed fixtures.
The normal compiler path remains byte-for-byte unaffected where promised.
```

### M2: scalar and structured-control lowering

Purpose: prove the basic HIR-to-MIR path before ownership or async complexity.

Work:

- literals, local declarations, assignments, parameters, and returns;
- integer, floating, Boolean, comparison, and conversion operations;
- function calls and top-level execution;
- `if`, `while`, `break`, and `continue` CFG construction;
- strict left-to-right evaluation and single evaluation of effectful operands;
- defined overflow, division, cast, and trap behavior;
- a small MIR reference interpreter for this subset.

Exit gate:

```text
HIR and MIR interpreter observations agree.
C++ and LLVM scalar outputs agree with the MIR interpreter.
Malformed control-flow graphs are rejected before emission.
```

### M3: canonical desugaring and cleanup

Purpose: remove repeated semantic lowering from individual emitters.

Work:

- short-circuit `and` and `or`;
- value-producing `if` and `match`;
- `guard`, destructuring, safe navigation, and null coalescing;
- postfix Result propagation;
- lexical `defer` cleanup chains;
- `try`/`catch`, normal edges, unwind edges, panic, and trap separation;
- `for` lowering through a defined iterator protocol;
- cleanup correctness for return, throw, break, and continue.

Exit gate:

```text
Canonical MIR contains no structured constructs assigned to this milestone.
Every exit path executes each required cleanup exactly once.
Emitters no longer independently lower these source semantics.
```

### M4: aggregates, ownership, memory, and ABI

Purpose: make value semantics and physical representation explicit.

Work:

- arrays, structs, payload enums, Option, and Result layouts;
- places for field, index, dereference, and variant projection;
- explicit copy, move, borrow, retain, release, and drop operations;
- initialization and move-state analysis;
- target-independent logical types and target-specific storage layouts;
- argument, return, indirect return, and ownership calling conventions;
- Bundle ABI v2 design without breaking Bundle ABI v1;
- explicit C-compatible FFI representation and checked adapter contracts.

Exit gate:

```text
Array and struct value behavior is identical across stable targets.
The verifier detects use-after-move and double-drop states.
ABI fixtures validate size, alignment, field offsets, and ownership transfer.
```

### M5: backend migration through legalization

Purpose: make MIR the shared semantic source while retaining target-specific
representations and runtimes.

Migration order:

```text
C++ -> LLVM -> Wasm -> Rust -> JavaScript -> Python -> C17
```

Work:

- define legal operation, type, effect, runtime, and ABI profiles per backend;
- create target legalization passes rather than emitter fallbacks;
- reject every unsupported operation with a stable capability diagnostic;
- migrate one backend at a time while the old path remains available as an
  oracle;
- delete repeated emitter lowering only after differential parity passes;
- retain C++ as the default until release gates justify a change.

Exit gate:

```text
No illegal MIR operation reaches an emitter.
Every migrated backend passes positive, negative, runtime, and parity corpora.
Fallback to approximate target semantics is impossible.
```

### M6: vertical language-surface expansion

Purpose: resume source-language growth without recreating backend duplication.

Candidate order:

```text
closures
generic constraints
static trait dispatch
iterator protocol and yield
visibility and module exports
named arguments
async state machines
channels and select
```

Every feature must complete one vertical slice:

```text
grammar
parser
name resolution
type checker
Typed HIR
MIR lowering
MIR verification
target legalization
runtime
positive tests
negative tests
cross-target parity
documentation
```

Exit gate:

```text
A feature cannot be marked supported from syntax or one emitter alone.
The feature manifest and generated capability documentation agree with tests.
```

### M7: standard library, packages, and ecosystem adapters

Purpose: turn compiler capability into applications people can actually build.

Work:

- split `std/core`, `std/portable`, `std/sys`, and host-specific adapters;
- expand collections, iteration, strings, paths, processes, networking, time,
  serialization, and concurrency under consistent Result contracts;
- generate typed binding manifests and adapter stubs;
- preserve deterministic package resolution, checksums, and offline operation;
- add WIT Component Model output as a separate Wasm profile;
- provide real native CLI, server, embedding, package, and web consumers;
- keep target-specific implementation code behind capability boundaries.

Exit gate:

```text
Portable APIs have defined cross-target observations.
Host-specific APIs fail at capability checking rather than late emission.
Each supported ecosystem has at least one real end-to-end consumer.
```

### M8: new backends, verification, and promotion

Purpose: add ecosystems only after the shared semantic path is stable.

Backend order:

```text
Go -> C#/.NET -> Java/JVM
```

Lua may move earlier only if embedded scripting becomes a primary product
direction. Initial Go, C#, and Java implementations should emit source and use
their official toolchains. Direct CIL or JVM bytecode emission is a later
optimization, not an initial requirement.

Work:

- require a target legalization profile and runtime adapter before an emitter;
- use a concrete acceptance application for every new backend;
- add translation validation for critical MIR optimizations;
- begin formalizing the scalar/control-flow Nyx Core;
- extract or implement a trusted reference interpreter and MIR verifier;
- require clean platform CI, reproducible artifacts, checksums, SBOM, and
  provenance before maturity promotion.

Exit gate:

```text
A backend is not promoted because it merely produces a file.
It must compile, run, reject unsupported semantics, and pass differential tests.
Formal claims clearly identify their trusted computing base and proof boundary.
```

## 30. Delivery phases

### v5.1: compiler foundations

- Stable SourceId, ModuleId, DefId, TypeId, and InstanceId.
- Preserved module graph and public interface fingerprints.
- Exact type identity separated from assignment compatibility.
- MIR model, printer, serialization, and verifier.
- `nyx emit mir` and `nyx verify mir`.

### v5.2: control flow and cleanup

- CFG lowering.
- Short-circuit logic.
- Match, guard, destructuring, and Result propagation.
- Lexical defer and drop cleanup chains.
- Abstract exception and unwind edges.
- Internal effect metadata.

### v5.3: generics and dispatch

- Substitution engine.
- Monomorphization collector.
- Stable instance mangling.
- Generic constraints and diagnostics.
- Static trait dispatch.
- Duplicate-instantiation cache.

### v5.4: ownership, layout, and ABI

- Explicit ownership operations.
- Drop elaboration.
- Target data layouts.
- Aggregate calling conventions.
- Bundle ABI v2 draft.
- Explicit C-compatible FFI representation.

### v5.5: async runtime

- Coroutine frame construction.
- Suspend, resume, completion, and destruction.
- Formal Task behavior.
- Channel and cancellation contracts.
- C++, Rust, JavaScript, and Wasm runtime adapters.

### v5.6: backend migration

- C++ consumes MIR.
- LLVM consumes legalized MIR.
- Wasm consumes legalized MIR.
- Rust consumes legalized MIR.
- JavaScript, Python, and C17 migrate after semantic parity.
- Repeated semantic lowering is removed from emitters.

### v6: semantic platform

- MIR becomes the default compiler route.
- Incremental query engine.
- Source-level debug metadata.
- WIT Component profile.
- Expanded portable and host standard libraries.
- Go source-backend pilot.
- C#/.NET and Java/JVM backend RFCs.
- Initial formal Nyx Core and executable reference semantics.

## 31. Formalization maturity levels

Formal work should advance gradually:

```text
Level 0  precise English contracts
Level 1  executable reference interpreter
Level 2  property-based and differential testing
Level 3  MIR translation validator
Level 4  formal scalar and control-flow core
Level 5  mechanized type soundness
Level 6  verified critical lowering passes
Level 7  end-to-end semantic preservation
```

The project should not block practical compiler progress on complete formal
verification. Each level should produce usable tooling and stronger evidence.

## 32. Immediate starting sequence

The first implementation batch should remain narrow:

1. Publish a MIR design record defining stage boundaries and invariants.
2. Introduce stable compiler identities and stop relying on display names where
   MIR requires resolved identities.
3. Implement MIR model, canonical serialization, printer, and verifier.
4. Lower literals, locals, assignments, arithmetic, calls, branches, loops, and
   returns behind an experimental compiler path.
5. Implement the reference MIR interpreter for that scalar subset.
6. Differentially compare interpreter, C++, and LLVM results.
7. Add cleanup, Result propagation, match, aggregates, and ownership one
   vertical semantic slice at a time.

No new public keyword is required for this sequence.

## 33. Research references

- Rust MIR: <https://rustc-dev-guide.rust-lang.org/mir/index.html>
- Rust MIR passes: <https://rustc-dev-guide.rust-lang.org/mir/passes.html>
- Rust monomorphization: <https://rustc-dev-guide.rust-lang.org/backend/monomorph.html>
- Rust incremental compilation: <https://rustc-dev-guide.rust-lang.org/queries/incremental-compilation.html>
- Rust type layout: <https://doc.rust-lang.org/stable/reference/type-layout.html>
- Rust memory model: <https://doc.rust-lang.org/reference/memory-model.html>
- LLVM language reference: <https://llvm.org/docs/LangRef.html>
- LLVM undefined behavior: <https://llvm.org/docs/UndefinedBehavior.html>
- LLVM exception handling: <https://llvm.org/docs/ExceptionHandling.html>
- LLVM coroutines: <https://llvm.org/docs/Coroutines.html>
- LLVM source-level debugging: <https://llvm.org/docs/SourceLevelDebugging.html>
- MLIR dialect conversion: <https://mlir.llvm.org/docs/DialectConversion/>
- MLIR pass management: <https://mlir.llvm.org/docs/PassManagement/>
- WebAssembly specification: <https://webassembly.github.io/spec/>
- WebAssembly Component Model: <https://github.com/WebAssembly/component-model>
- WebAssembly Canonical ABI: <https://component-model.bytecodealliance.org/advanced/canonical-abi.html>
- Haxe standard library organization: <https://haxe.org/documentation/introduction/stdlib-introduction.html>
- CompCert semantic preservation: <https://compcert.org/man/manual001.html>
- Alive2 translation validation: <https://github.com/AliveToolkit/alive2>
- K Framework: <https://kframework.org/docs/user_manual/>
- Iris concurrent separation logic: <https://iris-project.org/>
- Rocq trusted kernel: <https://github.com/rocq-prover/rocq/blob/master/doc/sphinx/language/core/index.rst>
- Fully abstract compilation: <https://doi.org/10.1145/2951913.2951941>
- Go language specification: <https://go.dev/ref/spec>
- Go memory model: <https://go.dev/ref/mem>
- .NET asynchronous programming: <https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/>
- JVM specification: <https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-2.html>
- Lua 5.4 reference manual: <https://www.lua.org/manual/5.4/>
- Zig language reference and C interoperability: <https://ziglang.org/documentation/master/>
- Kotlin and Java interoperability: <https://kotlinlang.org/docs/java-interop.html>
- Kotlin coroutine semantics: <https://kotlinlang.org/spec/asynchronous-programming-with-coroutines.html>
- TypeScript runtime and type erasure: <https://www.typescriptlang.org/docs/handbook/typescript-from-scratch>
- Swift ABI stability: <https://www.swift.org/blog/abi-stability-and-more/>
- Ruby documentation and C extension guide: <https://www.ruby-lang.org/en/documentation/>
- Dart C interoperability: <https://dart.dev/interop/c-interop>
- Erlang process semantics: <https://www.erlang.org/doc/system/ref_man_processes.html>

## 34. Final principle

Nyx should not measure language maturity by keyword count or backend count.
Maturity should mean:

```text
The source program has a target-independent meaning.
Every lowering stage has explicit invariants.
Every backend either preserves that meaning or rejects the program clearly.
No backend silently approximates unsupported semantics.
The evidence can progress from tests to executable validation and eventually
to machine-checked proofs.
```

The long-term differentiator is not merely that Nyx can emit many languages.
It is that high-level, approachable syntax can lower into a small, precise,
observable, and increasingly verifiable semantic core across all targets.

Formal verification proves conformance to a specification; it does not prove
that humans chose the intended specification. Nyx should therefore maintain
three mutually checked sources of truth:

```text
Human intent
  readable language contract

Formal model
  mathematical semantics

Executable evidence
  reference interpreter and conformance corpus
```

A material disagreement among these sources should block a stable release. The
ultimate evidence chain is:

```text
English specification
        <->
Formal semantics
        <->
Reference interpreter
        <->
Typed HIR and MIR
        <->
Generated target
        <->
Observed execution
```

The goal is for every edge in this chain to have an explicit validation method
rather than relying on one backend or one test suite as the definition of the
language.
