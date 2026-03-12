# FO Monitor - Quick Start Guide

## 🚀 5-Minute Setup

### Option 1: Docker (Recommended)
```bash
cd stockmarket
docker-compose up -d
```
Open browser:
- Frontend: http://localhost:3000
- Admin: http://localhost:8000/admin

### Option 2: Manual Setup

#### Backend
```bash
cd backend

# Setup Python env
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install + migrate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser

# Run 3 terminals:
# Terminal 1:
python manage.py runserver

# Terminal 2:
celery -A config worker -l info

# Terminal 3:
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

#### Frontend
```bash
cd ../frontend

npm install
npm run dev
```

## Default Credentials

**Admin Panel**
- URL: http://localhost:8000/admin
- User: (create via `createsuperuser`)

**Test User** (create via register page)
- Email: test@example.com
- Password: Test@123

## Key Files to Customize

1. **Backend Configuration**
   - `backend/.env` - Database, Redis, email settings
   - `backend/config/settings/base.py` - Django settings

2. **Frontend Configuration**
   - `frontend/.env` - API & WebSocket URLs
   - `frontend/src/utils/index.js` - Signal colors, constants

3. **Real Market Data**
   - `backend/apps/market/services/data_fetcher.py` - Replace mock data with real API

## Testing the System

### 1. Register a User
```
POST http://localhost:8000/api/users/register/
{
  "email": "trader@example.com",
  "password": "SecurePass123",
  "password2": "SecurePass123",
  "phone": "9999999999"
}
```

### 2. Get JWT Token
```
POST http://localhost:8000/api/auth/login/
{
  "email": "trader@example.com",
  "password": "SecurePass123"
}
```

### 3. Test Market Data Endpoint
```
GET http://localhost:8000/api/market/live/
Headers: Authorization: Bearer <access_token>
```

### 4. Test WebSocket
```javascript
// In browser console
const ws = new WebSocket(
  'ws://localhost:8000/ws/market/?token=' + accessToken
);
ws.onmessage = (event) => {
  console.log('Market update:', JSON.parse(event.data));
};
```

### 5. Check Market Phase
```
GET http://localhost:8000/api/market/phase/
```

## Database Queries (for debugging)

```bash
# Enter Django shell
python manage.py shell

# View latest signals
from apps.signals_log.models import SignalEvent
from django.utils import timezone

SignalEvent.objects.filter(
    created_at__date=timezone.now().date()
).values('signal_type').annotate(count=Count('id'))

# View stocks
from apps.market.models import Stock
Stock.objects.filter(is_active=True).values('symbol')

# Check user watchlists
from apps.users.models import Watchlist
Watchlist.objects.filter(user__email='trader@example.com')
```

## Common Issues & Solutions

### Issue: WebSocket Connection Refused
**Solution**: Ensure backend is running and Redis is active
```bash
redis-cli ping  # Should return PONG
```

### Issue: Database Error
**Solution**: Check PostgreSQL connection
```bash
psql -h localhost -U postgres -d fo_monitor  # Test connection
python manage.py migrate  # Re-run migrations
```

### Issue: CORS Error
**Solution**: Update `CORS_ALLOWED_ORIGINS` in `backend/config/settings/base.py`

### Issue: Celery Tasks Not Running
**Solution**: Check if beat scheduler is running
```bash
# Verify in Django admin:
# Settings → Periodic Tasks
# Should see 4 tasks configured
```

## Market Hours (IST)

- **PRE**: Before 9:15 AM (no trading)
- **CANDLE**: 9:15-9:20 AM (candle building)
- **WATCH**: 9:20-9:30 AM ⭐ (hottest signals)
- **OPEN**: 9:30 AM-3:30 PM (normal trading)
- **CLOSED**: After 3:30 PM

## Signal Types

| Signal | Meaning | Strength |
|--------|---------|----------|
| **BEARISH** | Price below prev_close + OI up | STRONG |
| **BEARISH_TRAP** | Dead-cat bounce setup | STRONG/MODERATE |
| **BEARISH_ZONE** | Potential reversal zone | WATCH |
| **BULLISH** | Price above prev_close + OI up | STRONG |
| **BULLISH_PULLBACK** | Healthy pullback setup | STRONG/MODERATE |
| **BULLISH_ZONE** | Potential support zone | WATCH |
| **NEUTRAL** | No clear setup | - |

## Next Steps

1. **Configure Real Market Data**
   - Update MARKET_API_URL and MARKET_API_KEY in `.env`
   - Modify `data_fetcher.py` to call your API

2. **Setup Email Notifications**
   - Add SMTP credentials to `.env`
   - Test via Django admin

3. **Deploy to Production**
   - Use Gunicorn + Nginx
   - Enable HTTPS/SSL
   - Setup monitoring (Sentry, DataDog, etc.)

4. **Optimize for Trading**
   - Add technical indicators
   - Implement position tracking
   - Add risk management features

## Support

For issues or questions:
- Check logs: `docker-compose logs backend`
- Debug Celery: `celery -A config inspect active`
- Django debug toolbar: Install `django-debug-toolbar`

---

**Happy Trading! 📈**
