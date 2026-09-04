@echo off
setlocal
chcp 65001 >nul 2>&1

set "PY_EXE=C:\Users\USER\AppData\Local\Programs\Python\Python312\python.exe"
if not exist "%PY_EXE%" (
    where python >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set "PY_EXE=python"
    ) else (
        echo [ERROR] Python 3.10+ is required to launch Tour of Nyx.
        exit /b 1
    )
)

"%PY_EXE%" "%~dp0tour\tour.py" %*
