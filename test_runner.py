from app import create_app
import json

app = create_app()
client = app.test_client()

with app.test_request_context():
    from models import User
    user = User.get_by_id(1)
    print('User:', user['name'] if user else 'None')

    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_name'] = user['name'] if user else 'test'

    resp = client.post('/api/submit-result',
        data=json.dumps({'match_id': 1, 'is_draw': False, 'winner_id': 1}),
        content_type='application/json')
    print('Submit status:', resp.status_code)
    print('Submit response:', resp.get_json())

    resp = client.post('/api/admin/adjust-result',
        data=json.dumps({'match_id': 1, 'user_id': 1, 'adjustment': 5}),
        content_type='application/json')
    print('Adjust status:', resp.status_code)
    print('Adjust response:', resp.get_json())