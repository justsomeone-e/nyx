"""Safe command construction for explicit STM32 firmware flashing."""

from __future__ import annotations

import os
import shutil
import subprocess
from typing import Dict, List, Optional

from .board_model import BoardProfile


class FirmwareFlashError(RuntimeError):
    pass


class FirmwareFlasher:
    def __init__(self, board: BoardProfile):
        self.board = board

    @staticmethod
    def find_cube_programmer() -> Optional[str]:
        for executable in ("STM32_Programmer_CLI", "STM32_Programmer_CLI.exe"):
            located = shutil.which(executable)
            if located:
                return located

        candidates = []
        for env_name in ("ProgramFiles", "ProgramFiles(x86)"):
            root = os.environ.get(env_name)
            if root:
                candidates.append(
                    os.path.join(
                        root,
                        "STMicroelectronics",
                        "STM32Cube",
                        "STM32CubeProgrammer",
                        "bin",
                        "STM32_Programmer_CLI.exe",
                    )
                )
        return next((path for path in candidates if os.path.isfile(path)), None)

    def build_command(
        self,
        firmware: str,
        *,
        probe: str = "auto",
        serial_number: str = "",
        connect_under_reset: bool = False,
        tool_override: str = "",
    ) -> List[str]:
        image = os.path.abspath(firmware)
        if not os.path.isfile(image):
            raise FirmwareFlashError(f"Firmware file not found: {image}")

        selected_probe = probe.lower()
        if selected_probe == "auto":
            selected_probe = "cube" if (tool_override or self.find_cube_programmer()) else "openocd"
        if selected_probe in ("cube", "stlink", "stm32cubeprogrammer"):
            tool = tool_override or self.find_cube_programmer()
            if not tool:
                raise FirmwareFlashError(
                    "STM32CubeProgrammer CLI was not found. Install it from ST or use --probe openocd."
                )
            connection = ["port=SWD"]
            if serial_number:
                connection.append(f"sn={serial_number}")
            if connect_under_reset:
                connection.extend(("mode=UR", "reset=HWrst"))
            command = [tool, "-c", *connection, "-w", image]
            if image.lower().endswith(".bin"):
                command.append(f"0x{self.board.flash_origin:08X}")
            command.extend(["-v", "-rst"])
            return command

        if selected_probe == "openocd":
            tool = tool_override or shutil.which("openocd")
            if not tool:
                raise FirmwareFlashError(
                    "OpenOCD was not found. Install OpenOCD or STM32CubeProgrammer."
                )
            if not self.board.openocd_target:
                raise FirmwareFlashError(
                    f"Board '{self.board.name}' does not declare an OpenOCD target configuration"
                )
            program = f"program {{{image}}} verify reset exit"
            if image.lower().endswith(".bin"):
                program = f"program {{{image}}} 0x{self.board.flash_origin:08X} verify reset exit"
            return [
                tool,
                "-f",
                "interface/stlink.cfg",
                "-f",
                f"target/{self.board.openocd_target}.cfg",
                "-c",
                program,
            ]

        raise FirmwareFlashError(f"Unknown probe/programmer '{probe}'")

    def flash(self, firmware: str, **options) -> Dict[str, object]:
        command = self.build_command(firmware, **options)
        process = subprocess.run(command, capture_output=True, text=True)
        return {
            "success": process.returncode == 0,
            "returncode": process.returncode,
            "command": command,
            "stdout": process.stdout,
            "stderr": process.stderr,
        }
