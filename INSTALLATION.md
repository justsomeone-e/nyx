# 📦 HolyEasyLang Installation Guide

This guide walks you through installing and configuring HolyEasyLang across Windows, Linux, and macOS.

---

## 1. Prerequisites

HolyEasyLang core requires **Python 3.10+**. 
To compile native executables (`hecpp`), a modern C++20 compiler (`clang++` or `g++`) is recommended.

| Platform | Recommended Toolchain | Quick Install Command |
| :--- | :--- | :--- |
| **Windows** | LLVM Clang or LLVM-MinGW | `winget install LLVM.LLVM` or `winget install MartinStorsjo.LLVM-MinGW.UCRT` |
| **Ubuntu / Debian** | Clang 16+ or GCC 12+ | `sudo apt update && sudo apt install -y clang nodejs` |
| **Fedora / RHEL** | Clang or GCC | `sudo dnf install -y clang nodejs` |
| **macOS** | Apple Clang (Xcode CLI) | `xcode-select --install` or `brew install llvm` |

---

## 2. Automated Installation

### Windows (PowerShell)
Run in an elevated or standard PowerShell terminal:
```powershell
irm https://raw.githubusercontent.com/holyeasy/holyeasylang/main/install.ps1 | iex
```
This clones/downloads the toolchain to `~/.holyeasy` and appends `~/.holyeasy/bin` to your User `PATH`.

### Linux / macOS (Bash)
```bash
curl -fsSL https://raw.githubusercontent.com/holyeasy/holyeasylang/main/install.sh | bash
```

---

## 3. Manual Installation (From Source)

1. Clone the repository:
   ```bash
   git clone https://github.com/holyeasy/holyeasylang.git
   cd holyeasylang
   ```

2. Verify host diagnostics:
   * **Windows**:
     ```powershell
     .\he.bat doctor
     ```
   * **Linux / macOS**:
     ```bash
     chmod +x bin/he
     ./bin/he doctor
     ```

3. Add HolyEasyLang to your `PATH`:
   * **Windows**: Add `C:\path\to\holyeasylang` to your environment variables.
   * **Linux / macOS**: Add `export PATH="$PATH:/path/to/holyeasylang/bin"` in `~/.bashrc` or `~/.zshrc`.

---

## 4. Verifying Installation

Run:
```bash
he doctor
```
Output should indicate detected compilers and runtimes with green checkmarks `[✓]`.
