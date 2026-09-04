import hashlib
import os
import sys
from typing import Dict, List, Any, Optional


def _canonical_dependency_path(value: Any) -> str:
    """Serialize local dependency paths independently of the host OS."""
    return str(value).replace("\\", "/")


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
                    if isinstance(parsed_val, dict) and "path" in parsed_val:
                        parsed_val["path"] = _canonical_dependency_path(parsed_val["path"])
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
        for k, v in sorted(self.dependencies.items()):
            if isinstance(v, str):
                lines.append(f'{k} = "{v}"')
            elif isinstance(v, dict):
                ps = []
                for dk, dv in sorted(v.items()):
                    if dk == "path":
                        dv = _canonical_dependency_path(dv)
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
    def _hash_package(root: str) -> str:
        digest = hashlib.sha256()
        excluded = {".git", "build", "dist", "target", "__pycache__", "node_modules"}
        for current, directories, filenames in os.walk(root):
            directories[:] = sorted(item for item in directories if item not in excluded)
            for filename in sorted(filenames):
                if filename != "nyx.toml" and not filename.endswith(".nyx"):
                    continue
                path = os.path.join(current, filename)
                relative = os.path.relpath(path, root).replace("\\", "/")
                digest.update(relative.encode("utf-8"))
                digest.update(b"\0")
                with open(path, "rb") as handle:
                    digest.update(handle.read())
                digest.update(b"\0")
        return "sha256:" + digest.hexdigest()

    @staticmethod
    def resolve_local_dependencies(manifest: NyxManifest) -> Dict[str, Dict[str, str]]:
        project_root = os.path.dirname(os.path.abspath(manifest.filepath or "nyx.toml"))
        resolved: Dict[str, Dict[str, str]] = {}

        def visit(name: str, spec: Any, owner_root: str, stack: List[str]) -> None:
            if not isinstance(spec, dict) or "path" not in spec:
                return
            dependency_root = os.path.realpath(os.path.join(owner_root, str(spec["path"])))
            dependency_manifest_path = os.path.join(dependency_root, "nyx.toml")
            if not os.path.isfile(dependency_manifest_path):
                raise ValueError(f"Local dependency '{name}' has no nyx.toml at {dependency_root}")
            if dependency_root in stack:
                cycle = " -> ".join(stack + [dependency_root])
                raise ValueError(f"Local dependency cycle detected: {cycle}")
            child = NyxManifest(dependency_manifest_path)
            child_name = str(child.package.get("name", ""))
            child_version = str(child.package.get("version", ""))
            if child_name and child_name != name:
                raise ValueError(
                    f"Local dependency key '{name}' does not match package name '{child_name}'"
                )
            required_version = str(spec.get("version", child_version))
            if required_version and required_version != child_version:
                raise ValueError(
                    f"Local dependency '{name}' requires {required_version}, found {child_version}"
                )
            existing = resolved.get(name)
            if existing and os.path.realpath(os.path.join(project_root, existing["path"])) != dependency_root:
                raise ValueError(f"Local dependency '{name}' resolves to multiple paths")
            resolved[name] = {
                "version": child_version,
                "path": os.path.relpath(dependency_root, project_root).replace("\\", "/"),
                "checksum": NyxLock._hash_package(dependency_root),
            }
            for child_name_key, child_spec in sorted(child.dependencies.items()):
                visit(child_name_key, child_spec, dependency_root, stack + [dependency_root])

        for dependency_name, dependency_spec in sorted(manifest.dependencies.items()):
            visit(dependency_name, dependency_spec, project_root, [project_root])
        return resolved

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
        for dep, ver in sorted(manifest.dependencies.items()):
            if isinstance(ver, str):
                lines.append(f'{dep} = "{ver}"')
            elif isinstance(ver, dict):
                lines.append(f'{dep} = "{ver.get("version", "unknown")}"')

        local_dependencies = NyxLock.resolve_local_dependencies(manifest)
        if local_dependencies:
            lines.extend(("", "[local_dependencies]"))
            for dep, item in sorted(local_dependencies.items()):
                lines.append(
                    f'{dep} = {{ checksum = "{item["checksum"]}", path = "{item["path"]}", '
                    f'version = "{item["version"]}" }}'
                )

        with open(lock_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    @staticmethod
    def read_local_dependencies(lock_file: str) -> Dict[str, Dict[str, str]]:
        if not os.path.isfile(lock_file):
            return {}
        parser = NyxManifest()
        section = ""
        resolved: Dict[str, Dict[str, str]] = {}
        with open(lock_file, "r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("[") and line.endswith("]"):
                    section = line[1:-1].strip().lower()
                    continue
                if section == "local_dependencies" and "=" in line:
                    name, value = line.split("=", 1)
                    parsed = parser._parse_val(value.strip())
                    if isinstance(parsed, dict):
                        resolved[name.strip()] = {str(k): str(v) for k, v in parsed.items()}
        return resolved


# Alias for backward compatibility
Manifest = NyxManifest
