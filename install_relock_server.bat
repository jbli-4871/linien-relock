@echo off
setlocal ENABLEDELAYEDEXPANSION

echo ------------------------------------------------------------
echo     LINIEN SERVER DEPLOYMENT STARTED
echo ------------------------------------------------------------
echo.

:: ------------------------------
:: CONFIGURATION (EDIT THESE)
:: ------------------------------
set RP_IP=rp-f0c261.local
set LOCAL_DIR=.\linien\server
set RP_TARGET_DIR=/usr/local/lib/python3.5/dist-packages/linien/server
:: ------------------------------

:: 1. Verify local directory
if not exist "%LOCAL_DIR%" (
    echo ERROR: Local directory "%LOCAL_DIR%" does not exist.
    exit /b 1
)

echo Local directory: %LOCAL_DIR%
echo Remote directory: %RP_TARGET_DIR%
echo.

:: 2. Test passwordless SSH connection
echo Testing SSH connectivity to Red Pitaya (%RP_IP%)...
ssh -o BatchMode=yes root@%RP_IP% "echo test" >nul 2>&1

if %errorlevel% neq 0 (
    echo ERROR: Cannot connect via SSH without password.
    echo You must install your SSH public key on the Red Pitaya.
    exit /b 1
)

echo SSH connection OK.
echo.

:: 3. Copy modified files
echo Copying modified linien_server files to Red Pitaya...
scp -r "%LOCAL_DIR%\*" root@%RP_IP%:%RP_TARGET_DIR%/

if %errorlevel% neq 0 (
    echo ERROR: scp failed. Deployment aborted.
    exit /b 1
)

echo Files copied successfully.
echo.

:: 4. Reboot the Red Pitaya
echo Rebooting Red Pitaya...
ssh root@%RP_IP% "reboot"

if %errorlevel% neq 0 (
    echo ERROR: Failed to reboot Red Pitaya.
    exit /b 1
)

echo Reboot command sent. The device will reboot shortly.
echo.

:: Finished
echo ------------------------------------------------------------
echo     LINIEN SERVER DEPLOYMENT COMPLETE
echo ------------------------------------------------------------
echo.

endlocal
exit /b 0
