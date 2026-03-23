import os
import django
import sys

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")
django.setup()

def test_imports():
    try:
        print("Importing logging...")
        import logging
        print("OK")
        
        print("Importing celery...")
        from celery import shared_task
        print("OK")
        
        print("Importing asgiref...")
        from asgiref.sync import async_to_sync
        print("OK")
        
        print("Importing channels...")
        from channels.layers import get_channel_layer
        print("OK")
        
        print("Importing redis_client...")
        from utils.redis_client import set_stock
        print("OK")
        
        print("Importing signal_engine...")
        from apps.market.services.signal_engine import classify_signal
        print("OK")
        
        print("Importing data_fetcher...")
        from apps.market.services.data_fetcher import fetch_market_data
        print("OK")
        
        print("Importing tasks...")
        import apps.market.tasks
        print("OK")
    except Exception as e:
        print(f"FAILED with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_imports()
