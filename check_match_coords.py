import pymysql
conn = pymysql.connect(host='localhost', user='root', password='', database='sports_buddy', cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()
cur.execute("SELECT COUNT(*) as cnt FROM matches WHERE latitude IS NOT NULL AND longitude IS NOT NULL AND status = 'open'")
print('open matches with coords:', cur.fetchone()['cnt'])
cur.execute("SELECT sport_name, latitude, longitude FROM matches WHERE status = 'open' LIMIT 3")
[print(r) for r in cur.fetchall()]
cur.close()
conn.close()