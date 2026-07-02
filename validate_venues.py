import json

with open('frontend/nearby_venues.json') as f:
    data = json.load(f)

venues = data['venues']
print(f'Total venues: {len(venues)}')

sports = {}
for v in venues:
    for s in v['sport_types']:
        sports.setdefault(s, []).append(v['name'])

for s, vlist in sports.items():
    print(f'{s}: {len(vlist)} venues - {vlist}')

multi = [v['name'] for v in venues if len(v['sport_types']) > 1]
print(f'\nMulti-sport venues ({len(multi)}): {multi}')

# Validate all required fields
required = ['id','name','sport_types','address','latitude','longitude','rating','available_slots','distance_km','image_url']
for v in venues:
    for r in required:
        assert r in v, f'Missing {r} in venue {v.get("id")}'

print('\nAll validations passed!')