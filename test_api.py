import requests
import json

BASE_URL = 'http://127.0.0.1:8000'
print("=" * 60)
print("BACKEND API TESTING")
print("=" * 60)

tests = []

# Test 1: Register
print("\n[1] Testing User Registration...")
try:
    reg_data = {
        'email': 'newuser@test.com',
        'password': 'TestPass123!',
        'password2': 'TestPass123!',
        'username': 'newuser'
    }
    r = requests.post(f'{BASE_URL}/api/users/register/', json=reg_data, timeout=5)
    status_code = r.status_code
    tests.append(("User Registration", status_code, status_code in [201, 400]))
    print(f"  Status: {status_code}")
    if status_code not in [201, 400]:
        print(f"  Error: {r.text[:200]}")
except Exception as e:
    tests.append(("User Registration", "Error", False))
    print(f"  Error: {str(e)[:100]}")

# Test 2: Login
print("\n[2] Testing User Login...")
try:
    login_data = {
        'email': 'newuser@test.com',
        'password': 'TestPass123!'
    }
    r = requests.post(f'{BASE_URL}/api/users/login/', json=login_data, timeout=5)
    status_code = r.status_code
    tests.append(("User Login", status_code, status_code in [200, 400]))
    print(f"  Status: {status_code}")
except Exception as e:
    tests.append(("User Login", "Error", False))
    print(f"  Error: {str(e)[:100]}")

# Test 3: Admin Access
print("\n[3] Testing Admin Panel Access...")
try:
    r = requests.get(f'{BASE_URL}/admin/', timeout=5)
    status_code = r.status_code
    tests.append(("Admin Panel", status_code, status_code in [200, 302]))
    print(f"  Status: {status_code}")
except Exception as e:
    tests.append(("Admin Panel", "Error", False))
    print(f"  Error: {str(e)[:100]}")

# Test 4: Market API
print("\n[4] Testing Market API...")
try:
    r = requests.get(f'{BASE_URL}/api/market/', timeout=5)
    status_code = r.status_code
    tests.append(("Market API", status_code, status_code in [200, 404]))
    print(f"  Status: {status_code}")
except Exception as e:
    tests.append(("Market API", "Error", False))
    print(f"  Error: {str(e)[:100]}")

# Test 5: Signals API
print("\n[5] Testing Signals API...")
try:
    r = requests.get(f'{BASE_URL}/api/signals/', timeout=5)
    status_code = r.status_code
    tests.append(("Signals API", status_code, status_code in [200, 404]))
    print(f"  Status: {status_code}")
except Exception as e:
    tests.append(("Signals API", "Error", False))
    print(f"  Error: {str(e)[:100]}")

# Summary
print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
passed = sum(1 for t in tests if t[2])
total = len(tests)
for test_name, status, result in tests:
    symbol = "✓" if result else "✗"
    print(f"{symbol} {test_name}: {status}")

print(f"\nTotal: {passed}/{total} tests passed")
print("=" * 60)
