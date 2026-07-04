from app import create_app
app = create_app()
with app.app_context():
    from models import mysql
    cur = mysql.connection.cursor()
    cur.execute('''
        SELECT ub.user_id, ub.badge_code, b.badge_name, b.description
        FROM user_badges ub
        LEFT JOIN badges b ON ub.badge_code = b.badge_code
        ORDER BY ub.user_id, ub.awarded_at DESC
    ''')
    rows = cur.fetchall()
    print('All user badges (including potential NULLs):')
    for r in rows:
        print(f'  User {r["user_id"]}: code={r["badge_code"]}, name={r["badge_name"]}')
    cur.close()