"""
Clean up duplicate sports in game_categories table
"""
import pymysql

conn = pymysql.connect(host='localhost', user='root', password='', database='sports_buddy')
cur = conn.cursor()

# For all sports that have duplicates, keep only the one with the highest ID
cur.execute("""
    DELETE gc1 FROM game_categories gc1
    INNER JOIN game_categories gc2
    WHERE gc1.name = gc2.name
    AND gc1.id < gc2.id
""")
conn.commit()
print(f'Deleted duplicate rows. Affected: {cur.rowcount}')

# Verify
cur.execute('SELECT COUNT(*) FROM game_categories')
print(f'Total sports: {cur.fetchone()[0]}')

cur.execute('SELECT id, name, category, display_order FROM game_categories ORDER BY display_order')
for r in cur.fetchall():
    cat = r[2] if r[2] else 'N/A'
    print(f'  {r[0]:2}. {r[1]:22} [{cat:10}] (order:{r[3]})')

cur.close()
conn.close()
print('Cleanup complete!')