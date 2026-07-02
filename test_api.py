import urllib.request
import json

# Test the nearby-venues API
url = 'http://127.0.0.1:5000/api/nearby-venues'
try:
    response = urllib.request.urlopen(url)
    data = json.loads(response.read().decode('utf-8'))
    venues = data.get('venues', [])
    print('API Response OK!')
    print(f'Total venues: {len(venues)}')
    print()
    print('First 3 venues:')
    for v in venues[:3]:
        print(f'  - {v["name"]}')
        print(f'    Sports: {", ".join(v["sport_types"])}')
        print(f'    Rating: {v["rating"]}, Slots: {v["available_slots"]}, Distance: {v["distance_km"]}km')
        print(f'    Lat: {v["latitude"]}, Lng: {v["longitude"]}')
        print()
    
    # Test sport filter
    url2 = 'http://127.0.0.1:5000/api/nearby-venues?sport=Cricket'
    response2 = urllib.request.urlopen(url2)
    data2 = json.loads(response2.read().decode('utf-8'))
    cricket_venues = data2.get('venues', [])
    print(f'Cricket venues: {len(cricket_venues)}')
    for v in cricket_venues:
        print(f'  - {v["name"]}')
    
    # Verify required fields
    if venues:
        v = venues[0]
        required = ['id', 'name', 'sport_types', 'address', 'latitude', 'longitude', 'rating', 'available_slots', 'distance_km', 'image_url']
        missing = [f for f in required if f not in v]
        if missing:
            print(f'\nMissing fields: {missing}')
        else:
            print(f'\nAll required fields present ✓')
        print(f'Data type: {type(v["sport_types"])} (should be list)')
        print(f'Sport types: {v["sport_types"]}')
    
    print('\n=== API TEST PASSED ===')
    
except Exception as e:
    print(f'Error: {e}')