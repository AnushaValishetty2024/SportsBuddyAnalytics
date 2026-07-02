import requests
import json

BASE = 'http://127.0.0.1:5000'

# Step 1: Login to get a session
s = requests.Session()
login_data = {'email': 'anusha@gmail.com', 'password': 'anusha123'}
print("=== LOGIN ===")
r = s.post(f'{BASE}/login', data=login_data, allow_redirects=False)
print(f'Login status: {r.status_code}')
print(f'Cookies: {dict(s.cookies)}')
if r.status_code == 302:
    print(f'Redirect to: {r.headers.get("Location")}')

# Step 2: Try the discover-matches API with session
print("\n=== DISCOVER MATCHES - No filters ===")
r = s.get(f'{BASE}/api/discover-matches')
print(f'Status: {r.status_code}')
print(f'Response: {r.text[:500]}')

# Step 3: Try with sport filter
print("\n=== DISCOVER MATCHES - Sport=cricket ===")
r = s.get(f'{BASE}/api/discover-matches?sport=cricket')
print(f'Status: {r.status_code}')
print(f'Response: {r.text[:500]}')

# Step 4: Try with location
print("\n=== DISCOVER MATCHES - Location=Vijayawada ===")
r = s.get(f'{BASE}/api/discover-matches?location=Vijayawada')
print(f'Status: {r.status_code}')
print(f'Response: {r.text[:500]}')

# Step 5: Try with date
print("\n=== DISCOVER MATCHES - Date=2026-06-23 ===")
r = s.get(f'{BASE}/api/discover-matches?date=2026-06-23')
print(f'Status: {r.status_code}')
print(f'Response: {r.text[:500]}')