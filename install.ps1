# nyx Official Windows Installer
$ErrorActionPreference = "Stop"

Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "Installing nyx Core Toolchain (v3.0.0-beta.5)..." -ForegroundColor Cyan
Write-Host "===================================================================" -ForegroundColor Cyan

$InstallDir = Join-Path $HOME ".nyx"
$BinDir = Join-Path $InstallDir "bin"
$SrcDir = Join-Path $InstallDir "src"

# 1. Create directory structure
if (-not (Test-Path $BinDir)) {
    New-Item -ItemType Directory -Path $BinDir -Force | Out-Null
}
if (-not (Test-Path $SrcDir)) {
    New-Item -ItemType Directory -Path $SrcDir -Force | Out-Null
}

# 2. Populate source tree
$CurrentRoot = $PSScriptRoot
if ($CurrentRoot -and (Test-Path (Join-Path $CurrentRoot "src"))) {
    Write-Host "[*] Copying local files to $InstallDir..." -ForegroundColor Cyan
    Copy-Item -Path (Join-Path $CurrentRoot "src\*") -Destination $SrcDir -Recurse -Force
} else {
    Write-Host "[*] Downloading latest release from GitHub..." -ForegroundColor Cyan
    $ZipUrl = "https://github.com/justsomeone-e/nyx/archive/refs/heads/main.zip"
    $TempZip = Join-Path $env:TEMP "nyx_install.zip"
    $TempExtract = Join-Path $env:TEMP "nyx_extract"
    
    Invoke-WebRequest -Uri $ZipUrl -OutFile $TempZip -UseBasicParsing
    Expand-Archive -Path $TempZip -DestinationPath $TempExtract -Force
    
    $ExtractedSrc = Join-Path $TempExtract "nyx-main\src"
    if (Test-Path $ExtractedSrc) {
        Copy-Item -Path (Join-Path $ExtractedSrc "*") -Destination $SrcDir -Recurse -Force
    }
    Remove-Item -Path $TempZip, $TempExtract -Recurse -Force -ErrorAction SilentlyContinue
}

# Ensure src/__init__.py exists
$InitPy = Join-Path $SrcDir "__init__.py"
if (-not (Test-Path $InitPy)) {
    [System.IO.File]::WriteAllText($InitPy, "# nyx core`n", [System.Text.UTF8Encoding]::new($false))
}

# 3. Check for Python
$PythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $PythonExe) {
    Write-Host "[!] Warning: Python 3.10+ is required to run nyx." -ForegroundColor Yellow
    Write-Host "    Install via winget: winget install Python.Python.3.12" -ForegroundColor Yellow
} else {
    Write-Host "[OK] Found Python: $PythonExe" -ForegroundColor Green
}

# 4. Create robust executable wrappers in bin directory
$SrcCli = Join-Path $SrcDir "cli.py"

# A. PowerShell Wrapper (.ps1)
$Ps1Content = "& python `"$SrcCli`" @args"
Set-Content -Path (Join-Path $BinDir "nyx.ps1") -Value $Ps1Content -Encoding UTF8
Set-Content -Path (Join-Path $BinDir "he.ps1") -Value $Ps1Content -Encoding UTF8

# B. Batch / CMD Wrapper (.bat & .cmd)
$BatContent = "@echo off`r`npython `"$SrcCli`" %*"
Set-Content -Path (Join-Path $BinDir "nyx.bat") -Value $BatContent -Encoding ASCII
Set-Content -Path (Join-Path $BinDir "nyx.cmd") -Value $BatContent -Encoding ASCII
Set-Content -Path (Join-Path $BinDir "he.bat") -Value $BatContent -Encoding ASCII
Set-Content -Path (Join-Path $BinDir "he.cmd") -Value $BatContent -Encoding ASCII

# C. Shell Wrapper (for Git Bash / WSL / MSYS2)
$ShContent = "#!/usr/bin/env bash`nexec python3 `"$SrcCli`" `"`$@`""
Set-Content -Path (Join-Path $BinDir "nyx") -Value $ShContent -Encoding ASCII
Set-Content -Path (Join-Path $BinDir "he") -Value $ShContent -Encoding ASCII

# Copy to common PATH locations for instant availability across existing shells
$ExistingPathTargets = @(
    (Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Links"),
    (Join-Path $env:LOCALAPPDATA "Programs\Python\Python314\Scripts"),
    (Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\Scripts"),
    (Join-Path $env:LOCALAPPDATA "Programs\Python\Python311\Scripts")
)
foreach ($target in $ExistingPathTargets) {
    if (Test-Path $target) {
        Copy-Item -Path (Join-Path $BinDir "nyx.bat") -Destination (Join-Path $target "nyx.bat") -Force
        Copy-Item -Path (Join-Path $BinDir "nyx.cmd") -Destination (Join-Path $target "nyx.cmd") -Force
        Copy-Item -Path (Join-Path $BinDir "nyx.ps1") -Destination (Join-Path $target "nyx.ps1") -Force
        Copy-Item -Path (Join-Path $BinDir "he.bat") -Destination (Join-Path $target "he.bat") -Force
        Copy-Item -Path (Join-Path $BinDir "he.cmd") -Destination (Join-Path $target "he.cmd") -Force
        Copy-Item -Path (Join-Path $BinDir "he.ps1") -Destination (Join-Path $target "he.ps1") -Force
    }
}

# 5. Add BinDir & MinGW to User PATH & Current Session PATH
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if (-not $UserPath) {
    $UserPath = ""
}
if ($UserPath -notlike "*$BinDir*") {
    $UserPath = if ($UserPath.Length -gt 0) { "$UserPath;$BinDir" } else { $BinDir }
    Write-Host "[OK] Added $BinDir to User PATH." -ForegroundColor Green
} else {
    Write-Host "[OK] $BinDir already present in User PATH." -ForegroundColor Green
}

# Check for MinGW toolchain
$MinGWPath = "C:\Users\USER\AppData\Local\Microsoft\WinGet\Packages\MartinStorsjo.LLVM-MinGW.UCRT_Microsoft.Winget.Source_8wekyb3d8bbwe\llvm-mingw-20260616-ucrt-x86_64\bin"
if ((Test-Path $MinGWPath) -and ($UserPath -notlike "*$MinGWPath*")) {
    $UserPath = "$UserPath;$MinGWPath"
    Write-Host "[OK] Added MinGW Toolchain to User PATH: $MinGWPath" -ForegroundColor Green
}

[Environment]::SetEnvironmentVariable("Path", $UserPath, "User")

if ($env:Path -notlike "*$BinDir*") {
    $env:Path = "$BinDir;$env:Path"
}
if ((Test-Path $MinGWPath) -and ($env:Path -notlike "*$MinGWPath*")) {
    $env:Path = "$MinGWPath;$env:Path"
}

# 6. Install / Sync VS Code Extension directly
$VsCodeExtDir = Join-Path $HOME ".vscode\extensions\nyx-lang-support"
$LocalExtDir = Join-Path $CurrentRoot "vscode-extension"
if (Test-Path $LocalExtDir) {
    if (-not (Test-Path $VsCodeExtDir)) {
        New-Item -ItemType Directory -Path $VsCodeExtDir -Force | Out-Null
    }
    Copy-Item -Path (Join-Path $LocalExtDir "*") -Destination $VsCodeExtDir -Recurse -Force
    Write-Host "[OK] Synced nyx VS Code Extension to $VsCodeExtDir" -ForegroundColor Green
}

Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "[OK] nyx installed successfully!" -ForegroundColor Green
Write-Host "     Run 'nyx doctor' or 'nyx --help' to get started." -ForegroundColor Green
Write-Host "===================================================================" -ForegroundColor Cyan