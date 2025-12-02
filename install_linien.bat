@echo off
setlocal ENABLEDELAYEDEXPANSION

:: ------------------------------------------------------------
::    LINIEN CLIENT INSTALLATION
:: ------------------------------------------------------------

:: EDIT THIS PATH (Windows-style path required)
set VENV=C:\Users\jeffreyli\Desktop\Ni Lab\linienvenv

:: Check if the virtual environment exists
if not exist "%VENV%\Scripts\python.exe" (
    echo ERROR: Virtual environment not found at:
    echo    %VENV%
    echo.
    echo Make sure the venv is created first. Example:
    echo    python -m venv "%VENV%"
    exit /b 1
)

echo Virtual environment found at:
echo    %VENV%
echo.

set PYTHON="%VENV%\Scripts\python.exe"

:: Install dependent GUI packages
%PYTHON% -m pip install --no-deps -r requirements_gui

if %errorlevel% neq 0 (
    echo ERROR: Failed to install GUI requirements.
    exit /b 1
)

:: Install Linien GUI component
%PYTHON% setup_gui.py install
if %errorlevel% neq 0 (
    echo ERROR installing setup_gui.py
    exit /b 1
)

:: Install Linien client component
%PYTHON% setup_client.py install
if %errorlevel% neq 0 (
    echo ERROR installing setup_client.py
    exit /b 1
)

echo.
echo Linien client installation completed successfully!
echo.

endlocal
exit /b 0
