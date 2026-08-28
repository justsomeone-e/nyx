# -*- coding: utf-8 -*-
import os
import sys
import tempfile
import shutil

_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

from src.core.module_loader import ModuleLoader
from src.core.type_checker import TypeChecker
from src.codegen.codegen import UniversalCodeGen
from src.codegen.cpp_toolchain import CppToolchain

def run_hardware_suite() -> bool:
    print("=" * 70)
    print("NYX PHASE 3.6 HARDWARE & OS BINDINGS HARNESS")
    print("=" * 70)
    sys.stdout.flush()

    compiler = CppToolchain.find_compiler()
    if not compiler:
        print("[!] Native C++ compiler not found. Skipping Hardware execution suite.")
        return True

    tests = [
        (
            "hw_01_gpio_advanced",
            """#target hecpp
import "native/gpio"

set_mode(4, GPIO_PULLUP)
analog_write(5, 128)
pwm_write(6, 255)
var v = analog_read(7)
print("Analog read val:", v)
""",
            "Analog read val: 512"
        ),
        (
            "hw_02_serial_port",
            """#target hecpp
import "native/serial"

var h = serial_open("COM3", SERIAL_BAUD_115200)
serial_write(h, "AT+PING")
var resp = serial_read(h, 2)
print("Serial Response:", resp)
serial_close(h)
""",
            "Serial Response: OK"
        ),
        (
            "hw_03_spi_bus",
            """#target hecpp
import "native/spi"

var h = spi_open(0, 0)
var out_d = spi_transfer(h, 170)
print("SPI Transfer Complete:", out_d > 0)
spi_close(h)
""",
            "SPI Transfer Complete: true"
        )
    ]

    passed = 0
    total = len(tests)

    for name, source, expected in tests:
        print(f"[*] Testing {name}...")
        sys.stdout.flush()
        try:
            loader = ModuleLoader(base_dir=os.path.join(_root_dir, "tests"))
            ast = loader.load_program("<memory>", source)
            TypeChecker(ast, f"{name}.nyx", source).check()

            codegen = UniversalCodeGen(ast)
            cpp_code = codegen.gen_cpp()
            link_libs = codegen.get_link_libraries()

            temp_dir = tempfile.mkdtemp(prefix="nyx_hw_test_")
            try:
                cpp_file = os.path.join(temp_dir, f"{name}.cpp")
                exe_file = os.path.join(temp_dir, f"{name}.exe")
                with open(cpp_file, "w", encoding="utf-8") as f:
                    f.write(cpp_code)

                ok, msg = CppToolchain.compile_cpp(cpp_file, exe_file, link_libs)
                if not ok:
                    print(f"  [FAIL] Compilation Error: {msg}")
                    sys.stdout.flush()
                    continue

                code, output = CppToolchain.run_executable(exe_file)
                output = output.strip().replace("\r\n", "\n")
                if expected in output:
                    print(f"  [PASS] {name} -> Output matched")
                    passed += 1
                else:
                    print(f"  [FAIL] {name} -> Expected:\n{expected}\nGot:\n{output}")
                sys.stdout.flush()
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"  [FAIL] {name} -> Exception: {e}")
            sys.stdout.flush()

    print("=" * 70)
    print(f"[OK] Hardware & OS Bindings Suite: {passed}/{total} Passed")
    print("=" * 70)
    sys.stdout.flush()
    return passed == total

if __name__ == "__main__":
    success = run_hardware_suite()
    sys.exit(0 if success else 1)