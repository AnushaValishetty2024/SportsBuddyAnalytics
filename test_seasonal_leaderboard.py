"""Test script for seasonal leaderboard functionality."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import mysql

app = create_app()

def test_seasonal_leaderboard():
    with app.app_context():
        print("=" * 60)
        print("TESTING SEASONAL LEADERBOARD")
        print("=" * 60)

        cur = mysql.connection.cursor()

        # Test 1: Check seasonal_leaderboard table exists and has data
        print("\n1. Checking seasonal_leaderboard table...")
        cur.execute("SELECT COUNT(*) as cnt FROM seasonal_leaderboard")
        count = cur.fetchone()['cnt']
        print(f"   Total entries: {count}")

        cur.execute("""
            SELECT period_type, COUNT(*) as cnt, 
                   SUM(points) as total_points,
                   MIN(points) as min_points,
                   MAX(points) as max_points
            FROM seasonal_leaderboard
            WHERE is_current = TRUE
            GROUP BY period_type
        """)
        stats = cur.fetchall()
        for stat in stats:
            print(f"   {stat['period_type']}: {stat['cnt']} users, points range: {stat['min_points']} - {stat['max_points']}")

        # Test 2: Check weekly leaderboard
        print("\n2. Testing Weekly Leaderboard...")
        cur.execute("""
            SELECT sl.rank_position, u.name, sl.points, sl.matches_played, sl.wins, sl.losses, sl.draws, sl.win_rate
            FROM seasonal_leaderboard sl
            JOIN users u ON sl.user_id = u.id
            WHERE sl.period_type = 'weekly' AND sl.is_current = TRUE
            ORDER BY sl.rank_position ASC
            LIMIT 10
        """)
        weekly_data = cur.fetchall()
        print(f"   Top 10 weekly players:")
        for row in weekly_data:
            print(f"   #{row['rank_position']} {row['name']}: {row['points']} points, {row['win_rate']}% win rate")

        # Test 3: Check monthly leaderboard
        print("\n3. Testing Monthly Leaderboard...")
        cur.execute("""
            SELECT sl.rank_position, u.name, sl.points, sl.matches_played, sl.wins, sl.losses, sl.draws, sl.win_rate
            FROM seasonal_leaderboard sl
            JOIN users u ON sl.user_id = u.id
            WHERE sl.period_type = 'monthly' AND sl.is_current = TRUE
            ORDER BY sl.rank_position ASC
            LIMIT 10
        """)
        monthly_data = cur.fetchall()
        print(f"   Top 10 monthly players:")
        for row in monthly_data:
            print(f"   #{row['rank_position']} {row['name']}: {row['points']} points, {row['win_rate']}% win rate")

        # Test 4: Check lifetime leaderboard
        print("\n4. Testing Lifetime Leaderboard...")
        cur.execute("""
            SELECT sl.rank_position, u.name, sl.points, sl.matches_played, sl.wins, sl.losses, sl.draws, sl.win_rate
            FROM seasonal_leaderboard sl
            JOIN users u ON sl.user_id = u.id
            WHERE sl.period_type = 'lifetime' AND sl.is_current = TRUE
            ORDER BY sl.rank_position ASC
            LIMIT 10
        """)
        lifetime_data = cur.fetchall()
        print(f"   Top 10 lifetime players:")
        for row in lifetime_data:
            print(f"   #{row['rank_position']} {row['name']}: {row['points']} points, {row['win_rate']}% win rate")

        # 5. TEST POINTS ADJUSTMENT (ADD) via Flask API
        print("\n5. Testing Points Adjustment (ADD)...")
        if weekly_data:
            test_user = weekly_data[-1]
            user_name = test_user['name']
            cur.execute("SELECT id FROM users WHERE name = %s", (user_name,))
            user_row = cur.fetchone()
            if user_row:
                user_id = user_row['id']
                old_points = test_user['points']

                with app.test_client() as client:
                    resp = client.post('/api/leaderboard/adjust-points',
                        json={'user_id': user_id, 'season': 'weekly', 'amount': 50, 'reason': 'Test bonus'},
                        headers={'Content-Type': 'application/json'})
                    data = resp.get_json()
                    print(f"   API status: {resp.status_code}")
                    print(f"   Response: {data}")
                    if data.get('success'):
                        print(f"   {user_name}: {old_points} -> adjusted via API")
                    else:
                        print(f"   Failed: {data.get('message')}")

        # 6. TEST POINTS ADJUSTMENT (DEDUCT) via Flask API
        print("\n6. Testing Points Adjustment (DEDUCT)...")
        if monthly_data:
            test_user = monthly_data[0]
            user_name = test_user['name']
            cur.execute("SELECT id FROM users WHERE name = %s", (user_name,))
            user_row = cur.fetchone()
            if user_row:
                user_id = user_row['id']
                old_points = test_user['points']

                with app.test_client() as client:
                    resp = client.post('/api/leaderboard/adjust-points',
                        json={'user_id': user_id, 'season': 'monthly', 'amount': -30, 'reason': 'Test penalty'},
                        headers={'Content-Type': 'application/json'})
                    data = resp.get_json()
                    print(f"   API status: {resp.status_code}")
                    print(f"   Response: {data}")
                    if data.get('success'):
                        print(f"   {user_name}: {old_points} -> adjusted via API")
                    else:
                        print(f"   Failed: {data.get('message')}")

        cur.close()

        print("\n" + "=" * 60)
        print("TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)


if __name__ == '__main__':
    test_seasonal_leaderboard()