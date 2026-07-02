"""Seed demo data for Sports Buddy application."""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import mysql, User, Match, Leaderboard, GameCategory
from werkzeug.security import generate_password_hash

app = create_app()


def seed_demo_data():
    with app.app_context():
        print("=" * 50)
        print("Seeding Demo Data")
        print("=" * 50)

        # 1. USERS
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM users")
        user_count = cur.fetchone()['cnt']
        cur.close()

        if user_count < 15:
            print(f"\nCurrent users: {user_count}. Adding users...")
            demo_users = [
                ("Anusha", "anusha@sportsbuddy.com", "demo123"),
                ("Chutky", "chutky@sportsbuddy.com", "demo123"),
                ("Yamini", "yamini@sportsbuddy.com", "demo123"),
                ("Riyanshika", "riyanshika@sportsbuddy.com", "demo123"),
                ("Rahul", "rahul@sportsbuddy.com", "demo123"),
                ("Kiran", "kiran@sportsbuddy.com", "demo123"),
                ("Priya", "priya@sportsbuddy.com", "demo123"),
                ("Arjun", "arjun@sportsbuddy.com", "demo123"),
                ("Sai", "sai@sportsbuddy.com", "demo123"),
                ("Neha", "neha@sportsbuddy.com", "demo123"),
                ("Vikram", "vikram@sportsbuddy.com", "demo123"),
                ("Sneha", "sneha@sportsbuddy.com", "demo123"),
                ("Ravi", "ravi@sportsbuddy.com", "demo123"),
                ("Pooja", "pooja@sportsbuddy.com", "demo123"),
                ("Karthik", "karthik@sportsbuddy.com", "demo123"),
            ]

            cur = mysql.connection.cursor()
            for name, email, password in demo_users:
                pw_hash = generate_password_hash(password)
                try:
                    cur.execute(
                        "INSERT IGNORE INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                        (name, email, pw_hash)
                    )
                except Exception as e:
                    print(f"  Error inserting user {name}: {e}")
            mysql.connection.commit()
            cur.close()
        else:
            print(f"\nUsers already exist ({user_count}). Skipping.")

        # 2. GAME CATEGORIES
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM game_categories")
        sport_count = cur.fetchone()['cnt']
        cur.close()

        if sport_count < 18:
            print(f"Current sports: {sport_count}. Adding sports...")
            sports = [
                ('Cricket', 'Outdoor', 'Popular bat-and-ball game', 11, 'Bat, Ball, Wickets', 'Oval field', 'Two innings, 11 players', 'ICC Cricket World Cup, IPL', 'Advanced', 'Ground with pitch', 1),
                ('Football', 'Outdoor', 'World\'s most popular sport', 11, 'Ball, Cleats, Goals', 'Rectangular field', '90 minutes, 2 halves', 'FIFA World Cup, UEFA Champions League', 'Intermediate', 'Grass or turf field', 2),
                ('Badminton', 'Indoor', 'Fast-paced racket sport', 2, 'Racket, Shuttlecock', 'Rectangular court', 'Best of 3 games, 21 points', 'Olympics, All England Open', 'Advanced', 'Indoor court', 3),
                ('Basketball', 'Indoor', 'High-energy team sport', 5, 'Ball, Hoop, Court shoes', 'Indoor court', '4 quarters, 12 min each', 'NBA, Olympics', 'Intermediate', 'Indoor court', 4),
                ('Tennis', 'Outdoor', 'Classic racket sport', 2, 'Racket, Tennis balls', 'Rectangular court', 'Best of 3/5 sets, 6 games', 'Wimbledon, US Open', 'Advanced', 'Hard/Clay/Grass court', 5),
                ('Volleyball', 'Outdoor', 'Jump and spike!', 6, 'Ball, Knee pads, Net', 'Sand/Indoor court', 'Best of 5 sets, 25 points', 'Olympics, FIVB World League', 'Intermediate', 'Beach or indoor court', 6),
                ('Table Tennis', 'Indoor', 'Lightning fast rallies', 2, 'Paddle, Ball, Table', 'Indoor table', 'Best of 7 games, 11 points', 'Olympics, World Championships', 'Advanced', 'Indoor room', 7),
                ('Kabaddi', 'Outdoor', 'Traditional Indian sport', 7, 'Mat, Knee pads', 'Indoor/Outdoor court', '2 halves, 20 min each', 'Pro Kabaddi League, Olympics', 'Intermediate', 'Raised court', 8),
                ('Hockey', 'Outdoor', 'Fast skating and goals', 11, 'Stick, Ball, Skates', 'Ice/Field rink', '3 periods, 20 min each', 'Olympics, FIH World Cup', 'Intermediate', 'Ice rink or turf', 9),
                ('Baseball', 'Outdoor', 'America\'s pastime', 9, 'Bat, Ball, Glove', 'Diamond field', '9 innings', 'MLB World Series', 'Intermediate', 'Diamond field', 10),
                ('Rugby', 'Outdoor', 'Physical and strategic', 15, 'Ball, Mouthguard, Cleats', 'Grass field', '2 halves, 40 min each', 'Rugby World Cup', 'Advanced', 'Grass field', 11),
                ('Athletics', 'Outdoor', 'Track and field events', 1, 'Running shoes', 'Track/Field', 'Varies by event', 'Olympics, World Athletics', 'Intermediate', 'Running track', 12),
                ('Cycling', 'Outdoor', 'Speed and endurance', 1, 'Bicycle, Helmet', 'Road/Track', 'Varies by race type', 'Tour de France, Olympics', 'Advanced', 'Road or velodrome', 13),
                ('Archery', 'Outdoor', 'Focus and precision', 1, 'Bow, Arrows, Target', 'Flat terrain', 'Varies by round', 'Olympics, World Archery', 'Advanced', 'Outdoor range', 14),
                ('Golf', 'Outdoor', 'Precision club sport', 4, 'Clubs, Balls, Tees', 'Golf course', '18 holes, ~4 hours', 'Masters, US Open, Ryder Cup', 'Intermediate', 'Golf course', 15),
                ('Chess', 'Indoor', 'Mental battle of wits', 2, 'Chessboard, Pieces', 'Indoor table', 'Depends on time control', 'World Chess Championship', 'Advanced', 'Indoor room', 16),
                ('Carrom', 'Indoor', 'Popular board game sport', 4, 'Carrom board, Coins, Striker', 'Indoor table', 'Best of 3/5 boards', 'Carrom World Cup', 'Intermediate', 'Indoor room', 17),
                ('Squash', 'Indoor', 'Intense racket sport', 2, 'Racket, Ball, Court', 'Enclosed court', 'Best of 5 games, 11 points', 'British Open, World Championships', 'Advanced', 'Enclosed court', 18),
            ]

            cur = mysql.connection.cursor()
            for s in sports:
                try:
                    cur.execute("""
                        INSERT IGNORE INTO game_categories
                            (name, category, description, num_players, equipment, playing_area, basic_rules, popular_tournaments, difficulty_level, location_info, display_order)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, s)
                except Exception as e:
                    print(f"  Error inserting sport {s[0]}: {e}")

            mysql.connection.commit()
            cur.close()
            print(f"  Added {len(sports)} sports.")
        else:
            print(f"\nSports already exist ({sport_count}). Skipping.")

        # 3. VENUES
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM sports_venues")
        venue_count = cur.fetchone()['cnt']
        cur.close()
        print(f"\nSports venues: {venue_count}")

        # 4. MATCHES
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM users LIMIT 1")
        user_row = cur.fetchone()
        if not user_row:
            cur.execute("INSERT INTO users (name, email) VALUES (%s, %s)", ('Demo User', 'demo@sportsbuddy.com'))
            mysql.connection.commit()
            default_user_id = cur.lastrowid
        else:
            default_user_id = user_row['id']
        cur.close()

        sports_list = ['Cricket', 'Football', 'Badminton', 'Basketball', 'Tennis', 'Volleyball', 'Table Tennis', 'Kabaddi', 'Hockey', 'Baseball']
        venues = [
            ("Elite Cricket Ground", 16.5062, 80.6480),
            ("SNR Law College Football Ground", 16.5185, 80.6565),
            ("APSRTC Indoor Stadium", 16.5102, 80.6345),
            ("Sports Authority of India Complex", 16.4955, 80.6385),
            ("Andhra Tennis Academy", 16.5160, 80.6495),
            ("VGTM Urban Sports Park", 16.5275, 80.6710),
            ("Vijayawada Badminton Centre", 16.5090, 80.6460),
            ("GM Cricket Grounds", 16.4920, 80.6680),
        ]

        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM matches WHERE status = 'open'")
        upcoming_count = cur.fetchone()['cnt']
        cur.close()

        if upcoming_count < 20:
            print(f"\nCurrent upcoming matches: {upcoming_count}. Adding more...")
            matches_to_add = []
            base_date = datetime.now().date()

            for i in range(20 - upcoming_count):
                sport = sports_list[i % len(sports_list)]
                venue = venues[i % len(venues)]
                match_date = base_date + timedelta(days=i + 1)
                match_time = f"{17 + (i % 4):02d}:00:00"
                matches_to_add.append((
                    default_user_id,
                    'outdoor' if sport not in ['Badminton', 'Basketball', 'Table Tennis', 'Chess', 'Carrom', 'Squash'] else 'indoor',
                    sport,
                    match_date.strftime('%Y-%m-%d'),
                    match_time,
                    venue[0],
                    10 + (i % 6),
                    'Vijayawada',
                    venue[1],
                    venue[2],
                    'intermediate' if i % 3 != 0 else 'beginner',
                    'all',
                    'open'
                ))

            cur = mysql.connection.cursor()
            for m in matches_to_add:
                try:
                    cur.execute("""
                        INSERT INTO matches
                            (creator_id, sport_type, sport_name, match_date, match_time, venue_name, max_players, location, latitude, longitude, skill_level, gender_preference, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, m)
                except Exception as e:
                    print(f"  Error inserting match: {e}")

            mysql.connection.commit()
            cur.close()
            print(f"  Added {len(matches_to_add)} upcoming matches.")
        else:
            print(f"\nUpcoming matches already exist ({upcoming_count}). Skipping.")

        # 5. COMPLETED MATCHES
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM matches WHERE status = 'completed'")
        completed_count = cur.fetchone()['cnt']
        cur.close()

        if completed_count < 8:
            print(f"Current completed matches: {completed_count}. Adding completed matches...")
            completed_matches = []
            base_date = datetime.now().date() - timedelta(days=10)

            for i in range(8 - completed_count):
                sport = sports_list[i % len(sports_list)]
                venue = venues[i % len(venues)]
                match_date = base_date + timedelta(days=i * 2)
                match_time = f"{15 + (i % 3):02d}:00:00"
                completed_matches.append((
                    default_user_id,
                    'outdoor' if sport not in ['Badminton', 'Basketball', 'Table Tennis'] else 'indoor',
                    sport,
                    match_date.strftime('%Y-%m-%d'),
                    match_time,
                    venue[0],
                    10 + (i % 6),
                    'Vijayawada',
                    venue[1],
                    venue[2],
                    'intermediate' if i % 3 != 0 else 'beginner',
                    'all',
                    'completed'
                ))

            cur = mysql.connection.cursor()
            for m in completed_matches:
                try:
                    cur.execute("""
                        INSERT INTO matches
                            (creator_id, sport_type, sport_name, match_date, match_time, venue_name, max_players, location, latitude, longitude, skill_level, gender_preference, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, m)
                except Exception as e:
                    print(f"  Error inserting completed match: {e}")

            mysql.connection.commit()
            cur.close()
            print(f"  Added {len(completed_matches)} completed matches.")
        else:
            print(f"Completed matches already exist ({completed_count}). Skipping.")

        # 6. LEADERBOARD POINTS
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM match_results_new")
        results_count = cur.fetchone()['cnt']
        cur.close()

        if results_count == 0:
            print("\nLeaderboard is empty. Generating points for players...")
            cur = mysql.connection.cursor()
            cur.execute("SELECT id FROM users ORDER BY id ASC LIMIT 15")
            users = cur.fetchall()
            cur.close()

            if users:
                points_map = {
                    1: 1850, 2: 1760, 3: 1695, 4: 1610, 5: 1540,
                    6: 1480, 7: 1420, 8: 1360, 9: 1290, 10: 1220,
                    11: 1150, 12: 1080, 13: 1010, 14: 940, 15: 870
                }

                # Get all match IDs
                cur = mysql.connection.cursor()
                cur.execute("SELECT id FROM matches WHERE status = 'completed' ORDER BY id ASC")
                match_rows = cur.fetchall()
                cur.close()

                if match_rows and len(match_rows) >= 2:
                    import random
                    random.seed(42)

                    for idx, user in enumerate(users[:15]):
                        user_id = user['id']
                        target_points = points_map.get(idx + 1, 500)
                        matches_to_use = random.sample(match_rows, min(8, len(match_rows)))

                        points_per_match = target_points // 10
                        cur = mysql.connection.cursor()
                        for match in matches_to_use:
                            points = points_per_match + random.randint(-2, 2)
                            if points < 0:
                                points = 0
                            try:
                                cur.execute("""
                                    INSERT IGNORE INTO match_results_new (match_id, user_id, points_awarded, admin_adjustment)
                                    VALUES (%s, %s, %s, 0)
                                """, (match['id'], user_id, points))
                            except Exception as e:
                                print(f"  Error inserting match result: {e}")

                        mysql.connection.commit()
                        cur.close()
                    print(f"  Leaderboard populated with points for {len(users[:15])} users.")
                else:
                    print("  No completed matches found for leaderboard. Run this after matches are created.")
            else:
                print("  No users found.")
        else:
            print(f"\nLeaderboard already has {results_count} results. Skipping.")

        # 7. SEASONAL LEADERBOARD DATA
        print("\nPopulating seasonal leaderboard with demo data...")
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM seasonal_leaderboard")
        seasonal_count = cur.fetchone()['cnt']
        cur.close()

        # Always refresh seasonal leaderboard with demo data
        print(f"  Refreshing seasonal leaderboard ({seasonal_count} existing entries)...")
        
        # Clear existing seasonal leaderboard data
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM seasonal_leaderboard")
        mysql.connection.commit()
        cur.close()

        # Get all users with their stats from match_results_new
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT 
                u.id as user_id,
                u.name as user_name,
                COALESCE(SUM(mr.points_awarded), 0) as lifetime_points,
                COUNT(DISTINCT mr.match_id) as matches_played,
                COUNT(DISTINCT CASE WHEN mr.points_awarded >= 10 THEN mr.match_id END) as wins,
                COUNT(DISTINCT CASE WHEN mr.points_awarded = 0 AND mr.match_id IS NOT NULL THEN mr.match_id END) as losses,
                COUNT(DISTINCT CASE WHEN mr.points_awarded = 5 THEN mr.match_id END) as draws
            FROM users u
            LEFT JOIN match_results_new mr ON u.id = mr.user_id
            GROUP BY u.id, u.name
            ORDER BY lifetime_points DESC
        """)
        user_stats = cur.fetchall()
        cur.close()

        if user_stats:
            import random
            random.seed(42)

            # Compute date ranges in Python to avoid MySQL format issues
            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            month_start = today.replace(day=1)
            if today.month == 12:
                month_end = today.replace(year=today.year + 1, month=1, day=1)
            else:
                month_end = today.replace(month=today.month + 1, day=1)
            month_end = month_end - timedelta(days=1)

            weekly_date_start = week_start.strftime('%Y-%m-%d')
            weekly_date_end = week_end.strftime('%Y-%m-%d')
            monthly_date_start = month_start.strftime('%Y-%m-%d')
            monthly_date_end = month_end.strftime('%Y-%m-%d')

            # Build all INSERT statements
            weekly_inserts = []
            monthly_inserts = []
            lifetime_inserts = []

            for idx, stat in enumerate(user_stats):
                user_id = stat['user_id']
                user_name = stat['user_name']
                lifetime_points = stat['lifetime_points']

                # Convert to float for calculations
                lifetime_points_float = float(lifetime_points)

                # For users with 0 lifetime points, assign realistic demo points
                if lifetime_points_float == 0:
                    # Scale demo points based on rank position
                    demo_points_map = {
                        1: 1850, 2: 1760, 3: 1695, 4: 1610, 5: 1540,
                        6: 1480, 7: 1420, 8: 1360, 9: 1290, 10: 1220,
                        11: 1150, 12: 1080, 13: 1010, 14: 940, 15: 870,
                        16: 800, 17: 750, 18: 700, 19: 650, 20: 600,
                        21: 550, 22: 500, 23: 450, 24: 400
                    }
                    lifetime_points_float = demo_points_map.get(idx + 1, 350)

                # Generate weekly points (35-55% of lifetime)
                weekly_points = int(lifetime_points_float * random.uniform(0.35, 0.55))

                # Generate monthly points (65-85% of lifetime)
                monthly_points = int(lifetime_points_float * random.uniform(0.65, 0.85))

                # Ensure monthly >= weekly
                if monthly_points < weekly_points:
                    monthly_points = weekly_points

                matches_played = stat['matches_played']
                wins = stat['wins']
                losses = stat['losses']
                draws = stat['draws']
                
                # If no matches, create realistic match stats
                if matches_played == 0:
                    matches_played = random.randint(20, 100)
                    wins = int(matches_played * random.uniform(0.4, 0.7))
                    losses = int(matches_played * random.uniform(0.2, 0.4))
                    draws = matches_played - wins - losses
                    if draws < 0:
                        draws = 0
                        losses = matches_played - wins

                win_rate = round((wins / matches_played * 100) if matches_played > 0 else 0, 2)

                weekly_inserts.append((weekly_date_start, weekly_date_end, user_id, weekly_points, matches_played, wins, losses, draws, win_rate))
                monthly_inserts.append((monthly_date_start, monthly_date_end, user_id, monthly_points, matches_played, wins, losses, draws, win_rate))
                lifetime_inserts.append(('2000-01-01', '2099-12-31', user_id, lifetime_points, matches_played, wins, losses, draws, win_rate))

            # Use executemany for batch inserts to avoid SQL injection and format issues
            weekly_sql = """
                INSERT INTO seasonal_leaderboard
                    (period_type, period_start, period_end, user_id, points, matches_played, wins, losses, draws, win_rate, rank_position, is_current)
                VALUES ('weekly', %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, TRUE)
            """
            monthly_sql = """
                INSERT INTO seasonal_leaderboard
                    (period_type, period_start, period_end, user_id, points, matches_played, wins, losses, draws, win_rate, rank_position, is_current)
                VALUES ('monthly', %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, TRUE)
            """
            lifetime_sql = """
                INSERT INTO seasonal_leaderboard
                    (period_type, period_start, period_end, user_id, points, matches_played, wins, losses, draws, win_rate, rank_position, is_current)
                VALUES ('lifetime', %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, TRUE)
            """

            cur = mysql.connection.cursor()
            try:
                cur.executemany(weekly_sql, weekly_inserts)
                mysql.connection.commit()
            except Exception as e:
                print(f"  Error in weekly batch: {e}")
                mysql.connection.rollback()
            cur.close()

            cur = mysql.connection.cursor()
            try:
                cur.executemany(monthly_sql, monthly_inserts)
                mysql.connection.commit()
            except Exception as e:
                print(f"  Error in monthly batch: {e}")
                mysql.connection.rollback()
            cur.close()

            cur = mysql.connection.cursor()
            try:
                cur.executemany(lifetime_sql, lifetime_inserts)
                mysql.connection.commit()
            except Exception as e:
                print(f"  Error in lifetime batch: {e}")
                mysql.connection.rollback()
            cur.close()

            # Set ranks for each period type using separate queries
            for period in ['weekly', 'monthly', 'lifetime']:
                cur = mysql.connection.cursor()
                try:
                    cur.execute("SET @rank = 0")
                    cur.execute("""
                        UPDATE seasonal_leaderboard sl
                        INNER JOIN (
                            SELECT id, (@rank := @rank + 1) as new_rank
                            FROM seasonal_leaderboard
                            WHERE period_type = %s AND is_current = TRUE
                            ORDER BY points DESC, wins DESC
                        ) ranked ON sl.id = ranked.id
                        SET sl.rank_position = ranked.new_rank
                        WHERE sl.period_type = %s AND sl.is_current = TRUE
                    """, (period, period))
                    mysql.connection.commit()
                except Exception as e:
                    print(f"  Error setting ranks for {period}: {e}")
                    mysql.connection.rollback()
                cur.close()
            print(f"  Seasonal leaderboard refreshed with demo data for {len(user_stats)} users.")
        else:
            print("  No user stats found.")

        # 8. BADGES AND ACHIEVEMENTS
        print("\nPopulating badges and achievements...")
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM badges")
        badges_count = cur.fetchone()['cnt']
        cur.close()

        if badges_count == 0:
            print("  Inserting badge definitions...")
            badges = [
                ('first_match', 'First Match', 'Completed your first match', 'bi-trophy-fill', 'matches_played', 1),
                ('matches_5', '5 Matches Played', 'Played 5 matches', 'bi-trophy-fill', 'matches_played', 5),
                ('matches_10', '10 Matches Played', 'Played 10 matches', 'bi-trophy-fill', 'matches_played', 10),
                ('first_win', 'First Victory', 'Won your first match', 'bi-star-fill', 'wins', 1),
                ('wins_5', '5 Wins', 'Won 5 matches', 'bi-star-fill', 'wins', 5),
                ('weekly_top', 'Weekly Top Player', 'Ranked #1 this week', 'bi-calendar-week-fill', 'weekly_top', 1),
                ('monthly_top', 'Monthly Top Player', 'Ranked #1 this month', 'bi-calendar-month-fill', 'monthly_top', 1),
                ('mvp', 'Most Valuable Player', 'Earned MVP in a match', 'bi-award-fill', 'custom', 1),
                ('tournament_champion', 'Tournament Champion', 'Won a tournament', 'bi-trophy-fill', 'tournaments_won', 1),
                ('rising_star', 'Rising Star', 'Showed exceptional improvement', 'bi-arrow-up-circle-fill', 'custom', 1),
            ]

            cur = mysql.connection.cursor()
            for b in badges:
                try:
                    cur.execute("""
                        INSERT IGNORE INTO badges (badge_code, badge_name, description, icon, criteria_type, criteria_value)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, b)
                except Exception as e:
                    print(f"  Error inserting badge {b[0]}: {e}")
            mysql.connection.commit()
            cur.close()
            print(f"  Inserted {len(badges)} badges.")

        # 9. USER BADGES
        print("\nAssigning badges to users...")
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM user_badges")
        user_badges_count = cur.fetchone()['cnt']
        cur.close()

        if user_badges_count == 0:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id FROM users LIMIT 10")
            users = cur.fetchall()
            cur.close()

            if users:
                badge_assignments = [
                    (1, 'first_match'), (1, 'mvp'), (1, 'weekly_top'),
                    (2, 'first_match'), (2, 'first_win'),
                    (3, 'first_match'), (3, 'rising_star'),
                    (4, 'first_match'), (4, 'wins_5'),
                    (5, 'first_match'), (5, 'mvp'), (5, 'monthly_top'),
                    (6, 'first_match'), (6, 'matches_5'),
                    (7, 'first_match'), (7, 'first_win'),
                    (8, 'first_match'), (8, 'rising_star'),
                    (9, 'first_match'), (9, 'matches_5'),
                    (10, 'first_match'), (10, 'first_win'), (10, 'weekly_top'),
                ]

                import random
                random.seed(42)
                badge_codes = ['first_match', 'matches_5', 'first_win', 'wins_5', 'weekly_top', 'monthly_top', 'mvp', 'rising_star']

                cur = mysql.connection.cursor()
                assignments_count = 0
                for idx, user in enumerate(users):
                    user_id = user['id']
                    num_badges = random.randint(2, 4)
                    selected_badges = random.sample(badge_codes, min(num_badges, len(badge_codes)))
                    for badge_code in selected_badges:
                        try:
                            cur.execute("""
                                INSERT IGNORE INTO user_badges (user_id, badge_code, awarded_at)
                                VALUES (%s, %s, NOW())
                            """, (user_id, badge_code))
                            assignments_count += 1
                        except Exception as e:
                            print(f"  Error assigning badge: {e}")

                mysql.connection.commit()
                cur.close()
                print(f"  Assigned {assignments_count} badges to users.")

        # 10. FOLLOWERS DATA
        print("\nPopulating followers data...")
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM followers")
        followers_count = cur.fetchone()['cnt']
        cur.close()

        if followers_count < 50:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id FROM users ORDER BY id ASC LIMIT 15")
            users = cur.fetchall()
            cur.close()

            if users:
                import random
                random.seed(42)

                follower_pairs = []
                user_ids = [u['id'] for u in users]

                for follower in user_ids:
                    num_following = random.randint(3, 8)
                    following_targets = random.sample([uid for uid in user_ids if uid != follower], min(num_following, len(user_ids) - 1))
                    for target in following_targets:
                        follower_pairs.append((follower, target))

                cur = mysql.connection.cursor()
                inserted = 0
                for pair in follower_pairs:
                    try:
                        cur.execute("""
                            INSERT IGNORE INTO followers (follower_id, following_id, created_at)
                            VALUES (%s, %s, NOW())
                        """, (pair[0], pair[1]))
                        inserted += 1
                    except Exception as e:
                        print(f"  Error inserting follower: {e}")

                mysql.connection.commit()
                cur.close()
                print(f"  Inserted {inserted} follower relationships.")
        else:
            print(f"  Followers already exist ({followers_count}). Skipping.")

        print("\n" + "=" * 50)
        print("Demo data seeding complete!")
        print("=" * 50)


if __name__ == '__main__':
    seed_demo_data()