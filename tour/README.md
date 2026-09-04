# Tour of Nyx 🌙

> An interactive, guided terminal tour of the Nyx programming language, inspired by `rustlings`, with high-fidelity ANSI graphics, instant diagnostics, and live file-watching.

```text
  ████████╗ ██████╗ ██╗   ██╗██████╗      ██████╗ ███████╗    ███╗   ██╗██╗   ██╗██╗  ██╗
  ╚══██╔══╝██╔═══██╗██║   ██║██╔══██╗    ██╔═══██╗██╔════╝    ████╗  ██║╚██╗ ██╔╝╚██╗██╔╝
     ██║   ██║   ██║██║   ██║██████╔╝    ██║   ██║█████╗      ██╔██╗ ██║ ╚████╔╝  ╚███╔╝ 
     ██║   ██║   ██║██║   ██║██╔══██╗    ██║   ██║██╔══╝      ██║╚██╗██║  ╚██╔╝   ██╔██╗ 
     ██║   ╚██████╔╝╚██████╔╝██║  ██║    ╚██████╔╝██║         ██║ ╚████║   ██║   ██╔╝ ██╗
     ╚═╝    ╚═════╝  ╚═════╝ ╚═╝  ╚═╝     ╚═════╝ ╚═╝         ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝
```

---

## 🚀 Quick Start

From the repository root:
```bash
# Windows Command Prompt
tour.bat

# PowerShell
.\tour.ps1

# Direct Python
python tour/tour.py
```

Or double-click **`Tour of Nyx.bat`** on your Desktop!

---

## 🎮 Interactive Controls in Watch Mode

While in watch mode, the Tour monitors your current exercise file in real-time. Whenever you save changes in your code editor (like VS Code), the compiler immediately verifies your solution.

| Hotkey | Action | Description |
| :---: | :--- | :--- |
| **`n`** | **Next** | Advance to the next exercise |
| **`p`** | **Prev** | Go back to the previous exercise |
| **`h`** | **Hint** | View progressive hints for the current exercise |
| **`r`** | **Re-run** | Force a re-compilation / re-execution |
| **`l`** | **List** | Open full interactive curriculum tree |
| **`s`** | **Solution** | Toggle reference solution view if stuck |
| **`q`** | **Quit** | Save progress and exit cleanly |

---

## 📚 Curriculum (33 Exercises across 13 Modules)

1. **`00_intro`**
   - `intro01`: Welcome to Nyx & verifying your environment.
   - `intro02`: Fixing syntax errors in string literals.
2. **`01_variables`**
   - `variables01`: Immutable bindings with `let`.
   - `variables02`: Mutable variables with `var` and `set`.
   - `variables03`: Static type annotations (`int`, `string`, `bool`).
   - `variables04`: Constant declarations with `const`.
   - `variables05`: Arithmetic operations and variable scoping.
   - `variables06`: Destructuring patterns (`let [x, y] = coords`).
3. **`02_types`**
   - `types01`: Scalar types: `int`, `float`, and widening.
   - `types02`: Boolean logic with `and`, `or`, and `not`.
   - `types03`: String concatenation and escapes.
4. **`03_functions`**
   - `functions01`: Function declarations with `fn`.
   - `functions02`: Parameters and explicit return types (`-> int`).
   - `functions03`: Expression-bodied functions (`fn square(x) = x * x`).
   - `functions04`: Trailing default parameter values.
5. **`04_control_flow`**
   - `if01`: Multi-branch `if` / `elif` / `else`.
   - `if02`: Value-producing `if` expressions.
   - `loops01`: Inclusive range loops (`for i in 1..5`).
   - `loops02`: State-driven `while` loops.
   - `loops03`: Unconditional `loop`, `break`, and `continue`.
   - `match01`: Pattern matching with mandatory wildcard `_`.
6. **`05_arrays`**
   - `arrays01`: Array literals and 0-based indexing.
   - `arrays02`: In-place element modification with `set arr[i] = ...`.
   - `arrays03`: Iterating and aggregating array data.
7. **`06_structs`**
   - `structs01`: Declaring and instantiating data structs.
   - `structs02`: Methods and `self` with `impl StructName`.
8. **`07_traits`**
   - `traits01`: Trait definitions and contract implementations (`impl Trait for Type`).
9. **`08_error_handling`**
   - `errors01`: Structured exceptions with `try`, `catch`, and `throw`.
10. **`09_null_safety`**
    - `null01`: Optional types (`string?`, `null`) and null coalescing (`??`).
    - `null02`: Precondition enforcement with `guard ... else { return }`.
11. **`10_pipelines`**
    - `pipeline01`: Function composition with the pipeline operator (`|>`).
12. **`11_testing`**
    - `tests01`: In-file unit testing with `test "name" { assert(...) }`.
13. **`12_quizzes`**
    - `quiz01`: Capstone RPG inventory score calculator combining structs, methods, loops, match, and guards!

---

## 🛠️ CLI Subcommands

```bash
# Watch mode (default)
tour.bat

# Check all exercises and display overall progress table
tour.bat check-all

# Run a specific exercise
tour.bat run variables01

# Display hints for an exercise
tour.bat hint variables02

# List the full curriculum tree
tour.bat list

# Reset an exercise to its initial broken state
tour.bat reset variables01

# Reset all exercises and reset state
tour.bat reset all
```

---

## 🧪 Autonomous Test Suite

To verify that all 33 unsolved exercises fail as expected and all 33 reference solutions compile and pass with 0 errors:

```bash
python tour/verify_all.py
```
Output:
```text
======================================================================
Tour of Nyx - Autonomous Verification Suite (33 Exercises)
======================================================================
[01/33] ✅ PASS intro01        (Unsolved: FAIL as expected | Solved: OK in 374ms)
...
[33/33] ✅ PASS quiz01         (Unsolved: FAIL as expected | Solved: OK in 432ms)
======================================================================
Verification Summary: 33/33 passed.
🎉 ALL 33 EXERCISES AND SOLUTIONS VERIFIED 100% CLEANLY!
======================================================================
```
