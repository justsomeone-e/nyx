# HolyEasyLang — Native Interoperability & FFI Guide

> [!IMPORTANT]
> Native bindings (`#native`) allow direct integration with platform-specific C++, JavaScript, and Rust libraries. They are distinct from the standard cross-platform language library and are target-dependent.

---

## 1. The `#native` Directive

The `#native` block embeds platform-specific code directly into the transpiled output:

```holyeasy
#target hecpp

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

### 2.1 C++20 (`hecpp` — Gate 8 / Stable)
When targeting `hecpp`, native blocks have direct access to:
* The C++ Standard Library (`<vector>`, `<string>`, `<chrono>`, `<cmath>`, `<thread>`).
* Win32 / POSIX system APIs.
* External C libraries (`extern "C"`).

### 2.2 JavaScript / Node.js (`hejs` — Gate 8 / Stable)
When targeting `hejs`, native blocks can access the Node.js or Browser runtime:
```holyeasy
#target hejs

#native js {
    import fs from 'fs';
    function read_config_file(path) {
        return fs.readFileSync(path, 'utf8');
    }
}
```

### 2.3 Rust 2021 (`hers` — Gate 6 / Active Conformance)
When targeting `hers`, native blocks integrate with `std` and external crates:
```holyeasy
#target hers

#native rust {
    use std::time::Instant;
    fn start_timer() -> Instant {
        Instant::now()
    }
}
```

---

## 3. Unsafe Memory Operations & Direct Pointer Access

Low-level operations that bypass HolyEasyLang's memory safety guarantees must be enclosed in an `unsafe { ... }` block:

```holyeasy
fn inspect_raw_memory(target: int) {
    unsafe {
        var p = addr(target)
        var val = peek(p)
        print("Raw pointer:", p, "Value:", val)
    }
}
```

Attempting to call `addr()`, `peek()`, or raw memory modifications outside an `unsafe` block triggers diagnostic `E2000: Unsafe Operation Outside Unsafe Block`.
