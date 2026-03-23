from apps.market.tasks import fetch_and_broadcast
try:
    fetch_and_broadcast()
    print("SUCCESS")
except Exception as e:
    import traceback
    traceback.print_exc()
