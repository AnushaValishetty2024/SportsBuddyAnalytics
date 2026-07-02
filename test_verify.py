"""Quick verification script for leaderboard database state."""
import pymysql

conn = pymysql.connect(
    host='localhost', user='root', password='', db='sports_buddy',
    cursorclass=pymysql.cursors.DictCursor
)
cur = conn.cursor()

print("=== match_results_new ===")
cur.execute("SELECT * FROM match_results_new")
rows = cur.fetchall()
for r in rows:
    print(f"  id={r['id']}, match_id={r['match_id']}, user_id={r['user_id']}, "
          f"points={r['points_awarded']}, adj={r['admin_adjustment']}")

if not rows:
    print("  (empty)")

print("\n=== Match 1 status ===")
cur.execute("SELECT id, sport_name, status FROM matches WHERE id=1")
m = cur.fetchone()
print(f"  {m}")

print("\n=== Dynamic Leaderboard (SQL) ===")
cur.execute("""
    SELECT u.id, u.name,
           COALESCE(SUM(mr.points_awarded + COALESCE(mr.admin_adjustment, 0)), 0) AS total_points
    FROM users u
    LEFT JOIN match_results_new mr ON u.id = mr.user_id
    GROUP BY u.id, u.name
    ORDER BY total_points DESC
""")
rows = cur.fetchall()
for r in rows:
    print(f"  {r['name']}: {r['total_points']} pts")

cur.close()
conn.close()
print("\nDone.")