"""
nyx Embedded Cross-Compilation & Firmware Generation Engine
Manages toolchain discovery, target compilation, linker script orchestration,
and ELF/HEX/BIN firmware artifact production.
"""

import os
import re
import shutil
import subprocess
from typing import Optional, Dict, Any, Tuple, List
from .board_model import BoardProfile
from .target_model import TargetSpec
from src.codegen.cpp_toolchain import CppToolchain

class EmbeddedBuilder:
    def __init__(self, target_spec: TargetSpec, project_dir: str, board: Optional[BoardProfile] = None):
        self.spec = target_spec
        self.project_dir = os.path.abspath(project_dir)
        self.board = board
        self.bsp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "targets", "embedded")

    @property
    def build_identity(self) -> str:
        return self.board.name if self.board else self.spec.name

    def find_cross_tools(self) -> Dict[str, Optional[str]]:
        """Finds cross-compiler, objcopy, and size tools."""
        c_compiler = shutil.which(self.spec.c_compiler)
        cxx = shutil.which(self.spec.cxx_compiler)
        objcopy = shutil.which(self.spec.objcopy)
        size_tool = shutil.which(self.spec.size_tool)

        # Fallback to host LLVM Clang / LLD if GNU ARM is not explicitly installed
        if not cxx:
            host_cxx = CppToolchain.find_compiler()
            if host_cxx and ("clang" in host_cxx.lower()):
                cxx = host_cxx
                bin_dir = os.path.dirname(host_cxx)
                if not c_compiler:
                    clang_name = "clang.exe" if os.name == "nt" else "clang"
                    candidate_c = os.path.join(bin_dir, clang_name)
                    c_compiler = candidate_c if os.path.isfile(candidate_c) else shutil.which("clang")
                if not objcopy:
                    cand_obj = os.path.join(bin_dir, "llvm-objcopy.exe")
                    if os.path.exists(cand_obj): objcopy = cand_obj
                    else: objcopy = shutil.which("llvm-objcopy")
                if not size_tool:
                    cand_sz = os.path.join(bin_dir, "llvm-size.exe")
                    if os.path.exists(cand_sz): size_tool = cand_sz
                    else: size_tool = shutil.which("llvm-size")

        if cxx and not c_compiler:
            cxx_name = os.path.basename(cxx)
            if "g++" in cxx_name:
                candidate_c = os.path.join(os.path.dirname(cxx), cxx_name.replace("g++", "gcc"))
                if os.path.isfile(candidate_c):
                    c_compiler = candidate_c
            elif "clang++" in cxx_name:
                candidate_c = os.path.join(os.path.dirname(cxx), cxx_name.replace("clang++", "clang"))
                if os.path.isfile(candidate_c):
                    c_compiler = candidate_c

        return {
            "cc": c_compiler,
            "cxx": cxx,
            "objcopy": objcopy,
            "size": size_tool
        }

    def _asset(self, value: str) -> str:
        if not value:
            return ""
        return value if os.path.isabs(value) else os.path.join(self.bsp_dir, value)

    def _resolve_assets(self, build_dir: str) -> Tuple[str, str, str]:
        if self.board:
            if not self.board.is_build_ready:
                raise ValueError(
                    f"Board '{self.board.name}' is recognized but its {self.board.support} BSP "
                    "is not configured. Install/configure the matching STM32Cube CMSIS pack "
                    "or pass a custom board.toml with bsp_header, startup_file, and linker data."
                )
            header = self._asset(self.board.bsp_header)
            startup = self._asset(self.board.startup_file)
            linker = self._asset(self.board.linker_script)
            if not linker:
                linker = self._write_linker_script(build_dir)
        else:
            # Compatibility default for '#target stm32f4'.
            header = os.path.join(self.bsp_dir, "stm32f4_hal.h")
            startup = os.path.join(self.bsp_dir, "startup_stm32f4.cpp")
            linker = os.path.join(self.bsp_dir, "stm32f401.ld")

        for label, path in (("BSP header", header), ("startup file", startup), ("linker script", linker)):
            if not path or not os.path.isfile(path):
                raise ValueError(f"{label} not found for '{self.build_identity}': {path or '<missing>'}")
        return header, startup, linker

    def _write_linker_script(self, build_dir: str) -> str:
        if not self.board or self.board.flash_length <= 0 or self.board.ram_length <= 0:
            raise ValueError(f"Board '{self.build_identity}' has no linker script or complete memory layout")
        path = os.path.join(build_dir, f"{self.board.name}.ld")
        content = f"""ENTRY(Reset_Handler)

MEMORY
{{
    FLASH (rx)  : ORIGIN = 0x{self.board.flash_origin:08X}, LENGTH = 0x{self.board.flash_length:X}
    RAM   (rwx) : ORIGIN = 0x{self.board.ram_origin:08X}, LENGTH = 0x{self.board.ram_length:X}
}}

_estack = ORIGIN(RAM) + LENGTH(RAM);

SECTIONS
{{
    .isr_vector : {{ . = ALIGN(4); KEEP(*(.isr_vector)) . = ALIGN(4); }} > FLASH
    .text :
    {{
        . = ALIGN(4); *(.text) *(.text*) *(.rodata) *(.rodata*)
        *(.glue_7) *(.glue_7t) . = ALIGN(4); _etext = .;
    }} > FLASH
    _sidata = LOADADDR(.data);
    .data :
    {{
        . = ALIGN(4); _sdata = .; *(.data) *(.data*) . = ALIGN(4); _edata = .;
    }} > RAM AT> FLASH
    .bss :
    {{
        . = ALIGN(4); _sbss = .; *(.bss) *(.bss*) *(COMMON) . = ALIGN(4); _ebss = .;
    }} > RAM
    /DISCARD/ : {{ *(.ARM.exidx*) }}
}}
"""
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        return path

    @staticmethod
    def _interrupt_handlers(cpp_source_path: str) -> Tuple[str, ...]:
        with open(cpp_source_path, "r", encoding="utf-8") as handle:
            source = handle.read()
        return tuple(dict.fromkeys(re.findall(r"NYX_INTERRUPT_HANDLER:\s*([A-Za-z_][A-Za-z0-9_]*)", source)))

    def _write_vector_source(self, build_dir: str, handlers: Tuple[str, ...]) -> str:
        if not self.board:
            raise ValueError("interrupt fn requires an explicit --board profile")
        unknown = [name for name in handlers if name not in self.board.interrupt_vectors]
        if unknown:
            available = ", ".join(sorted(self.board.interrupt_vectors)) or "none"
            raise ValueError(
                f"Unknown interrupt handler(s) for '{self.board.name}': {', '.join(unknown)}. "
                f"Declared profile handlers: {available}"
            )
        if self.board.startup_owns_vectors:
            # Official CMSIS startup files already emit .isr_vector and weak
            # handler aliases. Nyx's strong extern "C" handler replaces the
            # weak symbol without creating a second vector table.
            return ""
        selected = {self.board.interrupt_vectors[name]: name for name in handlers}
        max_irq = max(selected)
        entries = ["    (void (*)(void))(&_estack)", "    Reset_Handler"]
        entries.extend((
            "    Default_Handler",  # NMI
            "    Default_Handler",  # HardFault
            "    Default_Handler",  # MemManage
            "    Default_Handler",  # BusFault
            "    Default_Handler",  # UsageFault
            "    0", "    0", "    0", "    0",
            "    Default_Handler",  # SVC
            "    Default_Handler",  # DebugMon
            "    0",
            "    Default_Handler",  # PendSV
            "    Default_Handler",  # SysTick
        ))
        for irq_number in range(max_irq + 1):
            entries.append(f"    {selected.get(irq_number, 'Default_Handler')}")

        declarations = "\n".join(f'extern "C" void {name}(void);' for name in handlers)
        entries_text = ",\n".join(entries)
        source = f"""#include <stdint.h>

extern uint32_t _estack;
extern "C" void Reset_Handler(void);
extern "C" void Default_Handler(void);
{declarations}

__attribute__((section(".isr_vector"), used))
void (* const g_pfnVectors[])(void) = {{
{entries_text}
}};
"""
        path = os.path.join(build_dir, f"{self.board.name}_vectors.cpp")
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(source)
        return path

    @staticmethod
    def _clang_target_for_cpu(cpu: str) -> str:
        return {
            "cortex-m0": "armv6m-none-eabi",
            "cortex-m0plus": "armv6m-none-eabi",
            "cortex-m3": "armv7m-none-eabi",
            "cortex-m4": "armv7em-none-eabi",
            "cortex-m7": "armv7em-none-eabi",
            "cortex-m33": "armv8m.main-none-eabi",
        }.get(cpu, "arm-none-eabi")

    @staticmethod
    def _source_language(path: str) -> str:
        suffix = os.path.splitext(path)[1]
        if suffix == ".c":
            return "c"
        if suffix in (".cc", ".cpp", ".cxx"):
            return "c++"
        if suffix == ".S":
            return "assembler-with-cpp"
        if suffix == ".s":
            return "assembler"
        raise ValueError(f"Unsupported embedded source type: {path}")

    def _compile_flags(self, language: str) -> List[str]:
        flags = list(self.board.cflags) if self.board and self.board.cflags else list(self.spec.default_cflags)
        cxx_only = {"-fno-exceptions", "-fexceptions", "-fno-rtti", "-frtti", "-fno-threadsafe-statics"}
        if language != "c++":
            flags = [flag for flag in flags if flag not in cxx_only]
        if language.startswith("assembler"):
            allowed_prefixes = ("-m", "-O", "-g", "-W", "-fdebug-prefix-map=")
            flags = [flag for flag in flags if flag.startswith(allowed_prefixes)]
        return flags

    def _clang_target(self) -> str:
        if self.board and self.board.clang_target:
            return self.board.clang_target
        return self._clang_target_for_cpu(self.spec.cpu)

    def _profile_include_dirs(self, header: str, startup: str) -> Tuple[str, ...]:
        include_dirs = {
            self.bsp_dir,
            os.path.dirname(header),
            os.path.dirname(startup),
        }
        if self.board:
            include_dirs.update(self.board.include_dirs)
            include_dirs.update(os.path.dirname(path) for path in self.board.source_files)
        return tuple(sorted(path for path in include_dirs if path))

    def _profile_defines(self, vector_source: str) -> Tuple[str, ...]:
        defines: List[str] = list(self.board.defines) if self.board else []
        if self.board:
            macro = re.sub(r"[^A-Z0-9]", "_", self.board.name.upper())
            defines.append(f"NYX_BOARD_{macro}=1")
            for name, pin in sorted(self.board.pins.items()):
                pin_macro = re.sub(r"[^A-Z0-9]", "_", name.upper())
                defines.append(f"NYX_PIN_{pin_macro}={pin}")
        if vector_source:
            defines.append("NYX_GENERATED_VECTOR_TABLE=1")
        return tuple(dict.fromkeys(defines))

    def _compile_command(
        self,
        source: str,
        destination: str,
        *,
        tools: Dict[str, Optional[str]],
        include_dirs: Tuple[str, ...],
        defines: Tuple[str, ...],
        force_header: str = "",
    ) -> List[str]:
        language = self._source_language(source)
        compiler_key = "cxx" if language == "c++" else "cc"
        compiler = tools.get(compiler_key)
        if not compiler:
            required = self.spec.cxx_compiler if compiler_key == "cxx" else self.spec.c_compiler
            raise ValueError(
                f"Cross-toolchain is missing {compiler_key.upper()} compiler '{required}' "
                f"required by {os.path.basename(source)}"
            )
        is_clang = "clang" in os.path.basename(compiler).lower()
        command = [compiler]
        if is_clang:
            command.append(f"--target={self._clang_target()}")
        command.extend(self._compile_flags(language))
        if language == "c++":
            command.extend(("-std=c++20", "-fno-exceptions", "-fno-rtti", "-fno-threadsafe-statics", "-fno-use-cxa-atexit"))
            if is_clang:
                command.append("-nostdinc++")
        elif language == "c":
            command.append("-std=c11")
        elif language == "assembler-with-cpp":
            command.extend(("-x", "assembler-with-cpp"))
        else:
            command.extend(("-x", "assembler"))
        command.extend(("-ffunction-sections", "-fdata-sections"))
        for include_dir in include_dirs:
            command.append(f"-I{include_dir}")
        for define in defines:
            command.append(f"-D{define}")
        if force_header:
            command.extend(("-include", force_header))
        command.extend(("-c", source, "-o", destination))
        return command

    def build_commands(
        self,
        cpp_source_path: str,
        output_name: str,
        tools: Optional[Dict[str, Optional[str]]] = None,
    ) -> Tuple[List[List[str]], Dict[str, str]]:
        """Create a mixed C/C++/assembly compile graph followed by one link."""
        build_dir = os.path.join(self.project_dir, "build", self.build_identity)
        object_dir = os.path.join(build_dir, "obj")
        os.makedirs(object_dir, exist_ok=True)
        paths = {
            "build_dir": build_dir,
            "elf": os.path.join(build_dir, f"{output_name}.elf"),
            "hex": os.path.join(build_dir, f"{output_name}.hex"),
            "bin": os.path.join(build_dir, f"{output_name}.bin"),
            "map": os.path.join(build_dir, f"{output_name}.map"),
        }
        selected_tools = tools or self.find_cross_tools()
        cxx = selected_tools.get("cxx")
        if not cxx:
            raise ValueError(
                f"Cross-toolchain missing for target '{self.build_identity}'.\n"
                f"Required: {self.spec.cxx_compiler} or LLVM Clang\n"
                "Windows: winget install Arm.GnuArmEmbeddedToolchain\n"
                "Ubuntu/Debian: sudo apt install gcc-arm-none-eabi binutils-arm-none-eabi"
            )

        header, startup, linker = self._resolve_assets(build_dir)
        handlers = self._interrupt_handlers(cpp_source_path)
        vector_source = self._write_vector_source(build_dir, handlers) if handlers else ""
        if vector_source:
            paths["vectors"] = vector_source
        include_dirs = self._profile_include_dirs(header, startup)
        defines = self._profile_defines(vector_source)

        source_entries: List[Tuple[str, bool]] = [(os.path.abspath(cpp_source_path), True)]
        source_entries.append((os.path.abspath(startup), False))
        if self.board and self.board.startup_owns_vectors:
            source_entries.append((os.path.join(self.bsp_dir, "cmsis_runtime.cpp"), False))
        if vector_source:
            source_entries.append((os.path.abspath(vector_source), False))
        if self.board:
            source_entries.extend((os.path.abspath(path), False) for path in self.board.source_files)

        seen = set()
        commands: List[List[str]] = []
        objects: List[str] = []
        for index, (source, force_bsp_header) in enumerate(source_entries):
            if source in seen:
                continue
            seen.add(source)
            stem = re.sub(r"[^A-Za-z0-9_.-]", "_", os.path.basename(source))
            destination = os.path.join(object_dir, f"{index:02d}_{stem}.o")
            commands.append(self._compile_command(
                source,
                destination,
                tools=selected_tools,
                include_dirs=include_dirs,
                defines=defines,
                force_header=header if force_bsp_header else "",
            ))
            objects.append(destination)

        is_clang = "clang" in os.path.basename(cxx).lower()
        link_command = [cxx]
        if is_clang:
            link_command.extend((f"--target={self._clang_target()}", "-fuse-ld=lld"))
        architecture_flags = [
            flag for flag in self._compile_flags("c++")
            if flag == "-mthumb" or flag.startswith(("-mcpu=", "-march=", "-mabi=", "-mfpu=", "-mfloat-abi="))
        ]
        link_command.extend(architecture_flags)
        link_flags = list(self.spec.default_ldflags)
        if self.board:
            link_flags.extend(self.board.ldflags)
        if "-nostdlib" not in link_flags:
            link_flags.append("-nostdlib")
        if not any("--gc-sections" in flag for flag in link_flags):
            link_flags.append("-Wl,--gc-sections")
        link_command.extend(dict.fromkeys(link_flags))
        link_command.extend((f"-Wl,-T,{linker}", f"-Wl,-Map,{paths['map']}"))
        link_command.extend(objects)
        link_command.extend(("-o", paths["elf"]))
        commands.append(link_command)
        return commands, paths

    def build_command(
        self,
        cpp_source_path: str,
        output_name: str,
        tools: Optional[Dict[str, Optional[str]]] = None,
    ) -> Tuple[List[str], Dict[str, str]]:
        if self.board and (
            self.board.source_files
            or self._source_language(self._asset(self.board.startup_file)) != "c++"
        ):
            raise ValueError(
                f"Board '{self.board.name}' requires the multi-stage mixed-source pipeline; "
                "use build_commands() instead of build_command()."
            )
        build_dir = os.path.join(self.project_dir, "build", self.build_identity)
        os.makedirs(build_dir, exist_ok=True)
        paths = {
            "build_dir": build_dir,
            "elf": os.path.join(build_dir, f"{output_name}.elf"),
            "hex": os.path.join(build_dir, f"{output_name}.hex"),
            "bin": os.path.join(build_dir, f"{output_name}.bin"),
        }
        selected_tools = tools or self.find_cross_tools()
        cxx = selected_tools.get("cxx")
        if not cxx:
            raise ValueError(
                f"Cross-toolchain missing for target '{self.build_identity}'.\n"
                f"Required: {self.spec.cxx_compiler} or LLVM Clang\n"
                "Windows: winget install Arm.GnuArmEmbeddedToolchain\n"
                "Ubuntu/Debian: sudo apt install gcc-arm-none-eabi binutils-arm-none-eabi"
            )

        header, startup, linker = self._resolve_assets(build_dir)
        handlers = self._interrupt_handlers(cpp_source_path)
        vector_source = self._write_vector_source(build_dir, handlers) if handlers else ""
        is_clang = "clang" in os.path.basename(cxx).lower()
        board_flags = list(self.board.cflags) if self.board and self.board.cflags else list(self.spec.default_cflags)
        cmd = [cxx, "-std=c++20"]
        if is_clang:
            clang_target = self.board.clang_target if self.board else self._clang_target_for_cpu(self.spec.cpu)
            cmd.append(f"--target={clang_target}")
            cmd.extend(board_flags)
            cmd.extend(["-fno-threadsafe-statics", "-nostdinc++", "-fuse-ld=lld", "-nostdlib"])
        else:
            cmd.extend(board_flags)
            cmd.extend(self.spec.default_ldflags)

        include_dirs = {self.bsp_dir, os.path.dirname(header), os.path.dirname(startup)}
        for include_dir in sorted(path for path in include_dirs if path):
            cmd.append(f"-I{include_dir}")
        cmd.extend(["-include", header])

        if self.board:
            macro = re.sub(r"[^A-Z0-9]", "_", self.board.name.upper())
            cmd.append(f"-DNYX_BOARD_{macro}=1")
            for name, pin in sorted(self.board.pins.items()):
                pin_macro = re.sub(r"[^A-Z0-9]", "_", name.upper())
                cmd.append(f"-DNYX_PIN_{pin_macro}={pin}")

        if vector_source:
            cmd.append("-DNYX_GENERATED_VECTOR_TABLE=1")

        cmd.extend([f"-Wl,-T,{linker}", cpp_source_path, startup])
        if vector_source:
            cmd.append(vector_source)
            paths["vectors"] = vector_source
        cmd.extend(["-o", paths["elf"]])
        return cmd, paths

    def build_firmware(self, cpp_source_path: str, output_name: str) -> Dict[str, Any]:
        """Compile freestanding C++ into ELF and, when tools exist, HEX/BIN."""
        tools = self.find_cross_tools()
        try:
            commands, paths = self.build_commands(cpp_source_path, output_name, tools)
        except ValueError as exc:
            return {"success": False, "error": str(exc)}

        for stage, command in enumerate(commands, start=1):
            proc = subprocess.run(command, capture_output=True, text=True)
            if proc.returncode != 0:
                return {
                    "success": False,
                    "error": (
                        f"Cross-compilation stage {stage}/{len(commands)} failed:\n"
                        f"{proc.stderr or proc.stdout}\nCommand: {' '.join(command)}"
                    ),
                    "command": command,
                    "commands": commands,
                }

        conversion_errors = []
        objcopy = tools.get("objcopy")
        if objcopy:
            for output_format, destination in (("ihex", paths["hex"]), ("binary", paths["bin"])):
                converted = subprocess.run(
                    [objcopy, "-O", output_format, paths["elf"], destination],
                    capture_output=True,
                    text=True,
                )
                if converted.returncode != 0:
                    conversion_errors.append(converted.stderr or converted.stdout)

        size_output = ""
        size_tool = tools.get("size")
        if size_tool:
            measured = subprocess.run([size_tool, paths["elf"]], capture_output=True, text=True)
            if measured.returncode == 0:
                size_output = measured.stdout.strip()

        return {
            "success": True,
            "board": self.board.name if self.board else None,
            "elf": paths["elf"],
            "hex": paths["hex"] if os.path.exists(paths["hex"]) else None,
            "bin": paths["bin"] if os.path.exists(paths["bin"]) else None,
            "size": size_output,
            "toolchain": tools.get("cxx"),
            "command": commands[-1],
            "commands": commands,
            "warnings": conversion_errors,
        }
