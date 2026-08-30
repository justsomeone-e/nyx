"""Resolve official STM32Cube/CMSIS assets for known Nyx board profiles."""

from __future__ import annotations

from dataclasses import replace
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Dict, Iterable, Optional, Tuple

from .board_model import BoardProfile, BoardProfileError


_DEVICE_MACRO_RE = re.compile(r"\bSTM32[A-Za-z0-9_]+\b")
_MCU_RE = re.compile(
    r"^STM32(?P<model>[A-Z]{1,2}\d{2,3})(?P<package>[A-Z])(?P<density>[A-Z0-9])",
    re.IGNORECASE,
)
_IRQ_RE = re.compile(r"\b([A-Za-z][A-Za-z0-9_]*)_IRQn\s*=\s*(-?\d+)")
SUPPORTED_CUBE_FAMILIES = frozenset(("F0", "F1", "F3", "F4", "G0", "G4", "H7", "L0", "L1", "L4", "U5", "WB", "WL"))


class STM32CubeProviderError(BoardProfileError):
    """Raised when an installed STM32Cube package is incomplete or ambiguous."""


def cube_repository_url(family: str) -> str:
    family = family.strip().upper()
    if family not in SUPPORTED_CUBE_FAMILIES:
        supported = ", ".join(sorted(SUPPORTED_CUBE_FAMILIES))
        raise STM32CubeProviderError(f"Unsupported STM32Cube family '{family}'; expected one of: {supported}")
    return f"https://github.com/STMicroelectronics/STM32Cube{family}.git"


def install_cube_package(
    family: str,
    destination_root: str,
    *,
    dry_run: bool = False,
    git_executable: Optional[str] = None,
) -> dict:
    """Install only CMSIS and Nucleo project assets from an official Cube repo."""
    family = family.strip().upper()
    repository = cube_repository_url(family)
    git = git_executable or shutil.which("git")
    if not git:
        raise STM32CubeProviderError("Git is required to install STM32Cube packages")
    root = Path(destination_root).expanduser().resolve()
    destination = root / f"STM32Cube{family}"
    device_relative = f"Drivers/CMSIS/Device/ST/STM32{family}xx"
    if _looks_like_package(destination, family):
        return {
            "family": family,
            "repository": repository,
            "destination": str(destination),
            "installed": True,
            "already_present": True,
            "commands": [],
        }
    if destination.exists():
        raise STM32CubeProviderError(
            f"Refusing to overwrite incomplete STM32Cube directory: {destination}"
        )

    commands = [
        [git, "clone", "--depth", "1", "--filter=blob:none", "--sparse", repository, str(destination)],
        [
            git, "-C", str(destination), "sparse-checkout", "set", "--no-cone",
            "/.gitmodules", "/LICENSE.md", "/Drivers/CMSIS/Include/",
            f"/{device_relative}/", "/Projects/*NUCLEO*/",
        ],
        [git, "-C", str(destination), "submodule", "update", "--init", "--depth", "1", device_relative],
    ]
    if dry_run:
        return {
            "family": family,
            "repository": repository,
            "destination": str(destination),
            "installed": False,
            "already_present": False,
            "commands": commands,
        }

    root.mkdir(parents=True, exist_ok=True)
    for command in commands:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise STM32CubeProviderError(
                f"STM32Cube{family} installation failed:\n{result.stderr or result.stdout}\n"
                f"Command: {' '.join(command)}\n"
                f"Partial files were left at {destination} for inspection; nothing was deleted."
            )
    if not _looks_like_package(destination, family):
        raise STM32CubeProviderError(
            f"STM32Cube{family} checkout completed but CMSIS device assets are missing: {destination}"
        )
    return {
        "family": family,
        "repository": repository,
        "destination": str(destination),
        "installed": True,
        "already_present": False,
        "commands": commands,
    }


def cube_family_from_mcu(mcu: str) -> str:
    match = re.match(r"^STM32([A-Z]{1,2})(\d)", mcu.strip().upper())
    if not match:
        raise STM32CubeProviderError(f"Cannot derive STM32Cube family from MCU '{mcu}'")
    letters, first_digit = match.groups()
    return letters if len(letters) == 2 else f"{letters}{first_digit}"


def _natural_key(path: Path) -> tuple:
    return tuple(int(piece) if piece.isdigit() else piece.lower() for piece in re.split(r"(\d+)", path.name))


def _looks_like_package(path: Path, family: str) -> bool:
    device_root = path / "Drivers" / "CMSIS" / "Device" / "ST" / f"STM32{family}xx"
    return device_root.is_dir()


def _candidate_roots(family: str, explicit_root: Optional[str]) -> Iterable[Path]:
    values = []
    if explicit_root:
        values.append(explicit_root)
    values.extend((
        os.environ.get(f"NYX_STM32CUBE_{family}_ROOT", ""),
        os.environ.get(f"STM32CUBE_{family}_PATH", ""),
        os.environ.get("NYX_STM32CUBE_ROOT", ""),
        os.environ.get("STM32CUBE_REPOSITORY", ""),
        str(Path.home() / "STM32Cube" / "Repository"),
    ))
    seen = set()
    for value in values:
        if not value:
            continue
        candidate = Path(value).expanduser().resolve()
        if candidate not in seen:
            seen.add(candidate)
            yield candidate


def find_cube_package(family: str, cube_root: Optional[str] = None) -> Optional[str]:
    """Return the newest matching full STM32Cube package without downloading it."""
    family = family.strip().upper()
    package_names = (
        f"STM32Cube{family}",
        f"STM32Cube_FW_{family}",
    )
    matches = []
    for root in _candidate_roots(family, cube_root):
        if _looks_like_package(root, family):
            matches.append(root)
            continue
        if not root.is_dir():
            continue
        for child in root.iterdir():
            if child.is_dir() and child.name.startswith(package_names) and _looks_like_package(child, family):
                matches.append(child)
    if not matches:
        return None
    return str(sorted(set(matches), key=_natural_key)[-1])


def _select_device_macro(main_header: Path, mcu: str) -> str:
    match = _MCU_RE.match(mcu.strip().upper())
    if not match:
        raise STM32CubeProviderError(f"Cannot derive CMSIS device selector from MCU '{mcu}'")
    model = f"STM32{match.group('model')}"
    density = match.group("density")
    expected = (f"{model}x{density}", f"{model}xx")
    text = main_header.read_text(encoding="utf-8", errors="replace")
    available = sorted({token for token in _DEVICE_MACRO_RE.findall(text) if token.upper().startswith(model)})
    by_lower = {token.lower(): token for token in available}
    for candidate in expected:
        if candidate.lower() in by_lower:
            return by_lower[candidate.lower()]
    if len(available) == 1:
        return available[0]
    found = ", ".join(available) if available else "none"
    raise STM32CubeProviderError(
        f"No unambiguous CMSIS device macro for {mcu} in {main_header}; candidates: {found}"
    )


def _select_startup(device_root: Path, device_macro: str, cpu: str) -> Path:
    startup_dir = device_root / "Source" / "Templates" / "gcc"
    if not startup_dir.is_dir():
        raise STM32CubeProviderError(f"CMSIS GCC startup directory not found: {startup_dir}")
    macro_key = device_macro.lower()
    candidates = [
        path for path in startup_dir.iterdir()
        if path.is_file()
        and path.suffix in (".s", ".S")
        and path.stem.lower().removeprefix("startup_").startswith(macro_key)
    ]
    if not candidates:
        raise STM32CubeProviderError(
            f"No GCC startup source matching {device_macro} under {startup_dir}"
        )
    core_hint = {
        "cortex-m0plus": "cm0plus",
        "cortex-m4": "cm4",
        "cortex-m7": "cm7",
        "cortex-m33": "cm33",
    }.get(cpu, "")
    candidates.sort(key=lambda path: (0 if core_hint and core_hint in path.stem.lower() else 1, len(path.name), path.name))
    return candidates[0]


def _select_device_header(device_include: Path, device_macro: str) -> Path:
    exact = device_include / f"{device_macro.lower()}.h"
    if exact.is_file():
        return exact
    candidates = sorted(
        path for path in device_include.glob("*.h")
        if path.stem.lower().startswith(device_macro.lower())
    )
    if not candidates:
        raise STM32CubeProviderError(
            f"CMSIS device header for {device_macro} not found under {device_include}"
        )
    return candidates[0]


def _interrupt_vectors(device_header: Path) -> Dict[str, int]:
    text = device_header.read_text(encoding="utf-8", errors="replace")
    vectors = {}
    for name, number_text in _IRQ_RE.findall(text):
        number = int(number_text)
        if number >= 0:
            vectors[f"{name}_IRQHandler"] = number
    return vectors


def _normalized(value: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", value.upper())


def _select_linker_script(package_root: Path, profile: BoardProfile) -> Path:
    projects = package_root / "Projects"
    if not projects.is_dir():
        raise STM32CubeProviderError(f"STM32Cube Projects directory not found: {projects}")
    board_code = profile.name.removeprefix("nucleo-").upper()
    board_key = _normalized(board_code)
    board_key_without_revision = board_key[:-1] if board_key.endswith("2") else board_key
    mcu_match = _MCU_RE.match(profile.mcu.strip().upper())
    part_key = ""
    model_key = ""
    if mcu_match:
        model_key = _normalized(mcu_match.group("model"))
        part_key = _normalized(
            f"{mcu_match.group('model')}{mcu_match.group('package')}{mcu_match.group('density')}"
        )

    project_candidates = []
    for child in projects.iterdir():
        if not child.is_dir():
            continue
        key = _normalized(child.name)
        score = 100
        if key == f"NUCLEO{board_key}":
            score = 0
        elif key == f"NUCLEO{board_key_without_revision}":
            score = 1
        elif board_key in key or board_key_without_revision in key:
            score = 2
        elif part_key and part_key in key:
            score = 3
        elif model_key and model_key in key:
            score = 4
        if score < 100:
            project_candidates.append((score, child.name, child))
    if not project_candidates:
        raise STM32CubeProviderError(
            f"No STM32Cube project directory matches {profile.name} under {projects}"
        )

    _, _, board_project = sorted(project_candidates)[0]
    linker_candidates = list(board_project.rglob("*.ld"))
    if not linker_candidates:
        raise STM32CubeProviderError(f"No GNU linker script found under {board_project}")

    def linker_score(path: Path) -> tuple:
        normalized_path = _normalized(str(path))
        normalized_name = _normalized(path.name)
        return (
            0 if "STM32CUBEIDE" in normalized_path else 1,
            0 if part_key and part_key in normalized_name else 1,
            0 if "FLASH" in normalized_name else 1,
            len(path.parts),
            str(path),
        )

    return sorted(linker_candidates, key=linker_score)[0]


def materialize_cube_board(profile: BoardProfile, cube_root: Optional[str] = None) -> BoardProfile:
    """Turn a known cmsis-pack profile into a build-ready immutable profile."""
    if profile.support != "cmsis-pack" or profile.is_build_ready:
        return profile
    family = cube_family_from_mcu(profile.mcu)
    package_text = find_cube_package(family, cube_root)
    if not package_text:
        root_hint = cube_root or "STM32Cube repository"
        raise STM32CubeProviderError(
            f"STM32Cube{family} package not found under '{root_hint}'. "
            f"Pass --cube-root PATH or set NYX_STM32CUBE_ROOT."
        )
    package_root = Path(package_text)
    device_root = package_root / "Drivers" / "CMSIS" / "Device" / "ST" / f"STM32{family}xx"
    device_include = device_root / "Include"
    cmsis_include = package_root / "Drivers" / "CMSIS" / "Include"
    main_header = device_include / f"stm32{family.lower()}xx.h"
    system_source = device_root / "Source" / "Templates" / f"system_stm32{family.lower()}xx.c"
    for label, path in (
        ("CMSIS core include", cmsis_include),
        ("CMSIS device include", device_include),
        ("CMSIS family header", main_header),
        ("CMSIS system source", system_source),
    ):
        if not path.exists():
            raise STM32CubeProviderError(f"{label} not found in {package_root}: {path}")

    device_macro = _select_device_macro(main_header, profile.mcu)
    startup = _select_startup(device_root, device_macro, profile.cpu)
    device_header = _select_device_header(device_include, device_macro)
    linker = _select_linker_script(package_root, profile)
    interrupts = _interrupt_vectors(device_header)
    return replace(
        profile,
        bsp_header=str(main_header),
        startup_file=str(startup),
        linker_script=str(linker),
        include_dirs=(str(cmsis_include), str(device_include)),
        source_files=(str(system_source),),
        defines=(device_macro,),
        ldflags=("-Wl,--gc-sections",),
        startup_owns_vectors=True,
        interrupt_vectors=interrupts,
        source_path=str(package_root),
        note=(
            f"Build-ready through official STM32Cube{family} CMSIS assets at {package_root}; "
            "Nyx exposes portable MMIO until a family HAL bridge is configured."
        ),
    )


def cube_board_report(profile: BoardProfile, cube_root: Optional[str] = None) -> dict:
    """Return machine-readable provider evidence without throwing to the CLI."""
    try:
        resolved = materialize_cube_board(profile, cube_root)
    except STM32CubeProviderError as exc:
        return {
            "board": profile.name,
            "family": cube_family_from_mcu(profile.mcu),
            "build_ready": False,
            "error": str(exc),
        }
    return {
        "board": resolved.name,
        "family": cube_family_from_mcu(resolved.mcu),
        "build_ready": resolved.is_build_ready,
        "package_root": resolved.source_path,
        "device_define": resolved.defines[0] if resolved.defines else "",
        "startup": resolved.startup_file,
        "linker_script": resolved.linker_script,
        "interrupt_count": len(resolved.interrupt_vectors),
    }
