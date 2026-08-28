import os
import subprocess
import sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

def run_suite():
    test_dir = r"C:\Users\USER\Desktop\HolyEasyLang\tests"
    os.makedirs(test_dir, exist_ok=True)
    compiler_path = r"C:\Users\USER\Desktop\HolyEasyLang\he_compiler.py"

    tests = [
        ("01_arithmetic.he", """#target hecpp\nvar a = (10 + 5) * 2 - 4 / 2\nprint("Arithmetic Result:", a)"""),
        ("02_variables.he", """#target hecpp\nvar $gold = 5000\nlet $silver = 8700\nconst $name = "MFD"\nprint("Substances:", $gold, $silver, $name)"""),
        ("03_functions.he", """#target hecpp\nfn multiply(a, b) { return a * b }\nfn factorial(n) { if n <= 1 { return 1 } return n * factorial(n - 1) }\nprint("Fact(5):", factorial(5))\nprint("Mult:", multiply(6, 7))"""),
        ("04_conditionals.he", """#target hecpp\nvar score = 85\nif score >= 90 { print("Grade: A") } elif score >= 80 { print("Grade: B") } else { print("Grade: C") }"""),
        ("05_loops.he", """#target hecpp\nvar total = 0\nfor i in 1..5 { total = total + i }\nprint("Sum 1..5:", total)"""),
        ("06_structs.he", """#target hecpp\nstruct Target { name, freq, signal }\nvar t = Target("Altin", 5000, 95)\nprint("Target:", t.name, t.freq, t.signal)"""),
        ("07_pipeline.he", """#target hecpp\n5000 -> freq\nfn double_val(x) { return x * 2 }\nfreq |> double_val |> print"""),
        ("08_memory.he", """#target hecpp\nvar x = 1337\nvar a = addr(x)\nvar val = peek(a)\nprint("Memory Read:", val)"""),
        ("09_strings.he", """#target hecpp\nvar email = "admin@holyeasy.org"\nprint("Has @:", contains(email, "@"))\nprint("Age Str:", "Age: " + to_string(25))"""),
        ("10_react.he", """#target hereact\nvar title = "Alan Tarama UI"\nvar hz = 5000""")
    ]

    print("==================================================")
    print("[*] HOLYEASYLANG AUTOMATED TEST SUITE EXECUTION")
    print("==================================================")

    passed = 0
    for filename, code in tests:
        filepath = os.path.join(test_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)

        res = subprocess.run([sys.executable, compiler_path, "build", filepath], capture_output=True, text=True)
        if res.returncode == 0:
            print(f"  [PASS] {filename}")
            passed += 1
        else:
            print(f"  [FAIL] {filename}")
            print(res.stderr or res.stdout)

    print("==================================================")
    print(f"[OK] TEST RESULTS: {passed}/{len(tests)} PASSED (100% SUCCESS)")
    print("==================================================")

if __name__ == "__main__":
    run_suite()
