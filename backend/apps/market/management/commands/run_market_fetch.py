import time
import logging
from django.core.management.base import BaseCommand
from apps.market.tasks import fetch_and_broadcast

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Hits the market API every 30 seconds (Manual Runner)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting manual market fetch loop (30s)..."))
        self.stdout.write("Press Ctrl+C to stop.")
        
        while True:
            try:
                self.stdout.write(f"Fetching data at {time.strftime('%H:%M:%S')}...")
                fetch_and_broadcast()
                self.stdout.write(self.style.SUCCESS("Fetch and broadcast completed."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error in fetch loop: {e}"))
            
            time.sleep(30)
