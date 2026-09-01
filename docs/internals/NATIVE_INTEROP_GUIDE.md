# Nyx — Native Interoperability & FFI Guide

> [!IMPORTANT]
> Native bindings (`#native`) allow direct integration with platform-specific C++, JavaScript, and Rust libraries. They are distinct from the standard cross-platform language library and are target-dependent.

Application code should prefer typed-HIR foreign imports when a library can be
called directly. `#native` remains the escape hatch for ABI adapters and code
that cannot be represented by Nyx yet.

```nyx
#target cpp
import cpp "std::filesystem" from "<filesystem>" as fs

fn main() {
    print(fs.current_path().string())
}
```

The first supported integrations are C++ namespaces, Node.js modules,
and Python modules. Every import requires an alias and is target-gated:

```nyx
import js "node:os" as os
import python "platform" as platform
```

Rust and WASM foreign import syntax is reserved but intentionally rejected
until crate/package resolution and ABI lowering are implemented.

Foreign calls use versioned data-only binding manifests for argument and return
types. Nyx ships contracts for `std::filesystem`, `node:os`, `node:fs`, Python
`platform`, and Python `os`. A project can extend the catalog with a
`nyx.bindings.json` file at its root:

```json
{
  "schema_version": 1,
  "modules": [{
    "ecosystem": "js",
    "module": "node:path",
    "functions": {
      "basename": { "params": ["string"], "returns": "string" }
    },
    "types": {}
  }]
}
```

When a module has a binding contract, unknown functions, incorrect argument
counts, and incompatible argument types are compiler errors. Unbound modules
remain available as explicitly dynamic foreign APIs.

---

## 1. The `#native` Escape Hatch

The `#native` block embeds platform-specific code directly into the transpiled output:

```nyx
#target cpp

#native cpp {
    #include <cmath>
    double native_sin(double x) { return std::sin(x); }
}

fn calculate_wave(deg: float) -> float {
    // Calls embedded C++ function directly
    return native_sin(deg)
}
```

---

## 2. Target-Specific Interoperability

### 2.1 C++20 (`cpp` — Gate 8 / Stable)
When targeting `cpp`, native blocks have direct access to:
* The C++ Standard Library (`<vector>`, `<string>`, `<chrono>`, `<cmath>`, `<thread>`).
* Win32 / POSIX system APIs.
* External C libraries (`extern "C"`).

### 2.2 JavaScript / Node.js (`js` — Gate 8 / Stable)
When targeting `js`, native blocks can access the Node.js or Browser runtime:
```nyx
#target js

#native js {
    import fs from 'fs';
    function read_config_file(path) {
        return fs.readFileSync(path, 'utf8');
    }
}
```

### 2.3 Rust 2021 (`rust` — Gate 6 / Active Conformance)
When targeting `rust`, native blocks integrate with `std` and external crates:
```nyx
#target rust

#native rust {
    use std::time::Instant;
    fn start_timer() -> Instant {
        Instant::now()
    }
}
```

---

## 3. Unsafe Memory Operations & Direct Pointer Access

Low-level operations that bypass Nyx's memory safety guarantees must be enclosed in an `unsafe { ... }` block:

```nyx
fn inspect_raw_memory(target: int) {
    unsafe {
        var p = addr(target)
        var val = peek(p)
        print("Raw pointer:", p, "Value:", val)
    }
}
```

Attempting to call `addr()`, `peek()`, or raw memory modifications outside an `unsafe` block triggers diagnostic `E2000: Unsafe Operation Outside Unsafe Block`.
