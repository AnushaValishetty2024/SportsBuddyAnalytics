"""
Fix and seed leaderboard data:
1. Ensure match_results_new has realistic completed match data
2. Verify leaderboard calculations
3. Clean up inconsistencies
"""
import pymysql
import random

DB = {'host': 'localhost', 'user': 'root', 'password': '', 'database': 'sports_buddy', 'cursorclass': pymysql.cursors.DictCursor}

conn = pymysql.connect(**DB)
cur = conn.cursor()

# Get all users
cur.execute("SELECT id, name FROM users")
users = cur.fetchall()
print("Users (%d):" % len(users))
for u in users:
    print("  ID=%d: %s" % (u['id'], u['name']))

# Ensure match_results_new table structure is correct
cur.execute("""
    CREATE TABLE IF NOT EXISTS match_results_new (
        id INT AUTO_INCREMENT PRIMARY KEY,
        match_id INT NOT NULL,
        user_id INT NOT NULL,
        points_awarded INT NOT NULL DEFAULT 0,
        admin_adjustment INT NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        INDEX idx_user_id (user_id),
        INDEX idx_match_id (match_id),
        UNIQUE KEY uk_match_user (match_id, user_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
""")
conn.commit()

# Clear old results to start fresh
cur.execute("DELETE FROM match_results_new")
conn.commit()
print("\nCleared old match_results_new")

# Get existing match IDs
cur.execute("SELECT id FROM matches ORDER BY id")
match_ids = [r['id'] for r in cur.fetchall()]
print("Existing match IDs: %s" % match_ids)

# Create realistic completed matches with 2-4 participants each
# Generate results for ALL existing matches
for match_id in match_ids:
    # Pick 2-4 random participants
    num_participants = random.randint(2, 4)
    participants = random.sample(users, num_participants)
    
    # Determine result type: 70% win/loss, 30% draw
    result_type = random.choices(['win_loss', 'draw'], weights=[70, 30], k=1)[0]
    
    if result_type == 'draw':
        # All participants get draw points (5 each)
        for p in participants:
            cur.execute("""
                INSERT INTO match_results_new (match_id, user_id, points_awarded, admin_adjustment)
                VALUES (%s, %s, %s, %s)
            """, (match_id, p['id'], 5, 0))
    else:
        # One winner gets 10, others get 0
        winner = random.choice(participants)
        for p in participants:
            points = 10 if p['id'] == winner['id'] else 0
            cur.execute("""
                INSERT INTO match_results_new (match_id, user_id, points_awarded, admin_adjustment)
                VALUES (%s, %s, %s, %s)
            """, (match_id, p['id'], points, 0))
    
    # Update match status to completed
    cur.execute("UPDATE matches SET status='completed' WHERE id=%s", (match_id,))
    
    # Ensure participants exist in match_participants
    for p in participants:
        cur.execute("""
            INSERT IGNORE INTO match_participants (match_id, user_id) VALUES (%s, %s)
        """, (match_id, p['id']))

conn.commit()
print("Created results for %d completed matches" % len(match_ids))

# Verify leaderboard
print("\n=== LEADERBOARD ===")
cur.execute("""
    SELECT 
        u.id AS user_id,
        u.name AS user_name,
        COALESCE(SUM(mr.points_awarded + COALESCE(mr.admin_adjustment, 0)), 0) AS total_points,
        COUNT(DISTINCT mr.match_id) AS matches_played,
        COUNT(DISTINCT CASE WHEN (mr.points_awarded + COALESCE(mr.admin_adjustment, 0)) >= 10 THEN mr.match_id END) AS wins,
        COUNT(DISTINCT CASE WHEN (mr.points_awarded + COALESCE(mr.admin_adjustment, 0)) = 0 AND mr.match_id IS NOT NULL THEN mr.match_id END) AS losses,
        COUNT(DISTINCT CASE WHEN (mr.points_awarded + COALESCE(mr.admin_adjustment, 0)) = 5 AND mr.match_id IS NOT NULL THEN mr.match_id END) AS draws
    FROM users u
    LEFT JOIN match_results_new mr ON u.id = mr.user_id
    GROUP BY u.id, u.name
    ORDER BY total_points DESC, wins DESC, u.name ASC
""")
rows = cur.fetchall()

rank = 1
for row in rows:
    print("Rank %d: %s - %d pts (%dW/%dL/%dD, %d matches)" % (
        rank, row['user_name'], row['total_points'], row['wins'], row['losses'], row['draws'], row['matches_played']))
    rank += 1

# Summary
cur.execute("""
    SELECT 
        COUNT(DISTINCT u.id) AS total_players,
        COALESCE(COUNT(DISTINCT mr.match_id), 0) AS total_matches,
        COALESCE(SUM(mr.points_awarded + COALESCE(mr.admin_adjustment, 0)), 0) AS total_points
    FROM users u
    LEFT JOIN match_results_new mr ON u.id = mr.user_id
""")
summary = cur.fetchone()
print("\nSummary: %d players, %d matches, %d total points" % (
    summary['total_players'], summary['total_matches'], summary['total_points']))

cur.close()
conn.close()
print("\nDone! Leaderboard is now populated with realistic data.")