import os
import sys
from typing import Dict, List, Any, Optional

class NyxManifest:
    def __init__(self, filepath: Optional[str] = None):
        self.filepath = filepath
        self.package: Dict[str, Any] = {
            "name": "nyx_app",
            "version": "0.1.0",
            "edition": "2026",
            "target": "cpp",
            "entry": "src/main.nyx",
            "author": "",
            "license": "MIT",
            "description": ""
        }
        self.dependencies: Dict[str, Any] = {}
        self.native: Dict[str, Any] = {
            "includes": [],
            "links": [],
            "cflags": [],
            "ldflags": []
        }
        self.build: Dict[str, Any] = {
            "opt_level": 2,
            "output_type": "exe",
            "output_name": ""
        }
        if filepath and os.path.exists(filepath):
            self.load(filepath)

    def load(self, filepath: str):
        self.filepath = filepath
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        self._parse(lines)

    def _parse(self, lines: List[str]):
        current_section = "package"
        for raw_line in lines:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("[") and line.endswith("]"):
                current_section = line[1:-1].strip().lower()
                continue

            if "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip()

                parsed_val = self._parse_val(val)

                if current_section == "package":
                    self.package[key] = parsed_val
                elif current_section == "dependencies":
                    self.dependencies[key] = parsed_val
                elif current_section == "native":
                    self.native[key] = parsed_val
                elif current_section == "build":
                    self.build[key] = parsed_val

    def _parse_val(self, val: str) -> Any:
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            return val[1:-1]
        if val.lower() == "true":
            return True
        if val.lower() == "false":
            return False
        if val.startswith("[") and val.endswith("]"):
            items = val[1:-1].split(",")
            res = []
            for item in items:
                item = item.strip()
                if item:
                    res.append(self._parse_val(item))
            return res
        if val.startswith("{") and val.endswith("}"):
            res_dict = {}
            pairs = val[1:-1].split(",")
            for pair in pairs:
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    res_dict[k.strip()] = self._parse_val(v.strip())
            return res_dict
        try:
            if "." in val:
                return float(val)
            return int(val)
        except ValueError:
            return val

    def save(self, filepath: Optional[str] = None):
        target = filepath or self.filepath or "nyx.toml"
        p_name = self.package.get("name", "nyx_app")
        p_ver = self.package.get("version", "0.1.0")
        p_ed = self.package.get("edition", "2026")
        p_targ = self.package.get("target", "cpp")
        p_entry = self.package.get("entry", "src/main.nyx")

        lines = [
            "[package]",
            f'name = "{p_name}"',
            f'version = "{p_ver}"',
            f'edition = "{p_ed}"',
            f'target = "{p_targ}"',
            f'entry = "{p_entry}"'
        ]
        if self.package.get("description"):
            lines.append(f'description = "{self.package["description"]}"')
        if self.package.get("license"):
            lines.append(f'license = "{self.package["license"]}"')

        lines.append("\n[dependencies]")
        for k, v in self.dependencies.items():
            if isinstance(v, str):
                lines.append(f'{k} = "{v}"')
            elif isinstance(v, dict):
                ps = []
                for dk, dv in v.items():
                    if isinstance(dv, str):
                        ps.append(f'{dk} = "{dv}"')
                    else:
                        ps.append(f'{dk} = {dv}')
                lines.append(f'{k} = {{ {", ".join(ps)} }}')

        lines.append("\n[native]")
        incs = ", ".join(f'"{i}"' for i in self.native.get("includes", []))
        links = ", ".join(f'"{l}"' for l in self.native.get("links", []))
        lines.append(f'includes = [{incs}]')
        lines.append(f'links = [{links}]')

        lines.append("\n[build]")
        lines.append(f'opt_level = {self.build.get("opt_level", 2)}')
        lines.append(f'output_type = "{self.build.get("output_type", "exe")}"')
        if self.build.get("output_name"):
            lines.append(f'output_name = "{self.build["output_name"]}"')

        with open(target, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")


class NyxLock:
    @staticmethod
    def generate(manifest: NyxManifest, lock_file: str = "nyx.lock"):
        v = manifest.package.get("version", "0.1.0")
        t = manifest.package.get("target", "cpp")
        lines = [
            "# Auto-generated lockfile for nyx package manager",
            "# Manual modifications will be overwritten",
            f'manifest_version = "{v}"',
            f'target = "{t}"',
            ""
        ]
        lines.append("[resolved_dependencies]")
        for dep, ver in manifest.dependencies.items():
            if isinstance(ver, str):
                lines.append(f'{dep} = "{ver}"')
            elif isinstance(ver, dict):
                lines.append(f'{dep} = "{ver.get("version", "unknown")}"')

        with open(lock_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")


# Alias for backward compatibility
Manifest = NyxManifest
