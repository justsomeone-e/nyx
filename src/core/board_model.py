"""Data-driven embedded board profiles for Nyx firmware builds.

Board identity is deliberately separate from compiler backend identity.  A
backend describes language/code-generation semantics; a board profile selects
the concrete MCU flags, BSP, connector aliases, and programmer transport.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
import re
import tomllib
from typing import Dict, Iterable, Mapping, Optional, Tuple


BOARD_SCHEMA_VERSION = 2
_BOARD_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_DEFINE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:=.*)?$")


class BoardProfileError(ValueError):
    """Raised when a built-in or custom board profile is invalid."""


@dataclass(frozen=True)
class BoardProfile:
    name: str
    display_name: str
    mcu: str
    compiler_target: str
    cpu: str
    clang_target: str
    cflags: Tuple[str, ...]
    support: str
    programmer: str = "stm32cubeprogrammer"
    openocd_target: str = ""
    aliases: Tuple[str, ...] = ()
    bsp_header: str = ""
    startup_file: str = ""
    linker_script: str = ""
    include_dirs: Tuple[str, ...] = ()
    source_files: Tuple[str, ...] = ()
    defines: Tuple[str, ...] = ()
    ldflags: Tuple[str, ...] = ()
    startup_owns_vectors: bool = False
    flash_origin: int = 0x08000000
    flash_length: int = 0
    ram_origin: int = 0x20000000
    ram_length: int = 0
    pins: Mapping[str, int] = field(default_factory=dict)
    interrupt_vectors: Mapping[str, int] = field(default_factory=dict)
    peripherals: Tuple[str, ...] = ()
    source_path: str = ""
    note: str = ""

    @property
    def is_build_ready(self) -> bool:
        return self.support in ("standalone", "custom", "cmsis-pack") and bool(
            self.bsp_header and self.startup_file
        )

    def to_dict(self, *, include_layout: bool = False) -> dict:
        result = {
            "name": self.name,
            "display_name": self.display_name,
            "mcu": self.mcu,
            "compiler_target": self.compiler_target,
            "cpu": self.cpu,
            "support": self.support,
            "programmer": self.programmer,
            "aliases": list(self.aliases),
            "pins": dict(sorted(self.pins.items())),
            "interrupts": dict(sorted(self.interrupt_vectors.items())),
            "peripherals": list(self.peripherals),
            "build_ready": self.is_build_ready,
            "note": self.note,
        }
        if include_layout:
            result["memory"] = {
                "flash_origin": self.flash_origin,
                "flash_length": self.flash_length,
                "ram_origin": self.ram_origin,
                "ram_length": self.ram_length,
            }
            result["bsp"] = {
                "header": self.bsp_header,
                "startup": self.startup_file,
                "linker_script": self.linker_script,
                "include_dirs": list(self.include_dirs),
                "source_files": list(self.source_files),
                "defines": list(self.defines),
                "ldflags": list(self.ldflags),
                "startup_owns_vectors": self.startup_owns_vectors,
            }
        return result


# UM1724 Nucleo-64 boards share the Arduino Uno V3 connector assignment for
# these common signals.  Raw PA/PB/PC aliases remain available through the
# numeric port encoding (PA0=0, PB0=16, PC0=32, ...).
NUCLEO64_ARDUINO_PINS: Dict[str, int] = {
    "D0": 3,    # PA3, USART2 RX
    "D1": 2,    # PA2, USART2 TX
    "D2": 10,   # PA10
    "D3": 19,   # PB3
    "D4": 21,   # PB5
    "D5": 20,   # PB4
    "D6": 26,   # PB10
    "D7": 8,    # PA8
    "D8": 9,    # PA9
    "D9": 39,   # PC7
    "D10": 22,  # PB6
    "D11": 7,   # PA7 / SPI1 MOSI
    "D12": 6,   # PA6 / SPI1 MISO
    "D13": 5,   # PA5 / SPI1 SCK / LD2
    "D14": 25,  # PB9 / I2C1 SDA
    "D15": 24,  # PB8 / I2C1 SCL
    "A0": 0,    # PA0
    "A1": 1,    # PA1
    "A2": 4,    # PA4
    "A3": 16,   # PB0
    "A4": 33,   # PC1
    "A5": 32,   # PC0
    "LED": 5,
    "BUTTON": 45,  # PC13
    "UART_TX": 2,
    "UART_RX": 3,
    "SPI_SCK": 5,
    "SPI_MISO": 6,
    "SPI_MOSI": 7,
    "I2C_SDA": 25,
    "I2C_SCL": 24,
}


_F4_FLAGS = (
    "-mcpu=cortex-m4",
    "-mthumb",
    "-mfloat-abi=soft",
    "-ffreestanding",
    "-fno-exceptions",
    "-fno-rtti",
    "-fno-threadsafe-statics",
    "-Os",
    "-Wall",
)
_F4_COMMON_INTERRUPTS: Dict[str, int] = {
    "WWDG_IRQHandler": 0,
    "PVD_IRQHandler": 1,
    "TAMP_STAMP_IRQHandler": 2,
    "RTC_WKUP_IRQHandler": 3,
    "FLASH_IRQHandler": 4,
    "RCC_IRQHandler": 5,
    "EXTI0_IRQHandler": 6,
    "EXTI1_IRQHandler": 7,
    "EXTI2_IRQHandler": 8,
    "EXTI3_IRQHandler": 9,
    "EXTI4_IRQHandler": 10,
    "DMA1_Stream0_IRQHandler": 11,
    "DMA1_Stream1_IRQHandler": 12,
    "DMA1_Stream2_IRQHandler": 13,
    "DMA1_Stream3_IRQHandler": 14,
    "DMA1_Stream4_IRQHandler": 15,
    "DMA1_Stream5_IRQHandler": 16,
    "DMA1_Stream6_IRQHandler": 17,
    "ADC_IRQHandler": 18,
    "EXTI9_5_IRQHandler": 23,
    "TIM1_BRK_TIM9_IRQHandler": 24,
    "TIM1_TRG_COM_TIM11_IRQHandler": 26,
    "TIM1_CC_IRQHandler": 27,
    "I2C1_EV_IRQHandler": 31,
    "I2C1_ER_IRQHandler": 32,
    "I2C2_EV_IRQHandler": 33,
    "I2C2_ER_IRQHandler": 34,
    "SPI1_IRQHandler": 35,
    "SPI2_IRQHandler": 36,
    "USART1_IRQHandler": 37,
    "USART2_IRQHandler": 38,
    "EXTI15_10_IRQHandler": 40,
    "RTC_Alarm_IRQHandler": 41,
    "DMA1_Stream7_IRQHandler": 47,
    "TIM5_IRQHandler": 50,
    "DMA2_Stream0_IRQHandler": 56,
    "DMA2_Stream1_IRQHandler": 57,
    "DMA2_Stream2_IRQHandler": 58,
    "DMA2_Stream3_IRQHandler": 59,
    "DMA2_Stream4_IRQHandler": 60,
    "DMA2_Stream5_IRQHandler": 68,
    "DMA2_Stream6_IRQHandler": 69,
    "DMA2_Stream7_IRQHandler": 70,
    "USART6_IRQHandler": 71,
    "FPU_IRQHandler": 81,
}

_F401_INTERRUPTS: Dict[str, int] = {
    **_F4_COMMON_INTERRUPTS,
    "TIM1_UP_TIM10_IRQHandler": 25,
    "TIM2_IRQHandler": 28,
    "TIM3_IRQHandler": 29,
    "TIM4_IRQHandler": 30,
    "OTG_FS_WKUP_IRQHandler": 42,
    "SDIO_IRQHandler": 49,
    "SPI3_IRQHandler": 51,
    "OTG_FS_IRQHandler": 67,
    "I2C3_EV_IRQHandler": 72,
    "I2C3_ER_IRQHandler": 73,
    "SPI4_IRQHandler": 84,
}

_F410_INTERRUPTS: Dict[str, int] = {
    **_F4_COMMON_INTERRUPTS,
    "TIM1_UP_IRQHandler": 25,
    "TIM6_DAC_IRQHandler": 54,
    "RNG_IRQHandler": 80,
    "SPI5_IRQHandler": 85,
    "FMPI2C1_EV_IRQHandler": 95,
    "FMPI2C1_ER_IRQHandler": 96,
    "LPTIM1_IRQHandler": 97,
}

_F411_INTERRUPTS: Dict[str, int] = {
    **_F401_INTERRUPTS,
    "SPI5_IRQHandler": 85,
}

_F446_INTERRUPTS: Dict[str, int] = {
    **_F4_COMMON_INTERRUPTS,
    "CAN1_TX_IRQHandler": 19,
    "CAN1_RX0_IRQHandler": 20,
    "CAN1_RX1_IRQHandler": 21,
    "CAN1_SCE_IRQHandler": 22,
    "TIM1_UP_TIM10_IRQHandler": 25,
    "TIM2_IRQHandler": 28,
    "TIM3_IRQHandler": 29,
    "TIM4_IRQHandler": 30,
    "USART3_IRQHandler": 39,
    "OTG_FS_WKUP_IRQHandler": 42,
    "TIM8_BRK_TIM12_IRQHandler": 43,
    "TIM8_UP_TIM13_IRQHandler": 44,
    "TIM8_TRG_COM_TIM14_IRQHandler": 45,
    "TIM8_CC_IRQHandler": 46,
    "FMC_IRQHandler": 48,
    "SDIO_IRQHandler": 49,
    "SPI3_IRQHandler": 51,
    "UART4_IRQHandler": 52,
    "UART5_IRQHandler": 53,
    "TIM6_DAC_IRQHandler": 54,
    "TIM7_IRQHandler": 55,
    "CAN2_TX_IRQHandler": 63,
    "CAN2_RX0_IRQHandler": 64,
    "CAN2_RX1_IRQHandler": 65,
    "CAN2_SCE_IRQHandler": 66,
    "OTG_FS_IRQHandler": 67,
    "I2C3_EV_IRQHandler": 72,
    "I2C3_ER_IRQHandler": 73,
    "OTG_HS_EP1_OUT_IRQHandler": 74,
    "OTG_HS_EP1_IN_IRQHandler": 75,
    "OTG_HS_WKUP_IRQHandler": 76,
    "OTG_HS_IRQHandler": 77,
    "DCMI_IRQHandler": 78,
    "SPI4_IRQHandler": 84,
    "SAI1_IRQHandler": 87,
    "SAI2_IRQHandler": 91,
    "QUADSPI_IRQHandler": 92,
    "CEC_IRQHandler": 93,
    "SPDIF_RX_IRQHandler": 94,
    "FMPI2C1_EV_IRQHandler": 95,
    "FMPI2C1_ER_IRQHandler": 96,
}

_F4_PERIPHERALS = (
    "board", "gpio", "mmio", "serial", "spi", "i2c", "timer", "adc", "interrupt",
)
_F4_PWM_PERIPHERALS = _F4_PERIPHERALS + ("pwm",)


def _f4_board(
    name: str,
    mcu: str,
    flash_length: int,
    ram_length: int,
    *,
    aliases: Iterable[str] = (),
    interrupt_vectors: Mapping[str, int],
    peripherals: Tuple[str, ...] = _F4_PWM_PERIPHERALS,
) -> BoardProfile:
    return BoardProfile(
        name=name,
        display_name=name.upper(),
        mcu=mcu,
        compiler_target="stm32f4",
        cpu="cortex-m4",
        clang_target="armv7em-none-eabi",
        cflags=_F4_FLAGS,
        support="standalone",
        openocd_target="stm32f4x",
        aliases=tuple(aliases),
        bsp_header="stm32f4_hal.h",
        startup_file="startup_stm32f4.cpp",
        flash_length=flash_length,
        ram_length=ram_length,
        pins=NUCLEO64_ARDUINO_PINS,
        interrupt_vectors=interrupt_vectors,
        peripherals=peripherals,
        note="Built-in register-level Nyx BSP; no vendor HAL source is required.",
    )


def _pack_board(
    name: str,
    mcu: str,
    compiler_target: str,
    cpu: str,
    clang_target: str,
    *,
    aliases: Iterable[str] = (),
    openocd_target: str = "",
) -> BoardProfile:
    return BoardProfile(
        name=name,
        display_name=name.upper(),
        mcu=mcu,
        compiler_target=compiler_target,
        cpu=cpu,
        clang_target=clang_target,
        cflags=(f"-mcpu={cpu}", "-mthumb", "-ffreestanding", "-fno-exceptions", "-fno-rtti", "-Os", "-Wall"),
        support="cmsis-pack",
        openocd_target=openocd_target,
        aliases=tuple(aliases),
        pins=NUCLEO64_ARDUINO_PINS,
        peripherals=("mmio",),
        note="Known Nucleo profile; configure an STM32Cube/CMSIS BSP or a custom board.toml before building.",
    )


BOARD_REGISTRY: Dict[str, BoardProfile] = {
    # Built-in standalone F4 BSP matrix.
    "nucleo-f401re": _f4_board(
        "nucleo-f401re", "STM32F401RET6", 512 * 1024, 96 * 1024,
        aliases=("f401re",), interrupt_vectors=_F401_INTERRUPTS,
    ),
    "nucleo-f410rb": _f4_board(
        "nucleo-f410rb", "STM32F410RBT6", 128 * 1024, 32 * 1024,
        aliases=("f410rb",), interrupt_vectors=_F410_INTERRUPTS, peripherals=_F4_PERIPHERALS,
    ),
    "nucleo-f411re": _f4_board(
        "nucleo-f411re", "STM32F411RET6", 512 * 1024, 128 * 1024,
        aliases=("f411re",), interrupt_vectors=_F411_INTERRUPTS,
    ),
    "nucleo-f446re": _f4_board(
        "nucleo-f446re", "STM32F446RET6", 512 * 1024, 128 * 1024,
        aliases=("f446re",), interrupt_vectors=_F446_INTERRUPTS,
    ),

    # Remaining MB1136 Nucleo-64 models from ST UM1724.  They are registered
    # now so CLI/project contracts are stable while family BSP adapters land.
    "nucleo-f030r8": _pack_board("nucleo-f030r8", "STM32F030R8T6", "embedded", "cortex-m0", "armv6m-none-eabi", openocd_target="stm32f0x"),
    "nucleo-f070rb": _pack_board("nucleo-f070rb", "STM32F070RBT6", "embedded", "cortex-m0", "armv6m-none-eabi", openocd_target="stm32f0x"),
    "nucleo-f072rb": _pack_board("nucleo-f072rb", "STM32F072RBT6", "embedded", "cortex-m0", "armv6m-none-eabi", openocd_target="stm32f0x"),
    "nucleo-f091rc": _pack_board("nucleo-f091rc", "STM32F091RCT6", "embedded", "cortex-m0", "armv6m-none-eabi", openocd_target="stm32f0x"),
    "nucleo-f103rb": _pack_board("nucleo-f103rb", "STM32F103RBT6", "stm32f1", "cortex-m3", "armv7m-none-eabi", aliases=("f103rb",), openocd_target="stm32f1x"),
    "nucleo-f302r8": _pack_board("nucleo-f302r8", "STM32F302R8T6", "embedded", "cortex-m4", "armv7em-none-eabi", openocd_target="stm32f3x"),
    "nucleo-f303re": _pack_board("nucleo-f303re", "STM32F303RET6", "embedded", "cortex-m4", "armv7em-none-eabi", openocd_target="stm32f3x"),
    "nucleo-f334r8": _pack_board("nucleo-f334r8", "STM32F334R8T6", "embedded", "cortex-m4", "armv7em-none-eabi", openocd_target="stm32f3x"),
    "nucleo-l010rb": _pack_board("nucleo-l010rb", "STM32L010RBT6", "embedded", "cortex-m0plus", "armv6m-none-eabi", openocd_target="stm32l0"),
    "nucleo-l053r8": _pack_board("nucleo-l053r8", "STM32L053R8T6", "embedded", "cortex-m0plus", "armv6m-none-eabi", openocd_target="stm32l0"),
    "nucleo-l073rz": _pack_board("nucleo-l073rz", "STM32L073RZT6", "embedded", "cortex-m0plus", "armv6m-none-eabi", openocd_target="stm32l0"),
    "nucleo-l152re": _pack_board("nucleo-l152re", "STM32L152RET6", "embedded", "cortex-m3", "armv7m-none-eabi", openocd_target="stm32l1"),
    "nucleo-l452re": _pack_board("nucleo-l452re", "STM32L452RET6", "embedded", "cortex-m4", "armv7em-none-eabi", openocd_target="stm32l4x"),
    "nucleo-l476rg": _pack_board("nucleo-l476rg", "STM32L476RGT6", "embedded", "cortex-m4", "armv7em-none-eabi", aliases=("l476rg",), openocd_target="stm32l4x"),

    # Common newer Nucleo boards use the same profile/provider contract.
    "nucleo-g071rb": _pack_board("nucleo-g071rb", "STM32G071RBT6", "embedded", "cortex-m0plus", "armv6m-none-eabi", openocd_target="stm32g0x"),
    "nucleo-g431rb": _pack_board("nucleo-g431rb", "STM32G431RBT6", "embedded", "cortex-m4", "armv7em-none-eabi", aliases=("g431rb",), openocd_target="stm32g4x"),
    "nucleo-g474re": _pack_board("nucleo-g474re", "STM32G474RET6", "embedded", "cortex-m4", "armv7em-none-eabi", openocd_target="stm32g4x"),
    "nucleo-h743zi2": _pack_board("nucleo-h743zi2", "STM32H743ZIT6", "embedded", "cortex-m7", "armv7em-none-eabi", aliases=("h743zi2",), openocd_target="stm32h7x"),
    "nucleo-u575zi-q": _pack_board("nucleo-u575zi-q", "STM32U575ZIT6Q", "embedded", "cortex-m33", "armv8m.main-none-eabi", aliases=("u575zi-q",), openocd_target="stm32u5x"),
    "nucleo-wb55rg": _pack_board("nucleo-wb55rg", "STM32WB55RG", "embedded", "cortex-m4", "armv7em-none-eabi", aliases=("wb55rg",), openocd_target="stm32wbx"),
    "nucleo-wl55jc": _pack_board("nucleo-wl55jc", "STM32WL55JC", "embedded", "cortex-m4", "armv7em-none-eabi", aliases=("wl55jc",), openocd_target="stm32wlx"),
}


_BOARD_ALIASES: Dict[str, str] = {name: name for name in BOARD_REGISTRY}
for _name, _profile in BOARD_REGISTRY.items():
    for _alias in _profile.aliases:
        _BOARD_ALIASES[_alias.lower()] = _name


def normalize_board_name(name: str) -> str:
    clean = name.strip().lower().replace("_", "-")
    if clean.startswith("nucleo-"):
        return _BOARD_ALIASES.get(clean, clean)
    return _BOARD_ALIASES.get(clean, f"nucleo-{clean}" if f"nucleo-{clean}" in BOARD_REGISTRY else clean)


def resolve_board(name_or_path: Optional[str], *, cube_root: Optional[str] = None) -> Optional[BoardProfile]:
    if not name_or_path:
        return None
    candidate = os.path.abspath(os.path.expanduser(name_or_path))
    if os.path.isfile(candidate):
        return load_board_file(candidate)
    profile = BOARD_REGISTRY.get(normalize_board_name(name_or_path))
    if not profile or profile.support != "cmsis-pack":
        return profile
    from .stm32cube_provider import STM32CubeProviderError, materialize_cube_board
    try:
        return materialize_cube_board(profile, cube_root)
    except STM32CubeProviderError:
        if cube_root:
            raise
        return profile


def _require_string(section: Mapping[str, object], key: str, path: str) -> str:
    value = section.get(key)
    if not isinstance(value, str) or not value.strip():
        raise BoardProfileError(f"{path}: missing non-empty '{key}'")
    return value.strip()


def _resolve_profile_asset(base_dir: str, value: object) -> str:
    if not value:
        return ""
    path = os.path.expanduser(str(value))
    return os.path.abspath(path if os.path.isabs(path) else os.path.join(base_dir, path))


def _string_array(section: Mapping[str, object], key: str, profile_path: str) -> Tuple[str, ...]:
    value = section.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise BoardProfileError(f"{profile_path}: build.{key} must be an array of strings")
    return tuple(item.strip() for item in value if item.strip())


def load_board_file(path: str) -> BoardProfile:
    profile_path = os.path.abspath(path)
    try:
        with open(profile_path, "rb") as handle:
            data = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise BoardProfileError(f"Cannot read board profile '{profile_path}': {exc}") from exc

    board = data.get("board", {})
    build = data.get("build", {})
    memory = data.get("memory", {})
    programmer = data.get("programmer", {})
    pins = data.get("pins", {})
    interrupts = data.get("interrupts", {})
    if not all(isinstance(section, dict) for section in (board, build, memory, programmer, pins, interrupts)):
        raise BoardProfileError(f"{profile_path}: board/build/memory/programmer/pins/interrupts must be TOML tables")

    name = _require_string(board, "name", profile_path).lower()
    if not _BOARD_NAME_RE.fullmatch(name):
        raise BoardProfileError(f"{profile_path}: invalid board name '{name}'")
    base_dir = os.path.dirname(profile_path)
    parsed_pins: Dict[str, int] = {}
    for pin_name, pin_value in pins.items():
        if not isinstance(pin_value, int) or isinstance(pin_value, bool) or pin_value < 0:
            raise BoardProfileError(f"{profile_path}: pin '{pin_name}' must be a non-negative integer")
        parsed_pins[str(pin_name).upper()] = pin_value
    parsed_interrupts: Dict[str, int] = {}
    for handler_name, irq_number in interrupts.items():
        if not isinstance(irq_number, int) or isinstance(irq_number, bool) or irq_number < 0:
            raise BoardProfileError(f"{profile_path}: interrupt '{handler_name}' must be a non-negative IRQ number")
        parsed_interrupts[str(handler_name)] = irq_number

    cflags_value = _string_array(build, "cflags", profile_path)
    include_dirs_value = _string_array(build, "include_dirs", profile_path)
    source_files_value = _string_array(build, "source_files", profile_path)
    defines_value = _string_array(build, "defines", profile_path)
    ldflags_value = _string_array(build, "ldflags", profile_path)
    for define in defines_value:
        if not _DEFINE_RE.fullmatch(define):
            raise BoardProfileError(
                f"{profile_path}: invalid build.defines entry '{define}'; use NAME or NAME=value"
            )
    startup_owns_vectors = build.get("startup_owns_vectors", False)
    if not isinstance(startup_owns_vectors, bool):
        raise BoardProfileError(f"{profile_path}: build.startup_owns_vectors must be a boolean")
    aliases_value = board.get("aliases", [])
    if not isinstance(aliases_value, list) or not all(isinstance(item, str) for item in aliases_value):
        raise BoardProfileError(f"{profile_path}: board.aliases must be an array of strings")
    peripherals_value = board.get("peripherals", [])
    if not isinstance(peripherals_value, list) or not all(isinstance(item, str) for item in peripherals_value):
        raise BoardProfileError(f"{profile_path}: board.peripherals must be an array of strings")
    peripheral_aliases = {"uart": "serial", "interrupts": "interrupt"}
    parsed_peripherals = tuple(dict.fromkeys(
        peripheral_aliases.get(item.strip().lower(), item.strip().lower())
        for item in peripherals_value
        if item.strip()
    ))

    profile = BoardProfile(
        name=name,
        display_name=str(board.get("display_name", name)),
        mcu=_require_string(board, "mcu", profile_path),
        compiler_target=str(build.get("target", "embedded")),
        cpu=_require_string(build, "cpu", profile_path),
        clang_target=str(build.get("clang_target", "armv7em-none-eabi")),
        cflags=cflags_value,
        support="custom",
        programmer=str(programmer.get("kind", "stm32cubeprogrammer")),
        openocd_target=str(programmer.get("openocd_target", "")),
        aliases=tuple(item.lower() for item in aliases_value),
        bsp_header=_resolve_profile_asset(base_dir, build.get("bsp_header")),
        startup_file=_resolve_profile_asset(base_dir, build.get("startup_file")),
        linker_script=_resolve_profile_asset(base_dir, build.get("linker_script")),
        include_dirs=tuple(_resolve_profile_asset(base_dir, item) for item in include_dirs_value),
        source_files=tuple(_resolve_profile_asset(base_dir, item) for item in source_files_value),
        defines=defines_value,
        ldflags=ldflags_value,
        startup_owns_vectors=startup_owns_vectors,
        flash_origin=int(memory.get("flash_origin", 0x08000000)),
        flash_length=int(memory.get("flash_length", 0)),
        ram_origin=int(memory.get("ram_origin", 0x20000000)),
        ram_length=int(memory.get("ram_length", 0)),
        pins=parsed_pins,
        interrupt_vectors=parsed_interrupts,
        peripherals=parsed_peripherals,
        source_path=profile_path,
        note=str(board.get("note", "Custom board profile.")),
    )
    validate_board_profile(profile)
    return profile


def validate_board_profile(profile: BoardProfile) -> None:
    if profile.support == "custom":
        for label, value in (
            ("build.bsp_header", profile.bsp_header),
            ("build.startup_file", profile.startup_file),
        ):
            if not value or not os.path.isfile(value):
                raise BoardProfileError(f"{profile.source_path}: {label} does not exist: {value or '<missing>'}")
        if not profile.linker_script and (profile.flash_length <= 0 or profile.ram_length <= 0):
            raise BoardProfileError(
                f"{profile.source_path}: provide build.linker_script or positive memory flash_length/ram_length"
            )
        if profile.linker_script and not os.path.isfile(profile.linker_script):
            raise BoardProfileError(
                f"{profile.source_path}: build.linker_script does not exist: {profile.linker_script}"
            )
        for include_dir in profile.include_dirs:
            if not os.path.isdir(include_dir):
                raise BoardProfileError(
                    f"{profile.source_path}: build.include_dirs entry does not exist: {include_dir}"
                )
        for source_file in profile.source_files:
            if not os.path.isfile(source_file):
                raise BoardProfileError(
                    f"{profile.source_path}: build.source_files entry does not exist: {source_file}"
                )
            if Path(source_file).suffix not in (".c", ".cc", ".cpp", ".cxx", ".s", ".S"):
                raise BoardProfileError(
                    f"{profile.source_path}: unsupported vendor source type: {source_file}"
                )


def board_manifest(*, include_layout: bool = False) -> dict:
    return {
        "schema_version": BOARD_SCHEMA_VERSION,
        "boards": [
            BOARD_REGISTRY[name].to_dict(include_layout=include_layout)
            for name in sorted(BOARD_REGISTRY)
        ],
    }


def write_board_template(path: str) -> None:
    """Write a documented custom profile template without overwriting a file."""
    destination = Path(path)
    if destination.exists():
        raise BoardProfileError(f"Refusing to overwrite existing board profile '{destination}'")
    destination.write_text(
        """[board]
name = "my-nucleo-shield"
display_name = "My Nucleo + custom circuit"
mcu = "STM32F401RET6"
peripherals = ["board", "gpio", "serial", "spi", "i2c", "adc", "pwm", "timer", "interrupt", "mmio"]

[build]
target = "stm32f4"
cpu = "cortex-m4"
clang_target = "armv7em-none-eabi"
cflags = ["-mcpu=cortex-m4", "-mthumb", "-mfloat-abi=soft", "-ffreestanding", "-Os"]
bsp_header = "./my_board_hal.h"
startup_file = "./startup.cpp"
include_dirs = ["./include"]
source_files = ["./system_clock.c", "./vendor_driver.cpp"]
defines = ["STM32F401xE", "USE_NYX_BOARD=1"]
ldflags = ["-Wl,--gc-sections"]
startup_owns_vectors = false

[memory]
flash_origin = 0x08000000
flash_length = 0x00080000
ram_origin = 0x20000000
ram_length = 0x00018000

[programmer]
kind = "stm32cubeprogrammer"
openocd_target = "stm32f4x"

[pins]
STATUS_LED = 5
RELAY = 22
SENSOR_ADC = 0

[interrupts]
EXTI0_IRQHandler = 6
TIM2_IRQHandler = 28
""",
        encoding="utf-8",
        newline="\n",
    )
