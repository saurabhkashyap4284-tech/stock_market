import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.market.services.data_fetcher import fetch_market_data
from django.conf import settings

print(f"USE_MOCK_DATA: {settings.USE_MOCK_DATA}")
print("Fetching real market data (NSE)...")

# Force real API for this test
settings.USE_MOCK_DATA = False

try:
    stocks = fetch_market_data()
    print(f"Successfully fetched {len(stocks)} stocks.")
    
    if stocks:
        print("\nFirst 3 processed stocks:")
        for stock in stocks[:3]:
            print(json.dumps(stock, indent=2))
    else:
        print("No stocks returned.")
        
except Exception as e:
    print(f"Integration test failed: {e}")
    import traceback
    traceback.print_exc()
