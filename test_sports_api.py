"""
Test the Sports Categories API endpoints
Run with: python test_sports_api.py
"""
import requests
import json

BASE_URL = 'http://localhost:5000'

def test_sports_categories():
    print("=== Sports Categories API ===")
    try:
        r = requests.get(BASE_URL + '/api/sports-categories', timeout=5)
        data = r.json()
        print("Success:", data.get('success'))
        print("Total sports:", data.get('total'))
        if data.get('sports'):
            for s in data['sports'][:5]:
                print(f"  - {s['name']:20} [{s['category']:8}] venues:{s['venue_count']} matches:{s['match_count']}")
            print(f"  ... and {len(data['sports']) - 5} more")
        return data
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_sport_detail(sport_id, sport_name):
    print(f"\n=== Sport Detail API ({sport_name}, id={sport_id}) ===")
    try:
        r = requests.get(BASE_URL + f'/api/sport-detail/{sport_id}', timeout=5)
        data = r.json()
        if data.get('success'):
            s = data['sport']
            print(f"Name: {s['name']}")
            print(f"Category: {s['category']}")
            print(f"Players: {s['num_players']}")
            print(f"Duration: {s['match_duration']}")
            print(f"Difficulty: {s['difficulty_level']}")
            print(f"Venue count: {s['venue_count']}")
            print(f"Match count: {s['match_count']}")
            print(f"Nearby venues: {len(s['nearby_venues'])}")
            print(f"Upcoming matches: {len(s['upcoming_matches'])}")
        else:
            print("Error:", data.get('message'))
    except Exception as e:
        print(f"Error: {e}")

def test_games_api():
    print("\n=== All Games API (backward compat) ===")
    try:
        r = requests.get(BASE_URL + '/api/games', timeout=5)
        data = r.json()
        print("Success:", data.get('success'))
        print("Total games:", data.get('total'))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # First test sports categories
    sports_data = test_sports_categories()
    
    # Test sport detail with first sport if available
    if sports_data and sports_data.get('sports'):
        first = sports_data['sports'][0]
        test_sport_detail(first['id'], first['name'])
    
    # Test games API
    test_games_api()
    
    print("\n=== All tests complete! ===")