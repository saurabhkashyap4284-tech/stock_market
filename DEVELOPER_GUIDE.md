# FO Monitor - Developer Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                         │
│  Vite Dev Server (3000) → API Routes (8000) & WebSocket (8000)  │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP + WebSocket
┌────────────────────────────▼────────────────────────────────────┐
│                       BACKEND (Django)                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ REST API Views + WebSocket Consumer                       │ │
│  └───────────────┬──────────────────────────────┬────────────┘ │
│                  │ Read/Write                   │ Real-time    │
│  ┌───────────────▼───────────┐  ┌──────────────▼──────────┐   │
│  │   PostgreSQL Database      │  │   Redis Cache + Pub/Sub │   │
│  │  ┌─ Stock                  │  │  ┌─ Current tick data   │   │
│  │  ├─ OISnapshot             │  │  ├─ Latest signals      │   │
│  │  ├─ Candle5Min             │  │  ├─ Candle snapshots    │   │
│  │  ├─ SignalEvent            │  │  └─ Market phase       │   │
│  │  ├─ AlertRule              │  │                         │   │
│  │  ├─ AlertLog               │  └─────────────────────────┘   │
│  │  ├─ CustomUser             │                                │
│  │  └─ Watchlist              │                                │
│  └────────────────────────────┘                                │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Celery Tasks (Background Jobs)              │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │ Every 30 seconds:                                   │ │  │
│  │  │  1. fetch_and_broadcast                            │ │  │
│  │  │     ├─ Fetch market data (real API or mock)        │ │  │
│  │  │     ├─ Update candles in Redis                     │ │  │
│  │  │     ├─ Run signal engine                           │ │  │
│  │  │     ├─ Check alert rules                           │ │  │
│  │  │     └─ Broadcast to WebSocket                      │ │  │
│  │  │                                                     │ │  │
│  │  │  2. Daily at 9:20 AM: build_5min_candle()          │ │  │
│  │  │  3. During WATCH phase: run_signal_engine()        │ │  │
│  │  │  4. Every 30s: check_and_fire_alerts()             │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Frontend Architecture

### State Management Flow
```
User Action (UI Click) 
    ↓
Zustand Store Action (useAuthStore, useMarketStore, useAlertsStore)
    ↓
API Call (via api/index.js with JWT)
    ↓
Backend Response
    ↓
Update Store State
    ↓
Re-render Components
```

### WebSocket Data Flow
```
User connects → Frontend useWebSocket hook
    ↓
WebSocket to /ws/market/
    ↓
Backend sends initial_state
    ↓
Frontend updates useMarketStore
    ↓
Every 30s: Backend broadcasts market_update
    ↓
Frontend updates store
    ↓
Components re-render (via Zustand subscription)
```

### Folder Structure Philosophy
- `api/` - External communication (HTTP)
- `hooks/` - Custom React hooks (logic reuse)
- `store/` - Global state (Zustand)
- `components/` - Reusable UI pieces
- `pages/` - Full page components (route-based)
- `utils/` - Formatters, constants, helpers

## Backend Architecture

### Request Lifecycle
```
Request comes in
    ↓
Django Middleware (CORS, Auth, etc.)
    ↓
URL Routing (config/urls.py)
    ↓
View Handler (APIView or ViewSet)
    ↓
Permission Check (IsAuthenticated, etc.)
    ↓
Serializer Validation
    ↓
Database Query / Redis Read
    ↓
Response Serialization
    ↓
HTTP Response to Frontend
```

### WebSocket Lifecycle
```
Frontend connects to ws://localhost:8000/ws/market/?token=JWT
    ↓
Django Channels Consumer (MarketConsumer.connect)
    ↓
Auth check (token validation)
    ↓
Join Redis group (market_data)
    ↓
Send initial_state to client
    ↓
Listen for group messages (from Celery)
    ↓
Broadcast to all connected clients
```

### Celery Task Flow
```
Beat Scheduler triggers task (every 30s)
    ↓
Task runs in worker process
    ↓
fetch_and_broadcast():
    ├─ Fetch market data
    ├─ Save to Redis
    ├─ Run signal engine
    ├─ Check alerts
    └─ Broadcast via channels layer
        ↓
    WebSocket consumer receives
        ↓
    Sends to all connected clients
```

## Adding New Features

### Adding a New API Endpoint

**Example: GET /api/market/trending/**

1. **Create View** (`backend/apps/market/views.py`)
```python
class TrendingStocksView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get top 5 stocks by volume
        trending = (
            Stock.objects
            .filter(is_active=True)
            .annotate(vol_24h=...)
            .order_by('-vol_24h')[:5]
        )
        return Response(StockSerializer(trending, many=True).data)
```

2. **Add URL** (`backend/apps/market/urls.py`)
```python
path("trending/", views.TrendingStocksView.as_view(), name="trending"),
```

3. **Call from Frontend** (`frontend/src/api/index.js`)
```javascript
trending: () => api.get('/market/trending/'),
```

4. **Use in Component**
```javascript
import { apiClient } from '../api';

const { data: trending } = await apiClient.marketAPI.trending();
```

### Adding a New Celery Task

**Example: Daily report generation**

1. **Create Task** (`backend/apps/market/tasks.py`)
```python
@shared_task(name="apps.market.tasks.generate_daily_report")
def generate_daily_report():
    """Generate daily summary report"""
    from apps.signals_log.models import SignalEvent
    from django.utils import timezone
    
    today = timezone.now().date()
    signals = SignalEvent.objects.filter(date=today)
    
    report = {
        'date': today,
        'total_signals': signals.count(),
        'by_type': signals.values('signal_type').annotate(count=Count('id'))
    }
    
    # Save or send report
    return report
```

2. **Register in Beat Schedule** (`backend/config/celery.py`)
```python
app.conf.beat_schedule = {
    # ... existing tasks ...
    
    "daily-report": {
        "task": "apps.market.tasks.generate_daily_report",
        "schedule": crontab(hour=16, minute=0),  # 4 PM
    },
}
```

### Adding a New Component

**Example: Signal statistics card**

1. **Create Component** (`frontend/src/components/dashboard/SignalStats.jsx`)
```javascript
export function SignalStats() {
  const getCounts = useMarketStore(state => state.getCounts);
  const counts = getCounts();
  
  return (
    <div className="card">
      <h3>Today's Statistics</h3>
      <div className="stats-grid">
        <Stat label="Total" value={counts.total} color="#e2e8f0" />
        <Stat label="Bullish" value={counts.bullish} color="#10b981" />
        <Stat label="Bearish" value={counts.bearish} color="#ef4444" />
      </div>
    </div>
  );
}
```

2. **Use in Dashboard** (`frontend/src/pages/DashboardPage.jsx`)
```javascript
import { SignalStats } from '../components/dashboard/SignalStats';

export default function DashboardPage() {
  return (
    <>
      <Header />
      <SignalStats />
      <StockTable />
      <AlertToasts />
    </>
  );
}
```

### Adding a Signal Detection Pattern

**Example: Volume breakout signal**

1. **Update Signal Engine** (`backend/apps/market/services/signal_engine.py`)
```python
def classify_signal(stock: dict, candle5: dict, phase: str) -> dict:
    # ... existing checks ...
    
    # Volume breakout check
    volume = stock.get('volume', 0)
    avg_volume = 1000000  # Your average
    
    if volume > avg_volume * 1.5:
        return {
            "signal": "VOLUME_BREAKOUT",
            "strength": "STRONG" if volume > avg_volume * 2 else "MODERATE",
            "reason": f"Volume {volume} exceeds average {avg_volume}"
        }
```

2. **Update Signal Types** (`frontend/src/utils/index.js`)
```javascript
export const SIGNAL_META = {
    VOLUME_BREAKOUT: {
        color: "#6366f1",
        bg: "bg-indigo-950",
        border: "border-indigo-700",
        icon: "📊",
        label: "Vol. Breakout",
    },
    // ... rest of signals ...
};
```

## Debugging Tips

### Frontend Debugging
```javascript
// Check Zustand store
console.log(useMarketStore.getState());

// WebSocket messages
ws.onmessage = (e) => console.log('WS:', e.data);

// API calls
// Network tab in DevTools or Axios interceptor logging
```

### Backend Debugging
```python
# Django shell exploration
python manage.py shell

# Check Redis
redis-cli
> KEYS *
> GET stock:RELIANCE

# Celery task inspection
celery -A config inspect active
celery -A config inspect registered

# Django debug SQL
# Add to settings: LOGGING = { 'django.db.backends': { 'level': 'DEBUG' } }
```

### WebSocket Debugging
```python
# Add logging to MarketConsumer
import logging
logger = logging.getLogger(__name__)

async def receive(self, text_data):
    logger.info(f"Received: {text_data}")
    # ... rest of method

# Check Redis Pub/Sub
redis-cli PSUBSCRIBE '*'
```

## Performance Optimization Tips

### Database Queries
```python
# Bad: N+1 problem
stocks = Stock.objects.all()
for stock in stocks:
    print(stock.latest_signal.signal_type)

# Good: Use select_related
stocks = Stock.objects.select_related('latest_signal').all()
```

### WebSocket Messages
```python
# Bad: Send everything
broadcast_payload = {
    'stocks': all_stocks_with_all_fields
}

# Good: Send only changed fields
broadcast_payload = {
    'stocks': [{
        'symbol': stock['symbol'],
        'ltp': stock['ltp'],
        'signal': stock['signal'],
    }]
}
```

### Redis Usage
```python
# Cache complex queries
from django.core.cache import cache

def get_signal_summary():
    key = f"signal_summary:{date}"
    summary = cache.get(key)
    if not summary:
        summary = expensive_query()
        cache.set(key, summary, timeout=3600)
    return summary
```

## Testing Strategy

### Frontend Unit Tests
```javascript
import { render, screen } from '@testing-library/react';
import { SignalBadge } from './SignalBadge';

test('renders bearish badge with correct color', () => {
  render(<SignalBadge signal="BEARISH" />);
  expect(screen.getByRole('badge')).toHaveClass('bg-red-950');
});
```

### Backend Unit Tests
```python
from django.test import TestCase
from apps.market.services.signal_engine import classify_signal

class SignalEngineTestCase(TestCase):
    def test_bearish_detection(self):
        stock = {
            'prev_close': 100,
            'ltp': 95,
            'oi': 1000,
            'oi_prev': 900,
        }
        candle = {
            'open': 95,
            'high': 97,
            'low': 92,
            'close': 96,
        }
        
        signal = classify_signal(stock, candle, 'WATCH')
        self.assertEqual(signal['signal'], 'BEARISH')
        self.assertEqual(signal['strength'], 'STRONG')
```

### API Tests
```python
from rest_framework.test import APITestCase
from rest_framework.test import APIClient

class MarketAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Create test data
        
    def test_live_snapshot_returns_stocks(self):
        response = self.client.get('/api/market/live/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('stocks', response.data)
```

## Deployment Checklist

- [ ] Change Django SECRET_KEY
- [ ] Set DEBUG = False
- [ ] Configure ALLOWED_HOSTS
- [ ] Setup SSL/HTTPS
- [ ] Configure database backups
- [ ] Setup monitoring (Sentry, DataDog)
- [ ] Enable rate limiting
- [ ] Configure CDN for static files
- [ ] Setup log aggregation
- [ ] Configure alert notifications
- [ ] Load testing
- [ ] Security audit

## Useful Commands

```bash
# Backend
python manage.py runserver                    # Dev server
python manage.py shell                       # Django shell
python manage.py makemigrations              # Create migrations
python manage.py migrate                     # Apply migrations
python manage.py createsuperuser             # Admin user
python manage.py collectstatic              # Collect static files
celery -A config worker -l info             # Celery worker
celery -A config beat -l info               # Beat scheduler

# Frontend
npm run dev                                  # Dev server
npm run build                               # Production build
npm run preview                             # Preview build
npm run lint                                # Linting

# Docker
docker-compose up -d                        # Start all services
docker-compose down                         # Stop all services
docker-compose logs -f backend              # View backend logs
docker exec <container> <command>           # Run command in container
```

## Common Patterns

### Creating a Custom Management Command
```python
# backend/apps/market/management/commands/populate_stocks.py
from django.core.management.base import BaseCommand
from apps.market.models import Stock

class Command(BaseCommand):
    def handle(self, *args, **options):
        stocks = [
            {'symbol': 'RELIANCE', 'name': 'Reliance', 'is_index': False},
            # ... more stocks
        ]
        Stock.objects.bulk_create([Stock(**s) for s in stocks])
        self.stdout.write("Stocks created!")
```

Run with: `python manage.py populate_stocks`

### Middleware for Logging Requests
```python
# backend/config/middleware.py
import logging
logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        logger.info(f"{request.method} {request.path}")
        response = self.get_response(request)
        logger.info(f"Status: {response.status_code}")
        return response
```

## Resources

- [Django Docs](https://docs.djangoproject.com/)
- [DRF Docs](https://www.django-rest-framework.org/)
- [Channels Docs](https://channels.readthedocs.io/)
- [Celery Docs](https://docs.celeryproject.org/)
- [React Docs](https://react.dev/)
- [WebSocket MDN](https://developer.mozilla.org/docs/Web/API/WebSocket)

---

**Happy coding! 🚀**
