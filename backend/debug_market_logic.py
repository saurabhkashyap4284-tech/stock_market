import os
import django
import sys
from datetime import datetime

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")
django.setup()

from django.conf import settings
from apps.market.tasks import fetch_and_broadcast
from apps.market.models import OISnapshot, Stock

def debug():
    print(f"USE_MOCK_DATA: {settings.USE_MOCK_DATA}")
    print(f"Initial Snapshots: {OISnapshot.objects.count()}")
    print(f"Initial Stocks: {Stock.objects.count()}")
    
    print("\nRunning fetch_and_broadcast()...")
    try:
        fetch_and_broadcast()
        print("Task completed.")
    except Exception as e:
        print(f"Task failed with error: {e}")
        import traceback
        traceback.print_exc()

    print(f"\nFinal Snapshots: {OISnapshot.objects.count()}")
    print(f"Final Stocks: {Stock.objects.count()}")
    
    if OISnapshot.objects.exists():
        last = OISnapshot.objects.last()
        print(f"Last Snapshot Stock: {last.stock.symbol}, LTP: {last.ltp}")

if __name__ == "__main__":
    debug()
