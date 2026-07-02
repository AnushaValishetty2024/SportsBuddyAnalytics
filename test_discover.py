import pymysql
conn = pymysql.connect(host='localhost',user='root',password='',db='sports_buddy',cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()

print("=== ALL MATCHES ===")
cur.execute('SELECT m.*, u.name as creator_name, (SELECT COUNT(*) FROM match_participants mp WHERE mp.match_id = m.id) as player_count FROM matches m JOIN users u ON m.creator_id = u.id WHERE 1=1 ORDER BY m.match_date ASC, m.match_time ASC LIMIT 20')
results = cur.fetchall()
print(f'No filters: {len(results)} matches')
for r in results:
    print(f'  id={r["id"]}, sport={r["sport_name"]}, venue={r["venue_name"]}')

print("\n=== FILTER BY SPORT 'cricket' ===")
cur.execute("SELECT m.*, u.name as creator_name, (SELECT COUNT(*) FROM match_participants mp WHERE mp.match_id = m.id) as player_count FROM matches m JOIN users u ON m.creator_id = u.id WHERE 1=1 AND LOWER(m.sport_name) = LOWER(%s) ORDER BY m.match_date ASC, m.match_time ASC LIMIT 20", ['cricket'])
results = cur.fetchall()
print(f'Filter cricket: {len(results)} matches')
for r in results:
    print(f'  id={r["id"]}, sport={r["sport_name"]}')

print("\n=== FILTER BY LOCATION 'vijayawada' ===")
cur.execute("SELECT m.*, u.name as creator_name, (SELECT COUNT(*) FROM match_participants mp WHERE mp.match_id = m.id) as player_count FROM matches m JOIN users u ON m.creator_id = u.id WHERE 1=1 AND (LOWER(m.venue_name) LIKE LOWER(%s) OR LOWER(m.venue_name) LIKE LOWER(%s)) ORDER BY m.match_date ASC, m.match_time ASC LIMIT 20", ['%vijayawada%', '%vijayawada%'])
results = cur.fetchall()
print(f'Filter location: {len(results)} matches')
for r in results:
    print(f'  id={r["id"]}, venue={r["venue_name"]}')

print("\n=== FILTER BY DATE '2026-06-23' ===")
cur.execute("SELECT m.*, u.name as creator_name, (SELECT COUNT(*) FROM match_participants mp WHERE mp.match_id = m.id) as player_count FROM matches m JOIN users u ON m.creator_id = u.id WHERE 1=1 AND m.match_date = %s ORDER BY m.match_date ASC, m.match_time ASC LIMIT 20", ['2026-06-23'])
results = cur.fetchall()
print(f'Filter date: {len(results)} matches')
for r in results:
    print(f'  id={r["id"]}, date={r["match_date"]}, venue={r["venue_name"]}')

print("\n=== CHECK USERS TABLE ===")
cur.execute('SELECT id, name, email FROM users')
users = cur.fetchall()
print(f'Users: {len(users)}')
for u in users:
    print(f'  id={u["id"]}, name={u["name"]}, email={u["email"]}')

# Check the password_hash
cur.execute('SELECT id, password_hash FROM users')
print('\n=== PASSWORD CHECK ===')
for u in cur.fetchall():
    print(f'  id={u["id"]}, has_hash={u["password_hash"] is not None and len(u["password_hash"]) > 0}')

# Check the session table
cur.execute("SHOW TABLES LIKE '%session%'")
tables = cur.fetchall()
print(f'\nSession tables: {tables}')

cur.close()
conn.close()