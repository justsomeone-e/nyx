# Tour of Nyx PowerShell Launcher
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$preferredPython = 'C:\Users\USER\AppData\Local\Programs\Python\Python312\python.exe'
$python = if (Test-Path -LiteralPath $preferredPython) { $preferredPython } else { (Get-Command python, python3 -ErrorAction SilentlyContinue | Select-Object -First 1).Source }

if (-not $python) {
    Write-Error "Python 3.10+ is required to launch Tour of Nyx."
    exit 1
}

$tourScript = Join-Path $PSScriptRoot "tour\tour.py"
& $python $tourScript @args
exit $LASTEXITCODE
