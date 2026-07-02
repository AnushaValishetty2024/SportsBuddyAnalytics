import pymysql
conn = pymysql.connect(host='localhost',user='root',password='',db='sports_buddy',cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()

# Check the password_hash for user 1
cur.execute('SELECT id, name, email, password_hash FROM users')
for u in cur.fetchall():
    print(f'id={u["id"]}, name={u["name"]}, email={u["email"]}, hash_preview={u["password_hash"][:30] if u["password_hash"] else "NULL"}')

cur.close()
conn.close()