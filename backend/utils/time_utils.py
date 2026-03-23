from datetime import date
import pytz

IST = pytz.timezone("Asia/Kolkata")

# NSE Holidays 2025 (Hardcoded for now - example list)
NSE_HOLIDAYS_2025 = [
    date(2025, 1, 26),  # Republic Day
    date(2025, 2, 26),  # Mahashivratri
    date(2025, 3, 14),  # Holi
    date(2025, 3, 31),  # Id-ul-Fitr
    date(2025, 4, 10),  # Shri Mahavir Jayanti
    date(2025, 4, 14),  # Dr. Baba Saheb Ambedkar Jayanti
    date(2025, 4, 18),  # Good Friday
    date(2025, 5, 1),   # Maharashtra Day
    date(2025, 8, 15),  # Independence Day
    date(2025, 10, 2),  # Mahatma Gandhi Jayanti
    date(2025, 10, 20), # Diwali (Laxmi Pujan)
    date(2025, 12, 25), # Christmas
]

def is_market_holiday(today: date = None) -> bool:
    if today is None:
        from datetime import datetime
        today = datetime.now(IST).date()
    return today in NSE_HOLIDAYS_2025
