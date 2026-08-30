# -*- coding: utf-8 -*-
"""Embedded language, board-profile, firmware, vector, and flash contracts.

This suite deliberately does not emulate GPIO/SPI/I2C on the desktop. It
proves that Nyx emits and links real Cortex-M firmware, while physical signal
verification remains a hardware-in-the-loop release gate.
"""

from __future__ import annotations

import os
import shutil
import struct
import subprocess
import sys
import tempfile
import tomllib


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.core.backend_capabilities import get_stdlib_contract
from src.core.board_model import (
    BOARD_REGISTRY,
    BoardProfileError,
    resolve_board,
    write_board_template,
)
from src.core.diagnostics import DiagnosticEmitter, DiagnosticError
from src.core.embedded_builder import EmbeddedBuilder
from src.core.firmware_flasher import FirmwareFlasher
from src.core.module_loader import ModuleLoader
from src.core.stm32cube_provider import find_cube_package, materialize_cube_board
from src.core.target_model import resolve_target
from src.core.type_checker import TypeChecker


CLI_PATH = os.path.join(ROOT_DIR, "src", "cli.py")
FIXTURE = os.path.join(ROOT_DIR, "tests", "fixtures", "embedded_peripherals.nyx")
F410_FIXTURE = os.path.join(ROOT_DIR, "tests", "fixtures", "embedded_f410_peripherals.nyx")
STANDALONE_F4 = (
    "nucleo-f401re",
    "nucleo-f410rb",
    "nucleo-f411re",
    "nucleo-f446re",
)
PHYSICAL_MODULES = (
    "board", "gpio", "serial", "mmio", "spi", "i2c", "adc", "pwm", "timer", "interrupt",
)


def _elf32_sections(path: str):
    with open(path, "rb") as handle:
        data = handle.read()
    assert data[:4] == b"\x7fELF" and data[4] == 1 and data[5] == 1, "expected ELF32 little-endian"
    section_offset = struct.unpack_from("<I", data, 0x20)[0]
    entry_size = struct.unpack_from("<H", data, 0x2E)[0]
    section_count = struct.unpack_from("<H", data, 0x30)[0]
    names_index = struct.unpack_from("<H", data, 0x32)[0]
    headers = [
        struct.unpack_from("<10I", data, section_offset + index * entry_size)
        for index in range(section_count)
    ]
    names_header = headers[names_index]
    names = data[names_header[4]:names_header[4] + names_header[5]]

    def c_string(table: bytes, offset: int) -> str:
        end = table.find(b"\0", offset)
        return table[offset:end].decode("ascii")

    sections = {}
    for index, header in enumerate(headers):
        name = c_string(names, header[0]) if header[0] < len(names) else ""
        sections[name] = {"index": index, "header": header, "data": data[header[4]:header[4] + header[5]]}
    return data, headers, sections, c_string


def _elf32_symbol_and_vector(path: str, symbol_name: str, irq_number: int):
    data, headers, sections, c_string = _elf32_sections(path)
    symbol_section = sections[".symtab"]
    symbol_header = symbol_section["header"]
    string_header = headers[symbol_header[6]]
    strings = data[string_header[4]:string_header[4] + string_header[5]]
    entry_size = symbol_header[9] or 16
    symbol_value = None
    for offset in range(0, len(symbol_section["data"]), entry_size):
        name_offset, value = struct.unpack_from("<II", symbol_section["data"], offset)
        if name_offset < len(strings) and c_string(strings, name_offset) == symbol_name:
            symbol_value = value
            break
    assert symbol_value is not None, f"missing ELF symbol {symbol_name}"
    vector = sections[".isr_vector"]["data"]
    vector_offset = (16 + irq_number) * 4
    assert len(vector) >= vector_offset + 4, "interrupt vector table is too short"
    vector_value = struct.unpack_from("<I", vector, vector_offset)[0]
    return symbol_value, vector_value


def _check_desktop_rejection():
    source = '#target hecpp\nimport "std/spi"\nfn main() {}\n'
    with DiagnosticEmitter.scoped(exit_on_error=False, emit_output=False):
        try:
            ModuleLoader(base_dir=ROOT_DIR).load_program("<memory>", source)
        except DiagnosticError as error:
            assert error.code == "E1400"
        else:
            raise AssertionError("desktop target accepted a physical SPI HAL module")


def _check_board_rejection():
    source = '#target stm32f4\nimport "std/pwm"\nfn main() {}\n'
    board = resolve_board("f410rb")
    with DiagnosticEmitter.scoped(exit_on_error=False, emit_output=False):
        try:
            ModuleLoader(base_dir=ROOT_DIR, board=board).load_program("<memory>", source)
        except DiagnosticError as error:
            assert error.code == "E1403"
        else:
            raise AssertionError("F410 accepted the unsupported TIM2-backed PWM module")


def _expect_diagnostic(source: str, code: str):
    with DiagnosticEmitter.scoped(exit_on_error=False, emit_output=False):
        try:
            ast = ModuleLoader(base_dir=ROOT_DIR).load_program("<memory>", source)
            TypeChecker(ast, "<memory>", source).check()
        except DiagnosticError as error:
            assert error.code == code, f"expected {code}, got {error.code}"
        else:
            raise AssertionError(f"source unexpectedly passed; expected {code}: {source}")


def _check_buffer_contract():
    valid = (
        '#target stm32f4\n'
        'fn main() {\n'
        '    var packet: Buffer<u8, 4> = [1, 2]\n'
        '    set packet[1] = 9\n'
        '    var pointer = buffer_ptr(packet)\n'
        '    var capacity = len(packet)\n'
        '}\n'
    )
    ast = ModuleLoader(base_dir=ROOT_DIR).load_program("<memory>", valid)
    TypeChecker(ast, "<memory>", valid).check()
    _expect_diagnostic('fn main() { var b: Buffer<u8, 4> = [] }\n', "E2020")
    _expect_diagnostic('fn main() { var value = 1; var p = buffer_ptr(value) }\n', "E2020")
    _expect_diagnostic('#target stm32f4\nfn main() { var b: Buffer<u8, 0> = [] }\n', "E2026")
    _expect_diagnostic('#target stm32f4\nfn main() { var b: Buffer<u8, 2> = [1, 2, 3] }\n', "E2026")
    _expect_diagnostic('#target stm32f4\nfn main() { var b: Buffer<u8, 2> = [256] }\n', "E2024")
    _expect_diagnostic('#target stm32f4\nfn main() { var b: Buffer<u8, 2> = []; var x = b[2] }\n', "E2027")
    _expect_diagnostic('#target stm32f4\nfn main() { var values: Array<int> = [1] }\n', "E2028")
    _expect_diagnostic('#target stm32f4\nfn consume(values: Array<int>) {}\n', "E2028")
    _expect_diagnostic('#target stm32f4\nfn produce() -> Array<int> { return [1] }\n', "E2028")
    _expect_diagnostic('#target stm32f4\nstruct Packet { values: Array<u8> }\nfn main() {}\n', "E2028")
    _expect_diagnostic('#target stm32f4\nextern "C" fn send(values: Array<u8>) -> void\nfn main() {}\n', "E2028")
    _expect_diagnostic('#target stm32f4\nfn main() { var values = args() }\n', "E2028")
    _expect_diagnostic('#target stm32f4\nfn take() { print([1, 2]) }\n', "E2028")


def _check_board_template(temp_dir: str):
    template = os.path.join(temp_dir, "board.toml")
    write_board_template(template)
    with open(template, "rb") as handle:
        parsed = tomllib.load(handle)
    assert parsed["board"]["name"] == "my-nucleo-shield"
    assert parsed["pins"]["RELAY"] == 22
    assert parsed["interrupts"]["TIM2_IRQHandler"] == 28
    try:
        write_board_template(template)
    except BoardProfileError:
        pass
    else:
        raise AssertionError("board template overwrote an existing profile")


def _check_cube_provider_and_mixed_build(temp_dir: str):
    cube_root = os.path.join(temp_dir, "STM32CubeF1")
    cmsis_core = os.path.join(cube_root, "Drivers", "CMSIS", "Include")
    device_root = os.path.join(cube_root, "Drivers", "CMSIS", "Device", "ST", "STM32F1xx")
    device_include = os.path.join(device_root, "Include")
    template_dir = os.path.join(device_root, "Source", "Templates")
    startup_dir = os.path.join(template_dir, "gcc")
    linker_dir = os.path.join(
        cube_root, "Projects", "NUCLEO-F103RB", "Templates", "STM32CubeIDE",
    )
    for directory in (cmsis_core, device_include, startup_dir, linker_dir):
        os.makedirs(directory, exist_ok=True)

    files = {
        os.path.join(cmsis_core, "core_cm3.h"): "#pragma once\n",
        os.path.join(device_include, "stm32f1xx.h"): (
            "#pragma once\n"
            "#if !defined(STM32F103xB)\n"
            "#error wrong CMSIS device selector\n"
            "#endif\n"
            "#include \"stm32f103xb.h\"\n"
        ),
        os.path.join(device_include, "stm32f103xb.h"): (
            "#pragma once\n"
            "typedef enum IRQn { TIM2_IRQn = 28, USART1_IRQn = 37 } IRQn_Type;\n"
        ),
        os.path.join(template_dir, "system_stm32f1xx.c"): (
            "#include \"stm32f1xx.h\"\n"
            "void SystemInit(void) {}\n"
        ),
        os.path.join(startup_dir, "startup_stm32f103xb.s"): (
            ".syntax unified\n.cpu cortex-m3\n.thumb\n"
            ".extern _estack\n.extern SystemInit\n.extern main\n"
            ".section .isr_vector,\"a\",%progbits\n"
            ".global g_pfnVectors\ng_pfnVectors:\n.word _estack\n.word Reset_Handler\n"
            ".section .text.Reset_Handler,\"ax\",%progbits\n"
            ".global Reset_Handler\n.type Reset_Handler,%function\n.thumb_func\n"
            "Reset_Handler:\nbl SystemInit\nbl main\n1: b 1b\n"
        ),
        os.path.join(linker_dir, "STM32F103RBTX_FLASH.ld"): (
            "ENTRY(Reset_Handler)\n"
            "MEMORY { FLASH (rx) : ORIGIN = 0x08000000, LENGTH = 128K\n"
            "RAM (rwx) : ORIGIN = 0x20000000, LENGTH = 20K }\n"
            "_estack = ORIGIN(RAM) + LENGTH(RAM);\n"
            "SECTIONS {\n"
            ".isr_vector : { KEEP(*(.isr_vector)) } > FLASH\n"
            ".text : { *(.text*) *(.rodata*) } > FLASH\n"
            ".ARM.exidx : { *(.ARM.exidx*) } > FLASH\n"
            ".data : { *(.data*) } > RAM AT> FLASH\n"
            ".bss : { *(.bss*) *(COMMON) } > RAM\n"
            "}\n"
        ),
    }
    for path, content in files.items():
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)

    assert find_cube_package("F1", cube_root) == os.path.abspath(cube_root)
    profile = materialize_cube_board(BOARD_REGISTRY["nucleo-f103rb"], cube_root)
    assert profile.is_build_ready and profile.startup_owns_vectors
    assert profile.defines == ("STM32F103xB",)
    assert profile.interrupt_vectors["TIM2_IRQHandler"] == 28
    assert profile.source_files == (os.path.join(template_dir, "system_stm32f1xx.c"),)

    source = os.path.join(temp_dir, "cube_probe.cpp")
    with open(source, "w", encoding="utf-8", newline="\n") as handle:
        handle.write('extern "C" int main() { return 0; }\n')
    builder = EmbeddedBuilder(resolve_target("stm32f1"), temp_dir, profile)
    if not builder.find_cross_tools().get("cxx"):
        print("[SKIP] mixed CMSIS compile graph runtime check; Cortex-M compiler unavailable")
        return
    result = builder.build_firmware(source, "cube_probe")
    assert result["success"], result.get("error")
    assert os.path.isfile(result["elf"])
    assert any(command[0] == builder.find_cross_tools()["cc"] for command in result["commands"][:-1])
    assert any("startup_stm32f103xb.s" in argument for command in result["commands"] for argument in command)

    nyx_source = os.path.join(temp_dir, "cube_probe.nyx")
    with open(nyx_source, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("fn main() {}\n")
    cli_result = subprocess.run(
        [
            sys.executable, CLI_PATH, "build", nyx_source,
            "--board", "nucleo-f103rb", "--cube-root", cube_root,
        ],
        cwd=temp_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert cli_result.returncode == 0, cli_result.stdout + cli_result.stderr
    assert os.path.isfile(os.path.join(temp_dir, "build", "nucleo-f103rb", "cube_probe.elf"))


def _check_flasher_contract(temp_dir: str):
    firmware = os.path.join(temp_dir, "firmware.bin")
    with open(firmware, "wb") as handle:
        handle.write(b"NYX")
    board = resolve_board("f401re")
    flasher = FirmwareFlasher(board)
    cube = flasher.build_command(
        firmware,
        probe="cube",
        serial_number="STLINK123",
        connect_under_reset=True,
        tool_override="STM32_Programmer_CLI",
    )
    assert cube[:7] == [
        "STM32_Programmer_CLI", "-c", "port=SWD", "sn=STLINK123", "mode=UR", "reset=HWrst", "-w",
    ]
    assert f"0x{board.flash_origin:08X}" in cube
    openocd = flasher.build_command(firmware, probe="openocd", tool_override="openocd")
    assert "interface/stlink.cfg" in openocd
    assert f"target/{board.openocd_target}.cfg" in openocd
    assert any("verify reset exit" in argument for argument in openocd)


def _build_firmware_matrix(temp_dir: str):
    target = resolve_target("stm32f4")
    probe_builder = EmbeddedBuilder(target, temp_dir, resolve_board("f401re"))
    if not probe_builder.find_cross_tools().get("cxx"):
        print("[SKIP] Cortex-M compiler unavailable; static embedded contracts passed")
        return None

    built_elfs = {}
    for board_name in STANDALONE_F4:
        fixture = F410_FIXTURE if board_name == "nucleo-f410rb" else FIXTURE
        base_name = os.path.splitext(os.path.basename(fixture))[0]
        result = subprocess.run(
            [sys.executable, CLI_PATH, "build", fixture, "--board", board_name],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        output = result.stdout + result.stderr
        assert result.returncode == 0, f"{board_name} firmware build failed:\n{output}"
        artifact_dir = os.path.join(temp_dir, "build", board_name)
        artifacts = {
            extension: os.path.join(artifact_dir, f"{base_name}.{extension}")
            for extension in ("elf", "hex", "bin")
        }
        assert all(os.path.isfile(path) and os.path.getsize(path) > 0 for path in artifacts.values())
        generated_cpp = os.path.join(artifact_dir, f"{base_name}.cpp")
        with open(generated_cpp, "r", encoding="utf-8") as handle:
            cpp_source = handle.read()
        assert "NyxBuffer<uint8_t, 4>" in cpp_source
        assert "#include <vector>" not in cpp_source and "std::vector" not in cpp_source
        vectors = os.path.join(artifact_dir, f"{board_name}_vectors.cpp")
        with open(vectors, "r", encoding="utf-8") as handle:
            vector_source = handle.read()
        expected_handler = "TIM5_IRQHandler" if board_name == "nucleo-f410rb" else "TIM3_IRQHandler"
        assert expected_handler in vector_source
        built_elfs[board_name] = artifacts["elf"]
        print(f"[PASS] {board_name}: ELF + HEX + BIN")
    return built_elfs


def run_hardware_suite() -> bool:
    print("=" * 70)
    print("NYX EMBEDDED LANGUAGE, NUCLEO BSP & FIRMWARE CONTRACTS")
    print("=" * 70)
    try:
        with open(FIXTURE, "r", encoding="utf-8") as handle:
            source = handle.read()
        ast = ModuleLoader(
            base_dir=os.path.dirname(FIXTURE),
            board=resolve_board("f401re"),
        ).load_program(FIXTURE, source)
        TypeChecker(ast, FIXTURE, source).check()
        print("[PASS] volatile + interrupt fn + critical + fixed-width syntax")

        for module in PHYSICAL_MODULES:
            contract = get_stdlib_contract(module)
            assert contract and "stm32f4" in contract.targets and "hecpp" not in contract.targets
        _check_desktop_rejection()
        _check_board_rejection()
        _check_buffer_contract()
        print("[PASS] physical HAL modules reject fake desktop execution")
        print("[PASS] Buffer<T, N> const capacity, initialization, indexing, and target gates")

        for board_name in STANDALONE_F4:
            board = resolve_board(board_name)
            assert board and board.is_build_ready and board.support == "standalone"
            assert {"board", "gpio", "serial", "spi", "i2c", "adc", "timer", "interrupt"} <= set(board.peripherals)
        assert "pwm" not in resolve_board("f410rb").peripherals
        for board_name in ("f401re", "f411re", "f446re"):
            assert "pwm" in resolve_board(board_name).peripherals
        assert resolve_board("f401re").pins["D14"] == resolve_board("f401re").pins["I2C_SDA"] == 25
        assert resolve_board("f401re").pins["D15"] == resolve_board("f401re").pins["I2C_SCL"] == 24
        assert "TIM3_IRQHandler" not in resolve_board("f410rb").interrupt_vectors
        assert resolve_board("f410rb").interrupt_vectors["TIM5_IRQHandler"] == 50
        assert resolve_board("f401re").name == "nucleo-f401re"
        assert resolve_board("nucleo-f103rb") and not resolve_board("nucleo-f103rb").is_build_ready
        assert len(BOARD_REGISTRY) >= 20
        print(f"[PASS] board registry: {len(BOARD_REGISTRY)} Nucleo profiles, honest BSP readiness")

        with tempfile.TemporaryDirectory(prefix="nyx_embedded_suite_") as temp_dir:
            _check_board_template(temp_dir)
            _check_cube_provider_and_mixed_build(temp_dir)
            print("[PASS] STM32Cube provider resolves CMSIS C/ASM/linker assets and mixed compile graph")
            _check_flasher_contract(temp_dir)
            built_elfs = _build_firmware_matrix(temp_dir)
            if built_elfs:
                symbol, vector = _elf32_symbol_and_vector(
                    built_elfs["nucleo-f401re"], "TIM3_IRQHandler", 29,
                )
                assert vector == (symbol | 1), (
                    f"TIM3 vector 0x{vector:08x} does not point to Thumb handler 0x{symbol:08x}"
                )
                print("[PASS] ELF vector[16 + IRQ29] points to TIM3_IRQHandler with Thumb bit")
                symbol, vector = _elf32_symbol_and_vector(
                    built_elfs["nucleo-f410rb"], "TIM5_IRQHandler", 50,
                )
                assert vector == (symbol | 1), (
                    f"TIM5 vector 0x{vector:08x} does not point to Thumb handler 0x{symbol:08x}"
                )
                print("[PASS] F410 ELF vector[16 + IRQ50] points to TIM5_IRQHandler")
        print("[PASS] CubeProgrammer/OpenOCD commands are explicit dry-run contracts")
        print("=" * 70)
        print("[OK] Embedded suite passed (physical board execution not claimed)")
        print("=" * 70)
        return True
    except Exception as error:
        print(f"[FAIL] {type(error).__name__}: {error}")
        return False


if __name__ == "__main__":
    sys.exit(0 if run_hardware_suite() else 1)
