import requests
import json
import logging
from datetime import datetime, time
from django.conf import settings
from utils.time_utils import IST

logger = logging.getLogger(__name__)

class HistoricalService:
    """Fetch historical candle data from NSE (e.g. for lazy loading late-comers)."""

    def __init__(self):
        self.session = requests.Session()
        self.headers = settings.NSE_HEADERS
        self.base_url = "https://www.nseindia.com/api/chart-databyindex"

    def _initialize_session(self):
        try:
            self.session.get(settings.NSE_SESSION_URL, headers=self.headers, timeout=10)
            return True
        except Exception as e:
            logger.error(f"Failed to initialize session for HistoricalService: {e}")
            return False

    def fetch_915_candle(self, symbol: str) -> dict | None:
        """
        Symbol ke liye 9:15 to 9:20 ka OHLC fetch karo.
        """
        if not self._initialize_session():
            return None

        # index=SYMBOL&indices=true/false
        # Note: NSE Chart API structure usually: [timestamp, price] pairs
        url = f"{self.base_url}?index={symbol}&indices=false"
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Expected structure: { "grapthData": [[ts, p], [ts, p], ...] }
            # Timestamps are typically milliseconds.
            graph_data = data.get("grapthData", [])
            if not graph_data:
                return None

            # Filter for 9:15 to 9:20
            # Convert IST 9:15 and 9:20 to timestamps for comparison
            # Assuming today's date
            now = datetime.now(IST)
            start_dt = now.replace(hour=9, minute=15, second=0, microsecond=0)
            end_dt   = now.replace(hour=9, minute=20, second=0, microsecond=0)
            
            start_ts = int(start_dt.timestamp() * 1000)
            end_ts   = int(end_dt.timestamp() * 1000)

            relevant_ticks = [p for ts, p in graph_data if start_ts <= ts <= end_ts]
            
            if not relevant_ticks:
                logger.warning(f"No 9:15-9:20 ticks found for {symbol} in historical data")
                return None

            return {
                "open":  relevant_ticks[0],
                "high":  max(relevant_ticks),
                "low":   min(relevant_ticks),
                "close": relevant_ticks[-1]
            }

        except Exception as e:
            logger.error(f"Error fetching historical candle for {symbol}: {e}")
            return None

historical_service = HistoricalService()
