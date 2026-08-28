import os
import sys
import subprocess
import shutil
import glob
from typing import Optional, Tuple

class CppToolchain:
    @staticmethod
    def test_compiler_capabilities(compiler_path: str) -> bool:
        """Verifies that the compiler can actually compile and run on the current host architecture."""
        import tempfile
        compiler_name = os.path.basename(compiler_path).lower()
        temp_dir = tempfile.gettempdir()
        probe_cpp = os.path.join(temp_dir, "he_probe.cpp")
        probe_exe = os.path.join(temp_dir, "he_probe.exe")
        
        with open(probe_cpp, "w", encoding="utf-8") as f:
            f.write("#include <iostream>\n#include <string>\nint main(){ std::cout << 42 << std::endl; return 0; }\n")
            
        try:
            if "cl" in compiler_name and "clang" not in compiler_name:
                cmd = [compiler_path, "/std:c++20", "/EHsc", probe_cpp, f"/Fe:{probe_exe}"]
            else:
                cmd = [compiler_path, "-std=c++20", "-static", probe_cpp, "-o", probe_exe]
                
            res = subprocess.run(cmd, capture_output=True, timeout=8)
            if res.returncode != 0:
                return False
                
            if os.path.exists(probe_exe):
                bin_dir = os.path.dirname(compiler_path)
                env = {**os.environ, 'PATH': bin_dir + os.pathsep + os.environ.get('PATH', '')}
                run_res = subprocess.run([probe_exe], capture_output=True, text=True, env=env, timeout=5)
                return run_res.returncode == 0 and "42" in run_res.stdout
            return False
        except Exception:
            return False
        finally:
            if os.path.exists(probe_cpp):
                try: os.remove(probe_cpp)
                except: pass
            if os.path.exists(probe_exe):
                try: os.remove(probe_exe)
                except: pass

    @classmethod
    def find_compiler(cls) -> Optional[str]:
        candidates = []
        
        # 1. PATH (prefer x86_64 or native)
        for c in ('x86_64-w64-mingw32-clang++', 'x86_64-w64-mingw32-g++', 'clang++', 'g++', 'cl', 'gcc'):
            path = shutil.which(c)
            if path and path not in candidates:
                candidates.append(path)

        # 2. WinGet Packages (specifically search x86_64)
        local_app_data = os.environ.get('LOCALAPPDATA', '')
        if local_app_data:
            for pat in ('*clang++*.exe', '*g++*.exe'):
                matches = glob.glob(os.path.join(local_app_data, 'Microsoft', 'WinGet', 'Packages', '**', pat), recursive=True)
                for m in matches:
                    if 'aarch64' not in m and 'arm' not in m and 'i686' not in m and m not in candidates:
                        candidates.append(m)

        # 3. Standard Windows Locations
        fixed_paths = [
            os.path.join(local_app_data, 'Microsoft', 'WinGet', 'Packages', 'MartinStorsjo.LLVM-MinGW.UCRT_Microsoft.Winget.Source_8wekyb3d8bbwe', 'llvm-mingw-20260616-ucrt-x86_64', 'bin', 'clang++.exe'),
            r'C:\msys64\ucrt64\bin\g++.exe',
            r'C:\msys64\mingw64\bin\g++.exe',
            r'C:\MinGW\bin\g++.exe',
            r'C:\Program Files\llvm-mingw\bin\x86_64-w64-mingw32-clang++.exe',
            r'C:\Program Files\LLVM\bin\clang++.exe',
            r'C:\tools\msys64\mingw64\bin\g++.exe',
        ]
        for p in fixed_paths:
            if os.path.exists(p) and p not in candidates:
                candidates.append(p)

        # Validate with active compilation and execution capability probe
        for cand in candidates:
            if cls.test_compiler_capabilities(cand):
                return cand
                
        return None

    @classmethod
    def compile_cpp(cls, cpp_filepath: str, out_exe: Optional[str] = None) -> Tuple[bool, str]:
        compiler = cls.find_compiler()
        if not compiler:
            return False, "No capable C++20 compiler for host architecture found."

        if not out_exe:
            out_exe = os.path.splitext(cpp_filepath)[0] + (".exe" if os.name == 'nt' else "")

        compiler_name = os.path.basename(compiler).lower()
        if "cl" in compiler_name and "clang" not in compiler_name:
            cmd = [compiler, "/std:c++20", "/EHsc", "/O2", cpp_filepath, f"/Fe:{out_exe}"]
        else:
            cmd = [compiler, "-std=c++20", "-static", "-O2", cpp_filepath, "-o", out_exe]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                return True, out_exe
            else:
                return False, f"C++ Compilation Error:\n{res.stderr or res.stdout}"
        except Exception as e:
            return False, f"Failed to execute compiler '{compiler}': {e}"

    @classmethod
    def run_executable(cls, exe_filepath: str) -> Tuple[int, str]:
        compiler = cls.find_compiler()
        env = os.environ.copy()
        if compiler:
            bin_dir = os.path.dirname(compiler)
            env['PATH'] = bin_dir + os.pathsep + env.get('PATH', '')
        try:
            res = subprocess.run([exe_filepath], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env, timeout=10)
            return res.returncode, res.stdout or res.stderr
        except subprocess.TimeoutExpired:
            return -1, "Execution timed out (10s limit)"
        except Exception as e:
            return -1, f"Failed to run executable: {e}"
