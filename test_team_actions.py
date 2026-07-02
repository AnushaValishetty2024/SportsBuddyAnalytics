#!/usr/bin/env python
"""Quick test script to verify team action endpoints"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_endpoint(method, path, data=None):
    """Test an endpoint and return result"""
    url = f"{BASE_URL}{path}"
    try:
        if method == 'POST':
            resp = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        else:
            resp = requests.get(url)
        print(f"\n{method} {path}")
        print(f"  Status: {resp.status_code}")
        try:
            print(f"  Response: {json.dumps(resp.json(), indent=2)}")
        except:
            print(f"  Response: {resp.text[:200]}")
        return resp
    except Exception as e:
        print(f"\n{method} {path}")
        print(f"  Error: {e}")
        return None

if __name__ == '__main__':
    print("Testing Team Endpoints")
    print("=" * 50)
    
    # Test teams list
    test_endpoint('GET', '/teams')
    
    # Test join (will fail without login, but verifies endpoint exists)
    test_endpoint('POST', '/teams/join/1')
    
    # Test leave
    test_endpoint('POST', '/teams/leave/1')
    
    # Test delete (will fail without captain, but verifies endpoint exists)
    test_endpoint('POST', '/teams/delete/1')
    
    # Test team details
    test_endpoint('GET', '/teams/1')
    
    print("\n" + "=" * 50)
    print("Endpoint verification complete!")