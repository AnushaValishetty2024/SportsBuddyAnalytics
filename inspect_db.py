import pymysql

DB = {'host': 'localhost', 'user': 'root', 'password': '', 'database': 'sports_buddy', 'cursorclass': pymysql.cursors.DictCursor}

conn = pymysql.connect(**DB)
cur = conn.cursor()
try:
    cur.execute('SHOW TABLES')
    tables = [list(r.values())[0] for r in cur.fetchall()]
    print('Tables:', tables)
    for t in tables:
        cur.execute(f'DESCRIBE {t}')
        cols = cur.fetchall()
        print(f'\n{t}:')
        for c in cols:
            print(f"  {c['Field']} | {c['Type']} | Key: {c['Key']} | Extra: {c['Extra']}")
except Exception as e:
    print('Error:', e)
cur.close()
conn.close()