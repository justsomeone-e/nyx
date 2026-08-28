# HolyEasyLang v4.0 — Formal Language & Compiler Specification

## 1. Architecture Overview

HolyEasyLang is a statically analyzed, multi-target programming language designed with an emphasis on deterministic type inference, zero-cost abstractions, robust error diagnostics, and seamless native transpilation.

```text
               HolyEasyLang Source (*.he)
                            │
                     [ 1. Lexer ] ─── Tokens
                            │
                    [ 2. Parser ] ─── Pure AST
                            │
                 [ 3. TypeChecker ] ─── Typed / Validated AST
                            │
                 ┌──────────┴──────────┐
                 │                     │
          [ C++20 Codegen ]    [ Python Codegen ]
           (hecpp -> .cpp)      (hepy -> .py)
                 │                     │
           Clang / GCC            Python Runner
                 │                     │
          Native Binary (.exe)    Interpreted
```

---

## 2. Core Grammar & Syntax

### 2.1 Variables & Declarations
```he
var x: int = 10         // Explicit type annotation
var y = 20.5            // Inferred float
let $silver = 8700      // Scoped immutable variable with optional $ sigil
const PI = 3.14159      // Constant declaration
```

### 2.2 Functions & Return Types
```he
fn add(a: int, b: int) -> int {
    return a + b
}
```

### 2.3 Structs & Data Modeling
```he
struct Target {
    name: string,
    freq: int,
    signal: float
}

var t = Target("Altin", 5000, 95.0)
```

### 2.4 Optionals & Safe Navigation
```he
var user: User? = null
var city = user?.address?.city ?? "Default City"
```

### 2.5 Result & Pattern Matching
```he
var res = Ok(1337)
match res {
    Ok(val) => print("Success:", val),
    Err(e) => print("Error:", e),
    _ => print("Fallback")
}
```

### 2.6 Unsafe Memory Primitives
Raw memory operations (`addr`, `peek`, `memdump`) are strictly constrained inside `unsafe { ... }` blocks:
```he
var val = 42
unsafe {
    var ptr = addr(val)
    var read_back = peek(ptr)
    assert(read_back == 42)
}
```

---

## 3. Error Diagnostic System (`E1000..E2006`)

All compile-time syntax and semantic errors produce rustc-style source-located diagnostics with underlined caret (`^^^^^`) pointers:

* `E1000`: Unexpected Token in Expression
* `E1001`: Unclosed Parenthesis / Bracket
* `E1050`: Unsafe Memory Operation in Safe Context
* `E2001`: Variable Declaration Type Mismatch
* `E2002`: Variable Assignment Type Mismatch
* `E2003`: Function Argument Type Mismatch
* `E2004`: Function Return Type Mismatch
* `E2005`: Incompatible Operator Operands
* `E2006`: Struct Constructor Field Type Mismatch

---

## 4. Package Management (`he.toml` & `he.lock`)

```toml
[package]
name = "my_project"
version = "0.1.0"
edition = "2026"

[dependencies]
std = "4.0.0"
math = "1.0.0"

[targets]
default = "hecpp"
```

CLI Commands:
* `he init [name]`
* `he add <package>`
* `he remove <package>`
* `he install`
* `he test [file.he]`
* `he build <file.he>`
* `he run <file.he>`
