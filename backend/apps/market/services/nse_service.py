import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class NSEService:
    def __init__(self):
        self.session = requests.Session()
        self.headers = settings.NSE_HEADERS
        self.initialized = False

    def _initialize_session(self):
        """NSE requires a session from the main page first to set cookies."""
        try:
            self.session.get(settings.NSE_SESSION_URL, headers=self.headers, timeout=10)
            self.initialized = True
            logger.info("NSE session initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize NSE session: {e}")
            self.initialized = False

    def fetch_oi_spurts(self):
        """Fetch real-time OI spurts data from NSE."""
        if not self.initialized:
            self._initialize_session()

        if not self.initialized:
            return []

        try:
            response = self.session.get(settings.NSE_DATA_URL, headers=self.headers, timeout=10)
            if response.status_code == 401: # Session expired
                logger.warning("NSE session expired during OI fetch, re-initializing...")
                self._initialize_session()
                response = self.session.get(settings.NSE_DATA_URL, headers=self.headers, timeout=10)

            response.raise_for_status()
            data = response.json().get("data", [])
            logger.info(f"Fetched {len(data)} stocks from NSE OI Spurts")
            return data
        except Exception as e:
            logger.error(f"Error fetching NSE OI data: {e}")
            return []

    def fetch_fo_securities(self):
        """Fetch the full list of F&O securities with prices."""
        if not self.initialized:
            self._initialize_session()

        if not self.initialized:
            return []

        url = "https://www.nseindia.com/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O"
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            if response.status_code == 401:
                logger.warning("NSE session expired during FO fetch, re-initializing...")
                self._initialize_session()
                response = self.session.get(url, headers=self.headers, timeout=10)

            response.raise_for_status()
            data = response.json().get("data", [])
            # Skip the first item if it's the index itself (usually "NIFTY 50" etc.)
            stocks = [item for item in data if item.get("symbol") != "NIFTY 50" and item.get("symbol") != "NIFTY IT"]
            logger.info(f"Fetched {len(stocks)} stocks from NSE F&O Securities")
            return stocks
        except Exception as e:
            logger.error(f"Error fetching NSE FO Securities data: {e}")
            return []

# Singleton instance
nse_service = NSEService()
