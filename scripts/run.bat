@echo off
rem Phone Bridge launcher for Windows: installs the two dependencies once, then starts the app.
setlocal
cd /d "%~dp0.."
set "PY=py"
where py >nul 2>nul || set "PY=python"
%PY% -c "import PyQt6, pynput" >nul 2>nul
if errorlevel 1 (
  echo Installing dependencies ^(PyQt6, pynput^) ...
  %PY% -m pip install -r requirements.txt || goto :fail
)
%PY% phone_bridge.py %*
goto :eof
:fail
echo.
echo Could not install the dependencies. Is Python 3.10+ installed and added to PATH?
pause
