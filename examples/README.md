# Nyx Runnable Examples

This directory contains standalone, runnable examples demonstrating the syntax, type system, concurrency primitives, and multi-target compilation features of Nyx.

## Index of Examples

| File | Primary Focus | Targets |
| :-- | :-- | :-- |
| [`01_math.nyx`](01_math.nyx) | Top-level scripting, arithmetic expressions, zero-ceremony execution | `cpp`, `js`, `python` |
| [`02_radar_dsp.nyx`](02_radar_dsp.nyx) | Typed variables, pipeline operator (`\|>`), formatted output | `cpp`, `js`, `python` |
| [`03_null_safety.nyx`](03_null_safety.nyx) | Optional types (`T?`), safe navigation (`?.`), null coalescing (`??`) | `cpp`, `js`, `python` |
| [`04_in_file_tests.nyx`](04_in_file_tests.nyx) | In-file test suites (`test "..." { assert(...) }`), native assertion checks | `cpp` |
| [`05_system_inspector.nyx`](05_system_inspector.nyx) | Standard library `std/system` inspection (OS, CPU threads, RAM) | `cpp` |
| [`06_memory_inspector.nyx`](06_memory_inspector.nyx) | `unsafe` blocks, raw pointers (`addr`), memory inspection (`peek`, `memdump`) | `cpp` |
| [`07_foreign_cpp.nyx`](07_foreign_cpp.nyx) | Foreign function interface to C++ standard library (`<filesystem>`) | `cpp` |
| [`08_foreign_node.nyx`](08_foreign_node.nyx) | Foreign function interface to Node.js modules (`node:os`) | `js` |
| [`09_foreign_python.nyx`](09_foreign_python.nyx) | Foreign function interface to Python standard modules (`platform`) | `python` |
| [`10_concurrent_tasks.nyx`](10_concurrent_tasks.nyx) | Asynchronous functions (`async fn`), `Task<T>`, `await`, `guard`, and `defer` | `cpp`, `js`, `python` |
| [`11_data_pipeline.nyx`](11_data_pipeline.nyx) | Domain structs, traits (`impl Trait for Struct`), pattern matching, stream pipelines | `cpp`, `js`, `python` |

## How to Run

Execute any example with your target backend of choice:

```bash
# Run with the native C++20 backend (default)
nyx run examples/10_concurrent_tasks.nyx --target cpp

# Run with the Node.js backend
nyx run examples/10_concurrent_tasks.nyx --target js

# Run with the Python reference backend
nyx run examples/10_concurrent_tasks.nyx --target python

# Or check syntax and type validity only:
nyx check examples/11_data_pipeline.nyx
```
