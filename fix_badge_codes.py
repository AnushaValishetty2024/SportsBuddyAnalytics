from app import create_app
app = create_app()
with app.app_context():
    from models import mysql
    
    cur = mysql.connection.cursor()
    
    # First check what badge codes exist in badges table
    cur.execute('SELECT badge_code, badge_name FROM badges')
    badge_rows = cur.fetchall()
    valid_codes = {r['badge_code'] for r in badge_rows}
    print(f'Valid badge codes ({len(valid_codes)}): {sorted(valid_codes)}')
    
    # Check what badge codes exist in user_badges
    cur.execute('SELECT DISTINCT badge_code FROM user_badges')
    user_badge_codes = {r['badge_code'] for r in cur.fetchall()}
    print(f'User badge codes ({len(user_badge_codes)}): {sorted(user_badge_codes)}')
    
    # Find missing badges
    missing = user_badge_codes - valid_codes
    print(f'Missing badge codes: {sorted(missing)}')
    
    # Insert any missing badge definitions
    if missing:
        print(f'\nInserting {len(missing)} missing badge definitions...')
        default_badges = {
            'rising_star': ('Rising Star', 'Showed exceptional improvement', 'bi-arrow-up-circle-fill', 'custom', 1),
            'match_winner': ('Match Winner', 'Won a competitive match', 'bi-trophy-fill', 'wins', 1),
            'sharp_shooter': ('Sharp Shooter', 'High accuracy in matches', 'bi-bullseye', 'custom', 1),
            'sports_enthusiast': ('Sports Enthusiast', 'Participated in multiple sports', 'bi-heart-fill', 'custom', 1),
            'team_player': ('Team Player', 'Played 5 team matches', 'bi-people-fill', 'matches_played', 5),
            'winning_streak': ('Winning Streak', 'Won 3 matches in a row', 'bi-fire', 'wins', 3),
            'consistent_performer': ('Consistent Performer', 'Played 10 matches consistently', 'bi-check-circle-fill', 'matches_played', 10),
            'weekly_champion': ('Weekly Champion', 'Ranked #1 this week', 'bi-calendar-week-fill', 'weekly_top', 1),
            'monthly_champion': ('Monthly Champion', 'Ranked #1 this month', 'bi-calendar-month-fill', 'monthly_top', 1),
            'first_match': ('First Match', 'Awarded after completing the first match', 'bi-trophy-fill', 'matches_played', 1),
            'mvp': ('MVP', 'Most Valuable Player in a match', 'bi-award-fill', 'custom', 1),
            'tournament_champion': ('Tournament Champion', 'Won a tournament', 'bi-trophy-fill', 'tournaments_won', 1),
        }
        
        for code in missing:
            if code in default_badges:
                name, desc, icon, criteria, value = default_badges[code]
                try:
                    cur.execute("""
                        INSERT IGNORE INTO badges (badge_code, badge_name, description, icon, criteria_type, criteria_value)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (code, name, desc, icon, criteria, value))
                    print(f'  Inserted badge: {code} - {name}')
                except Exception as e:
                    print(f'  Error inserting {code}: {e}')
        
        mysql.connection.commit()
        print('Missing badges inserted successfully.')
    else:
        print('All badge codes in user_badges have matching definitions.')
    
    # Verify fix
    cur.execute('''
        SELECT ub.user_id, b.badge_name
        FROM user_badges ub
        LEFT JOIN badges b ON ub.badge_code = b.badge_code
        WHERE b.badge_name IS NULL
        LIMIT 10
    ''')
    null_badges = cur.fetchall()
    if null_badges:
        print(f'\nWARNING: Still have {len(null_badges)} badges with NULL names:')
        for r in null_badges:
            print(f'  User {r["user_id"]}: NULL badge')
    else:
        print('\nSUCCESS: All user badges now have valid names!')
    
    cur.close()