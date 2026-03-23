import os
import sys
import json
import redis
import django

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")
django.setup()

from utils.redis_client import get_redis

r = get_redis()
phase = r.get("market:phase")
symbols = r.smembers("market:symbols")
candles = r.keys("market:candle5:*")
signals = r.keys("market:signal:*")

print(f"PHASE: {phase}")
print(f"SYMBOLS_COUNT: {len(symbols)}")
print(f"CANDLE_KEYS_COUNT: {len(candles)}")
print(f"SIGNAL_KEYS_COUNT: {len(signals)}")

if len(signals) > 0:
    for sig_key in signals[:5]: # Show first 5
        sig_val = r.get(sig_key)
        print(f"SIGNAL ({sig_key}): {sig_val}")
