# FO Monitor Project Startup Script
# Starts both backend and frontend servers simultaneously

Write-Host "================================" -ForegroundColor Cyan
Write-Host "FO Monitor - Full Stack Startup" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Get the project root directory
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $projectRoot "backend"
$frontendDir = Join-Path $projectRoot "frontend"

Write-Host "Project Root: $projectRoot" -ForegroundColor Yellow
Write-Host ""

# ==================== Backend Setup ====================
Write-Host "[1/4] Starting Django Backend..." -ForegroundColor Cyan
Write-Host "Location: $backendDir" -ForegroundColor Gray

# Check if .env exists
$envFile = Join-Path $backendDir ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    @"
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-jwt-secret-key

# Market Data
NIFTY_SYMBOL=^NSEI
SENSEX_SYMBOL=^BSESN
"@ | Set-Content $envFile
    Write-Host "Created .env file" -ForegroundColor Green
}

# ==================== Frontend Setup ====================
Write-Host ""
Write-Host "[2/4] Setting up Frontend dependencies..." -ForegroundColor Cyan
Write-Host "Location: $frontendDir" -ForegroundColor Gray

# Check if node_modules exists
$nodeModules = Join-Path $frontendDir "node_modules"
if (-not (Test-Path $nodeModules)) {
    Write-Host "Installing npm packages..." -ForegroundColor Yellow
    Push-Location $frontendDir
    npm install
    Pop-Location
    Write-Host "npm packages installed" -ForegroundColor Green
} else {
    Write-Host "npm packages already installed" -ForegroundColor Green
}

# Check if .env exists for frontend
$frontendEnv = Join-Path $frontendDir ".env"
if (-not (Test-Path $frontendEnv)) {
    Write-Host "Creating frontend .env file..." -ForegroundColor Yellow
    @"
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
"@ | Set-Content $frontendEnv
    Write-Host "Created frontend .env file" -ForegroundColor Green
}

# ==================== Database Setup ====================
Write-Host ""
Write-Host "[3/4] Preparing Database..." -ForegroundColor Cyan

Push-Location $backendDir
Write-Host "Running migrations..." -ForegroundColor Yellow
python manage.py migrate
Pop-Location

Write-Host ""
Write-Host "[4/4] Starting Servers..." -ForegroundColor Cyan
Write-Host ""

# Start Backend in a new PowerShell window
Write-Host "▶ Starting Django Backend on http://localhost:8000" -ForegroundColor Green
$backendScript = @"
cd '$backendDir'
Write-Host 'Backend running on http://localhost:8000' -ForegroundColor Green
python manage.py runserver 0.0.0.0:8000
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript

# Start Frontend in a new PowerShell window
Write-Host "▶ Starting Vite Frontend on http://localhost:5173" -ForegroundColor Green
$frontendScript = @"
cd '$frontendDir'
Write-Host 'Frontend running on http://localhost:5173' -ForegroundColor Green
npm run dev
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✓ Project Started Successfully!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Yellow
Write-Host "  Frontend:  http://localhost:5173" -ForegroundColor Green
Write-Host "  Backend:   http://localhost:8000" -ForegroundColor Green
Write-Host "  API Docs:  http://localhost:8000/api/schema/" -ForegroundColor Green
Write-Host ""
Write-Host "Close this window to stop the startup process" -ForegroundColor Gray
Write-Host ""
