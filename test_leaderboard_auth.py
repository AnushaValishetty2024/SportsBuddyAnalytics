import requests

base = 'http://127.0.0.1:5000'
session = requests.Session()

# Check login page
resp = session.get(base + '/login')
print('GET /login status:', resp.status_code)

# Try login
payload = {'email': 'test@example.com', 'password': 'testpass123'}
resp = session.post(base + '/login', data=payload, allow_redirects=False)
print('POST /login status:', resp.status_code)

if resp.status_code == 302:
    print('Redirect to:', resp.headers.get('Location'))
    resp2 = session.get(base + '/dashboard', allow_redirects=False)
    print('GET /dashboard status:', resp2.status_code)
else:
    print('Login failed, trying to register...')
    reg_payload = {'name': 'Test User', 'email': 'test@example.com', 'password': 'testpass123'}
    resp = session.post(base + '/register', data=reg_payload, allow_redirects=False)
    print('POST /register status:', resp.status_code)
    
    # Now login
    resp = session.post(base + '/login', data=payload, allow_redirects=False)
    print('POST /login status:', resp.status_code)
    if resp.status_code == 302:
        print('Redirect to:', resp.headers.get('Location'))

# Test submit result with session
print('\n=== Test: POST /api/submit-result (with session) ===')
payload = {'match_id': 1, 'is_draw': False, 'winner_id': 1}
resp = session.post(base + '/api/submit-result', json=payload)
print('Status:', resp.status_code)
print('Response:', resp.text[:500])