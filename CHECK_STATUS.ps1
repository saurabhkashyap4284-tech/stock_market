#!/usr/bin/env powershell
# Check FO Monitor Server Status

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "FO Monitor - Server Status Check" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check Backend
Write-Host "[1/2] Checking Backend (Port 8000)..." -ForegroundColor Yellow
$backend = netstat -ano | Select-String ":8000"
if ($backend) {
    Write-Host "✓ Backend is RUNNING" -ForegroundColor Green
    Write-Host "   URL: http://localhost:8000" -ForegroundColor Green
    $pid = $backend -split '\s+' | Select-Object -Last 1
    Write-Host "   Process ID: $pid" -ForegroundColor Gray
} else {
    Write-Host "✗ Backend is NOT running" -ForegroundColor Red
}

Write-Host ""

# Check Frontend
Write-Host "[2/2] Checking Frontend (Port 5173)..." -ForegroundColor Yellow
$frontend = netstat -ano | Select-String ":5173"
if ($frontend) {
    Write-Host "✓ Frontend is RUNNING" -ForegroundColor Green
    Write-Host "   URL: http://localhost:5173" -ForegroundColor Green
    $pid = $frontend -split '\s+' | Select-Object -Last 1
    Write-Host "   Process ID: $pid" -ForegroundColor Gray
} else {
    Write-Host "✗ Frontend is NOT running" -ForegroundColor Red
}

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan

if ($backend -and $frontend) {
    Write-Host "✓ BOTH SERVERS ARE RUNNING!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Access your project:" -ForegroundColor Yellow
    Write-Host "  Frontend:  http://localhost:5173" -ForegroundColor Green
    Write-Host "  Backend:   http://localhost:8000" -ForegroundColor Green
    Write-Host "  API Docs:  http://localhost:8000/api/schema/" -ForegroundColor Green
} else {
    Write-Host "✗ Some servers are NOT running" -ForegroundColor Red
    Write-Host ""
    Write-Host "To start servers:" -ForegroundColor Yellow
    Write-Host "  Option 1: Run RUN.bat" -ForegroundColor Green
    Write-Host "  Option 2: Run manually in separate terminals:" -ForegroundColor Green
    Write-Host "    Terminal 1: cd backend; python manage.py runserver" -ForegroundColor Cyan
    Write-Host "    Terminal 2: cd frontend; npm run dev" -ForegroundColor Cyan
}

Write-Host ""
Read-Host "Press Enter to close"
