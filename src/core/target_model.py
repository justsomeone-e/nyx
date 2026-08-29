"""
nyx Embedded Target Model & Hardware Abstraction Layer (HAL)
Provides architecture definitions, target triples, toolchain drivers,
and platform abstraction configurations.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

@dataclass
class TargetSpec:
    name: str
    arch: str
    cpu: str
    pointer_width: int
    endianness: str
    toolchain: str
    c_compiler: str
    cxx_compiler: str
    objcopy: str
    size_tool: str
    default_cflags: List[str]
    default_ldflags: List[str]
    is_freestanding: bool = True
    output_formats: List[str] = field(default_factory=lambda: ["elf", "hex", "bin"])
    description: str = ""

TARGET_REGISTRY: Dict[str, TargetSpec] = {
    # 1. ARM Cortex-M4 (STM32F4 / NUCLEO-F401 / Discovery)
    "stm32f4": TargetSpec(
        name="stm32f4",
        arch="arm",
        cpu="cortex-m4",
        pointer_width=32,
        endianness="little",
        toolchain="arm-none-eabi",
        c_compiler="arm-none-eabi-gcc",
        cxx_compiler="arm-none-eabi-g++",
        objcopy="arm-none-eabi-objcopy",
        size_tool="arm-none-eabi-size",
        default_cflags=[
            "-mcpu=cortex-m4", "-mthumb", "-mfloat-abi=hard", "-mfpu=fpv4-sp-d16",
            "-ffreestanding", "-fno-exceptions", "-fno-rtti", "-Os", "-Wall"
        ],
        default_ldflags=["-nostdlib", "-Wl,--gc-sections"],
        description="STM32F4 series (ARM Cortex-M4 with FPU)"
    ),

    # 2. ARM Cortex-M3 (STM32F1 / BluePill)
    "stm32f1": TargetSpec(
        name="stm32f1",
        arch="arm",
        cpu="cortex-m3",
        pointer_width=32,
        endianness="little",
        toolchain="arm-none-eabi",
        c_compiler="arm-none-eabi-gcc",
        cxx_compiler="arm-none-eabi-g++",
        objcopy="arm-none-eabi-objcopy",
        size_tool="arm-none-eabi-size",
        default_cflags=[
            "-mcpu=cortex-m3", "-mthumb", "-ffreestanding",
            "-fno-exceptions", "-fno-rtti", "-Os", "-Wall"
        ],
        default_ldflags=["-nostdlib", "-Wl,--gc-sections"],
        description="STM32F1 series (ARM Cortex-M3 BluePill)"
    ),

    # 3. ARM Cortex-M0+ (Raspberry Pi RP2040 / Pico)
    "rp2040": TargetSpec(
        name="rp2040",
        arch="arm",
        cpu="cortex-m0plus",
        pointer_width=32,
        endianness="little",
        toolchain="arm-none-eabi",
        c_compiler="arm-none-eabi-gcc",
        cxx_compiler="arm-none-eabi-g++",
        objcopy="arm-none-eabi-objcopy",
        size_tool="arm-none-eabi-size",
        default_cflags=[
            "-mcpu=cortex-m0plus", "-mthumb", "-ffreestanding",
            "-fno-exceptions", "-fno-rtti", "-Os", "-Wall"
        ],
        default_ldflags=["-nostdlib", "-Wl,--gc-sections"],
        description="Raspberry Pi RP2040 Dual Cortex-M0+"
    ),

    # 4. AVR 8-bit (Atmega328P / Arduino Uno)
    "atmega328p": TargetSpec(
        name="atmega328p",
        arch="avr",
        cpu="atmega328p",
        pointer_width=16,
        endianness="little",
        toolchain="avr",
        c_compiler="avr-gcc",
        cxx_compiler="avr-g++",
        objcopy="avr-objcopy",
        size_tool="avr-size",
        default_cflags=[
            "-mmcu=atmega328p", "-DF_CPU=16000000UL", "-ffreestanding",
            "-fno-exceptions", "-fno-rtti", "-Os", "-Wall"
        ],
        default_ldflags=["-mmcu=atmega328p", "-Wl,--gc-sections"],
        description="ATmega328P 8-bit AVR Microcontroller (Arduino Uno)"
    ),

    # 5. Generic Embedded C/C++ HAL (Freestanding Bare-Metal)
    "embedded": TargetSpec(
        name="embedded",
        arch="generic",
        cpu="generic",
        pointer_width=32,
        endianness="little",
        toolchain="clang++",
        c_compiler="clang",
        cxx_compiler="clang++",
        objcopy="llvm-objcopy",
        size_tool="llvm-size",
        default_cflags=["-ffreestanding", "-fno-exceptions", "-fno-rtti", "-Os"],
        default_ldflags=[],
        description="Generic Freestanding Embedded HAL"
    ),

    # 6. Desktop Native Target (Host System)
    "desktop": TargetSpec(
        name="desktop",
        arch="x86_64",
        cpu="host",
        pointer_width=64,
        endianness="little",
        toolchain="host",
        c_compiler="clang",
        cxx_compiler="clang++",
        objcopy="",
        size_tool="",
        default_cflags=["-O3", "-Wall"],
        default_ldflags=[],
        is_freestanding=False,
        output_formats=["exe"],
        description="Desktop Host Native Application (Windows/Linux/macOS)"
    )
}

# Synonyms and aliases
TARGET_ALIASES: Dict[str, str] = {
    "stm32": "stm32f4",
    "f4": "stm32f4",
    "f1": "stm32f1",
    "bluepill": "stm32f1",
    "pico": "rp2040",
    "arduino": "atmega328p",
    "avr": "atmega328p",
    "uno": "atmega328p",
    "baremetal": "embedded"
}

def resolve_target(name: str) -> Optional[TargetSpec]:
    clean = name.lower().strip()
    resolved = TARGET_ALIASES.get(clean, clean)
    return TARGET_REGISTRY.get(resolved)