"""
nyx Embedded Cross-Compilation & Firmware Generation Engine
Manages toolchain discovery, target compilation, linker script orchestration,
and ELF/HEX/BIN firmware artifact production.
"""

import os
import shutil
import subprocess
from typing import Optional, Dict, Any, Tuple
from .target_model import TargetSpec, resolve_target
from src.codegen.cpp_toolchain import CppToolchain

class EmbeddedBuilder:
    def __init__(self, target_spec: TargetSpec, project_dir: str):
        self.spec = target_spec
        self.project_dir = project_dir
        self.bsp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "targets", "embedded")

    def find_cross_tools(self) -> Dict[str, Optional[str]]:
        """Finds cross-compiler, objcopy, and size tools."""
        cxx = shutil.which(self.spec.cxx_compiler)
        objcopy = shutil.which(self.spec.objcopy)
        size_tool = shutil.which(self.spec.size_tool)

        # Fallback to host LLVM Clang / LLD if GNU ARM is not explicitly installed
        if not cxx:
            host_cxx = CppToolchain.find_compiler()
            if host_cxx and ("clang" in host_cxx.lower()):
                cxx = host_cxx
                bin_dir = os.path.dirname(host_cxx)
                if not objcopy:
                    cand_obj = os.path.join(bin_dir, "llvm-objcopy.exe")
                    if os.path.exists(cand_obj): objcopy = cand_obj
                    else: objcopy = shutil.which("llvm-objcopy")
                if not size_tool:
                    cand_sz = os.path.join(bin_dir, "llvm-size.exe")
                    if os.path.exists(cand_sz): size_tool = cand_sz
                    else: size_tool = shutil.which("llvm-size")

        return {
            "cxx": cxx,
            "objcopy": objcopy,
            "size": size_tool
        }

    def build_firmware(self, cpp_source_path: str, output_name: str) -> Dict[str, Any]:
        """
        Compiles the transpiled C++20 freestanding source into ELF, HEX, and BIN.
        """
        build_dir = os.path.join(self.project_dir, "build", self.spec.name)
        os.makedirs(build_dir, exist_ok=True)

        elf_path = os.path.join(build_dir, f"{output_name}.elf")
        hex_path = os.path.join(build_dir, f"{output_name}.hex")
        bin_path = os.path.join(build_dir, f"{output_name}.bin")

        tools = self.find_cross_tools()
        cxx = tools["cxx"]
        if not cxx:
            return {
                "success": False,
                "error": (
                    f"Cross-toolchain missing for target '{self.spec.name}'.\n"
                    f"Required: {self.spec.cxx_compiler} or LLVM Clang\n"
                    f"To install on Windows: winget install Arm.GnuArmEmbeddedToolchain\n"
                    f"To install on Ubuntu/Debian: sudo apt install gcc-arm-none-eabi binutils-arm-none-eabi"
                )
            }

        linker_script = os.path.join(self.bsp_dir, "stm32f401.ld")
        startup_file = os.path.join(self.bsp_dir, "startup_stm32f4.cpp")
        bsp_header = os.path.join(self.bsp_dir, "stm32f4_hal.h")

        is_clang = "clang" in cxx.lower()

        # Build compiler command
        cmd = [cxx, "-std=c++20"]
        if is_clang:
            cmd.extend([
                "--target=armv7em-none-eabi",
                "-mcpu=cortex-m4",
                "-mthumb",
                "-mfloat-abi=soft",
                "-ffreestanding",
                "-fno-exceptions",
                "-fno-rtti",
                "-fno-threadsafe-statics",
                "-nostdinc++",
                "-Os",
                "-fuse-ld=lld",
                "-nostdlib"
            ])
        else:
            cmd.extend(self.spec.default_cflags)
            cmd.extend(self.spec.default_ldflags)

        cmd.extend([
            f"-I{self.bsp_dir}",
            f"-include", bsp_header,
        ])

        if os.path.exists(linker_script):
            cmd.append(f"-Wl,-T,{linker_script}")

        sources = [cpp_source_path]
        if os.path.exists(startup_file):
            sources.append(startup_file)

        cmd.extend(sources)
        cmd.extend(["-o", elf_path])

        # Execute compilation to ELF
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            return {
                "success": False,
                "error": f"Cross-Compilation Failed:\n{proc.stderr}\nCommand: {' '.join(cmd)}"
            }

        # 2. Produce HEX and BIN firmware
        objcopy = tools["objcopy"]
        if objcopy:
            subprocess.run([objcopy, "-O", "ihex", elf_path, hex_path])
            subprocess.run([objcopy, "-O", "binary", elf_path, bin_path])

        # 3. Size analysis
        size_tool = tools["size"]
        size_output = ""
        if size_tool:
            sproc = subprocess.run([size_tool, elf_path], capture_output=True, text=True)
            size_output = sproc.stdout.strip()

        return {
            "success": True,
            "elf": elf_path,
            "hex": hex_path if os.path.exists(hex_path) else None,
            "bin": bin_path if os.path.exists(bin_path) else None,
            "size": size_output,
            "toolchain": cxx
        }