import requests
import json

base_url = "http://127.0.0.1:5000"

# Test matches API
print("Testing /api/map/matches...")
try:
    r = requests.get(f"{base_url}/api/map/matches")
    print(f"Status: {r.status_code}")
    print(f"Raw response: {r.text[:500]}")
    data = r.json()
    print(f"Success: {data.get('success')}")
    print(f"Matches count: {len(data.get('matches', []))}")
    if data.get('matches'):
        print(f"Sample match: {json.dumps(data['matches'][0], indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*50 + "\n")

# Test venues API
print("Testing /api/map/venues...")
try:
    r = requests.get(f"{base_url}/api/map/venues")
    print(f"Status: {r.status_code}")
    print(f"Raw response: {r.text[:500]}")
    data = r.json()
    print(f"Success: {data.get('success')}")
    print(f"Venues count: {len(data.get('venues', []))}")
    if data.get('venues'):
        print(f"Sample venue: {json.dumps(data['venues'][0], indent=2)}")
except Exception as e:
    print(f"Error: {e}")
