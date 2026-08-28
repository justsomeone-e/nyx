# nyx Official Windows Installer
$ErrorActionPreference = "Stop"

Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "Installing nyx Core Toolchain (v3.0.0 Beta 1)..." -ForegroundColor Cyan
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

# 2. Copy source tree to ~/.nyx
$CurrentRoot = $PSScriptRoot
if ($CurrentRoot -and (Test-Path (Join-Path $CurrentRoot "src"))) {
    Copy-Item -Path (Join-Path $CurrentRoot "src\*") -Destination $SrcDir -Recurse -Force
}

# 3. Check for Python
$PythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $PythonExe) {
    Write-Host "[!] Warning: Python 3.10+ is required to run nyx." -ForegroundColor Yellow
    Write-Host "    Install via winget: winget install Python.Python.3.12" -ForegroundColor Yellow
} else {
    Write-Host "[OK] Found Python: $PythonExe" -ForegroundColor Green
}

# 4. Create nyx.bat and he.bat wrappers in bin directory
$SrcCli = Join-Path $InstallDir "src\cli.py"
$BatContent = "@echo off`r`npython `"$SrcCli`" %*"
Set-Content -Path (Join-Path $BinDir "nyx.bat") -Value $BatContent -Encoding ASCII
Set-Content -Path (Join-Path $BinDir "he.bat") -Value $BatContent -Encoding ASCII

# 5. Add BinDir to User PATH if not present
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if (-not $UserPath) {
    $UserPath = ""
}
if ($UserPath -notlike "*$BinDir*") {
    $NewPath = if ($UserPath.Length -gt 0) { "$UserPath;$BinDir" } else { $BinDir }
    [Environment]::SetEnvironmentVariable("Path", $NewPath, "User")
    Write-Host "[OK] Added $BinDir to User PATH." -ForegroundColor Green
} else {
    Write-Host "[OK] $BinDir already present in User PATH." -ForegroundColor Green
}

Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "[OK] nyx installed successfully!" -ForegroundColor Green
Write-Host "     Restart your terminal and run 'nyx doctor' to verify setup." -ForegroundColor Green
Write-Host "===================================================================" -ForegroundColor Cyan
