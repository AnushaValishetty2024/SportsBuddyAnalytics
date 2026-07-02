"""
Verify the Sports Categories implementation
"""
import pymysql

conn = pymysql.connect(host='localhost', user='root', password='', database='sports_buddy')
cur = conn.cursor()

# Verify table structure
cur.execute('DESCRIBE game_categories')
cols = [r[0] for r in cur.fetchall()]
print('Database columns:', cols)

# Verify data
cur.execute('SELECT COUNT(*) FROM game_categories')
total = cur.fetchone()[0]
print(f'\nTotal sports: {total}')

cur.execute('SELECT id, name, category, display_order, num_players, difficulty_level FROM game_categories ORDER BY display_order')
for r in cur.fetchall():
    cat = r[2] if r[2] else 'N/A'
    diff = r[5] if r[5] else ''
    print(f'  {r[3]:2}. {r[1]:22} [{cat:10}] {r[4]:25} {diff}')

# Count Indoor vs Outdoor
cur.execute("SELECT category, COUNT(*) FROM game_categories GROUP BY category")
rows = cur.fetchall()
print()
for r in rows:
    print(f'  {r[0] if r[0] else "N/A"}: {r[1]}')

# Check venue counts work
print('\nVenue counts for sports:')
cur.execute("SELECT name FROM game_categories ORDER BY display_order LIMIT 5")
for r in cur.fetchall():
    name = r[0]
    cur2 = conn.cursor()
    cur2.execute("SELECT COUNT(*) as c FROM sports_venues WHERE LOWER(sport_types) LIKE %s", (f'%{name.lower()}%',))
    cnt = cur2.fetchone()[0]
    cur2.close()
    print(f'  {name}: {cnt} venues')

# Check match counts exist
print('\nMatch counts for sports:')
cur.execute("SELECT LOWER(sport_name) as sport_key, COUNT(*) as cnt FROM matches WHERE status = 'open' OR status IS NULL GROUP BY LOWER(sport_name)")
for r in cur.fetchall():
    print(f'  {r[0]}: {r[1]} matches')

cur.close()
conn.close()
print('\nVerification complete!')