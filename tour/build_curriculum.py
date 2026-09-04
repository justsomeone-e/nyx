# -*- coding: utf-8 -*-
"""
Curriculum Builder for Tour of Nyx
Generates all 33 progressive exercises, reference solutions, and exercises.json.
"""

import os
import json

EXERCISES_DATA = [
    # 00_intro
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

    # 01_variables
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
// TODO: Add the missing keyword to declare `x`.

fn main() {
    x = 42
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
        "title": "Destructuring Declarations",
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

    # 02_types
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

    # 03_functions
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

    # 04_control_flow
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

    # 05_arrays
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

    # 06_structs
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

    # 07_traits
    {
        "id": "traits01",
        "name": "traits01",
        "topic": "07_traits",
        "title": "Traits and Interfaces",
        "path": "exercises/07_traits/traits01.nyx",
        "solution": "solutions/07_traits/traits01.nyx",
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

    # 08_error_handling
    {
        "id": "errors01",
        "name": "errors01",
        "topic": "08_error_handling",
        "title": "Try, Catch, and Throw",
        "path": "exercises/08_error_handling/errors01.nyx",
        "solution": "solutions/08_error_handling/errors01.nyx",
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

    # 09_null_safety
    {
        "id": "null01",
        "name": "null01",
        "topic": "09_null_safety",
        "title": "Nullable Types and Coalescing",
        "path": "exercises/09_null_safety/null01.nyx",
        "solution": "solutions/09_null_safety/null01.nyx",
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
    print("Welcome,", display_name)
}

main()
''',
        "solution_code": '''fn main() {
    let nickname: string? = null
    let display_name: string = nickname ?? "Guest"
    print("Welcome,", display_name)
}

main()
'''
    },
    {
        "id": "null02",
        "name": "null02",
        "topic": "09_null_safety",
        "title": "Guard Preconditions",
        "path": "exercises/09_null_safety/null02.nyx",
        "solution": "solutions/09_null_safety/null02.nyx",
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

    # 10_pipelines
    {
        "id": "pipeline01",
        "name": "pipeline01",
        "topic": "10_pipelines",
        "title": "Pipeline Operator (|&gt;)",
        "path": "exercises/10_pipelines/pipeline01.nyx",
        "solution": "solutions/10_pipelines/pipeline01.nyx",
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

    # 11_testing
    {
        "id": "tests01",
        "name": "tests01",
        "topic": "11_testing",
        "title": "In-File Unit Testing",
        "path": "exercises/11_testing/tests01.nyx",
        "solution": "solutions/11_testing/tests01.nyx",
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

    # 12_quizzes
    {
        "id": "quiz01",
        "name": "quiz01",
        "topic": "12_quizzes",
        "title": "Capstone Quiz: RPG Inventory Score",
        "path": "exercises/12_quizzes/quiz01.nyx",
        "solution": "solutions/12_quizzes/quiz01.nyx",
        "mode": "run",
        "description": "Accumulate total gear score across an array of item structs.",
        "hints": [
            "Loop `for i in 0..2`.",
            "Inside the loop: `let item = items[i]`, then `set total_score = total_score + item.calculate_value()`."
        ],
        "exercise_code": '''// I AM NOT DONE
// CAPSTONE QUIZ: RPG Inventory Scorer
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
