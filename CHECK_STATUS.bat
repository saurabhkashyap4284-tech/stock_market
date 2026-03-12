@echo off
REM Check if FO Monitor servers are running

setlocal enabledelayedexpansion
echo.
echo ====================================
echo FO Monitor - Server Status Check
echo ====================================
echo.

REM Check Backend (Port 8000)
echo [1/2] Checking Backend (Port 8000)...
netstat -ano | findstr :8000 >nul
if %errorlevel% equ 0 (
    echo ✓ Backend is RUNNING on http://localhost:8000
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
        echo   Process ID: %%a
    )
) else (
    echo ✗ Backend is NOT RUNNING
    echo   Start it with: cd backend ^&^& python manage.py runserver
)

echo.

REM Check Frontend (Port 5173)
echo [2/2] Checking Frontend (Port 5173)...
netstat -ano | findstr :5173 >nul
if %errorlevel% equ 0 (
    echo ✓ Frontend is RUNNING on http://localhost:5173
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173') do (
        echo   Process ID: %%a
    )
) else (
    echo ✗ Frontend is NOT RUNNING
    echo   Start it with: cd frontend ^&^& npm run dev
)

echo.
echo ====================================
echo Summary:
echo ====================================
echo.

REM Final check - are both running?
netstat -ano | findstr :8000 >nul
set backend_status=%errorlevel%

netstat -ano | findstr :5173 >nul
set frontend_status=%errorlevel%

if %backend_status% equ 0 if %frontend_status% equ 0 (
    echo ✓ ✓ BOTH SERVERS ARE RUNNING! 
    echo.
    echo Access your project:
    echo   Frontend:  http://localhost:5173
    echo   Backend:   http://localhost:8000
    echo.
) else (
    echo ✗ One or more servers are NOT running
    echo.
    echo To start all servers:
    echo   1. Run: RUN.bat
    echo   OR
    echo   2. Manually start in separate terminals:
    echo      Terminal 1: cd backend ^&^& python manage.py runserver
    echo      Terminal 2: cd frontend ^&^& npm run dev
    echo.
)

pause
