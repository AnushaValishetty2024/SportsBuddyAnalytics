"""Fix dashboard data issues."""
import pymysql
from datetime import date, timedelta

conn = pymysql.connect(host='localhost', user='root', password='', database='sports_buddy', cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()

today = date(2026, 6, 29)

# 1. Update existing matches to be upcoming (open status, future dates within next 14 days)
cur.execute("""
    UPDATE matches
    SET status = 'open',
        match_date = DATE_ADD(%s, INTERVAL FLOOR(RAND() * 14) DAY)
    WHERE status != 'open' OR match_date < %s
""", (today, today))

conn.commit()
print('Updated matches to open:', cur.rowcount)

# 2. Verify open matches
cur.execute("SELECT COUNT(*) as cnt FROM matches WHERE status = 'open'")
print('Open matches:', cur.fetchone()['cnt'])

cur.close()
conn.close()