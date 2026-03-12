# 🚀 FO Monitor - Project Startup Guide

## Quick Start (One Command)

### Option 1: Using the Batch Script
```bash
cd c:\Users\Saura\Desktop\stockmarket
.\START_PROJECT.bat
```

This will automatically:
1. Install dependencies
2. Run migrations
3. Start backend on `http://localhost:8000`
4. Start frontend on `http://localhost:5173`

---

## Manual Startup (Two Separate Terminals)

### Terminal 1 - Backend (Django)
```bash
cd c:\Users\Saura\Desktop\stockmarket\backend
python manage.py migrate
python manage.py runserver
```

**Backend runs on**: `http://localhost:8000`

**API Docs**: `http://localhost:8000/api/schema/`

---

### Terminal 2 - Frontend (Vite)
```bash
cd c:\Users\Saura\Desktop\stockmarket\frontend
npm install  # Only first time
npm run dev
```

**Frontend runs on**: `http://localhost:5173`

---

## Access URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:5173 | React UI Dashboard |
| **Backend API** | http://localhost:8000 | Django REST API |
| **API Documentation** | http://localhost:8000/api/schema/ | API Endpoints |
| **Admin Panel** | http://localhost:8000/admin | Django Admin (credentials: admin/admin) |

---

## What's Running

### Backend (Django + Daphne)
- REST API endpoints
- WebSocket support
- JWT authentication
- Database migrations
- Background tasks (Celery)

### Frontend (React + Vite)
- Dashboard with real-time updates
- WebSocket connections
- JWT token management
- Market data visualization

---

## Troubleshooting

### Port Already in Use
If port 8000 or 5173 is in use:

**For Backend:**
```bash
python manage.py runserver 8001
```

**For Frontend:**
```bash
npm run dev -- --port 5174
```

### Missing Dependencies
```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend
cd frontend && npm install
```

### Database Issues
```bash
cd backend
python manage.py migrate --run-syncdb
python manage.py createsuperuser  # Create admin user
```

### Port in Use (Find and Kill)
```bash
# Find process on port 8000
netstat -ano | findstr :8000

# Kill by PID
taskkill /PID <PID> /F
```

---

## Project Structure

```
stockmarket/
├── frontend/          # React + Vite
│   ├── src/
│   │   ├── pages/    # Page components
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── store/    # Zustand state
│   │   └── api/      # Axios client
│   └── package.json
├── backend/           # Django
│   ├── config/       # Settings
│   ├── apps/         # Django apps
│   ├── manage.py
│   └── requirements.txt
├── docker-compose.yml
└── nginx.conf
```

---

## Next Steps

1. ✅ Start both servers
2. Open `http://localhost:5173` in browser
3. Register a new account
4. Login with credentials
5. View market data and set up alerts

**Enjoy! 🎉**
