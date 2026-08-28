# HolyEasyLang Official Windows Installer
$ErrorActionPreference = "Stop"

Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "⚡ Installing HolyEasyLang Core Toolchain (v2.0.0 Beta 1)..." -ForegroundColor Cyan
Write-Host "===================================================================" -ForegroundColor Cyan

$InstallDir = Join-Path $HOME ".holyeasy"
$BinDir = Join-Path $InstallDir "bin"

# 1. Ensure Install Directory
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}
if (-not (Test-Path $BinDir)) {
    New-Item -ItemType Directory -Path $BinDir -Force | Out-Null
}

# 2. Check for Python
$PythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $PythonExe) {
    Write-Host "[!] Warning: Python 3.10+ is required to run HolyEasyLang." -ForegroundColor Yellow
    Write-Host "    Install via winget: winget install Python.Python.3.12" -ForegroundColor Yellow
} else {
    Write-Host "[✓] Found Python: $PythonExe" -ForegroundColor Green
}

# 3. Create he.bat wrapper in bin directory
$WrapperPath = Join-Path $BinDir "he.bat"
$SrcCli = Join-Path $InstallDir "src" "cli.py"
$BatContent = "@echo off`r`npython `"$SrcCli`" %*"
Set-Content -Path $WrapperPath -Value $BatContent -Encoding ASCII

# 4. Add BinDir to User PATH if not present
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -notlike "*$BinDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$UserPath;$BinDir", "User")
    Write-Host "[✓] Added $BinDir to User PATH." -ForegroundColor Green
}

Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "[✓] HolyEasyLang installed successfully!" -ForegroundColor Green
Write-Host "    Restart your terminal and run 'he doctor' to verify setup." -ForegroundColor Green
Write-Host "===================================================================" -ForegroundColor Cyan
