# FO Monitor - Options Market Signals

Real-time options market monitoring with AI-powered signal detection for NSE F&O.

## Features

- **Real-time Market Data**: WebSocket-based live updates every 30 seconds
- **Signal Detection**: Bearish, Bullish, Traps, and Zone breakouts
- **Market Phase Detection**: PRE, CANDLE BUILDING, WATCH WINDOW, OPEN
- **Alert System**: Custom price and signal alerts with email/app notifications
- **Watchlists**: Create and manage custom watchlists
- **Signal History**: Complete audit trail of all signals
- **Dashboard**: Live signal counters and market phase indicators

## Tech Stack

### Backend
- **Framework**: Django 4.2 + DRF
- **Real-time**: Django Channels + Redis
- **Task Queue**: Celery
- **Database**: PostgreSQL
- **API**: RESTful + WebSocket

### Frontend
- **Framework**: React 18
- **State**: Zustand
- **Routing**: React Router
- **HTTP**: Axios with JWT auth
- **Build**: Vite

## Setup

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 15
- Redis 7

### Quick Start with Docker

```bash
# Clone and navigate
cd fo-monitor

# Configure environment
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Build and run
docker-compose up -d

# Create superuser
docker-compose exec django python manage.py createsuperuser

# Apply migrations
docker-compose exec django python manage.py migrate
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/

### Manual Setup

**Backend**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
celery -A config worker -l info
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### Auth
- `POST /api/auth/login/` - Login
- `POST /api/auth/refresh/` - Refresh token
- `POST /api/users/register/` - Register

### Market
- `GET /api/market/live/` - Live snapshot
- `GET /api/market/stocks/` - All stocks
- `GET /api/market/phase/` - Current market phase
- `GET /api/market/candles/` - 5-min candles
- `GET /api/market/oi-history/` - OI history

### Signals
- `GET /api/signals/history/` - Signal history
- `GET /api/signals/summary/` - Signal counts
- `GET /api/signals/timeline/{symbol}/` - Stock timeline

### Alerts
- `GET /api/alerts/rules/` - Alert rules
- `POST /api/alerts/rules/` - Create alert
- `DELETE /api/alerts/rules/{id}/` - Delete alert

### Users
- `GET /api/users/profile/` - User profile
- `GET /api/users/watchlists/` - Watchlists
- `POST /api/users/watchlists/` - Create watchlist

## WebSocket

Connect to: `ws://localhost:8000/ws/market/?token={access_token}`

**Message Types**:
- `initial_state` - Full market snapshot on connect
- `market_update` - Live tick every 30 seconds

## Project Structure

```
fo-monitor/
├── backend/                    # Django project
│   ├── config/                 # Settings
│   ├── apps/market/            # Core logic
│   ├── apps/signals_log/       # Signal history
│   ├── apps/alerts/            # Alert system
│   ├── apps/users/             # Auth & profiles
│   └── manage.py
├── frontend/                   # React app
│   ├── src/
│   │   ├── api/                # API client
│   │   ├── hooks/              # Custom hooks
│   │   ├── store/              # Zustand stores
│   │   ├── components/         # React components
│   │   ├── pages/              # Page components
│   │   └── App.jsx
│   └── package.json
└── docker-compose.yml
```

## Signals Explained

| Signal | Meaning | Color |
|--------|---------|-------|
| **BEARISH** | Strongly bearish setup | 🔴 Red |
| **BEARISH_TRAP** | False bearish break | 🪤 Orange |
| **BEARISH_ZONE** | Potential reversal zone | ⚠️ Amber |
| **BULLISH** | Strongly bullish setup | 🟢 Green |
| **BULLISH_PULLBACK** | Pullback in uptrend | 🎯 Cyan |
| **BULLISH_ZONE** | Potential breakout zone | 👀 Gold |

## Contributing

1. Fork the repo
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

## License

MIT License - see LICENSE file

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Email: support@fomonitor.dev

---

**Disclaimer**: This tool is for educational and analysis purposes only. Always conduct your own research before trading. Past signals do not guarantee future results.
