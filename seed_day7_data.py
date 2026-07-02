#!/usr/bin/env python
"""Seed Day 7 demo data: notifications, followers, badges, and seasonal rankings."""
import pymysql
from datetime import datetime, timedelta

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'sportsbuddy'
}

def seed_data():
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        
        print("Seeding Day 7 demo data...")
        
        # ========================================
        # 1. SEED NOTIFICATIONS
        # ========================================
        print("Seeding notifications...")
        
        # Check if notifications exist
        cursor.execute("SELECT COUNT(*) as cnt FROM notifications")
        notif_count = cursor.fetchone()['cnt']
        
        if notif_count == 0:
            # Get all users
            cursor.execute("SELECT id FROM users LIMIT 5")
            users = cursor.fetchall()
            
            if users:
                user_ids = [u['id'] for u in users]
                
                # Create sample notifications
                notifications = []
                for user_id in user_ids[:3]:  # For first 3 users
                    notifications.append((
                        user_id, 'match_start_reminder', 'Match Starting Soon!',
                        'Your match "Cricket Friendly" starts in 30 minutes at Elite Cricket Ground',
                        None, 1, None
                    ))
                    notifications.append((
                        user_id, 'badge_unlocked', 'Badge Unlocked!',
                        'You earned the "First Victory" badge for winning your first match!',
                        None, None, None
                    ))
                
                if len(user_ids) >= 2:
                    notifications.append((
                        user_ids[1], 'new_follower', 'New Follower',
                        f'User {user_ids[0]} started following you!',
                        user_ids[0], None, None
                    ))
                
                for notif in notifications:
                    cursor.execute("""
                        INSERT INTO notifications (user_id, type, title, message, related_user_id, related_match_id, related_conversation_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, notif)
                
                conn.commit()
                print(f"  ✓ Created {len(notifications)} notifications")
        
        # ========================================
        # 2. SEED FOLLOWERS
        # ========================================
        print("Seeding followers...")
        
        cursor.execute("SELECT COUNT(*) as cnt FROM followers")
        follower_count = cursor.fetchone()['cnt']
        
        if follower_count == 0:
            cursor.execute("SELECT id FROM users LIMIT 10")
            users = cursor.fetchall()
            
            if len(users) >= 3:
                user_ids = [u['id'] for u in users]
                
                # Create random follow relationships
                followers_data = []
                for i in range(1, min(6, len(user_ids))):
                    follower_id = user_ids[0]
                    following_id = user_ids[i]
                    if follower_id != following_id:
                        followers_data.append((follower_id, following_id))
                
                # Add some more random follows
                if len(user_ids) >= 5:
                    followers_data.append((user_ids[1], user_ids[3]))
                    followers_data.append((user_ids[2], user_ids[1]))
                    followers_data.append((user_ids[3], user_ids[0]))
                
                for follower_id, following_id in followers_data:
                    try:
                        cursor.execute("""
                            INSERT INTO followers (follower_id, following_id) VALUES (%s, %s)
                        """, (follower_id, following_id))
                    except pymysql.err.IntegrityError:
                        pass  # Already exists
                
                conn.commit()
                print(f"  ✓ Created {len(followers_data)} follower relationships")
        
        # ========================================
        # 3. SEED BADGES (already in migration)
        # ========================================
        print("Seeding user badges...")
        
        cursor.execute("SELECT COUNT(*) as cnt FROM user_badges")
        badge_count = cursor.fetchone()['cnt']
        
        if badge_count == 0:
            cursor.execute("SELECT id FROM users LIMIT 5")
            users = cursor.fetchall()
            cursor.execute("SELECT id, badge_code, badge_name FROM badges LIMIT 10")
            badges = cursor.fetchall()
            
            if users and badges:
                user_badges = []
                for user in users[:3]:
                    for badge in badges[:3]:
                        user_badges.append((user['id'], badge['id'], badge['badge_code'], badge['badge_name'], 'Earned through participation'))
                
                for user_id, badge_id, badge_code, badge_name, description in user_badges:
                    try:
                        cursor.execute("""
                            INSERT INTO user_badges (user_id, badge_id, badge_code, badge_name, description)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (user_id, badge_id, badge_code, badge_name, description))
                    except pymysql.err.IntegrityError:
                        pass
                
                conn.commit()
                print(f"  ✓ Created {len(user_badges)} user badges")
        
        # ========================================
        # 4. UPDATE SEASONAL LEADERBOARD
        # ========================================
        print("Updating seasonal leaderboard...")
        
        cursor.execute("SELECT COUNT(*) as cnt FROM seasonal_leaderboard")
        seasonal_count = cursor.fetchone()['cnt']
        
        if seasonal_count == 0:
            # Get all users with their stats
            cursor.execute("""
                SELECT 
                    u.id AS user_id,
                    u.name AS user_name,
                    COALESCE(SUM(mr.points_awarded + COALESCE(mr.admin_adjustment, 0)), 0) + COALESCE(u.points, 0) AS points,
                    COUNT(DISTINCT mr.match_id) AS matches_played,
                    COUNT(DISTINCT CASE WHEN (mr.points_awarded + COALESCE(mr.admin_adjustment, 0)) >= 10 THEN mr.match_id END) AS wins,
                    COALESCE(SUM(mr.points_awarded + COALESCE(mr.admin_adjustment, 0)), 0) AS match_points
                FROM users u
                LEFT JOIN match_results_new mr ON u.id = mr.user_id
                GROUP BY u.id, u.name
                ORDER BY points DESC
            """)
            users_stats = cursor.fetchall()
            
            # Calculate losses and draws
            ranked_users = []
            for idx, user in enumerate(users_stats):
                wins = int(user['wins'])
                matches = int(user['matches_played'])
                losses = matches - wins  # Simplified
                draws = 0  # Simplified
                win_rate = round((wins / matches * 100) if matches > 0 else 0, 2)
                
                ranked_users.append({
                    'user_id': user['user_id'],
                    'points': int(user['points']),
                    'matches_played': matches,
                    'wins': wins,
                    'losses': losses,
                    'draws': draws,
                    'win_rate': win_rate,
                    'rank': idx + 1
                })
            
            # Insert lifetime rankings
            for user in ranked_users:
                cursor.execute("""
                    INSERT INTO seasonal_leaderboard 
                    (user_id, period_type, period_start, period_end, points, matches_played, wins, losses, draws, win_rate, rank_position, is_current)
                    VALUES (%s, 'lifetime', '2000-01-01', '2099-12-31', %s, %s, %s, %s, %s, %s, %s, TRUE)
                """, (
                    user['user_id'], user['points'], user['matches_played'],
                    user['wins'], user['losses'], user['draws'], user['win_rate'], user['rank']
                ))
            
            # Insert weekly rankings
            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            
            for user in ranked_users:
                cursor.execute("""
                    INSERT INTO seasonal_leaderboard 
                    (user_id, period_type, period_start, period_end, points, matches_played, wins, losses, draws, win_rate, rank_position, is_current)
                    VALUES (%s, 'weekly', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                """, (
                    user['user_id'], week_start, week_end,
                    user['points'], user['matches_played'],
                    user['wins'], user['losses'], user['draws'], user['win_rate'], user['rank']
                ))
            
            # Insert monthly rankings
            month_start = today.replace(day=1)
            month_end = today.replace(day=28) + timedelta(days=4)
            month_end = month_end - timedelta(days=month_end.day)
            
            for user in ranked_users:
                cursor.execute("""
                    INSERT INTO seasonal_leaderboard 
                    (user_id, period_type, period_start, period_end, points, matches_played, wins, losses, draws, win_rate, rank_position, is_current)
                    VALUES (%s, 'monthly', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                """, (
                    user['user_id'], month_start, month_end,
                    user['points'], user['matches_played'],
                    user['wins'], user['losses'], user['draws'], user['win_rate'], user['rank']
                ))
            
            conn.commit()
            print(f"  ✓ Created seasonal leaderboard for {len(ranked_users)} users")
        
        cursor.close()
        conn.close()
        
        print("\n✓ Day 7 demo data seeded successfully!")
        
    except Exception as e:
        print(f"\n✗ Error seeding data: {e}")

if __name__ == '__main__':
    seed_data()