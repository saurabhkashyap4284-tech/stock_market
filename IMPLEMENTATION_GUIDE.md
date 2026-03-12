# FO Monitor - Complete Project Implementation Guide

## Project Overview

**FO Monitor** is a real-time options market monitoring platform designed for NSE F&O (Futures & Options) traders. It provides AI-powered signal detection, real-time price updates, and intelligent alert management.

### Key Features
- ✅ Real-time WebSocket market data streaming
- ✅ AI signal detection (bearish/bullish patterns)
- ✅ User authentication with JWT tokens
- ✅ Custom watchlists and alert rules
- ✅ 30-second market data refresh with Celery
- ✅ Multi-phase market detection (PRE, CANDLE, WATCH, OPEN, CLOSED)
- ✅ 5-minute candle building and pattern analysis
- ✅ Email notification support for alerts
- ✅ PostgreSQL + Redis backend for performance

## Tech Stack

### Frontend
- **React 18.2.0** - UI framework
- **Vite 5.0.0** - Build tool with HMR
- **Zustand 4.4.7** - State management (auth, market, alerts)
- **Axios 1.6.2** - HTTP client with JWT interceptors
- **React Router 6.20.0** - Client-side routing
- **WebSocket API** - Real-time updates

### Backend
- **Django 4.2.7** - Web framework
- **Django REST Framework 3.14.0** - REST API
- **Django Channels 4.0.0** - WebSocket support
- **Celery 5.3.4** - Task queue with beat scheduler
- **PostgreSQL** - Primary database
- **Redis 5.0.1** - Cache & message broker
- **SimpleJWT 5.3.0** - JWT authentication

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Reverse proxy

## Project Structure

```
stockmarket/
├── frontend/                       # React Vite application
│   ├── src/
│   │   ├── api/index.js            # API client with JWT interceptors
│   │   ├── hooks/
│   │   │   ├── useAuth.js          # Authentication operations
│   │   │   └── useWebSocket.js     # WebSocket real-time connection
│   │   ├── store/index.js          # Zustand stores (auth, market, alerts)
│   │   ├── utils/index.js          # Formatters, constants, metadata
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Header.jsx      # Top navigation with phase indicator
│   │   │   │   └── AlertToasts.jsx # Toast notification system
│   │   │   ├── table/
│   │   │   │   ├── SignalBadge.jsx # Signal type color indicator
│   │   │   │   └── StockTable.jsx  # Main data table with tabs/filters
│   │   │   ├── dashboard/
│   │   │   │   └── DashboardWidgets.jsx # Signal count cards
│   │   │   └── auth/
│   │   │       └── ProtectedRoute.jsx # Route guard
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx       # User login form
│   │   │   ├── RegisterPage.jsx    # User registration
│   │   │   ├── DashboardPage.jsx   # Main monitoring dashboard
│   │   │   ├── SignalsPage.jsx     # Signal history table
│   │   │   ├── AlertsPage.jsx      # Alert rule management
│   │   │   └── WatchlistPage.jsx   # Watchlist CRUD
│   │   ├── App.jsx                 # Main router component
│   │   ├── main.jsx                # React entry point
│   │   └── index.css               # Global styles (dark theme)
│   ├── index.html                  # HTML template
│   ├── vite.config.js              # Vite configuration
│   ├── package.json                # Dependencies
│   ├── .env                        # API & WebSocket URLs
│   ├── Dockerfile                  # Frontend Docker image
│   └── nginx.conf                  # Nginx reverse proxy config
│
└── backend/                        # Django application
    ├── config/
    │   ├── settings/
    │   │   └── base.py             # Django settings (DB, Cache, JWT, Channels, Celery)
    │   ├── asgi.py                 # ASGI app for WebSocket
    │   ├── wsgi.py                 # WSGI app for HTTP
    │   ├── urls.py                 # Main URL router
    │   └── celery.py               # Celery configuration with periodic tasks
    ├── apps/
    │   ├── market/
    │   │   ├── models.py           # Stock, OISnapshot, Candle5Min models
    │   │   ├── serializers.py      # API serializers
    │   │   ├── views.py            # REST API endpoints (6 views)
    │   │   ├── urls.py             # Market URL patterns
    │   │   ├── consumers.py        # WebSocket consumer
    │   │   ├── routing.py          # WebSocket URL patterns
    │   │   ├── tasks.py            # Celery periodic tasks
    │   │   └── services/
    │   │       ├── __init__.py     # Redis client singleton
    │   │       ├── phase_detector.py     # Market phase detection (IST-based)
    │   │       ├── signal_engine.py      # Signal classification logic
    │   │       ├── data_fetcher.py       # API/mock market data fetch
    │   │       └── candle_builder.py     # 5-min candle OHLC building
    │   ├── signals_log/
    │   │   ├── models.py           # SignalEvent model
    │   │   ├── serializers.py      # Signal serializers
    │   │   ├── views.py            # Signal REST endpoints
    │   │   ├── urls.py             # Signal URL patterns
    │   │   └── __init__.py
    │   ├── alerts/
    │   │   ├── models.py           # AlertRule, AlertLog models
    │   │   ├── serializers.py      # Alert serializers
    │   │   ├── views.py            # Alert REST endpoints
    │   │   ├── urls.py             # Alert URL patterns
    │   │   ├── tasks.py            # Alert firing task
    │   │   └── __init__.py
    │   └── users/
    │       ├── models.py           # CustomUser, Watchlist models
    │       ├── serializers.py      # User serializers
    │       ├── views.py            # User REST endpoints
    │       ├── urls.py             # User URL patterns
    │       ├── admin.py            # Admin configuration
    │       └── __init__.py
    ├── manage.py                   # Django management script
    ├── requirements.txt            # Python dependencies
    ├── .env.example                # Environment variables template
    ├── Dockerfile                  # Backend Docker image
    └── docker-compose.yml          # Multi-container orchestration
```

## Database Models

### Market App
```
Stock
  - symbol (unique)
  - name
  - is_index
  - is_active
  - created_at

OISnapshot (Open Interest history every 30s)
  - stock (FK)
  - timestamp
  - date
  - prev_close
  - ltp
  - open, high, low
  - oi_current, oi_previous, oi_change%
  - volume

Candle5Min (5-minute OHLC)
  - stock (FK)
  - date (unique with stock)
  - open, high, low, close
  - prev_close
  - all_below_prev_close (computed)
  - all_above_prev_close (computed)
```

### Signals Log App
```
SignalEvent
  - stock (FK)
  - date
  - signal_type (BEARISH, BEARISH_TRAP, BEARISH_ZONE, BULLISH, BULLISH_PULLBACK, BULLISH_ZONE, NEUTRAL)
  - strength (STRONG, MODERATE, WATCH)
  - reason (text explanation)
  - ltp
  - phase (PRE, CANDLE, WATCH, OPEN)
  - created_at
```

### Alerts App
```
AlertRule
  - user (FK)
  - stock (FK, nullable - for all symbols)
  - signal_type
  - only_strong (boolean)
  - via_email (boolean)
  - is_active
  - created_at

AlertLog (sent alerts audit trail)
  - user (FK)
  - rule (FK)
  - stock (FK)
  - signal_type
  - strength
  - ltp
  - sent_at
  - delivered
```

### Users App
```
CustomUser (extends AbstractUser)
  - email (unique, login field)
  - username
  - phone
  - created_at

Watchlist
  - user (FK)
  - name
  - symbols (JSONField array)
  - created_at
  - updated_at
```

## API Endpoints

### Authentication
```
POST   /api/auth/login/        → Get access + refresh tokens
POST   /api/auth/refresh/      → Refresh access token
POST   /api/users/register/    → Register new user
```

### Market Data
```
GET    /api/market/live/                  → All stocks real-time
GET    /api/market/live/<symbol>/         → Single stock detail
GET    /api/market/stocks/                → List all active stocks
GET    /api/market/oi-history/?symbol=X   → OI historical snapshots
GET    /api/market/candles/?date=Y        → 5-min candles with filters
GET    /api/market/phase/                 → Current market phase
```

### Signals
```
GET    /api/signals/history/?date=Y&symbol=X  → Signal history
GET    /api/signals/summary/?date=Y           → Signal count summary
GET    /api/signals/timeline/<symbol>/?date=Y → Stock signal timeline
```

### Alerts
```
GET    /api/alerts/rules/                     → User's alert rules
POST   /api/alerts/rules/                     → Create new rule
GET    /api/alerts/rules/<id>/                → Rule detail
PUT    /api/alerts/rules/<id>/                → Update rule
DELETE /api/alerts/rules/<id>/                → Delete rule
POST   /api/alerts/rules/<id>/toggle/         → Toggle active status
GET    /api/alerts/logs/                      → Alert firing history
```

### Users
```
GET    /api/users/profile/                    → Current user profile
PUT    /api/users/profile/                    → Update profile
GET    /api/users/watchlists/                 → User's watchlists
POST   /api/users/watchlists/                 → Create watchlist
GET    /api/users/watchlists/<id>/            → Watchlist detail
PUT    /api/users/watchlists/<id>/            → Update watchlist
DELETE /api/users/watchlists/<id>/            → Delete watchlist
POST   /api/users/watchlists/<id>/add/        → Add symbol to watchlist
POST   /api/users/watchlists/<id>/remove/     → Remove symbol from watchlist
```

### WebSocket
```
ws://localhost:8000/ws/market/?token=<jwt>
├── Connects authenticated user to live market stream
├── Receives: initial_state (on connect)
├── Receives: market_update (every 30 seconds)
└── Sends: ping (keep-alive)
```

## Signal Detection Logic

### Bearish Setup
- All 4 candle points (O, H, L, C) below prev_close
- OI increased = fresh shorts entering
- If LTP in Open→High zone = dead-cat bounce (BEARISH_TRAP)

### Bullish Setup (mirror)
- All 4 candle points (O, H, L, C) above prev_close
- OI increased = fresh longs entering
- If LTP in Low→Open zone = healthy pullback (BULLISH_PULLBACK)

### Signal Strengths
- **STRONG**: Pattern confirmed + OI increased
- **MODERATE**: Pattern confirmed but OI unchanged
- **WATCH**: Partial pattern or watch-list signal

### Market Phases (IST Time)
- **PRE**: Before 9:15 AM (no trading)
- **CANDLE**: 9:15-9:20 AM (5-min candle building)
- **WATCH**: 9:20-9:30 AM (hottest signal window)
- **OPEN**: 9:30 AM-3:30 PM (main trading hours)
- **CLOSED**: After 3:30 PM (market closed)

## Celery Periodic Tasks

### Every 30 seconds (during market hours)
```
fetch_and_broadcast
├── Fetch market data (real API or mock)
├── Update candle OHLC in Redis
├── Classify signal via signal engine
└── Broadcast to WebSocket subscribers

check_and_fire_alerts
├── Check all active alert rules
├── Match against latest signals
└── Send notifications (toast + optional email)
```

### Once daily at 9:20 AM
```
build_5min_candle
├── Build official 5-min candle snapshot
└── Save to PostgreSQL for history
```

### Every 30 seconds (during WATCH phase)
```
run_signal_engine
├── Run advanced signal classification
└── Update signal strength levels
```

## Redis Cache Schema

```
stock:<symbol>              → Hash of current tick data
candle:<symbol>:<date>      → Hash of 5-min OHLC
signal:<symbol>:<date>      → Hash of latest signal
market:phase                → Current market phase string
market:updates              → Pub/Sub channel for WebSocket broadcast
```

## Setup & Installation

### Prerequisites
- Python 3.10+
- PostgreSQL 13+
- Redis 6+
- Node.js 18+ (for frontend)
- Docker & Docker Compose (optional)

### Backend Setup

1. **Clone and navigate to backend:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Create database:**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser (admin):**
```bash
python manage.py createsuperuser
```

7. **Run development server:**
```bash
# Terminal 1: Django dev server
python manage.py runserver

# Terminal 2: Celery worker
celery -A config worker -l info

# Terminal 3: Celery beat (periodic tasks)
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Frontend Setup

1. **Navigate to frontend:**
```bash
cd ../frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Create .env file:**
```bash
cat > .env << EOF
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws/market/
EOF
```

4. **Run development server:**
```bash
npm run dev
```

Access at: http://localhost:5173

## Docker Deployment

```bash
cd stockmarket
docker-compose up -d
```

Services will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Backend Admin: http://localhost:8000/admin
- Nginx: http://localhost

## Project Completion Status

### ✅ Completed Components
- [x] Frontend React application (18+ components)
- [x] Frontend API client with JWT authentication
- [x] Frontend Zustand state management
- [x] Frontend WebSocket real-time connection
- [x] Frontend protected routes & authentication
- [x] Backend Django models (8 models)
- [x] Backend REST API views (15+ endpoints)
- [x] Backend serializers with computed fields
- [x] Backend service layer (signal engine, phase detection, data fetcher)
- [x] Backend Celery periodic tasks
- [x] Backend WebSocket consumer & routing
- [x] Backend JWT authentication
- [x] PostgreSQL database schema
- [x] Redis cache integration
- [x] Docker & Docker Compose configuration
- [x] CORS & security middleware

### ⏳ Recommended Next Steps
1. **Setup real market data API** - Replace mock data in `data_fetcher.py`
2. **Email notification configuration** - Update `.env` with SMTP credentials
3. **Admin dashboard** - Add signal/alert management in Django admin
4. **Advanced monitoring** - Add Grafana/Prometheus for metrics
5. **Mobile app** - React Native version for on-the-go monitoring
6. **Machine learning** - Add ML-based signal confidence scoring
7. **Production deployment** - AWS/DigitalOcean/GCP setup
8. **Load testing** - Test with real trading volume

## Performance Considerations

- **Redis caching**: Current tick data, latest signals, phase (very fast)
- **Celery tasks**: Non-blocking, 30-second update frequency
- **WebSocket batching**: Updates grouped per 30-second cycle
- **Database indexing**: On date, symbol, signal_type fields
- **PostgreSQL connection pooling**: Via pgBouncer (optional)

## Security Notes

⚠️ **Before Production:**
1. Change `SECRET_KEY` to random value
2. Set `DEBUG = False`
3. Configure `ALLOWED_HOSTS` properly
4. Use HTTPS for all endpoints
5. Implement rate limiting on APIs
6. Add request validation & sanitization
7. Store API keys in environment variables
8. Enable Django security middleware features
9. Use strong database passwords
10. Implement CSRF tokens for state-changing operations

## Troubleshooting

**WebSocket Connection Fails**
- Check if backend is running: `http://localhost:8000`
- Verify Redis is running: `redis-cli ping`
- Check browser console for JWT token

**Celery Tasks Not Running**
- Verify Redis broker: `redis-cli`
- Check Celery worker logs
- Ensure Django settings are correct

**Database Migrations Failed**
- Ensure PostgreSQL is running
- Check DB credentials in `.env`
- Run: `python manage.py migrate --fake-initial` (if needed)

**CORS Errors**
- Check `CORS_ALLOWED_ORIGINS` in settings
- Verify frontend URL matches exactly

## Support & Documentation

- Django Documentation: https://docs.djangoproject.com
- Django REST Framework: https://www.django-rest-framework.org
- Channels Documentation: https://channels.readthedocs.io
- Celery Documentation: https://docs.celeryproject.org
- React Documentation: https://react.dev
- WebSocket API: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket

---

**Project Created**: 2026-03-09
**Status**: Production Ready (with config updates)
**Last Updated**: Project Completion Guide
