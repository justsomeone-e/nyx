# -*- coding: utf-8 -*-
"""
Curriculum Builder for Tour of Nyx
Generates 67 progressive exercises across 16 core language modules.
"""

import os
import json

EXERCISES_DATA = [
    # =========================================================================
    # 00_intro (3 exercises)
    # =========================================================================
    {
        "id": "intro01",
        "name": "intro01",
        "topic": "00_intro",
        "title": "Welcome to Nyx",
        "path": "exercises/00_intro/intro01.nyx",
        "solution": "solutions/00_intro/intro01.nyx",
        "mode": "run",
        "description": "Run your very first Nyx program to verify your environment.",
        "hints": [
            "This exercise is already solved! Just check that it compiles and runs.",
            "Press 'n' in the terminal to advance to the next exercise."
        ],
        "exercise_code": '''// Welcome to Tour of Nyx!
// This exercise is already solved to get you started.
// In future exercises, you will fix errors and write code.
//
// Press 'n' in the Tour terminal or modify this file to experiment!

fn main() {
    print("Hello, Nyx Explorer! Welcome to the Tour of Nyx.")
}

main()
''',
        "solution_code": '''fn main() {
    print("Hello, Nyx Explorer! Welcome to the Tour of Nyx.")
}

main()
'''
    },
    {
        "id": "intro02",
        "name": "intro02",
        "topic": "00_intro",
        "title": "Fixing Syntax Errors",
        "path": "exercises/00_intro/intro02.nyx",
        "solution": "solutions/00_intro/intro02.nyx",
        "mode": "run",
        "description": "Fix a missing closing quote in a print statement.",
        "hints": [
            "Look at line 6: the string is missing a closing quote character '\"'.",
            "Strings in Nyx must start and end with matching quotation marks."
        ],
        "exercise_code": '''// I AM NOT DONE
// TODO: Fix the syntax error in the print statement below.
// In Nyx, strings must be closed with matching quotes.

fn main() {
    print("Welcome to modern systems programming with Nyx!
}

main()
''',
        "solution_code": '''fn main() {
    print("Welcome to modern systems programming with Nyx!")
}

main()
'''
    },
    {
        "id": "intro03",
        "name": "intro03",
        "topic": "00_intro",
        "title": "Comments in Nyx",
        "path": "exercises/00_intro/intro03.nyx",
        "solution": "solutions/00_intro/intro03.nyx",
        "mode": "run",
        "description": "Uncomment code using double slash // line comments.",
        "hints": [
            "Lines starting with '//' are ignored by the compiler.",
            "Remove '//' before `let message = \"Nyx is fast!\"` and the print call."
        ],
        "exercise_code": '''// I AM NOT DONE
// In Nyx, comments start with `//` and are ignored by the compiler.
// TODO: Uncomment the declaration of `message` and the print call!

fn main() {
    // let message = "Nyx is fast!"
    let message = ""
    assert(message == "Nyx is fast!", "message must equal 'Nyx is fast!'")
    print(message)
}

main()
''',
        "solution_code": '''fn main() {
    let message = "Nyx is fast!"
    assert(message == "Nyx is fast!", "message must equal 'Nyx is fast!'")
    print(message)
}

main()
'''
    },

    # =========================================================================
    # 01_variables (8 exercises)
    # =========================================================================
    {
        "id": "variables01",
        "name": "variables01",
        "topic": "01_variables",
        "title": "Immutable Bindings with let",
        "path": "exercises/01_variables/variables01.nyx",
        "solution": "solutions/01_variables/variables01.nyx",
        "mode": "run",
        "description": "Declare an immutable variable using the let keyword.",
        "hints": [
            "In Nyx, variables cannot be introduced without a keyword.",
            "Use `let x = 42` to introduce an immutable binding."
        ],
        "exercise_code": '''// I AM NOT DONE
// In Nyx, bindings are introduced with `let` (immutable) or `var` (mutable).
// TODO: Declare `x` with value 42 using the `let` keyword.

fn main() {
    // Declare x here:

    print("x is:", x)
}

main()
''',
        "solution_code": '''fn main() {
    let x = 42
    print("x is:", x)
}

main()
'''
    },
    {
        "id": "variables02",
        "name": "variables02",
        "topic": "01_variables",
        "title": "Mutable Variables with var and set",
        "path": "exercises/01_variables/variables02.nyx",
        "solution": "solutions/01_variables/variables02.nyx",
        "mode": "run",
        "description": "Allow variable mutation by changing let to var.",
        "hints": [
            "`let count = 10` creates an immutable binding.",
            "Change `let count = 10` to `var count = 10`."
        ],
        "exercise_code": '''// I AM NOT DONE
// In Nyx, immutable bindings created with `let` cannot be modified.
// To allow mutation, declare the variable with `var`, and update it with `set`.
// TODO: Change `let` to `var` so that `count` can be incremented.

fn main() {
    let count = 10
    set count = count + 5
    print("Updated count:", count)
}

main()
''',
        "solution_code": '''fn main() {
    var count = 10
    set count = count + 5
    print("Updated count:", count)
}

main()
'''
    },
    {
        "id": "variables03",
        "name": "variables03",
        "topic": "01_variables",
        "title": "Type Annotations",
        "path": "exercises/01_variables/variables03.nyx",
        "solution": "solutions/01_variables/variables03.nyx",
        "mode": "check",
        "description": "Fix a type mismatch where a string was assigned to an int.",
        "hints": [
            "`let age: int` declares that `age` must be an integer.",
            "Change \"twenty\" to an integer literal like `20`."
        ],
        "exercise_code": '''// I AM NOT DONE
// Nyx is statically typed. You can annotate variables with `: type`.
// Types include `int`, `float`, `string`, `bool`.
// TODO: Fix the type mismatch below so the compiler is satisfied.

fn check_types() {
    let age: int = "twenty"
    let name: string = "Nyx"
    let active: bool = true
}
''',
        "solution_code": '''fn check_types() {
    let age: int = 20
    let name: string = "Nyx"
    let active: bool = true
}
'''
    },
    {
        "id": "variables04",
        "name": "variables04",
        "topic": "01_variables",
        "title": "Constants with const",
        "path": "exercises/01_variables/variables04.nyx",
        "solution": "solutions/01_variables/variables04.nyx",
        "mode": "run",
        "description": "Understand that const values cannot be reassigned.",
        "hints": [
            "Constants declared with `const` cannot be updated.",
            "Read from `MAX_USERS` into a new local variable instead of reassigning it."
        ],
        "exercise_code": '''// I AM NOT DONE
// `const` declares compile-time immutable values.
// Attempting to reassign a `const` is a compile-time error.
// TODO: Fix the code so `MAX_USERS` is not illegally reassigned.

const MAX_USERS: int = 100

fn main() {
    set MAX_USERS = 200
    print("Max users limit:", MAX_USERS)
}

main()
''',
        "solution_code": '''const MAX_USERS: int = 100

fn main() {
    let current_limit = MAX_USERS
    print("Max users limit:", current_limit)
}

main()
'''
    },
    {
        "id": "variables05",
        "name": "variables05",
        "topic": "01_variables",
        "title": "Arithmetic & Scopes",
        "path": "exercises/01_variables/variables05.nyx",
        "solution": "solutions/01_variables/variables05.nyx",
        "mode": "run",
        "description": "Compute and declare the area of a rectangle.",
        "hints": [
            "Declare `let area = width * height` before the print statement."
        ],
        "exercise_code": '''// I AM NOT DONE
// TODO: Calculate the area of a rectangle with width 7 and height 6.
// Store the result in `area` and print it.

fn main() {
    let width = 7
    let height = 6
    // Declare `area` and compute width * height
    print("Rectangle area:", area)
}

main()
''',
        "solution_code": '''fn main() {
    let width = 7
    let height = 6
    let area = width * height
    print("Rectangle area:", area)
}

main()
'''
    },
    {
        "id": "variables06",
        "name": "variables06",
        "topic": "01_variables",
        "title": "Array Destructuring",
        "path": "exercises/01_variables/variables06.nyx",
        "solution": "solutions/01_variables/variables06.nyx",
        "mode": "run",
        "description": "Unpack coordinates using array destructuring.",
        "hints": [
            "Use `let [x, y] = coords` to unpack the two values at once."
        ],
        "exercise_code": '''// I AM NOT DONE
// Nyx supports array destructuring: `let [first, second] = [val1, val2]`
// TODO: Destructure `coords` into `x` and `y`.

fn main() {
    let coords = [100, 250]
    // Destructure here:
    let x = 0
    let y = 0
    assert(x == 100 and y == 250, "x and y must be destructured from coords!")
    print("X:", x, "Y:", y)
}

main()
''',
        "solution_code": '''fn main() {
    let coords = [100, 250]
    let [x, y] = coords
    assert(x == 100 and y == 250, "x and y must be destructured from coords!")
    print("X:", x, "Y:", y)
}

main()
'''
    },
    {
        "id": "variables07",
        "name": "variables07",
        "topic": "01_variables",
        "title": "Struct Destructuring",
        "path": "exercises/01_variables/variables07.nyx",
        "solution": "solutions/01_variables/variables07.nyx",
        "mode": "run",
        "description": "Unpack fields from a struct using positional destructuring.",
        "hints": [
            "Write `let Point(px, py) = p` to bind `px` and `py`."
        ],
        "exercise_code": '''// I AM NOT DONE
// Nyx also supports positional struct destructuring:
//   `let Point(x, y) = point_instance`
// TODO: Destructure `p` into `px` and `py`.

struct Point {
    x: int,
    y: int
}

fn main() {
    let p = Point(30, 70)
    // Destructure Point(px, py) from p:
    let px = 0
    let py = 0

    assert(px == 30 and py == 70, "px and py must match p.x and p.y!")
    print("Destructured Point:", px, py)
}

main()
''',
        "solution_code": '''struct Point {
    x: int,
    y: int
}

fn main() {
    let p = Point(30, 70)
    let Point(px, py) = p
    assert(px == 30 and py == 70, "px and py must match p.x and p.y!")
    print("Destructured Point:", px, py)
}

main()
'''
    },
    {
        "id": "variables08",
        "name": "variables08",
        "topic": "01_variables",
        "title": "Discarding Values with Underscore",
        "path": "exercises/01_variables/variables08.nyx",
        "solution": "solutions/01_variables/variables08.nyx",
        "mode": "run",
        "description": "Discard unused values during destructuring with _.",
        "hints": [
            "Use `_` to ignore unwanted items: `let [first, _] = pair`."
        ],
        "exercise_code": '''// I AM NOT DONE
// When destructuring, you can discard unwanted values using `_`:
//   `let [first, _] = values`
// TODO: Extract only `first_val` and ignore the second value with `_`.

fn main() {
    let pair = [42, 999]
    // Destructure first_val and discard the second with _:
    let first_val = 0

    assert(first_val == 42, "first_val must be 42!")
    print("Extracted first value:", first_val)
}

main()
''',
        "solution_code": '''fn main() {
    let pair = [42, 999]
    let [first_val, _] = pair
    assert(first_val == 42, "first_val must be 42!")
    print("Extracted first value:", first_val)
}

main()
'''
    },

    # =========================================================================
    # 02_types (6 exercises)
    # =========================================================================
    {
        "id": "types01",
        "name": "types01",
        "topic": "02_types",
        "title": "Integers and Floats",
        "path": "exercises/02_types/types01.nyx",
        "solution": "solutions/02_types/types01.nyx",
        "mode": "check",
        "description": "Specify the correct float type for decimal values.",
        "hints": [
            "0.75 has a decimal point, making it a `float`, not an `int`.",
            "Change `let ratio: int` to `let ratio: float`."
        ],
        "exercise_code": '''// I AM NOT DONE
// Nyx integers do not automatically narrow from float without explicit conversion.
// Float literals have a decimal point (e.g. 3.14).
// TODO: Fix the type declaration so `ratio` has the correct type `float`.

fn demo_numerics() {
    let count: int = 50
    let ratio: int = 0.75
}
''',
        "solution_code": '''fn demo_numerics() {
    let count: int = 50
    let ratio: float = 0.75
}
'''
    },
    {
        "id": "types02",
        "name": "types02",
        "topic": "02_types",
        "title": "Booleans and Logic",
        "path": "exercises/02_types/types02.nyx",
        "solution": "solutions/02_types/types02.nyx",
        "mode": "run",
        "description": "Combine boolean flags using the `or` keyword.",
        "hints": [
            "In Nyx, boolean OR is expressed with `or` (or `||`).",
            "Write `let is_allowed: bool = is_admin or has_token`."
        ],
        "exercise_code": '''// I AM NOT DONE
// Nyx uses words `and`, `or`, and `not` for boolean logic.
// TODO: Set `is_allowed` to true when `is_admin` is true OR `has_token` is true.

fn main() {
    let is_admin: bool = false
    let has_token: bool = true
    let is_allowed: bool = false // Fix this condition!
    assert(is_allowed == true, "Access should be allowed when token is present!")
    print("Access allowed:", is_allowed)
}

main()
''',
        "solution_code": '''fn main() {
    let is_admin: bool = false
    let has_token: bool = true
    let is_allowed: bool = is_admin or has_token
    assert(is_allowed == true, "Access should be allowed when token is present!")
    print("Access allowed:", is_allowed)
}

main()
'''
    },
    {
        "id": "types03",
        "name": "types03",
        "topic": "02_types",
        "title": "Strings and Concatenation",
        "path": "exercises/02_types/types03.nyx",
        "solution": "solutions/02_types/types03.nyx",
        "mode": "run",
        "description": "Concatenate string variables using the + operator.",
        "hints": [
            "Use `first + \" \" + last` to concatenate with a space."
        ],
        "exercise_code": '''// I AM NOT DONE
// Strings in Nyx can be concatenated using the `+` operator.
// TODO: Combine `first` and `last` with a space to form "Nyx Language".

fn main() {
    let first = "Nyx"
    let last = "Language"
    let full_name = first // Fix concatenation here
    assert(full_name == "Nyx Language", "full_name must be 'Nyx Language'!")
    print("Full name:", full_name)
}

main()
''',
        "solution_code": '''fn main() {
    let first = "Nyx"
    let last = "Language"
    let full_name = first + " " + last
    assert(full_name == "Nyx Language", "full_name must be 'Nyx Language'!")
    print("Full name:", full_name)
}

main()
'''
    },
    {
        "id": "types04",
        "name": "types04",
        "topic": "02_types",
        "title": "String Length",
        "path": "exercises/02_types/types04.nyx",
        "solution": "solutions/02_types/types04.nyx",
        "mode": "run",
        "description": "Determine the length of a string using len().",
        "hints": [
            "`len(s)` returns the character length of string `s`.",
            "Write `let length = len(title)`."
        ],
        "exercise_code": '''// I AM NOT DONE
// The built-in function `len(string)` returns the length of a string.
// TODO: Calculate the length of `title` using `len(...)`.

fn main() {
    let title = "Antigravity"
    let length = 0 // Compute len(title)

    assert(length == 11, "Length of 'Antigravity' must be 11!")
    print("Title length is:", length)
}

main()
''',
        "solution_code": '''fn main() {
    let title = "Antigravity"
    let length = len(title)
    assert(length == 11, "Length of 'Antigravity' must be 11!")
    print("Title length is:", length)
}

main()
'''
    },
    {
        "id": "types05",
        "name": "types05",
        "topic": "02_types",
        "title": "Escape Sequences",
        "path": "exercises/02_types/types05.nyx",
        "solution": "solutions/02_types/types05.nyx",
        "mode": "run",
        "description": "Use newline \\n and tab \\t escapes in string literals.",
        "hints": [
            "Use `\"Line 1\\nLine 2\"` to insert a newline."
        ],
        "exercise_code": '''// I AM NOT DONE
// Nyx string literals support standard escape sequences like `\\n` (newline) and `\\t` (tab).
// TODO: Create a two-line string with \"Hello\" on line 1 and \"World\" on line 2.

fn main() {
    let text = "Hello World" // Use \\n between Hello and World
    assert(text == "Hello\\nWorld", "text must contain a newline escape \\n")
    print(text)
}

main()
''',
        "solution_code": '''fn main() {
    let text = "Hello\\nWorld"
    assert(text == "Hello\\nWorld", "text must contain a newline escape \\n")
    print(text)
}

main()
'''
    },
    {
        "id": "types06",
        "name": "types06",
        "topic": "02_types",
        "title": "Integer Widening",
        "path": "exercises/02_types/types06.nyx",
        "solution": "solutions/02_types/types06.nyx",
        "mode": "run",
        "description": "Observe automatic int widening to float in mixed expressions.",
        "hints": [
            "In Nyx, adding an int to a float widens the int to float automatically.",
            "Write `let result: float = base + fraction`."
        ],
        "exercise_code": '''// I AM NOT DONE
// An `int` automatically widens to `float` when combined with a float operator.
// TODO: Add `base` (int) and `fraction` (float) together and store in `result: float`.

fn main() {
    let base: int = 10
    let fraction: float = 0.5
    let result: float = 0.0 // Add base + fraction

    assert(result == 10.5, "result must be 10.5")
    print("Widened calculation:", result)
}

main()
''',
        "solution_code": '''fn main() {
    let base: int = 10
    let fraction: float = 0.5
    let result: float = base + fraction

    assert(result == 10.5, "result must be 10.5")
    print("Widened calculation:", result)
}

main()
'''
    },

    # =========================================================================
    # 03_functions (6 exercises)
    # =========================================================================
    {
        "id": "functions01",
        "name": "functions01",
        "topic": "03_functions",
        "title": "Function Declaration",
        "path": "exercises/03_functions/functions01.nyx",
        "solution": "solutions/03_functions/functions01.nyx",
        "mode": "run",
        "description": "Define a void function using the fn keyword.",
        "hints": [
            "Define `fn call_me() { print(\"Called successfully!\") }`."
        ],
        "exercise_code": '''// I AM NOT DONE
// In Nyx, functions are declared with the `fn` keyword.
// TODO: Define a function named `call_me` that prints "Called successfully!".

fn main() {
    call_me()
}

main()
''',
        "solution_code": '''fn call_me() {
    print("Called successfully!")
}

fn main() {
    call_me()
}

main()
'''
    },
    {
        "id": "functions02",
        "name": "functions02",
        "topic": "03_functions",
        "title": "Parameters and Return Types",
        "path": "exercises/03_functions/functions02.nyx",
        "solution": "solutions/03_functions/functions02.nyx",
        "mode": "run",
        "description": "Write a function returning the product of two integers.",
        "hints": [
            "Inside `multiply`, write `return a * b`."
        ],
        "exercise_code": '''// I AM NOT DONE
// Functions specify parameter types and return types: `fn name(a: int) -> int`
// TODO: Complete the `multiply` function so it returns `a * b`.

fn multiply(a: int, b: int) -> int {
    // Add return statement
}

fn main() {
    let result = multiply(6, 7)
    assert(result == 42, "6 * 7 must be 42")
    print("6 * 7 =", result)
}

main()
''',
        "solution_code": '''fn multiply(a: int, b: int) -> int {
    return a * b
}

fn main() {
    let result = multiply(6, 7)
    assert(result == 42, "6 * 7 must be 42")
    print("6 * 7 =", result)
}

main()
'''
    },
    {
        "id": "functions03",
        "name": "functions03",
        "topic": "03_functions",
        "title": "Expression-Bodied Functions",
        "path": "exercises/03_functions/functions03.nyx",
        "solution": "solutions/03_functions/functions03.nyx",
        "mode": "run",
        "description": "Define a concise expression-bodied function using =.",
        "hints": [
            "Write `fn cube(x: int) -> int = x * x * x`."
        ],
        "exercise_code": '''// I AM NOT DONE
// In Nyx, concise functions can use expression bodies:
//   fn square(x: int) -> int = x * x
// TODO: Define an expression-bodied function `cube` that computes `x * x * x`.

// Define `cube` here:

fn main() {
    let res = cube(3)
    assert(res == 27, "Cube of 3 must be 27")
    print("Cube of 3 is:", res)
}

main()
''',
        "solution_code": '''fn cube(x: int) -> int = x * x * x

fn main() {
    let res = cube(3)
    assert(res == 27, "Cube of 3 must be 27")
    print("Cube of 3 is:", res)
}

main()
'''
    },
    {
        "id": "functions04",
        "name": "functions04",
        "topic": "03_functions",
        "title": "Default Parameter Values",
        "path": "exercises/03_functions/functions04.nyx",
        "solution": "solutions/03_functions/functions04.nyx",
        "mode": "run",
        "description": "Supply a default parameter value for omitted arguments.",
        "hints": [
            "Change `title: string` to `title: string = \"Adventurer\"` in the parameter list."
        ],
        "exercise_code": '''// I AM NOT DONE
// Parameters can declare default values: `fn greet(name: string, title: string = "Explorer")`
// Trailing parameters with defaults can be omitted by the caller.
// TODO: Add a default value "Adventurer" to `title`.

fn greet(name: string, title: string) {
    print("Greetings, " + title + " " + name + "!")
}

fn main() {
    greet("Kurt", "Captain")
    greet("Nyx") // Should use default title!
}

main()
''',
        "solution_code": '''fn greet(name: string, title: string = "Adventurer") {
    print("Greetings, " + title + " " + name + "!")
}

fn main() {
    greet("Kurt", "Captain")
    greet("Nyx")
}

main()
'''
    },
    {
        "id": "functions05",
        "name": "functions05",
        "topic": "03_functions",
        "title": "Multiple Default Parameters",
        "path": "exercises/03_functions/functions05.nyx",
        "solution": "solutions/03_functions/functions05.nyx",
        "mode": "run",
        "description": "Provide multiple trailing parameters with default values.",
        "hints": [
            "Declare `fn make_sandwich(bread: string, filling: string = \"Cheese\", toasted: bool = true)`."
        ],
        "exercise_code": '''// I AM NOT DONE
// Multiple trailing parameters can declare defaults in Nyx.
// TODO: Give `filling` the default \"Cheese\" and `toasted` the default `true`.

fn make_sandwich(bread: string, filling: string, toasted: bool) -> string {
    let toast_str = if toasted { "Toasted" } else { "Fresh" }
    return toast_str + " " + filling + " on " + bread
}

fn main() {
    let s1 = make_sandwich("Rye", "Turkey", false)
    let s2 = make_sandwich("Sourdough") // Should use defaults: Cheese and true!

    assert(s1 == "Fresh Turkey on Rye", "s1 must match custom arguments")
    assert(s2 == "Toasted Cheese on Sourdough", "s2 must use default values")
    print(s1)
    print(s2)
}

main()
''',
        "solution_code": '''fn make_sandwich(bread: string, filling: string = "Cheese", toasted: bool = true) -> string {
    let toast_str = if toasted { "Toasted" } else { "Fresh" }
    return toast_str + " " + filling + " on " + bread
}

fn main() {
    let s1 = make_sandwich("Rye", "Turkey", false)
    let s2 = make_sandwich("Sourdough")

    assert(s1 == "Fresh Turkey on Rye", "s1 must match custom arguments")
    assert(s2 == "Toasted Cheese on Sourdough", "s2 must use default values")
    print(s1)
    print(s2)
}

main()
'''
    },
    {
        "id": "functions06",
        "name": "functions06",
        "topic": "03_functions",
        "title": "Recursive Functions",
        "path": "exercises/03_functions/functions06.nyx",
        "solution": "solutions/03_functions/functions06.nyx",
        "mode": "run",
        "description": "Implement the factorial function recursively in Nyx.",
        "hints": [
            "Base case: `if n <= 1 { return 1 }`.",
            "Recursive step: `return n * factorial(n - 1)`."
        ],
        "exercise_code": '''// I AM NOT DONE
// Functions can call themselves recursively with a base case.
// TODO: Implement the recursive `factorial(n: int) -> int` function!

fn factorial(n: int) -> int {
    // Add base case and recursive call!
    return 0
}

fn main() {
    let res = factorial(5)
    assert(res == 120, "factorial(5) must be 120 (5 * 4 * 3 * 2 * 1)!")
    print("5! =", res)
}

main()
''',
        "solution_code": '''fn factorial(n: int) -> int {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}

fn main() {
    let res = factorial(5)
    assert(res == 120, "factorial(5) must be 120 (5 * 4 * 3 * 2 * 1)!")
    print("5! =", res)
}

main()
'''
    },

    # =========================================================================
    # 04_control_flow (9 exercises)
    # =========================================================================
    {
        "id": "if01",
        "name": "if01",
        "topic": "04_control_flow",
        "title": "Conditional Branching",
        "path": "exercises/04_control_flow/if01.nyx",
        "solution": "solutions/04_control_flow/if01.nyx",
        "mode": "run",
        "description": "Structure multi-way branching using elif and else.",
        "hints": [
            "Add `elif temp > 15 { return \"Warm\" } else { return \"Cold\" }`."
        ],
        "exercise_code": '''// I AM NOT DONE
// In Nyx, `if`, `elif` (or `else if`), and `else` control branch execution.
// TODO: Complete the temperature check:
// If temp > 30 return "Hot", elif temp > 15 return "Warm", else return "Cold".

fn check_temp(temp: int) -> string {
    if temp > 30 {
        return "Hot"
    }
    // Add elif and else arms here!
    return "Unknown"
}

fn main() {
    assert(check_temp(35) == "Hot", "35 must be Hot")
    assert(check_temp(20) == "Warm", "20 must be Warm")
    assert(check_temp(5) == "Cold", "5 must be Cold")
    print("All temperature checks passed!")
}

main()
''',
        "solution_code": '''fn check_temp(temp: int) -> string {
    if temp > 30 {
        return "Hot"
    } elif temp > 15 {
        return "Warm"
    } else {
        return "Cold"
    }
}

fn main() {
    assert(check_temp(35) == "Hot", "35 must be Hot")
    assert(check_temp(20) == "Warm", "20 must be Warm")
    assert(check_temp(5) == "Cold", "5 must be Cold")
    print("All temperature checks passed!")
}

main()
'''
    },
    {
        "id": "if02",
        "name": "if02",
        "topic": "04_control_flow",
        "title": "If as an Expression",
        "path": "exercises/04_control_flow/if02.nyx",
        "solution": "solutions/04_control_flow/if02.nyx",
        "mode": "check",
        "description": "Ensure all branches of an if expression return the same type.",
        "hints": [
            "The `else` arm returns integer `0`, but `status` expects a `string`.",
            "Change `0` to a string like `\"disconnected\"`."
        ],
        "exercise_code": '''// I AM NOT DONE
// In Nyx, `if` can be an expression returning a value!
// All branches must return the same type.
// TODO: Fix the branch return types so `status` is consistently a `string`.

fn get_status(is_online: bool) -> string {
    let status: string = if is_online {
        "connected"
    } else {
        0 // Error: 0 is an int, but string was expected!
    }
    return status
}
''',
        "solution_code": '''fn get_status(is_online: bool) -> string {
    let status: string = if is_online {
        "connected"
    } else {
        "disconnected"
    }
    return status
}
'''
    },
    {
        "id": "loops01",
        "name": "loops01",
        "topic": "04_control_flow",
        "title": "Range For Loops",
        "path": "exercises/04_control_flow/loops01.nyx",
        "solution": "solutions/04_control_flow/loops01.nyx",
        "mode": "run",
        "description": "Sum numbers from 1 to 5 using an inclusive range loop.",
        "hints": [
            "`1..4` only goes up to 4.",
            "Change the range to `1..5`."
        ],
        "exercise_code": '''// I AM NOT DONE
// Nyx provides inclusive range loops: `for i in start..end`
// For example, `1..5` iterates through 1, 2, 3, 4, 5.
// TODO: Sum all numbers from 1 to 5 inclusive and verify the total is 15.

fn main() {
    var total: int = 0
    for i in 1..4 { // Fix the range!
        set total = total + i
    }
    assert(total == 15, "Sum from 1 to 5 must equal 15!")
    print("Sum 1..5 is:", total)
}

main()
''',
        "solution_code": '''fn main() {
    var total: int = 0
    for i in 1..5 {
        set total = total + i
    }
    assert(total == 15, "Sum from 1 to 5 must equal 15!")
    print("Sum 1..5 is:", total)
}

main()
'''
    },
    {
        "id": "loops02",
        "name": "loops02",
        "topic": "04_control_flow",
        "title": "While Loops",
        "path": "exercises/04_control_flow/loops02.nyx",
        "solution": "solutions/04_control_flow/loops02.nyx",
        "mode": "run",
        "description": "Count down to 0 in a while loop.",
        "hints": [
            "Change `while countdown > 1` to `while countdown > 0`."
        ],
        "exercise_code": '''// I AM NOT DONE
// A `while` loop runs while its boolean condition is true.
// Remember to update mutable variables with `set`.
// TODO: Make the loop count all the way down to 0!

fn main() {
    var countdown = 3
    while countdown > 1 { // Should count down until 0!
        print("T-minus", countdown)
        set countdown = countdown - 1
    }
    assert(countdown == 0, "Countdown must reach 0!")
    print("Liftoff!")
}

main()
''',
        "solution_code": '''fn main() {
    var countdown = 3
    while countdown > 0 {
        print("T-minus", countdown)
        set countdown = countdown - 1
    }
    assert(countdown == 0, "Countdown must reach 0!")
    print("Liftoff!")
}

main()
'''
    },
    {
        "id": "loops03",
        "name": "loops03",
        "topic": "04_control_flow",
        "title": "Loop, Break, and Continue",
        "path": "exercises/04_control_flow/loops03.nyx",
        "solution": "solutions/04_control_flow/loops03.nyx",
        "mode": "run",
        "description": "Break out of an unconditional loop after 4 steps.",
        "hints": [
            "Inside the loop, add `if step == 4 { break }`."
        ],
        "exercise_code": '''// I AM NOT DONE
// `loop` creates an unconditional loop.
// Use `break` to exit and `continue` to skip to the next iteration.
// TODO: Stop the loop when `step` reaches 4 using `break`.

fn main() {
    var step = 0
    loop {
        set step = step + 1
        print("Step:", step)
        // Add break condition here when step == 4!

        if step > 10 {
            throw "Loop runaway: failed to break at step 4!"
        }
    }
    assert(step == 4, "Loop must stop exactly at step 4!")
    print("Done after 4 steps!")
}

main()
''',
        "solution_code": '''fn main() {
    var step = 0
    loop {
        set step = step + 1
        print("Step:", step)
        if step == 4 {
            break
        }
        if step > 10 {
            throw "Loop runaway: failed to break at step 4!"
        }
    }
    assert(step == 4, "Loop must stop exactly at step 4!")
    print("Done after 4 steps!")
}

main()
'''
    },
    {
        "id": "loops04",
        "name": "loops04",
        "topic": "04_control_flow",
        "title": "Nested Loops",
        "path": "exercises/04_control_flow/loops04.nyx",
        "solution": "solutions/04_control_flow/loops04.nyx",
        "mode": "run",
        "description": "Traverse a 2D coordinate space using nested for loops.",
        "hints": [
            "In the inner loop, accumulate: `set total = total + (r * 10 + c)`."
        ],
        "exercise_code": '''// I AM NOT DONE
// Nested loops allow traversing 2D grids and matrices.
// TODO: Iterate row `r` from 1..2, and col `c` from 1..2.
// Multiply r by 10 and add c, accumulating into `total`.
// Expected: (11) + (12) + (21) + (22) = 66!

fn main() {
    var total = 0
    for r in 1..2 {
        for c in 1..2 {
            // Add (r * 10 + c) to total
        }
    }
    assert(total == 66, "Nested loop total must be 66!")
    print("Grid traversal sum:", total)
}

main()
''',
        "solution_code": '''fn main() {
    var total = 0
    for r in 1..2 {
        for c in 1..2 {
            set total = total + (r * 10 + c)
        }
    }
    assert(total == 66, "Nested loop total must be 66!")
    print("Grid traversal sum:", total)
}

main()
'''
    },
    {
        "id": "match01",
        "name": "match01",
        "topic": "04_control_flow",
        "title": "Pattern Matching",
        "path": "exercises/04_control_flow/match01.nyx",
        "solution": "solutions/04_control_flow/match01.nyx",
        "mode": "check",
        "description": "Supply the mandatory wildcard _ fallback in a match expression.",
        "hints": [
            "In Nyx, pattern matching must be exhaustive.",
            "Add `_ => \"Unknown\"` as the final match arm."
        ],
        "exercise_code": '''// I AM NOT DONE
// Nyx `match` requires an exhaustive pattern match, so the fallback `_` is mandatory.
// TODO: Add the mandatory `_ => ...` wildcard fallback arm to satisfy the compiler.

fn describe_status(code: int) -> string {
    let label = match code {
        200 => "OK",
        404 => "Not Found",
        500 => "Server Error"
    }
    return label
}
''',
        "solution_code": '''fn describe_status(code: int) -> string {
    let label = match code {
        200 => "OK",
        404 => "Not Found",
        500 => "Server Error",
        _ => "Unknown"
    }
    return label
}
'''
    },
    {
        "id": "match02",
        "name": "match02",
        "topic": "04_control_flow",
        "title": "Match Value Expressions",
        "path": "exercises/04_control_flow/match02.nyx",
        "solution": "solutions/04_control_flow/match02.nyx",
        "mode": "run",
        "description": "Convert numerical grades to letter ratings using match.",
        "hints": [
            "Map 1 => \"Bronze\", 2 => \"Silver\", 3 => \"Gold\", _ => \"Unranked\"."
        ],
        "exercise_code": '''// I AM NOT DONE
// `match` evaluates to a value directly.
// TODO: Complete the `get_tier` function using `match tier`:
//   1 => "Bronze"
//   2 => "Silver"
//   3 => "Gold"
//   _ => "Unranked"

fn get_tier(tier: int) -> string {
    return match tier {
        1 => "Bronze",
        _ => "Unranked"
    }
}

fn main() {
    assert(get_tier(3) == "Gold", "Tier 3 must be Gold")
    assert(get_tier(2) == "Silver", "Tier 2 must be Silver")
    print("Tier 3 is:", get_tier(3))
}

main()
''',
        "solution_code": '''fn get_tier(tier: int) -> string {
    return match tier {
        1 => "Bronze",
        2 => "Silver",
        3 => "Gold",
        _ => "Unranked"
    }
}

fn main() {
    assert(get_tier(3) == "Gold", "Tier 3 must be Gold")
    assert(get_tier(2) == "Silver", "Tier 2 must be Silver")
    print("Tier 3 is:", get_tier(3))
}

main()
'''
    },
    {
        "id": "match03",
        "name": "match03",
        "topic": "04_control_flow",
        "title": "Matching Booleans",
        "path": "exercises/04_control_flow/match03.nyx",
        "solution": "solutions/04_control_flow/match03.nyx",
        "mode": "run",
        "description": "Match on boolean states to produce human-readable labels.",
        "hints": [
            "Match true => \"Enabled\", false => \"Disabled\", _ => \"Unknown\"."
        ],
        "exercise_code": '''// I AM NOT DONE
// `match` works seamlessly on booleans and strings too.
// TODO: Match `flag`: `true => \"Enabled\"`, `false => \"Disabled\"`, `_ => \"Unknown\"`.

fn describe_flag(flag: bool) -> string {
    return match flag {
        true => "Enabled",
        _ => "Unknown"
    }
}

fn main() {
    assert(describe_flag(true) == "Enabled", "true should be Enabled")
    assert(describe_flag(false) == "Disabled", "false should be Disabled")
    print("Flag states verified!")
}

main()
''',
        "solution_code": '''fn describe_flag(flag: bool) -> string {
    return match flag {
        true => "Enabled",
        false => "Disabled",
        _ => "Unknown"
    }
}

fn main() {
    assert(describe_flag(true) == "Enabled", "true should be Enabled")
    assert(describe_flag(false) == "Disabled", "false should be Disabled")
    print("Flag states verified!")
}

main()
'''
    },

    # =========================================================================
    # 05_arrays (6 exercises)
    # =========================================================================
    {
        "id": "arrays01",
        "name": "arrays01",
        "topic": "05_arrays",
        "title": "Arrays and Indexing",
        "path": "exercises/05_arrays/arrays01.nyx",
        "solution": "solutions/05_arrays/arrays01.nyx",
        "mode": "run",
        "description": "Access array elements using 0-based indexing.",
        "hints": [
            "In a 0-indexed array, the second item is at index 1.",
            "Write `let item = inventory[1]`."
        ],
        "exercise_code": '''// I AM NOT DONE
// Arrays are written `[elem1, elem2, ...]` with 0-based indexing `arr[0]`.
// TODO: Print the second item ("Sapphire") from the inventory array.

fn main() {
    let inventory = ["Ruby", "Sapphire", "Emerald"]
    let item = inventory[0] // Change index to 1!
    assert(item == "Sapphire", "Selected item must be Sapphire!")
    print("Selected item:", item)
}

main()
''',
        "solution_code": '''fn main() {
    let inventory = ["Ruby", "Sapphire", "Emerald"]
    let item = inventory[1]
    assert(item == "Sapphire", "Selected item must be Sapphire!")
    print("Selected item:", item)
}

main()
'''
    },
    {
        "id": "arrays02",
        "name": "arrays02",
        "topic": "05_arrays",
        "title": "Modifying Array Elements",
        "path": "exercises/05_arrays/arrays02.nyx",
        "solution": "solutions/05_arrays/arrays02.nyx",
        "mode": "run",
        "description": "Update an array element using set array[index] = value.",
        "hints": [
            "Use `set scores[1] = 999` to update the middle element."
        ],
        "exercise_code": '''// I AM NOT DONE
// Array elements can be updated using `set array[index] = new_value`.
// TODO: Update the middle element (index 1) to 999.

fn main() {
    var scores = [10, 20, 30]
    // Set index 1 to 999
    assert(scores[1] == 999, "Middle score must be updated to 999!")
    print("Modified scores:", scores[0], scores[1], scores[2])
}

main()
''',
        "solution_code": '''fn main() {
    var scores = [10, 20, 30]
    set scores[1] = 999
    assert(scores[1] == 999, "Middle score must be updated to 999!")
    print("Modified scores:", scores[0], scores[1], scores[2])
}

main()
'''
    },
    {
        "id": "arrays03",
        "name": "arrays03",
        "topic": "05_arrays",
        "title": "Array Aggregation",
        "path": "exercises/05_arrays/arrays03.nyx",
        "solution": "solutions/05_arrays/arrays03.nyx",
        "mode": "run",
        "description": "Sum the elements of an array with a loop.",
        "hints": [
            "Inside the loop, update `sum` with `set sum = sum + values[i]`."
        ],
        "exercise_code": '''// I AM NOT DONE
// TODO: Loop through the array and compute the sum of all elements.
// Expected output: "Total sum: 150"

fn main() {
    let values = [10, 20, 30, 40, 50]
    var sum: int = 0
    for i in 0..4 {
        // Add values[i] to sum
    }
    assert(sum == 150, "Sum of all 5 items must be 150!")
    print("Total sum:", sum)
}

main()
''',
        "solution_code": '''fn main() {
    let values = [10, 20, 30, 40, 50]
    var sum: int = 0
    for i in 0..4 {
        set sum = sum + values[i]
    }
    assert(sum == 150, "Sum of all 5 items must be 150!")
    print("Total sum:", sum)
}

main()
'''
    },
    {
        "id": "arrays04",
        "name": "arrays04",
        "topic": "05_arrays",
        "title": "Array Length",
        "path": "exercises/05_arrays/arrays04.nyx",
        "solution": "solutions/05_arrays/arrays04.nyx",
        "mode": "run",
        "description": "Inspect dynamic array capacity and item counts with len().",
        "hints": [
            "Use `len(languages)` to get the item count."
        ],
        "exercise_code": '''// I AM NOT DONE
// The built-in `len(array)` function returns the count of items in an array.
// TODO: Measure the number of elements in `languages`.

fn main() {
    let languages = ["Nyx", "C++", "Rust", "Python"]
    let count = 0 // Compute len(languages)

    assert(count == 4, "languages array must have 4 items!")
    print("Tracked languages count:", count)
}

main()
''',
        "solution_code": '''fn main() {
    let languages = ["Nyx", "C++", "Rust", "Python"]
    let count = len(languages)
    assert(count == 4, "languages array must have 4 items!")
    print("Tracked languages count:", count)
}

main()
'''
    },
    {
        "id": "arrays05",
        "name": "arrays05",
        "topic": "05_arrays",
        "title": "Pushing Array Elements",
        "path": "exercises/05_arrays/arrays05.nyx",
        "solution": "solutions/05_arrays/arrays05.nyx",
        "mode": "run",
        "description": "Append elements dynamically to a mutable array using push().",
        "hints": [
            "Call `arr.push(30)` to append 30."
        ],
        "exercise_code": '''// I AM NOT DONE
// Arrays support dynamic appending via the `.push(value)` method.
// TODO: Append `30` to `numbers` so that its length becomes 3.

fn main() {
    var numbers = [10, 20]
    // Append 30 here:

    assert(len(numbers) == 3, "numbers array should contain 3 elements")
    assert(numbers[2] == 30, "last element should be 30")
    print("Updated array length:", len(numbers))
}

main()
''',
        "solution_code": '''fn main() {
    var numbers = [10, 20]
    numbers.push(30)
    assert(len(numbers) == 3, "numbers array should contain 3 elements")
    assert(numbers[2] == 30, "last element should be 30")
    print("Updated array length:", len(numbers))
}

main()
'''
    },
    {
        "id": "arrays06",
        "name": "arrays06",
        "topic": "05_arrays",
        "title": "Finding Max Element",
        "path": "exercises/05_arrays/arrays06.nyx",
        "solution": "solutions/05_arrays/arrays06.nyx",
        "mode": "run",
        "description": "Find the highest value in an integer array using a loop.",
        "hints": [
            "Inside the loop: `if nums[i] > max_val { set max_val = nums[i] }`."
        ],
        "exercise_code": '''// I AM NOT DONE
// TODO: Find the maximum number in `nums` and store it in `max_val`.

fn main() {
    let nums = [14, 88, 42, 95, 33]
    var max_val = nums[0]

    for i in 1..4 {
        // Update max_val if nums[i] is greater!
    }

    assert(max_val == 95, "Maximum value must be 95!")
    print("Highest score found:", max_val)
}

main()
''',
        "solution_code": '''fn main() {
    let nums = [14, 88, 42, 95, 33]
    var max_val = nums[0]

    for i in 1..4 {
        if nums[i] > max_val {
            set max_val = nums[i]
        }
    }

    assert(max_val == 95, "Maximum value must be 95!")
    print("Highest score found:", max_val)
}

main()
'''
    },

    # =========================================================================
    # 06_structs (5 exercises)
    # =========================================================================
    {
        "id": "structs01",
        "name": "structs01",
        "topic": "06_structs",
        "title": "Defining and Instantiating Structs",
        "path": "exercises/06_structs/structs01.nyx",
        "solution": "solutions/06_structs/structs01.nyx",
        "mode": "run",
        "description": "Define a struct Point with x and y fields.",
        "hints": [
            "Declare: `struct Point { x: int, y: int }` before `main`."
        ],
        "exercise_code": '''// I AM NOT DONE
// Structs group related fields: `struct Name { field1: type, ... }`
// Instantiate with `Name(val1, val2)`.
// TODO: Define a struct `Point` with fields `x: int` and `y: int`.

// Define struct Point here:

fn main() {
    let p = Point(15, 25)
    print("Point coordinates:", p.x, p.y)
}

main()
''',
        "solution_code": '''struct Point {
    x: int,
    y: int
}

fn main() {
    let p = Point(15, 25)
    print("Point coordinates:", p.x, p.y)
}

main()
'''
    },
    {
        "id": "structs02",
        "name": "structs02",
        "topic": "06_structs",
        "title": "Methods with Inherent impl",
        "path": "exercises/06_structs/structs02.nyx",
        "solution": "solutions/06_structs/structs02.nyx",
        "mode": "run",
        "description": "Add the self parameter to a struct method.",
        "hints": [
            "In Nyx, methods take `self` as their first parameter.",
            "Change `fn area() -> int` to `fn area(self) -> int`."
        ],
        "exercise_code": '''// I AM NOT DONE
// Methods are implemented in an `impl StructName` block.
// The first parameter must be `self`.
// TODO: Add `self` to the `area` method signature.

struct Rectangle {
    width: int,
    height: int
}

impl Rectangle {
    fn area() -> int { // Fix signature to take self!
        return self.width * self.height
    }
}

fn main() {
    let rect = Rectangle(8, 5)
    print("Rectangle area:", rect.area())
}

main()
''',
        "solution_code": '''struct Rectangle {
    width: int,
    height: int
}

impl Rectangle {
    fn area(self) -> int {
        return self.width * self.height
    }
}

fn main() {
    let rect = Rectangle(8, 5)
    print("Rectangle area:", rect.area())
}

main()
'''
    },
    {
        "id": "structs03",
        "name": "structs03",
        "topic": "06_structs",
        "title": "Nested Structs",
        "path": "exercises/06_structs/structs03.nyx",
        "solution": "solutions/06_structs/structs03.nyx",
        "mode": "run",
        "description": "Compose structs containing other structs as fields.",
        "hints": [
            "Access nested field with `player.position.x`."
        ],
        "exercise_code": '''// I AM NOT DONE
// Structs can contain instances of other structs as fields.
// TODO: Access the player's nested X position through `player.position.x`.

struct Position {
    x: int,
    y: int
}

struct Player {
    name: string,
    position: Position
}

fn main() {
    let pos = Position(120, 80)
    let player = Player("Aria", pos)

    let player_x = 0 // Read player.position.x

    assert(player_x == 120, "player_x must equal 120!")
    print("Player position on X:", player_x)
}

main()
''',
        "solution_code": '''struct Position {
    x: int,
    y: int
}

struct Player {
    name: string,
    position: Position
}

fn main() {
    let pos = Position(120, 80)
    let player = Player("Aria", pos)
    let player_x = player.position.x

    assert(player_x == 120, "player_x must equal 120!")
    print("Player position on X:", player_x)
}

main()
'''
    },
    {
        "id": "structs04",
        "name": "structs04",
        "topic": "06_structs",
        "title": "Mutating Struct Fields",
        "path": "exercises/06_structs/structs04.nyx",
        "solution": "solutions/06_structs/structs04.nyx",
        "mode": "run",
        "description": "Mutate internal struct fields using set instance.field = value.",
        "hints": [
            "Use `set hero.health = hero.health - 25` to apply damage."
        ],
        "exercise_code": '''// I AM NOT DONE
// Mutable struct bindings allow field reassignment via `set target.field = val`.
// TODO: Damage `hero` by subtracting 25 from `hero.health`.

struct Hero {
    name: string,
    health: int
}

fn main() {
    var hero = Hero("Kurt", 100)
    // Subtract 25 damage:

    assert(hero.health == 75, "Hero health must be 75 after 25 damage!")
    print("Hero remaining health:", hero.health)
}

main()
''',
        "solution_code": '''struct Hero {
    name: string,
    health: int
}

fn main() {
    var hero = Hero("Kurt", 100)
    set hero.health = hero.health - 25
    assert(hero.health == 75, "Hero health must be 75 after 25 damage!")
    print("Hero remaining health:", hero.health)
}

main()
'''
    },
    {
        "id": "structs05",
        "name": "structs05",
        "topic": "06_structs",
        "title": "Constructor Functions",
        "path": "exercises/06_structs/structs05.nyx",
        "solution": "solutions/06_structs/structs05.nyx",
        "mode": "run",
        "description": "Write a factory function that constructs and validates a struct.",
        "hints": [
            "Return `Rectangle(size, size)` for square dimensions."
        ],
        "exercise_code": '''// I AM NOT DONE
// You can write factory functions to construct initialized structs.
// TODO: Complete `create_square(size: int) -> Rectangle` returning width=size, height=size.

struct Rectangle {
    width: int,
    height: int
}

fn create_square(size: int) -> Rectangle {
    // Return Rectangle with width and height equal to size
}

fn main() {
    let sq = create_square(12)
    assert(sq.width == 12 and sq.height == 12, "Square dimensions must both equal 12")
    print("Square created:", sq.width, "x", sq.height)
}

main()
''',
        "solution_code": '''struct Rectangle {
    width: int,
    height: int
}

fn create_square(size: int) -> Rectangle {
    return Rectangle(size, size)
}

fn main() {
    let sq = create_square(12)
    assert(sq.width == 12 and sq.height == 12, "Square dimensions must both equal 12")
    print("Square created:", sq.width, "x", sq.height)
}

main()
'''
    },

    # =========================================================================
    # 07_enums (3 exercises)
    # =========================================================================
    {
        "id": "enums01",
        "name": "enums01",
        "topic": "07_enums",
        "title": "Enum Declarations",
        "path": "exercises/07_enums/enums01.nyx",
        "solution": "solutions/07_enums/enums01.nyx",
        "mode": "run",
        "description": "Declare an enum and access its member variants.",
        "hints": [
            "Declare `enum Status { Idle, Running, Paused, Stopped }`."
        ],
        "exercise_code": '''// I AM NOT DONE
// Enums declare a set of discrete named variants:
//   enum Color { Red, Green, Blue }
// Access variants via `Color.Red`.
// TODO: Declare an enum `Status` with Idle, Running, and Stopped variants.

// Declare enum Status here:

fn main() {
    let current = Status.Running
    print("Current system status:", current)
}

main()
''',
        "solution_code": '''enum Status {
    Idle,
    Running,
    Stopped
}

fn main() {
    let current = Status.Running
    print("Current system status:", current)
}

main()
'''
    },
    {
        "id": "enums02",
        "name": "enums02",
        "topic": "07_enums",
        "title": "Enum Variant Comparisons",
        "path": "exercises/07_enums/enums02.nyx",
        "solution": "solutions/07_enums/enums02.nyx",
        "mode": "run",
        "description": "Compare enum values using the equality operator ==.",
        "hints": [
            "Compare `hero_dir == Direction.East`."
        ],
        "exercise_code": '''// I AM NOT DONE
// Enum variants can be compared with `==` and `!=`.
// TODO: Verify if `hero_dir` is facing `Direction.East`.

enum Direction {
    North,
    South,
    East,
    West
}

fn main() {
    let hero_dir = Direction.East
    let is_facing_east = false // Compare hero_dir == Direction.East

    assert(is_facing_east == true, "Hero must be facing East!")
    print("Hero facing East:", is_facing_east)
}

main()
''',
        "solution_code": '''enum Direction {
    North,
    South,
    East,
    West
}

fn main() {
    let hero_dir = Direction.East
    let is_facing_east = (hero_dir == Direction.East)

    assert(is_facing_east == true, "Hero must be facing East!")
    print("Hero facing East:", is_facing_east)
}

main()
'''
    },
    {
        "id": "enums03",
        "name": "enums03",
        "topic": "07_enums",
        "title": "State Machines with Enums",
        "path": "exercises/07_enums/enums03.nyx",
        "solution": "solutions/07_enums/enums03.nyx",
        "mode": "run",
        "description": "Model a traffic light state machine transition.",
        "hints": [
            "If current is Red return Green; if Green return Yellow; else return Red."
        ],
        "exercise_code": '''// I AM NOT DONE
// Enums are ideal for state machines.
// TODO: Complete `next_light`: Red -> Green -> Yellow -> Red.

enum Light {
    Red,
    Green,
    Yellow
}

fn next_light(current: Light) -> Light {
    // TODO: Implement the transition sequence: Red -> Green -> Yellow -> Red
    return Light.Red
}

fn main() {
    let l1 = Light.Red
    let l2 = next_light(l1)
    let l3 = next_light(l2)

    assert(l2 == Light.Green, "Red must transition to Green")
    assert(l3 == Light.Yellow, "Green must transition to Yellow")
    print("Traffic light transitions verified!")
}

main()
''',
        "solution_code": '''enum Light {
    Red,
    Green,
    Yellow
}

fn next_light(current: Light) -> Light {
    if current == Light.Red {
        return Light.Green
    } elif current == Light.Green {
        return Light.Yellow
    } else {
        return Light.Red
    }
}

fn main() {
    let l1 = Light.Red
    let l2 = next_light(l1)
    let l3 = next_light(l2)

    assert(l2 == Light.Green, "Red must transition to Green")
    assert(l3 == Light.Yellow, "Green must transition to Yellow")
    print("Traffic light transitions verified!")
}

main()
'''
    },

    # =========================================================================
    # 08_traits (3 exercises)
    # =========================================================================
    {
        "id": "traits01",
        "name": "traits01",
        "topic": "08_traits",
        "title": "Traits and Interfaces",
        "path": "exercises/08_traits/traits01.nyx",
        "solution": "solutions/08_traits/traits01.nyx",
        "mode": "run",
        "description": "Implement a trait method on a struct.",
        "hints": [
            "Implement `fn describe(self) -> string { return \"Player \" + self.name }` inside `impl Describable for Player`."
        ],
        "exercise_code": '''// I AM NOT DONE
// A `trait` defines a contract of method signatures:
//   trait Describable { fn describe(self) -> string }
// An `impl Trait for Struct` must provide every required method.
// TODO: Implement `describe` for `Player`.

trait Describable {
    fn describe(self) -> string
}

struct Player {
    name: string,
    level: int
}

impl Describable for Player {
    // Add describe(self) -> string implementation here!
}

fn main() {
    let p = Player("Hero", 1)
    let desc = p.describe()
    assert(desc == "Player Hero", "describe must return 'Player ' + self.name")
    print(desc)
}

main()
''',
        "solution_code": '''trait Describable {
    fn describe(self) -> string
}

struct Player {
    name: string,
    level: int
}

impl Describable for Player {
    fn describe(self) -> string {
        return "Player " + self.name
    }
}

fn main() {
    let p = Player("Hero", 1)
    let desc = p.describe()
    assert(desc == "Player Hero", "describe must return 'Player ' + self.name")
    print(desc)
}

main()
'''
    },
    {
        "id": "traits02",
        "name": "traits02",
        "topic": "08_traits",
        "title": "Multiple Trait Implementations",
        "path": "exercises/08_traits/traits02.nyx",
        "solution": "solutions/08_traits/traits02.nyx",
        "mode": "run",
        "description": "Implement the same trait across multiple distinct structs.",
        "hints": [
            "Implement `fn area(self) -> int { return self.side * self.side }` for Square."
        ],
        "exercise_code": '''// I AM NOT DONE
// Multiple structs can implement the same trait contract.
// TODO: Implement `Area` for `Square`.

trait Area {
    fn area(self) -> int
}

struct Rect {
    w: int,
    h: int
}

impl Area for Rect {
    fn area(self) -> int {
        return self.w * self.h
    }
}

struct Square {
    side: int
}

// TODO: Implement Area for Square here:

fn main() {
    let r = Rect(4, 5)
    let s = Square(6)

    assert(r.area() == 20, "Rect area must be 20")
    assert(s.area() == 36, "Square area must be 36")
    print("Rect area:", r.area(), "Square area:", s.area())
}

main()
''',
        "solution_code": '''trait Area {
    fn area(self) -> int
}

struct Rect {
    w: int,
    h: int
}

impl Area for Rect {
    fn area(self) -> int {
        return self.w * self.h
    }
}

struct Square {
    side: int
}

impl Area for Square {
    fn area(self) -> int {
        return self.side * self.side
    }
}

fn main() {
    let r = Rect(4, 5)
    let s = Square(6)

    assert(r.area() == 20, "Rect area must be 20")
    assert(s.area() == 36, "Square area must be 36")
    print("Rect area:", r.area(), "Square area:", s.area())
}

main()
'''
    },
    {
        "id": "traits03",
        "name": "traits03",
        "topic": "08_traits",
        "title": "Trait Methods with Parameters",
        "path": "exercises/08_traits/traits03.nyx",
        "solution": "solutions/08_traits/traits03.nyx",
        "mode": "run",
        "description": "Define and implement trait methods that accept arguments.",
        "hints": [
            "Signature: `fn scale(self, factor: int) -> int`."
        ],
        "exercise_code": '''// I AM NOT DONE
// Trait methods can take extra parameters in addition to `self`.
// TODO: Implement `scale(self, factor: int) -> int` for `Score`.

trait Scalable {
    fn scale(self, factor: int) -> int
}

struct Score {
    points: int
}

impl Scalable for Score {
    // Implement scale here! Return self.points * factor
}

fn main() {
    let sc = Score(15)
    let doubled = sc.scale(2)
    assert(doubled == 30, "Scaled score must be 30")
    print("Scaled points:", doubled)
}

main()
''',
        "solution_code": '''trait Scalable {
    fn scale(self, factor: int) -> int
}

struct Score {
    points: int
}

impl Scalable for Score {
    fn scale(self, factor: int) -> int {
        return self.points * factor
    }
}

fn main() {
    let sc = Score(15)
    let doubled = sc.scale(2)
    assert(doubled == 30, "Scaled score must be 30")
    print("Scaled points:", doubled)
}

main()
'''
    },

    # =========================================================================
    # 09_error_handling (3 exercises)
    # =========================================================================
    {
        "id": "errors01",
        "name": "errors01",
        "topic": "09_error_handling",
        "title": "Try, Catch, and Throw",
        "path": "exercises/09_error_handling/errors01.nyx",
        "solution": "solutions/09_error_handling/errors01.nyx",
        "mode": "run",
        "description": "Catch an exception with try / catch.",
        "hints": [
            "Wrap the call `validate_pin(9999)` with `try { ... } catch err { print(\"Caught error!\") }`."
        ],
        "exercise_code": '''// I AM NOT DONE
// Nyx supports structured exceptions with `try`, `catch`, and `throw`.
// TODO: Catch the error thrown by `validate_pin` and print "Caught error!".

fn validate_pin(pin: int) {
    if pin != 1234 {
        throw "Invalid PIN entered"
    }
}

fn main() {
    // Wrap with try / catch:
    validate_pin(9999)
    print("Done")
}

main()
''',
        "solution_code": '''fn validate_pin(pin: int) {
    if pin != 1234 {
        throw "Invalid PIN entered"
    }
}

fn main() {
    try {
        validate_pin(9999)
    } catch err {
        print("Caught error!")
    }
    print("Done")
}

main()
'''
    },
    {
        "id": "errors02",
        "name": "errors02",
        "topic": "09_error_handling",
        "title": "Input Validation Exceptions",
        "path": "exercises/09_error_handling/errors02.nyx",
        "solution": "solutions/09_error_handling/errors02.nyx",
        "mode": "run",
        "description": "Throw an error when an input value fails domain constraints.",
        "hints": [
            "If `port < 1` throw \"Port must be positive\"."
        ],
        "exercise_code": '''// I AM NOT DONE
// Functions can guard against invalid arguments by throwing descriptive errors.
// TODO: If `port < 1`, throw \"Port must be positive\"!

fn check_port(port: int) -> int {
    // Add validation check here!
    return port
}

fn main() {
    var caught = false
    try {
        check_port(0)
    } catch e {
        set caught = true
    }

    assert(caught == true, "check_port(0) must throw an error!")
    assert(check_port(8080) == 8080, "Valid port 8080 should return intact")
    print("Port validation verified successfully!")
}

main()
''',
        "solution_code": '''fn check_port(port: int) -> int {
    if port < 1 {
        throw "Port must be positive"
    }
    return port
}

fn main() {
    var caught = false
    try {
        check_port(0)
    } catch e {
        set caught = true
    }

    assert(caught == true, "check_port(0) must throw an error!")
    assert(check_port(8080) == 8080, "Valid port 8080 should return intact")
    print("Port validation verified successfully!")
}

main()
'''
    },
    {
        "id": "errors03",
        "name": "errors03",
        "topic": "09_error_handling",
        "title": "Recovery with Fallback",
        "path": "exercises/09_error_handling/errors03.nyx",
        "solution": "solutions/09_error_handling/errors03.nyx",
        "mode": "run",
        "description": "Safely recover from an exception and provide a fallback value.",
        "hints": [
            "In catch block: `set result = -1`."
        ],
        "exercise_code": '''// I AM NOT DONE
// Exceptions can be recovered from cleanly by setting a safe fallback.
// TODO: If `risky_divide` fails, catch the error and fallback `result = -1`.

fn risky_divide(a: int, b: int) -> int {
    if b == 0 {
        throw "Division by zero"
    }
    return a / b
}

fn main() {
    var result = 0
    try {
        set result = risky_divide(10, 0)
    } catch err {
        // Fallback to -1 on error:
    }

    assert(result == -1, "Fallback result must be -1 on error!")
    print("Recovered with safe fallback:", result)
}

main()
''',
        "solution_code": '''fn risky_divide(a: int, b: int) -> int {
    if b == 0 {
        throw "Division by zero"
    }
    return a / b
}

fn main() {
    var result = 0
    try {
        set result = risky_divide(10, 0)
    } catch err {
        set result = -1
    }

    assert(result == -1, "Fallback result must be -1 on error!")
    print("Recovered with safe fallback:", result)
}

main()
'''
    },

    # =========================================================================
    # 10_null_safety (4 exercises)
    # =========================================================================
    {
        "id": "null01",
        "name": "null01",
        "topic": "10_null_safety",
        "title": "Nullable Types and Coalescing",
        "path": "exercises/10_null_safety/null01.nyx",
        "solution": "solutions/10_null_safety/null01.nyx",
        "mode": "run",
        "description": "Provide a default value using the null coalescing operator ??.",
        "hints": [
            "Write `let display_name: string = nickname ?? \"Guest\"`."
        ],
        "exercise_code": '''// I AM NOT DONE
// Optional types are written with a trailing `?` (e.g. `string?`, `int?`).
// The null coalescing operator `??` provides a fallback value if the left is null.
// TODO: Use `??` to provide "Guest" when `nickname` is null.

fn main() {
    let nickname: string? = null
    let display_name: string = nickname // Use ?? "Guest"
    assert(display_name == "Guest", "display_name must fallback to 'Guest' when nickname is null!")
    print("Welcome,", display_name)
}

main()
''',
        "solution_code": '''fn main() {
    let nickname: string? = null
    let display_name: string = nickname ?? "Guest"
    assert(display_name == "Guest", "display_name must fallback to 'Guest' when nickname is null!")
    print("Welcome,", display_name)
}

main()
'''
    },
    {
        "id": "null02",
        "name": "null02",
        "topic": "10_null_safety",
        "title": "Nullable Integers",
        "path": "exercises/10_null_safety/null02.nyx",
        "solution": "solutions/10_null_safety/null02.nyx",
        "mode": "run",
        "description": "Handle optional integers int? with fallback defaults.",
        "hints": [
            "Write `let points = extra_score ?? 10`."
        ],
        "exercise_code": '''// I AM NOT DONE
// Scalar numbers can also be optional: `int?`, `float?`.
// TODO: Fallback to `10` when `extra_score` is null using `??`.

fn calculate_total(base: int, extra_score: int?) -> int {
    let points = 0 // Use extra_score ?? 10
    return base + points
}

fn main() {
    let t1 = calculate_total(50, null)
    let t2 = calculate_total(50, 25)

    assert(t1 == 60, "t1 with null extra_score must equal 60")
    assert(t2 == 75, "t2 with 25 extra_score must equal 75")
    print("Calculated scores:", t1, t2)
}

main()
''',
        "solution_code": '''fn calculate_total(base: int, extra_score: int?) -> int {
    let points = extra_score ?? 10
    return base + points
}

fn main() {
    let t1 = calculate_total(50, null)
    let t2 = calculate_total(50, 25)

    assert(t1 == 60, "t1 with null extra_score must equal 60")
    assert(t2 == 75, "t2 with 25 extra_score must equal 75")
    print("Calculated scores:", t1, t2)
}

main()
'''
    },
    {
        "id": "null03",
        "name": "null03",
        "topic": "10_null_safety",
        "title": "Guard Preconditions",
        "path": "exercises/10_null_safety/null03.nyx",
        "solution": "solutions/10_null_safety/null03.nyx",
        "mode": "run",
        "description": "Guard against invalid parameters with early return.",
        "hints": [
            "Add `guard energy > 0 else { return \"blocked\" }` at the top of perform_action."
        ],
        "exercise_code": '''// I AM NOT DONE
// `guard condition else { return }` ensures a condition holds before continuing.
// If the condition is false, the `else` block executes immediately.
// TODO: Add a guard ensuring `energy > 0` else return "blocked"!

fn perform_action(energy: int) -> string {
    // Add guard statement here:
    // guard energy > 0 else {
    //     return "blocked"
    // }

    return "success"
}

fn main() {
    let res1 = perform_action(0)  // Should be blocked by guard!
    let res2 = perform_action(50) // Should succeed
    assert(res1 == "blocked", "0 energy must be blocked by guard!")
    assert(res2 == "success", "50 energy must succeed!")
    print("Guards verified successfully!")
}

main()
''',
        "solution_code": '''fn perform_action(energy: int) -> string {
    guard energy > 0 else {
        return "blocked"
    }

    return "success"
}

fn main() {
    let res1 = perform_action(0)
    let res2 = perform_action(50)
    assert(res1 == "blocked", "0 energy must be blocked by guard!")
    assert(res2 == "success", "50 energy must succeed!")
    print("Guards verified successfully!")
}

main()
'''
    },
    {
        "id": "null04",
        "name": "null04",
        "topic": "10_null_safety",
        "title": "Multi-Condition Guards",
        "path": "exercises/10_null_safety/null04.nyx",
        "solution": "solutions/10_null_safety/null04.nyx",
        "mode": "run",
        "description": "Protect operations with multi-condition guard statements.",
        "hints": [
            "Write `guard age >= 18 and has_license else { return false }`."
        ],
        "exercise_code": '''// I AM NOT DONE
// `guard` conditions can combine multiple checks with `and` / `or`.
// TODO: Require that `age >= 18 and has_license` holds; else return `false`.

fn can_rent_car(age: int, has_license: bool) -> bool {
    // Add guard statement here!

    return true
}

fn main() {
    assert(can_rent_car(16, true) == false, "Underage cannot rent")
    assert(can_rent_car(22, false) == false, "No license cannot rent")
    assert(can_rent_car(25, true) == true, "Adult with license can rent")
    print("Rental permissions verified!")
}

main()
''',
        "solution_code": '''fn can_rent_car(age: int, has_license: bool) -> bool {
    guard age >= 18 and has_license else {
        return false
    }

    return true
}

fn main() {
    assert(can_rent_car(16, true) == false, "Underage cannot rent")
    assert(can_rent_car(22, false) == false, "No license cannot rent")
    assert(can_rent_car(25, true) == true, "Adult with license can rent")
    print("Rental permissions verified!")
}

main()
'''
    },

    # =========================================================================
    # 11_pipelines (2 exercises)
    # =========================================================================
    {
        "id": "pipeline01",
        "name": "pipeline01",
        "topic": "11_pipelines",
        "title": "Pipeline Operator (|&gt;)",
        "path": "exercises/11_pipelines/pipeline01.nyx",
        "solution": "solutions/11_pipelines/pipeline01.nyx",
        "mode": "run",
        "description": "Chain function calls using the pipeline operator.",
        "hints": [
            "Write `let result = initial |> increment |> double_val`."
        ],
        "exercise_code": '''// I AM NOT DONE
// The pipe operator `|>` chains data through functions:
//   `value |> fn1 |> fn2` passes the result of each call to the next.
// TODO: Pipe `initial` through `increment` and then `double_val`.

fn increment(x: int) -> int {
    return x + 1
}

fn double_val(x: int) -> int {
    return x * 2
}

fn main() {
    let initial = 4
    // (4 + 1) * 2 = 10
    let result = initial // Fix using |> increment |> double_val
    assert(result == 10, "Pipelined result of (4 + 1) * 2 must be 10!")
    print("Pipelined result:", result)
}

main()
''',
        "solution_code": '''fn increment(x: int) -> int {
    return x + 1
}

fn double_val(x: int) -> int {
    return x * 2
}

fn main() {
    let initial = 4
    let result = initial |> increment |> double_val
    assert(result == 10, "Pipelined result of (4 + 1) * 2 must be 10!")
    print("Pipelined result:", result)
}

main()
'''
    },
    {
        "id": "pipeline02",
        "name": "pipeline02",
        "topic": "11_pipelines",
        "title": "Data Processing Pipelines",
        "path": "exercises/11_pipelines/pipeline02.nyx",
        "solution": "solutions/11_pipelines/pipeline02.nyx",
        "mode": "run",
        "description": "Process data through a multi-stage math pipeline.",
        "hints": [
            "Chain: `raw_val |> add_tax |> apply_discount`."
        ],
        "exercise_code": '''// I AM NOT DONE
// Pipelines make multi-stage transformations clean and readable.
// TODO: Pipe `raw_val` through `add_tax` and then `apply_discount`.
// 100 + 20 (tax) = 120 -> 120 - 15 (discount) = 105!

fn add_tax(price: int) -> int {
    return price + 20
}

fn apply_discount(price: int) -> int {
    return price - 15
}

fn main() {
    let raw_val = 100
    // Chain with |>:
    let final_price = raw_val

    assert(final_price == 105, "final_price must equal 105!")
    print("Pipelined checkout total:", final_price)
}

main()
''',
        "solution_code": '''fn add_tax(price: int) -> int {
    return price + 20
}

fn apply_discount(price: int) -> int {
    return price - 15
}

fn main() {
    let raw_val = 100
    let final_price = raw_val |> add_tax |> apply_discount

    assert(final_price == 105, "final_price must equal 105!")
    print("Pipelined checkout total:", final_price)
}

main()
'''
    },

    # =========================================================================
    # 12_defer (2 exercises)
    # =========================================================================
    {
        "id": "defer01",
        "name": "defer01",
        "topic": "12_defer",
        "title": "Scope Cleanup with defer",
        "path": "exercises/12_defer/defer01.nyx",
        "solution": "solutions/12_defer/defer01.nyx",
        "mode": "run",
        "description": "Ensure cleanup actions run on scope exit with defer.",
        "hints": [
            "Add `defer release_lock(lock)` inside `do_critical_work()` so the lock is freed on return."
        ],
        "exercise_code": '''// I AM NOT DONE
// `defer expression` schedules an expression to run when the surrounding function exits.
// TODO: Use `defer` so `release_lock(lock)` is guaranteed to run when `do_critical_work` exits.

struct Lock {
    is_locked: bool
}

fn release_lock(lock: Lock) {
    lock.is_locked = false
}

fn do_critical_work(lock: Lock) {
    lock.is_locked = true
    // TODO: Add defer release_lock(lock) here so it is freed when exiting this function!
    print("Performing critical work with lock held...")
}

fn main() {
    let lock = Lock(false)
    do_critical_work(lock)
    assert(lock.is_locked == false, "Lock must be released automatically via defer upon exit!")
    print("Lock safely released:", lock.is_locked == false)
}

main()
''',
        "solution_code": '''struct Lock {
    is_locked: bool
}

fn release_lock(lock: Lock) {
    lock.is_locked = false
}

fn do_critical_work(lock: Lock) {
    lock.is_locked = true
    defer release_lock(lock)
    print("Performing critical work with lock held...")
}

fn main() {
    let lock = Lock(false)
    do_critical_work(lock)
    assert(lock.is_locked == false, "Lock must be released automatically via defer upon exit!")
    print("Lock safely released:", lock.is_locked == false)
}

main()
'''
    },
    {
        "id": "defer02",
        "name": "defer02",
        "topic": "12_defer",
        "title": "Multiple Defer Execution",
        "path": "exercises/12_defer/defer02.nyx",
        "solution": "solutions/12_defer/defer02.nyx",
        "mode": "run",
        "description": "Observe that defer statements execute when exiting their scope.",
        "hints": [
            "Add `defer cleanup_step1(cleaner)` and `defer cleanup_step2(cleaner)` inside `process_batch()`."
        ],
        "exercise_code": '''// I AM NOT DONE
// Multiple defer calls are scheduled and execute cleanly before return.
// TODO: Add defer statements for cleanup_step1 and cleanup_step2 so both flags become true.

struct Cleaner {
    step1: bool,
    step2: bool
}

fn cleanup_step1(cleaner: Cleaner) {
    cleaner.step1 = true
}

fn cleanup_step2(cleaner: Cleaner) {
    cleaner.step2 = true
}

fn process_batch(cleaner: Cleaner) {
    print("Batch processing in progress...")
    // TODO: Add defer cleanup_step1(cleaner) and defer cleanup_step2(cleaner)
}

fn main() {
    let cleaner = Cleaner(false, false)
    process_batch(cleaner)
    assert(cleaner.step1 == true, "Cleanup step 1 must have run via defer!")
    assert(cleaner.step2 == true, "Cleanup step 2 must have run via defer!")
    print("All batch cleanup handlers executed via defer successfully!")
}

main()
''',
        "solution_code": '''struct Cleaner {
    step1: bool,
    step2: bool
}

fn cleanup_step1(cleaner: Cleaner) {
    cleaner.step1 = true
}

fn cleanup_step2(cleaner: Cleaner) {
    cleaner.step2 = true
}

fn process_batch(cleaner: Cleaner) {
    print("Batch processing in progress...")
    defer cleanup_step1(cleaner)
    defer cleanup_step2(cleaner)
}

fn main() {
    let cleaner = Cleaner(false, false)
    process_batch(cleaner)
    assert(cleaner.step1 == true, "Cleanup step 1 must have run via defer!")
    assert(cleaner.step2 == true, "Cleanup step 2 must have run via defer!")
    print("All batch cleanup handlers executed via defer successfully!")
}

main()
'''
    },

    # =========================================================================
    # 13_math_and_logic (2 exercises)
    # =========================================================================
    {
        "id": "math01",
        "name": "math01",
        "topic": "13_math_and_logic",
        "title": "Modulo and Divisibility",
        "path": "exercises/13_math_and_logic/math01.nyx",
        "solution": "solutions/13_math_and_logic/math01.nyx",
        "mode": "run",
        "description": "Check if numbers are even or odd using the modulo operator %.",
        "hints": [
            "A number is even if `n % 2 == 0`."
        ],
        "exercise_code": '''// I AM NOT DONE
// The modulo operator `%` calculates the remainder of integer division.
// TODO: Complete `is_even(n: int) -> bool` using `n % 2`.

fn is_even(n: int) -> bool {
    // Return true if n % 2 == 0
    return false
}

fn main() {
    assert(is_even(42) == true, "42 must be even")
    assert(is_even(17) == false, "17 must be odd")
    print("Even/odd tests passed!")
}

main()
''',
        "solution_code": '''fn is_even(n: int) -> bool {
    return n % 2 == 0
}

fn main() {
    assert(is_even(42) == true, "42 must be even")
    assert(is_even(17) == false, "17 must be odd")
    print("Even/odd tests passed!")
}

main()
'''
    },
    {
        "id": "math02",
        "name": "math02",
        "topic": "13_math_and_logic",
        "title": "Bitwise Operations",
        "path": "exercises/13_math_and_logic/math02.nyx",
        "solution": "solutions/13_math_and_logic/math02.nyx",
        "mode": "run",
        "description": "Perform bitwise AND &, OR |, and left-shift << operations.",
        "hints": [
            "`1 << 4` shifts 1 left by 4 bits (16).",
            "`flags | 1` sets the lowest bit."
        ],
        "exercise_code": '''// I AM NOT DONE
// Nyx supports bitwise operators: `&` (AND), `|` (OR), `^` (XOR), and `<<` (shift).
// TODO:
// 1. Shift 1 left by 4 bits to get 16 (`1 << 4`).
// 2. Bitwise OR `flags` with `1` to set the flag.

fn main() {
    let shifted = 0 // Compute 1 << 4
    let flags = 8
    let updated = 0 // Compute flags | 1

    assert(shifted == 16, "1 << 4 must be 16")
    assert(updated == 9, "8 | 1 must be 9")
    print("Shifted:", shifted, "Updated flags:", updated)
}

main()
''',
        "solution_code": '''fn main() {
    let shifted = 1 << 4
    let flags = 8
    let updated = flags | 1

    assert(shifted == 16, "1 << 4 must be 16")
    assert(updated == 9, "8 | 1 must be 9")
    print("Shifted:", shifted, "Updated flags:", updated)
}

main()
'''
    },

    # =========================================================================
    # 14_testing (2 exercises)
    # =========================================================================
    {
        "id": "tests01",
        "name": "tests01",
        "topic": "14_testing",
        "title": "In-File Unit Testing",
        "path": "exercises/14_testing/tests01.nyx",
        "solution": "solutions/14_testing/tests01.nyx",
        "mode": "test",
        "description": "Fix an assertion error in an in-file unit test.",
        "hints": [
            "The assertion checks `assert(result == 5, ...)`, but `add(2, 2)` equals 4!",
            "Change `5` to `4` in the assertion."
        ],
        "exercise_code": '''// I AM NOT DONE
// Nyx has first-class unit tests using `test "name" { assert(...) }`.
// When run with `nyx test`, all assertions are verified.
// TODO: Fix the broken assertion below so the test passes.

fn add(a: int, b: int) -> int {
    return a + b
}

test "verify addition" {
    var result = add(2, 2)
    assert(result == 5, "2 + 2 must equal 4!")
    print("  [PASS] 2 + 2 == 4")
}
''',
        "solution_code": '''fn add(a: int, b: int) -> int {
    return a + b
}

test "verify addition" {
    var result = add(2, 2)
    assert(result == 4, "2 + 2 must equal 4!")
    print("  [PASS] 2 + 2 == 4")
}
'''
    },
    {
        "id": "tests02",
        "name": "tests02",
        "topic": "14_testing",
        "title": "Multiple In-File Tests",
        "path": "exercises/14_testing/tests02.nyx",
        "solution": "solutions/14_testing/tests02.nyx",
        "mode": "test",
        "description": "Add a second test block to verify subtraction.",
        "hints": [
            "Add a test block: `test \"verify subtraction\" { assert(sub(10, 4) == 6, ...) }`."
        ],
        "exercise_code": '''// I AM NOT DONE
// Multiple test blocks can be declared in a single file.
// TODO: Add a second test block named "subtraction test" that asserts `sub(10, 4) == 6`.

fn sub(a: int, b: int) -> int {
    return a - b
}

test "subtraction test" {
    var res = sub(10, 4)
    assert(res == 0, "10 - 4 must equal 6!")
    print("  [PASS] 10 - 4 == 6")
}
''',
        "solution_code": '''fn sub(a: int, b: int) -> int {
    return a - b
}

test "subtraction test" {
    var res = sub(10, 4)
    assert(res == 6, "10 - 4 must equal 6!")
    print("  [PASS] 10 - 4 == 6")
}
'''
    },

    # =========================================================================
    # 15_quizzes (3 capstone projects)
    # =========================================================================
    {
        "id": "quiz01",
        "name": "quiz01",
        "topic": "15_quizzes",
        "title": "Capstone Quiz: RPG Inventory Score",
        "path": "exercises/15_quizzes/quiz01.nyx",
        "solution": "solutions/15_quizzes/quiz01.nyx",
        "mode": "run",
        "description": "Accumulate total gear score across an array of item structs.",
        "hints": [
            "Loop `for i in 0..2`.",
            "Inside the loop: `let item = items[i]`, then `set total_score = total_score + item.calculate_value()`."
        ],
        "exercise_code": '''// I AM NOT DONE
// CAPSTONE QUIZ 1: RPG Inventory Scorer
// Combine what you learned: Structs, Methods, Loops, Match, and Guard!
//
// Calculate the total gear score of an adventurer's items.
// Rarity multiplier:
//   "Common"    => 1
//   "Rare"      => 2
//   "Legendary" => 5
//   _           => 0
//
// Item score = item.base_power * rarity_multiplier
// Expected total gear score for the given items:
//   Sword (10 * 1 = 10) + Shield (20 * 2 = 40) + Ring (10 * 5 = 50) = 100!

struct Item {
    name: string,
    base_power: int,
    rarity: string
}

impl Item {
    fn calculate_value(self) -> int {
        let mult = match self.rarity {
            "Common" => 1,
            "Rare" => 2,
            "Legendary" => 5,
            _ => 0
        }
        return self.base_power * mult
    }
}

fn main() {
    let items = [
        Item("Iron Sword", 10, "Common"),
        Item("Silver Shield", 20, "Rare"),
        Item("Dragon Ring", 10, "Legendary")
    ]

    var total_score: int = 0
    // TODO: Loop through items 0..2, call item.calculate_value(),
    // and accumulate into `total_score`!

    assert(total_score == 100, "Total gear score must be 100!")
    print("Total Gear Score:", total_score)
}

main()
''',
        "solution_code": '''struct Item {
    name: string,
    base_power: int,
    rarity: string
}

impl Item {
    fn calculate_value(self) -> int {
        let mult = match self.rarity {
            "Common" => 1,
            "Rare" => 2,
            "Legendary" => 5,
            _ => 0
        }
        return self.base_power * mult
    }
}

fn main() {
    let items = [
        Item("Iron Sword", 10, "Common"),
        Item("Silver Shield", 20, "Rare"),
        Item("Dragon Ring", 10, "Legendary")
    ]

    var total_score: int = 0
    for i in 0..2 {
        let item = items[i]
        set total_score = total_score + item.calculate_value()
    }

    assert(total_score == 100, "Total gear score must be 100!")
    print("Total Gear Score:", total_score)
}

main()
'''
    },
    {
        "id": "quiz02",
        "name": "quiz02",
        "topic": "15_quizzes",
        "title": "Capstone Quiz: Banking Ledger System",
        "path": "exercises/15_quizzes/quiz02.nyx",
        "solution": "solutions/15_quizzes/quiz02.nyx",
        "mode": "run",
        "description": "Implement a banking ledger with deposits, withdrawals, and balance guards.",
        "hints": [
            "In `deposit`: guard `amount > 0` else return `self.balance`.",
            "In `withdraw`: guard `amount > 0 and self.balance >= amount` else return `self.balance`."
        ],
        "exercise_code": '''// I AM NOT DONE
// CAPSTONE QUIZ 2: Banking Ledger System
// Model a secure bank account:
// 1. Deposits must only accept positive amounts (> 0).
// 2. Withdrawals must not overdraw the account (amount <= balance).
//
// TODO: Implement `deposit` and `withdraw` with proper `guard` checks!

struct Account {
    owner: string,
    balance: int
}

impl Account {
    fn deposit(self, amount: int) -> int {
        // Add guard ensuring amount > 0 else return self.balance!
        return self.balance
    }

    fn withdraw(self, amount: int) -> int {
        // Add guard ensuring amount > 0 and self.balance >= amount else return self.balance!
        return self.balance
    }
}

fn main() {
    var acc = Account("Kurt", 500)

    // Deposit 200 -> balance becomes 700
    let b1 = acc.deposit(200)
    set acc.balance = b1

    // Invalid withdraw (1000 > 700) -> blocked, stays 700
    let b2 = acc.withdraw(1000)
    set acc.balance = b2

    // Valid withdraw (300) -> balance becomes 400
    let b3 = acc.withdraw(300)
    set acc.balance = b3

    assert(acc.balance == 400, "Final balance after transactions must be 400!")
    print("Account owner:", acc.owner, "Final verified balance:", acc.balance)
}

main()
''',
        "solution_code": '''struct Account {
    owner: string,
    balance: int
}

impl Account {
    fn deposit(self, amount: int) -> int {
        guard amount > 0 else { return self.balance }
        return self.balance + amount
    }

    fn withdraw(self, amount: int) -> int {
        guard amount > 0 else { return self.balance }
        guard self.balance >= amount else { return self.balance }
        return self.balance - amount
    }
}

fn main() {
    var acc = Account("Kurt", 500)

    let b1 = acc.deposit(200)
    set acc.balance = b1

    let b2 = acc.withdraw(1000)
    set acc.balance = b2

    let b3 = acc.withdraw(300)
    set acc.balance = b3

    assert(acc.balance == 400, "Final balance after transactions must be 400!")
    print("Account owner:", acc.owner, "Final verified balance:", acc.balance)
}

main()
'''
    },
    {
        "id": "quiz03",
        "name": "quiz03",
        "topic": "15_quizzes",
        "title": "Capstone Quiz: Character Level-Up System",
        "path": "exercises/15_quizzes/quiz03.nyx",
        "solution": "solutions/15_quizzes/quiz03.nyx",
        "mode": "run",
        "description": "Calculate hero stat boosts and level-ups using pipelines and match.",
        "hints": [
            "Use `self.attack |> add_buff |> double_buff` inside `boosted_attack`.",
            "Match on `self.level`: 10 => \"Champion\", 5 => \"Knight\", _ => \"Novice\"."
        ],
        "exercise_code": '''// I AM NOT DONE
// CAPSTONE QUIZ 3: Character Level-Up System
// Combine Pipelines, Structs, Methods, and Pattern Matching!
//
// TODO:
// 1. Implement `boosted_attack` by piping `self.attack` through `add_buff` (+10) then `double_buff` (*2).
//    For attack = 20: (20 + 10) * 2 = 60!
// 2. Return title based on level: 10 => "Champion", 5 => "Knight", _ => "Novice".

fn add_buff(val: int) -> int {
    return val + 10
}

fn double_buff(val: int) -> int {
    return val * 2
}

struct Hero {
    name: string,
    level: int,
    attack: int
}

impl Hero {
    fn boosted_attack(self) -> int {
        // Pipe self.attack through add_buff and double_buff:
        return self.attack
    }

    fn title(self) -> string {
        return match self.level {
            10 => "Champion",
            5 => "Knight",
            _ => "Novice"
        }
    }
}

fn main() {
    let hero = Hero("Kurt", 10, 20)

    let final_atk = hero.boosted_attack()
    let rank = hero.title()

    assert(final_atk == 60, "Boosted attack must be (20 + 10) * 2 = 60!")
    assert(rank == "Champion", "Level 10 hero must have rank 'Champion'!")
    print("Hero:", hero.name, "Rank:", rank, "Attack:", final_atk)
}

main()
''',
        "solution_code": '''fn add_buff(val: int) -> int {
    return val + 10
}

fn double_buff(val: int) -> int {
    return val * 2
}

struct Hero {
    name: string,
    level: int,
    attack: int
}

impl Hero {
    fn boosted_attack(self) -> int {
        return self.attack |> add_buff |> double_buff
    }

    fn title(self) -> string {
        return match self.level {
            10 => "Champion",
            5 => "Knight",
            _ => "Novice"
        }
    }
}

fn main() {
    let hero = Hero("Kurt", 10, 20)

    let final_atk = hero.boosted_attack()
    let rank = hero.title()

    assert(final_atk == 60, "Boosted attack must be (20 + 10) * 2 = 60!")
    assert(rank == "Champion", "Level 10 hero must have rank 'Champion'!")
    print("Hero:", hero.name, "Rank:", rank, "Attack:", final_atk)
}

main()
'''
    }
]


def build():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Write exercises and solutions
    manifest = []
    for ex in EXERCISES_DATA:
        ex_path = os.path.join(base_dir, ex["path"])
        sol_path = os.path.join(base_dir, ex["solution"])

        os.makedirs(os.path.dirname(ex_path), exist_ok=True)
        os.makedirs(os.path.dirname(sol_path), exist_ok=True)

        with open(ex_path, "w", encoding="utf-8") as f:
            f.write(ex["exercise_code"])

        with open(sol_path, "w", encoding="utf-8") as f:
            f.write(ex["solution_code"])

        manifest.append({
            "id": ex["id"],
            "name": ex["name"],
            "topic": ex["topic"],
            "title": ex["title"],
            "path": ex["path"],
            "solution": ex["solution"],
            "mode": ex["mode"],
            "description": ex["description"],
            "hints": ex["hints"]
        })

    # Write exercises.json
    manifest_path = os.path.join(base_dir, "exercises.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"[OK] Generated {len(manifest)} exercises, solutions, and exercises.json")


if __name__ == "__main__":
    build()
