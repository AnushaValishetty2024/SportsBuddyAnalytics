import pymysql
conn = pymysql.connect(host='localhost', user='root', password='', database='sports_buddy', cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()
cur.execute('SELECT COUNT(*) as cnt FROM sports_venues')
count = cur.fetchone()['cnt']
print('Venues in DB: ' + str(count))
cur.execute('SELECT name, sport_types FROM sports_venues LIMIT 3')
for r in cur.fetchall():
    print('  - ' + r['name'] + ': ' + r['sport_types'])
cur.close()
conn.close()