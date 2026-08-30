"""Canonical backend and standard-library capability contracts.

Every compiler entry point consumes this registry.  A target is therefore a
versioned contract instead of a collection of duplicated CLI aliases and
implicit code-generator behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet, Optional, Tuple


CAPABILITY_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class BackendSpec:
    name: str
    display_name: str
    family: str
    artifact: str
    maturity: str
    aliases: Tuple[str, ...]
    features: FrozenSet[str]

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "family": self.family,
            "artifact": self.artifact,
            "maturity": self.maturity,
            "aliases": list(self.aliases),
            "features": sorted(self.features),
            "stdlib_modules": sorted(stdlib_modules_for_target(self.name)),
        }


@dataclass(frozen=True)
class StdlibContract:
    module: str
    targets: FrozenSet[str]
    maturity: str = "stable"
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "module": self.module,
            "targets": sorted(self.targets),
            "maturity": self.maturity,
            "note": self.note,
        }


CORE_FEATURES = frozenset({
    "arrays", "control_flow", "functions", "optionals", "pattern_match",
    "strings", "structs", "unicode",
})
CONCURRENCY_FEATURES = frozenset({"channels", "spawn"})
NATIVE_FEATURES = CORE_FEATURES | frozenset({
    "filesystem", "native_ffi", "native_linking", "sockets", "threads",
    "unsafe_memory",
}) | CONCURRENCY_FEATURES
DYNAMIC_FEATURES = CORE_FEATURES | frozenset({
    "encoding", "filesystem", "hash", "json_lite", "math", "time",
}) | CONCURRENCY_FEATURES
V4_NUMERIC_FEATURES = frozenset({
    "canonical_scalar_text", "float64_ieee", "int64_wrap",
})
HIR_V1_FEATURES = frozenset({"typed_hir_v1"})
EMBEDDED_FEATURES = frozenset({
    "control_flow", "freestanding", "functions", "hardware_io", "interrupts",
    "static_memory", "structs", "unsafe_memory",
})


BACKENDS: Dict[str, BackendSpec] = {
    "hecpp": BackendSpec(
        "hecpp", "C++20 Native", "native", "executable/library", "stable",
        ("cpp", "c++", "native", "desktop"),
        NATIVE_FEATURES | V4_NUMERIC_FEATURES | HIR_V1_FEATURES | frozenset({"async_tasks", "exceptions"}),
    ),
    "heasm": BackendSpec(
        "heasm", "x86_64 Assembly", "native", "assembly", "beta",
        ("asm", "assembly"), NATIVE_FEATURES,
    ),
    "hejs": BackendSpec(
        "hejs", "Node.js ES2022", "hosted", "javascript", "stable",
        ("js", "node", "nodejs"),
        DYNAMIC_FEATURES | V4_NUMERIC_FEATURES | HIR_V1_FEATURES | frozenset({"async_tasks", "exceptions"}),
    ),
    "hepy": BackendSpec(
        "hepy", "Python 3", "hosted", "python", "stable",
        ("py", "python", "python3"),
        DYNAMIC_FEATURES | V4_NUMERIC_FEATURES | HIR_V1_FEATURES | frozenset({"async_tasks", "exceptions"}),
    ),
    "hers": BackendSpec(
        "hers", "Rust 2021", "native", "rust", "beta",
        ("rs", "rust"), CORE_FEATURES | HIR_V1_FEATURES | frozenset({"unsafe_memory"}),
    ),
    "hereact": BackendSpec(
        "hereact", "React 19 TSX", "web", "tsx", "beta",
        ("react", "tsx"), frozenset({"components", "react19", "tsx", "unicode"}),
    ),
    "hewasm": BackendSpec(
        "hewasm", "WebAssembly", "web", "wat/wasm", "beta",
        ("wasm", "wat", "webassembly"), HIR_V1_FEATURES | frozenset({
            "control_flow", "functions", "numeric", "string_abi", "unicode", "wasm32",
        }),
    ),
    "stm32f4": BackendSpec(
        "stm32f4", "STM32F4 Cortex-M4", "embedded", "elf/hex/bin", "experimental",
        ("stm32", "f4"), EMBEDDED_FEATURES,
    ),
    "stm32f1": BackendSpec(
        "stm32f1", "STM32F1 Cortex-M3", "embedded", "elf/hex/bin", "experimental",
        ("f1", "bluepill"), EMBEDDED_FEATURES,
    ),
    "rp2040": BackendSpec(
        "rp2040", "RP2040 Cortex-M0+", "embedded", "elf/hex/bin", "experimental",
        ("pico",), EMBEDDED_FEATURES,
    ),
    "atmega328p": BackendSpec(
        "atmega328p", "ATmega328P AVR", "embedded", "elf/hex/bin", "experimental",
        ("arduino", "avr", "uno"), EMBEDDED_FEATURES,
    ),
    "embedded": BackendSpec(
        "embedded", "Generic Freestanding", "embedded", "elf/hex/bin", "experimental",
        ("baremetal",), EMBEDDED_FEATURES,
    ),
}


_ALIASES: Dict[str, str] = {name: name for name in BACKENDS}
for _name, _backend in BACKENDS.items():
    for _alias in _backend.aliases:
        _ALIASES[_alias] = _name


CPP_HOSTS = frozenset({"hecpp", "heasm"})
PARITY_HOSTS = frozenset({"hecpp", "heasm", "hejs", "hepy"})
DYNAMIC_HOSTS = frozenset({"hecpp", "heasm", "hejs", "hepy", "hers"})
EMBEDDED_TARGETS = frozenset({"stm32f4", "stm32f1", "rp2040", "atmega328p", "embedded"})
MEMORY_TARGETS = CPP_HOSTS | EMBEDDED_TARGETS
PHYSICAL_HARDWARE_TARGETS = EMBEDDED_TARGETS
BOARD_SCOPED_STDLIB_MODULES = frozenset({
    "board", "gpio", "serial", "spi", "i2c", "mmio", "adc", "pwm", "timer", "interrupt",
})


STDLIB_CONTRACTS: Dict[str, StdlibContract] = {
    "encoding": StdlibContract("encoding", PARITY_HOSTS),
    "fs": StdlibContract("fs", PARITY_HOSTS),
    "hash": StdlibContract("hash", PARITY_HOSTS),
    "json_lite": StdlibContract("json_lite", PARITY_HOSTS),
    "json": StdlibContract("json", PARITY_HOSTS, "deprecated", "Use std/json_lite."),
    "math": StdlibContract("math", PARITY_HOSTS),
    "time": StdlibContract("time", PARITY_HOSTS),
    "str": StdlibContract("str", DYNAMIC_HOSTS),
    "io": StdlibContract("io", frozenset({"hecpp", "heasm", "hepy"})),
    "env": StdlibContract("env", CPP_HOSTS),
    "net": StdlibContract("net", CPP_HOSTS),
    "os": StdlibContract("os", CPP_HOSTS),
    "platform": StdlibContract("platform", CPP_HOSTS),
    "process": StdlibContract("process", CPP_HOSTS),
    "thread": StdlibContract("thread", CPP_HOSTS),
    "memory": StdlibContract("memory", MEMORY_TARGETS),
    "board": StdlibContract("board", PHYSICAL_HARDWARE_TARGETS),
    "gpio": StdlibContract("gpio", PHYSICAL_HARDWARE_TARGETS),
    "i2c": StdlibContract("i2c", PHYSICAL_HARDWARE_TARGETS),
    "mmio": StdlibContract("mmio", PHYSICAL_HARDWARE_TARGETS),
    "serial": StdlibContract("serial", PHYSICAL_HARDWARE_TARGETS),
    "spi": StdlibContract("spi", PHYSICAL_HARDWARE_TARGETS),
    "adc": StdlibContract("adc", PHYSICAL_HARDWARE_TARGETS),
    "pwm": StdlibContract("pwm", PHYSICAL_HARDWARE_TARGETS),
    "timer": StdlibContract("timer", PHYSICAL_HARDWARE_TARGETS),
    "interrupt": StdlibContract("interrupt", PHYSICAL_HARDWARE_TARGETS),
}


def normalize_backend_name(name: Optional[str], default: str = "hecpp") -> str:
    clean = (name or default).strip().lower()
    return _ALIASES.get(clean, clean)


def resolve_backend(name: Optional[str]) -> Optional[BackendSpec]:
    return BACKENDS.get(normalize_backend_name(name))


def get_stdlib_contract(module: str) -> Optional[StdlibContract]:
    clean = module.replace("\\", "/").strip("/")
    if clean.endswith(".nyx"):
        clean = clean[:-4]
    return STDLIB_CONTRACTS.get(clean)


def stdlib_modules_for_target(target: str) -> FrozenSet[str]:
    canonical = normalize_backend_name(target)
    return frozenset(
        name for name, contract in STDLIB_CONTRACTS.items()
        if canonical in contract.targets
    )


def stdlib_module_from_import(import_path: str) -> Optional[str]:
    clean = import_path.replace("::", "/").replace("\\", "/").strip("/")
    parts = clean.split("/", 1)
    if len(parts) != 2 or parts[0] not in ("std", "native"):
        return None
    module = parts[1]
    if module.endswith(".nyx"):
        module = module[:-4]
    return module


def capability_manifest() -> dict:
    return {
        "schema_version": CAPABILITY_SCHEMA_VERSION,
        "backends": [BACKENDS[name].to_dict() for name in sorted(BACKENDS)],
        "stdlib": [STDLIB_CONTRACTS[name].to_dict() for name in sorted(STDLIB_CONTRACTS)],
    }
