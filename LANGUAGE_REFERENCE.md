# 📖 HolyEasyLang Language Reference & Syntax Specification

HolyEasyLang is a statically-typed language engineered for multi-target execution with zero cognitive overhead.

---

## 1. Variables and Constants

```holyeasy
var age: int = 24       // Mutable variable with explicit type
var name = "Umut"       // Type inference (infers string)
val pi: float = 3.1415  // Immutable constant
```

---

## 2. Functions & Return Types

```holyeasy
fn add(a: int, b: int) -> int {
    return a + b
}

fn greet(name: string) {
    print("Hello, " + name)
}
```

---

## 3. Structs & Field Mutability

```holyeasy
struct Point {
    x: int,
    y: int
}

var p = Point(10, 20)
p.x = 15
print("Coordinates:", p.x, p.y)
```

---

## 4. Control Flow

### If / Else Conditionals
```holyeasy
if score >= 90 {
    print("Grade: A")
} else if score >= 80 {
    print("Grade: B")
} else {
    print("Grade: C")
}
```

### Loops
```holyeasy
// Range loop
for i in 1..10 {
    print(i)
}

// While loop
var count = 5
while count > 0 {
    count = count - 1
}
```

---

## 5. Modules & Imports

```holyeasy
import "./helper"                       // Local relative file helper.he
import "std/math"                       // Standard library math module
import { abs_val, power } from "std/math" // Selective symbol imports
```

---

## 6. Pattern Matching & Result Types

```holyeasy
var res: Result<int, string> = Ok(1337)

match res {
    Ok(val) => print("Operation succeeded with value:", val),
    Err(e) => print("Failed with error:", e),
    _ => print("Default fallback")
}
```

---

## 7. In-File Unit Tests

```holyeasy
fn multiply(a: int, b: int) -> int {
    return a * b
}

test "multiplication verification" {
    assert(multiply(4, 5) == 20, "4 * 5 must equal 20")
}
```

Run in-file tests directly:
```bash
he test src/main.he
```
