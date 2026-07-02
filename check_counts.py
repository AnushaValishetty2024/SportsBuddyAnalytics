import pymysql

conn = pymysql.connect(host='localhost', user='root', password='', database='sports_buddy', cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()
for t in ['users','matches','match_results_new','match_participants','player_points','user_stats']:
    cur.execute(f'SELECT COUNT(*) as cnt FROM {t}')
    r = cur.fetchone()
    print(f'{t}: {r["cnt"]}')
cur.close()
conn.close()