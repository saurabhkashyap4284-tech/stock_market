@echo off
REM FO Monitor Project Startup Script

title FO Monitor - Full Stack Startup
color 0A

echo.
echo ================================
echo FO Monitor - Full Stack Startup
echo ================================
echo.

REM Backend Setup
echo [1/3] Installing Backend Dependencies...
cd "%~dp0backend"
pip install -q django==4.2.7 djangorestframework==3.14.0 celery==5.3.4 redis==5.0.1 psycopg2-binary==2.9.9 djangorestframework-simplejwt==5.3.0 django-cors-headers==4.3.1 python-dotenv==1.0.0 requests==2.31.0 pandas==2.1.3 daphne==3.0.2 channels==3.0.5

if not exist ".env" (
    echo Creating .env file...
    (
        echo DEBUG=True
        echo SECRET_KEY=your-secret-key-here-change-in-production
        echo ALLOWED_HOSTS=localhost,127.0.0.1
        echo DB_ENGINE=django.db.backends.sqlite3
        echo DB_NAME=db.sqlite3
        echo REDIS_URL=redis://localhost:6379/0
        echo JWT_SECRET_KEY=your-jwt-secret-key
        echo NIFTY_SYMBOL=^NSEI
        echo SENSEX_SYMBOL=^BSESN
    ) > .env
    echo .env created
)

REM Frontend Setup
echo [2/3] Installing Frontend Dependencies...
cd "%~dp0frontend"

if not exist "node_modules" (
    echo Installing npm packages...
    call npm install
)

if not exist ".env" (
    echo Creating frontend .env file...
    (
        echo VITE_API_URL=http://localhost:8000
        echo VITE_WS_URL=ws://localhost:8000/ws
    ) > .env
    echo Frontend .env created
)

REM Database Setup
echo [3/3] Running Database Migrations...
cd "%~dp0backend"
python manage.py migrate --no-input

echo.
echo ================================
echo Starting Project Servers...
echo ================================
echo.
echo Frontend:  http://localhost:5173
echo Backend:   http://localhost:8000
echo API Docs:  http://localhost:8000/api/schema/
echo.

REM Start Backend
echo Starting Django Backend...
start cmd /k "cd "%~dp0backend" && python manage.py runserver"

REM Start Frontend  
echo Starting Vite Frontend...
timeout /t 3 /nobreak
start cmd /k "cd "%~dp0frontend" && npm run dev"

echo.
echo All servers started! Opening browser...
timeout /t 5 /nobreak
start http://localhost:5173

pause
