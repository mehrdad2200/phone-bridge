@echo off
rem Builds dist\PhoneBridge\PhoneBridge.exe (folder build) with PyInstaller.
rem NOTE: PyQt6 is GPLv3 — read docs\dev\release.md before you redistribute the result.
setlocal
cd /d "%~dp0.."
set "PY=py"
where py >nul 2>nul || set "PY=python"
%PY% -m pip install -r requirements.txt pyinstaller || exit /b 1
%PY% -m PyInstaller --noconfirm --clean --windowed --name PhoneBridge --icon assets\icon.ico phone_bridge.py || exit /b 1
echo.
echo Done: dist\PhoneBridge\PhoneBridge.exe
