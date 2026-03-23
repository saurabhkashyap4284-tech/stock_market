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
pip install -q django==4.2.7 djangorestframework==3.14.0 celery==5.3.4 redis==5.0.1 psycopg2-binary==2.9.9 djangorestframework-simplejwt==5.3.0 django-cors-headers==4.3.1 python-dotenv==1.0.0 requests==2.31.0 pandas==2.1.3 daphne==3.0.2 channels==3.0.5 channels-redis==4.1.0 PyJWT==2.8.0

if not exist ".env" (
    echo Creating .env file...
    (
        echo DEBUG=True
        echo SECRET_KEY=your-secret-key-here-change-in-production
        echo ALLOWED_HOSTS=127.0.0.1,localhost
        echo DB_ENGINE=django.db.backends.sqlite3
        echo DB_NAME=db.sqlite3
        echo REDIS_URL=redis://127.0.0.1:6379/0
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
        echo VITE_API_URL=http://127.0.0.1:8000
        echo VITE_WS_URL=ws://127.0.0.1:8000/ws/market/
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
start "Django Server" cmd /k "cd "%~dp0backend" && python manage.py runserver"

REM Start Celery
echo Starting Celery Worker...
start "Celery Worker" cmd /k "cd "%~dp0backend" && celery -A config worker --loglevel=info -P solo"
echo Starting Celery Beat...
start "Celery Beat" cmd /k "cd "%~dp0backend" && celery -A config beat --loglevel=info"

REM Start Frontend  
echo Starting Vite Frontend...
timeout /t 5 /nobreak
start "Vite Frontend" cmd /k "cd "%~dp0frontend" && npm run dev"

echo.
echo All servers started! Opening browser in 10 seconds...
timeout /t 10 /nobreak
start http://127.0.0.1:5173

pause
