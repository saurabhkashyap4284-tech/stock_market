#!/bin/bash
# FO Monitor - Simple Startup Script for WSL/Linux

echo "================================"
echo "FO Monitor - Full Stack Startup"
echo "================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found! Install Python first."
    exit 1
fi

# Check Node
if ! command -v node &> /dev/null; then
    echo "Node.js not found! Install Node.js first."
    exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo "Project Root: $PROJECT_ROOT"
echo ""

# Backend Setup
echo "[1/3] Installing Backend Dependencies..."
cd "$BACKEND_DIR"
pip install -q -r requirements.txt 2>/dev/null || pip3 install -q -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=jwt-secret-key-change
NIFTY_SYMBOL=^NSEI
SENSEX_SYMBOL=^BSESN
EOF
    echo ".env created"
fi

# Frontend Setup
echo "[2/3] Installing Frontend Dependencies..."
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    npm install -q
fi

if [ ! -f ".env" ]; then
    echo "Creating frontend .env..."
    cat > .env << EOF
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
EOF
    echo "Frontend .env created"
fi

# Database Setup
echo "[3/3] Running Database Migrations..."
cd "$BACKEND_DIR"
python manage.py migrate --no-input || python3 manage.py migrate --no-input

echo ""
echo "================================"
echo "Starting Project Servers..."
echo "================================"
echo ""
echo "Frontend:  http://localhost:5173"
echo "Backend:   http://localhost:8000"
echo "API Docs:  http://localhost:8000/api/schema/"
echo ""

# Start Backend
echo "Starting Django Backend..."
cd "$BACKEND_DIR"
python manage.py runserver &
BACKEND_PID=$!

# Start Frontend
echo "Starting Vite Frontend..."
sleep 2
cd "$FRONTEND_DIR"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Servers are running!"
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for both
wait
