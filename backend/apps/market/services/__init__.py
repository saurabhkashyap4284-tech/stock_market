"""
Utilities for interacting with Redis cache.
Handles real-time market data storage and retrieval.
"""
import redis
import json
from django.conf import settings
from datetime import datetime


class RedisClient:
    """Singleton Redis connection handler"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=0,
                decode_responses=True
            )
        return cls._instance

    def get_all_symbols(self):
        """Get all active stock symbols from Redis"""
        keys = self.client.keys("stock:*")
        symbols = [key.replace("stock:", "") for key in keys]
        return sorted(symbols)

    def get_stock(self, symbol):
        """Get single stock's current data"""
        data = self.client.hgetall(f"stock:{symbol.upper()}")
        if data:
            # Parse numeric fields
            for key in ['price', 'prev_close', 'open', 'high', 'low', 'oi_current', 'oi_previous', 'volume']:
                if key in data:
                    try:
                        data[key] = float(data[key])
                    except (ValueError, TypeError):
                        pass
            for key in ['oi_change_pct']:
                if key in data:
                    try:
                        data[key] = float(data[key])
                    except (ValueError, TypeError):
                        pass
        return data

    def set_stock(self, symbol, data, ttl=120):
        """Store stock data in Redis with expiry"""
        key = f"stock:{symbol.upper()}"
        self.client.hset(key, mapping=data)
        self.client.expire(key, ttl)

    def get_candle(self, symbol, date):
        """Get 5-min candle for a symbol on a date"""
        data = self.client.hgetall(f"candle:{symbol.upper()}:{date}")
        if data:
            for key in ['open', 'high', 'low', 'close', 'prev_close']:
                if key in data:
                    try:
                        data[key] = float(data[key])
                    except (ValueError, TypeError):
                        pass
        return data

    def set_candle(self, symbol, date, data, ttl=3600):
        """Store candle in Redis"""
        key = f"candle:{symbol.upper()}:{date}"
        self.client.hset(key, mapping=data)
        self.client.expire(key, ttl)

    def get_signal(self, symbol, date):
        """Get latest signal for a symbol on a date"""
        data = self.client.hgetall(f"signal:{symbol.upper()}:{date}")
        if data:
            try:
                data['ltp'] = float(data.get('ltp', 0))
            except (ValueError, TypeError):
                pass
        return data

    def set_signal(self, symbol, date, data, ttl=3600):
        """Store signal in Redis"""
        key = f"signal:{symbol.upper()}:{date}"
        self.client.hset(key, mapping=data)
        self.client.expire(key, ttl)

    def get_phase(self):
        """Get current market phase"""
        return self.client.get("market:phase") or "PRE"

    def set_phase(self, phase):
        """Store market phase"""
        self.client.set("market:phase", phase, ex=3600)

    def publish_market_update(self, data):
        """Publish market update to WebSocket subscribers via Redis Pub/Sub"""
        channel = "market:updates"
        self.client.publish(channel, json.dumps(data))


def get_redis_client():
    """Factory function to get Redis client singleton"""
    return RedisClient()
