from app import create_app
app = create_app()
with app.app_context():
    from models import mysql
    cur = mysql.connection.cursor()
    cur.execute('SELECT COUNT(*) as cnt FROM badges')
    print('Badges:', cur.fetchone()['cnt'])
    cur.execute('SELECT COUNT(*) as cnt FROM user_badges')
    print('User badges:', cur.fetchone()['cnt'])
    cur.execute('SELECT ub.user_id, b.badge_name FROM user_badges ub LEFT JOIN badges b ON ub.badge_code = b.badge_code LIMIT 10')
    rows = cur.fetchall()
    print('Sample user badges:')
    for r in rows:
        print('  User', r['user_id'], ':', r['badge_name'])
    cur.close()