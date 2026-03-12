@echo off
REM FO Monitor - Ultra Simple Startup
REM Just run this file!

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ====================================
echo FO Monitor - Project Startup
echo ====================================
echo.

REM Kill any existing processes on ports
echo Cleaning up old processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul

echo.
echo Starting servers...
echo.

REM Start backend in new window
echo Starting Backend on http://localhost:8000
start "FO Monitor Backend" cmd /k "cd backend && python manage.py migrate --no-input & python manage.py runserver"

REM Wait a bit
timeout /t 3 /nobreak

REM Start frontend in new window  
echo Starting Frontend on http://localhost:5173
start "FO Monitor Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ====================================
echo Servers started!
echo.
echo Frontend:  http://localhost:5173
echo Backend:   http://localhost:8000
echo API Docs:  http://localhost:8000/api/schema/
echo.
echo Opening Frontend in browser...
echo ====================================
echo.

timeout /t 4 /nobreak
start http://localhost:5173

echo Done! Close this window anytime.
pause
