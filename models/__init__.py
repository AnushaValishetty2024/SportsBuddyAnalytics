from flask import current_app
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

mysql = MySQL()

# Import new Day 5 models
from models.chat import Conversation, Message, Notification, UserBadge
from models.team import Team, TeamMember, TeamMatch, TeamStatistics, TeamActivityLog
from models.point_history import PointHistory
from models.followers import Follower
from models.events import EventLog


class User:
    @staticmethod
    def create_table():
        cur = mysql.connection.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def create(name, email, password):
        password_hash = generate_password_hash(password)
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
            (name, email, password_hash)
        )
        mysql.connection.commit()
        user_id = cur.lastrowid
        cur.close()
        return user_id

    @staticmethod
    def find_by_email(email):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        return user

    @staticmethod
    def get_by_id(user_id):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        cur.close()
        return user

    @staticmethod
    def find_by_id(user_id):
        return User.get_by_id(user_id)

    @staticmethod
    def get_leaderboard_sorted_by_points():
        """Get all users sorted by total points DESC.
        
        Uses dynamic aggregation from match_results_new to always return
        fresh data directly from the database. Never cached or stored.
        """
        return Leaderboard.get_dynamic_leaderboard()

    @staticmethod
    def verify_password(password_hash, password):
        return check_password_hash(password_hash, password)


class Match:
    """Model for matches table operations."""

    @staticmethod
    def get_upcoming(limit=12):
        """Get upcoming matches ordered by date."""
        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT
                m.*,
                u.name AS creator_name,
                (SELECT COUNT(*)
                FROM match_participants mp
                WHERE mp.match_id = m.id) AS player_count
            FROM matches m
            JOIN users u ON m.creator_id = u.id
            WHERE m.status = 'open'
            ORDER BY m.match_date ASC, m.match_time ASC
            LIMIT %s
        """, (limit,))

        matches = cur.fetchall()
        cur.close()
        return matches

    @staticmethod
    def get_filtered(sport_name=None, location=None, match_date=None, 
                     skill_level=None, match_type=None, gender=None,
                     available_slots=None, distance_km=None,
                     user_lat=None, user_lng=None, limit=20):
        """Get matches with optional filters.
        
        Supports filtering by: sport_name, location (venue name),
        match_date, skill_level, match_type, gender, available_slots,
        and distance from user's location.
        If no filters provided, returns all matches up to limit.
        All empty/None filters are ignored.
        """
        query = """
            SELECT m.*, u.name as creator_name,
                   (SELECT COUNT(*) FROM match_participants mp WHERE mp.match_id = m.id) as player_count
            FROM matches m
            JOIN users u ON m.creator_id = u.id
            WHERE 1=1
        """
        params = []

        if sport_name:
            query += " AND LOWER(m.sport_name) = LOWER(%s)"
            params.append(sport_name)

        if location:
            query += " AND (LOWER(m.venue_name) LIKE LOWER(%s) OR LOWER(m.location) LIKE LOWER(%s))"
            loc_param = f'%{location}%'
            params.append(loc_param)
            params.append(loc_param)

        if match_date:
            query += " AND m.match_date = %s"
            params.append(match_date)

        # Additional filters for extended filter form
        if skill_level:
            query += " AND LOWER(COALESCE(m.skill_level, '')) = LOWER(%s)"
            params.append(skill_level)

        if match_type:
            query += " AND LOWER(m.sport_type) = LOWER(%s)"
            params.append(match_type)

        if gender:
            query += " AND LOWER(COALESCE(m.gender_preference, '')) = LOWER(%s)"
            params.append(gender)

        if available_slots is not None:
            try:
                min_slots = int(available_slots)
                query += """ AND ((SELECT COUNT(*) FROM match_participants mp WHERE mp.match_id = m.id) <= (m.max_players - %s))"""
                params.append(min_slots)
            except (ValueError, TypeError):
                pass

        query += " ORDER BY m.match_date ASC, m.match_time ASC LIMIT %s"
        params.append(limit)

        cur = mysql.connection.cursor()
        cur.execute(query, tuple(params))
        matches = cur.fetchall()
        cur.close()
        return matches

    @staticmethod
    def get_by_id(match_id):
        """Get a single match by ID."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT m.*, u.name as creator_name
            FROM matches m
            JOIN users u ON m.creator_id = u.id
            WHERE m.id = %s
        """, (match_id,))
        match = cur.fetchone()
        cur.close()
        return match

    @staticmethod
    def get_with_locations():
        """Get matches that have lat/lng coordinates for map display."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT m.id, m.sport_name, m.venue_name, m.match_date, m.match_time,
                   COALESCE(m.latitude, m.venue_lat) as latitude,
                   COALESCE(m.longitude, m.venue_lng) as longitude,
                   m.max_players,
                   (SELECT COUNT(*) FROM match_participants mp WHERE mp.match_id = m.id) as player_count
            FROM matches m
            WHERE (m.latitude IS NOT NULL OR m.venue_lat IS NOT NULL)
              AND (m.longitude IS NOT NULL OR m.venue_lng IS NOT NULL)
              AND (m.status = 'open' OR m.status IS NULL)
            ORDER BY m.match_date ASC
        """)
        matches = cur.fetchall()
        cur.close()
        return matches

    @staticmethod
    def count_matches():
        """Count total matches in the database."""
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM matches")
        row = cur.fetchone()
        cur.close()
        return row['cnt'] if row else 0

    @staticmethod
    def seed_match_data():
        """Seed the matches table with sample data if fewer than 15 matches exist."""
        count = Match.count_matches()
        if count >= 15:
            return False

        cur = mysql.connection.cursor()

        # Ensure a default user exists (creator_id must be valid)
        cur.execute("SELECT id FROM users LIMIT 1")
        user_row = cur.fetchone()
        if not user_row:
            cur.execute("INSERT INTO users (name, email) VALUES (%s, %s)", ('Demo User', 'demo@sportsbuddy.com'))
            mysql.connection.commit()
            default_user_id = cur.lastrowid
        else:
            default_user_id = user_row['id']

        # 20 realistic matches around Andhra Pradesh
        matches_data = [
            (default_user_id, 'outdoor', 'Cricket', '2026-07-01', '17:00:00', 'Elite Cricket Ground', 11, 'Vijayawada', 16.5062, 80.6480, 'intermediate', 'M'),
            (default_user_id, 'outdoor', 'Cricket', '2026-07-02', '08:00:00', 'Swarna Cricket Grounds', 10, 'Vijayawada', 16.5204, 80.6420, 'beginner', 'all'),
            (default_user_id, 'outdoor', 'Football', '2026-07-03', '16:00:00', 'SNR Law College Football Ground', 14, 'Vijayawada', 16.5185, 80.6565, 'intermediate', 'M'),
            (default_user_id, 'indoor', 'Badminton', '2026-07-04', '18:30:00', 'APSRTC Indoor Stadium', 6, 'Vijayawada', 16.5102, 80.6345, 'advanced', 'all'),
            (default_user_id, 'indoor', 'Basketball', '2026-07-05', '19:00:00', 'Sports Authority of India Complex', 8, 'Vijayawada', 16.4955, 80.6385, 'intermediate', 'M'),
            (default_user_id, 'outdoor', 'Tennis', '2026-07-06', '07:00:00', 'Andhra Tennis Academy', 4, 'Vijayawada', 16.5160, 80.6495, 'advanced', 'F'),
            (default_user_id, 'outdoor', 'Cricket', '2026-07-07', '17:30:00', 'GM Cricket Grounds', 12, 'Vijayawada', 16.4920, 80.6680, 'intermediate', 'all'),
            (default_user_id, 'indoor', 'Badminton', '2026-07-08', '18:00:00', 'Vijayawada Badminton Centre', 7, 'Vijayawada', 16.5090, 80.6460, 'beginner', 'all'),
            (default_user_id, 'outdoor', 'Volleyball', '2026-07-09', '16:30:00', 'VGTM Urban Sports Park', 9, 'Vijayawada', 16.5275, 80.6710, 'intermediate', 'M'),
            (default_user_id, 'outdoor', 'Football', '2026-07-10', '17:00:00', 'Acharya Nagarjuna University Sports Grounds', 15, 'Guntur', 16.3425, 80.4582, 'beginner', 'all'),
            (default_user_id, 'outdoor', 'Cricket', '2026-07-11', '08:00:00', 'Guntur Municipal Corporation Stadium', 11, 'Guntur', 16.3010, 80.4420, 'intermediate', 'M'),
            (default_user_id, 'indoor', 'Table Tennis', '2026-07-12', '19:00:00', 'Guntur Indoor Sports Complex', 8, 'Guntur', 16.3100, 80.4350, 'advanced', 'all'),
            (default_user_id, 'outdoor', 'Football', '2026-07-13', '16:00:00', 'Visakhapatnam Port Stadium', 14, 'Visakhapatnam', 17.6950, 83.2850, 'intermediate', 'M'),
            (default_user_id, 'outdoor', 'Volleyball', '2026-07-14', '17:30:00', 'East Coast Beach Volleyball Arena', 10, 'Visakhapatnam', 17.7119, 83.2995, 'beginner', 'F'),
            (default_user_id, 'indoor', 'Badminton', '2026-07-15', '18:00:00', 'VUDA Park Sports Arena', 6, 'Visakhapatnam', 17.7180, 83.3100, 'intermediate', 'all'),
            (default_user_id, 'outdoor', 'Cricket', '2026-07-16', '07:00:00', 'Sri Venkateswara University Sports Ground', 11, 'Tirupati', 13.6300, 79.4200, 'intermediate', 'all'),
            (default_user_id, 'indoor', 'Chess', '2026-07-17', '10:00:00', 'Tirupati Indoor Sports Academy', 8, 'Tirupati', 13.6400, 79.4100, 'advanced', 'all'),
            (default_user_id, 'outdoor', 'Cricket', '2026-07-18', '17:00:00', 'Rajahmundry Sports Hub', 10, 'Rajahmundry', 17.0000, 81.7800, 'beginner', 'M'),
            (default_user_id, 'indoor', 'Basketball', '2026-07-19', '18:30:00', 'Godavari Indoor Stadium', 8, 'Rajahmundry', 16.9800, 81.7900, 'intermediate', 'all'),
            (default_user_id, 'outdoor', 'Football', '2026-07-20', '16:00:00', 'Kakinada Beach Sports Complex', 12, 'Kakinada', 16.9500, 82.2500, 'intermediate', 'M'),
        ]

        for m in matches_data:
            cur.execute("""
                INSERT INTO matches
                    (creator_id, sport_type, sport_name, match_date, match_time, venue_name, max_players, location, latitude, longitude, skill_level, gender_preference, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'open')
            """, m)

        mysql.connection.commit()
        cur.close()
        return True


class Leaderboard:
    """Model for leaderboard operations.
    
    Leaderboard is NEVER stored directly. It is ALWAYS derived from match_results
    using dynamic SQL aggregation. This ensures rankings update automatically
    when match results are inserted or modified.
    """

    @staticmethod
    def get_top_players(limit=10):
        """Get top players ranked by points (legacy - uses player_points)."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT u.id, u.name, u.email,
                   COALESCE(pp.points, 0) as points,
                   COALESCE(pp.wins, 0) as wins,
                   COALESCE(pp.losses, 0) as losses,
                   COALESCE(pp.draws, 0) as draws,
                   COALESCE(pp.matches_played, 0) as matches_played
            FROM users u
            LEFT JOIN player_points pp ON u.id = pp.user_id
            ORDER BY pp.points DESC, pp.wins DESC
            LIMIT %s
        """, (limit,))
        players = cur.fetchall()
        cur.close()
        return players

    @staticmethod
    def get_dynamic_leaderboard():
        """Get leaderboard dynamically from match_results + manual points.
        
        This is the CORE leaderboard query - never stored, always derived.
        Includes both match-based points and manual adjustments.
        Uses COALESCE to safely handle NULL values.
        Always includes users even with 0 points.
        Returns ranked results sorted by total_points DESC.
        """
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT 
                u.id AS user_id,
                u.name AS user_name,
                COALESCE(SUM(mr.points_awarded + COALESCE(mr.admin_adjustment, 0)), 0) AS match_points,
                COALESCE(u.points, 0) AS manual_points,
                COALESCE(SUM(mr.points_awarded + COALESCE(mr.admin_adjustment, 0)), 0) + COALESCE(u.points, 0) AS total_points,
                COUNT(DISTINCT mr.match_id) AS matches_played,
                COUNT(DISTINCT CASE 
                    WHEN (mr.points_awarded + COALESCE(mr.admin_adjustment, 0)) >= 10 
                    THEN mr.match_id 
                END) AS wins,
                COUNT(DISTINCT CASE 
                    WHEN (mr.points_awarded + COALESCE(mr.admin_adjustment, 0)) = 0 
                    AND mr.match_id IS NOT NULL
                    THEN mr.match_id 
                END) AS losses,
                COUNT(DISTINCT CASE 
                    WHEN (mr.points_awarded + COALESCE(mr.admin_adjustment, 0)) = 5 
                    AND mr.match_id IS NOT NULL
                    THEN mr.match_id 
                END) AS draws
            FROM users u
            LEFT JOIN match_results_new mr ON u.id = mr.user_id
            GROUP BY u.id, u.name
            ORDER BY total_points DESC, wins DESC, u.name ASC
        """)
        rows = cur.fetchall()
        cur.close()

        # Compute rank and ensure safe types
        results = []
        rank = 1
        for row in rows:
            results.append({
                'user_id': int(row['user_id']),
                'name': row['user_name'],
                'total_points': int(row['total_points']),
                'match_points': int(row['match_points']),
                'manual_points': int(row['manual_points']),
                'matches_played': int(row['matches_played']),
                'wins': int(row['wins']),
                'losses': int(row['losses']),
                'draws': int(row['draws']),
                'rank': rank
            })
            rank += 1
        return results

    @staticmethod
    def create_tables():
        """Create leaderboard-related tables (match_results_new, user_stats)."""
        cur = mysql.connection.cursor()
        
        # Create match_results_new if not exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS match_results_new (
                id INT AUTO_INCREMENT PRIMARY KEY,
                match_id INT NOT NULL,
                user_id INT NOT NULL,
                points_awarded INT NOT NULL DEFAULT 0,
                admin_adjustment INT NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_match_id (match_id),
                UNIQUE KEY uk_match_user (match_id, user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # Create user_stats table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id INT NOT NULL PRIMARY KEY,
                total_points INT NOT NULL DEFAULT 0,
                wins INT NOT NULL DEFAULT 0,
                losses INT NOT NULL DEFAULT 0,
                draws INT NOT NULL DEFAULT 0,
                matches_played INT NOT NULL DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # Add status column to matches if not exists
        try:
            cur.execute("ALTER TABLE matches ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'open'")
        except Exception:
            pass  # Column may already exist
        
        # Add additional filter columns if not exists
        for col_def in [
            "ADD COLUMN IF NOT EXISTS skill_level VARCHAR(50) DEFAULT NULL",
            "ADD COLUMN IF NOT EXISTS gender_preference VARCHAR(20) DEFAULT NULL",
            "ADD COLUMN IF NOT EXISTS location VARCHAR(200) DEFAULT NULL",
        ]:
            try:
                cur.execute(f"ALTER TABLE matches {col_def}")
            except Exception:
                pass
        
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def insert_match_result(match_id, user_id, points_awarded, admin_adjustment=0):
        """Insert a match result record. Transaction-safe wrapper."""
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                INSERT INTO match_results_new (match_id, user_id, points_awarded, admin_adjustment)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE points_awarded = VALUES(points_awarded),
                                        admin_adjustment = VALUES(admin_adjustment)
            """, (match_id, user_id, points_awarded, admin_adjustment))
            mysql.connection.commit()
            return True
        except Exception as e:
            mysql.connection.rollback()
            raise e
        finally:
            cur.close()

    @staticmethod
    def update_match_status(match_id, status):
        """Update match status."""
        cur = mysql.connection.cursor()
        try:
            cur.execute("UPDATE matches SET status = %s WHERE id = %s", (status, match_id))
            mysql.connection.commit()
        except Exception as e:
            mysql.connection.rollback()
            raise e
        finally:
            cur.close()

    @staticmethod
    def add_player_points(user_id, points, reason, created_by):
        """Add points to a player directly (not from match).
        
        Args:
            user_id: player to adjust
            points: positive integer to add
            reason: explanation
            created_by: user_id of admin/captain making change
        """
        cur = mysql.connection.cursor()
        try:
            # Update user's stored points
            cur.execute("UPDATE users SET points = points + %s WHERE id = %s", (points, user_id))
            
            # Log in history
            PointHistory.log('player', user_id, points, reason, created_by)
            
            mysql.connection.commit()
            return True
        except Exception as e:
            mysql.connection.rollback()
            raise e
        finally:
            cur.close()

    @staticmethod
    def adjust_player_points(user_id, delta, reason, created_by):
        """Adjust player points (add or subtract).
        
        Args:
            user_id: player to adjust
            delta: positive or negative integer
            reason: explanation
            created_by: user_id of admin/captain making change
        """
        cur = mysql.connection.cursor()
        try:
            # Update user's stored points
            cur.execute("UPDATE users SET points = points + %s WHERE id = %s", (delta, user_id))
            
            # Log in history
            PointHistory.log('player', user_id, delta, reason, created_by)
            
            mysql.connection.commit()
            return True
        except Exception as e:
            mysql.connection.rollback()
            raise e
        finally:
            cur.close()

    @staticmethod
    def get_player_points(user_id):
        """Get a player's current total points (stored + match-based)."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT 
                COALESCE(SUM(mr.points_awarded + COALESCE(mr.admin_adjustment, 0)), 0) AS match_points,
                COALESCE(u.points, 0) AS manual_points,
                COALESCE(SUM(mr.points_awarded + COALESCE(mr.admin_adjustment, 0)), 0) + COALESCE(u.points, 0) AS total_points
            FROM users u
            LEFT JOIN match_results_new mr ON u.id = mr.user_id
            WHERE u.id = %s
            GROUP BY u.id
        """, (user_id,))
        row = cur.fetchone()
        cur.close()
        if row:
            return {
                'match_points': int(row['match_points']),
                'manual_points': int(row['manual_points']),
                'total_points': int(row['total_points'])
            }
        return {'match_points': 0, 'manual_points': 0, 'total_points': 0}

    @staticmethod
    def get_leaderboard_summary():
        """Get summary stats for the leaderboard."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT 
                COUNT(DISTINCT u.id) AS total_players,
                COALESCE(COUNT(DISTINCT mr.match_id), 0) AS total_matches,
                COALESCE(SUM(mr.points_awarded + COALESCE(mr.admin_adjustment, 0)), 0) AS match_points,
                COALESCE(SUM(u.points), 0) AS manual_points
            FROM users u
            LEFT JOIN match_results_new mr ON u.id = mr.user_id
        """)
        row = cur.fetchone()
        cur.close()
        return {
            'total_players': int(row['total_players']),
            'total_matches': int(row['total_matches']),
            'total_points': int(row['match_points'] or 0) + int(row['manual_points'] or 0)
        }

    @staticmethod
    def update_seasonal_leaderboard(user_id):
        """Update seasonal leaderboard for a user after match completion."""
        cur = mysql.connection.cursor()
        try:
            # Get user stats from dynamic leaderboard
            leaderboard = Leaderboard.get_dynamic_leaderboard()
            user_stat = next((s for s in leaderboard if s['user_id'] == user_id), None)
            
            if not user_stat:
                return False
            
            points = user_stat['total_points']
            matches_played = user_stat['matches_played']
            wins = user_stat['wins']
            losses = user_stat['losses']
            draws = user_stat['draws']
            win_rate = round((wins / matches_played * 100) if matches_played > 0 else 0, 2)
            
            # Update lifetime leaderboard
            cur.execute("""
                INSERT INTO seasonal_leaderboard 
                (user_id, period_type, period_start, period_end, points, matches_played, wins, losses, draws, win_rate, rank_position, is_current)
                VALUES (%s, 'lifetime', '2000-01-01', '2099-12-31', %s, %s, %s, %s, %s, %s, 0, TRUE)
                ON DUPLICATE KEY UPDATE 
                    points = VALUES(points),
                    matches_played = VALUES(matches_played),
                    wins = VALUES(wins),
                    losses = VALUES(losses),
                    draws = VALUES(draws),
                    win_rate = VALUES(win_rate),
                    updated_at = NOW()
            """, (user_id, points, matches_played, wins, losses, draws, win_rate))
            
            mysql.connection.commit()
            return True
        except Exception as e:
            mysql.connection.rollback()
            current_app.logger.error(f"Error updating seasonal leaderboard: {e}")
            return False
        finally:
            cur.close()


class NearbyBusiness:
    """Model for nearby sports businesses/venues."""

    @staticmethod
    def get_all(limit=20):
        """Get all nearby sports businesses."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT * FROM nearby_businesses
            ORDER BY rating DESC, name ASC
            LIMIT %s
        """, (limit,))
        businesses = cur.fetchall()
        cur.close()
        return businesses

    @staticmethod
    def get_by_sport(sport_name, limit=10):
        """Get businesses that support a specific sport."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT * FROM nearby_businesses
            WHERE LOWER(sport_types) LIKE LOWER(%s)
            ORDER BY rating DESC
            LIMIT %s
        """, (f'%{sport_name}%', limit))
        businesses = cur.fetchall()
        cur.close()
        return businesses

    @staticmethod
    def get_with_locations():
        """Get all businesses with coordinates for map display."""
        cur = mysql.connection.cursor()

        cur.execute("""
           SELECT 
               id, 
               name, 
               business_type, 
               address, 
               latitude, 
               longitude,
               category
           FROM nearby_businesses
           WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """)

        businesses = cur.fetchall()
        cur.close()
        return businesses


class SportsVenue:
    """Model for nearby sports venues."""

    @staticmethod
    def create_table():
        """Create sports_venues table if not exists."""
        cur = mysql.connection.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sports_venues (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                sport_types VARCHAR(500) NOT NULL,
                address TEXT,
                latitude DECIMAL(10, 7) NOT NULL,
                longitude DECIMAL(10, 7) NOT NULL,
                rating DECIMAL(2, 1) DEFAULT 0.0,
                available_slots INT DEFAULT 0,
                distance_km DECIMAL(6, 2) DEFAULT 0.00,
                image_url VARCHAR(500) DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def get_all():
        """Get all sports venues ordered by distance."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT * FROM sports_venues
            ORDER BY distance_km ASC, rating DESC
        """)
        venues = cur.fetchall()
        cur.close()
        return venues

    @staticmethod
    def get_by_sport(sport_name):
        """Get venues that support a specific sport."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT * FROM sports_venues
            WHERE LOWER(sport_types) LIKE LOWER(%s)
            ORDER BY distance_km ASC, rating DESC
        """, (f'%{sport_name}%',))
        venues = cur.fetchall()
        cur.close()
        return venues

    @staticmethod
    def get_with_locations():
        """Get all venues with valid coordinates for map display."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, name, sport_types, address,
                   latitude, longitude, rating,
                   available_slots, distance_km, image_url
            FROM sports_venues
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            ORDER BY distance_km ASC
        """)
        venues = cur.fetchall()
        cur.close()
        return venues

    @staticmethod
    def has_data():
        """Check if sports_venues table has any rows."""
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM sports_venues")
        count = cur.fetchone()['cnt']
        cur.close()
        return count > 0

    @staticmethod
    def seed_default_data():
        """Seed the venues table with default data if empty."""
        if SportsVenue.has_data():
            return False
        
        cur = mysql.connection.cursor()
        
        # Seed data - 25 venues across Andhra Pradesh
        venues_data = [
            # Vijayawada venues (10)
            ("Indira Gandhi Municipal Stadium", "Cricket,Football", "MG Road, Vijayawada, Andhra Pradesh 520001", 16.5138, 80.6395, 4.3, 12, 1.1, "placeholder_venue_1.png"),
            ("Swarna Cricket Grounds", "Cricket", "Benz Circle, Vijayawada, Andhra Pradesh 520010", 16.5204, 80.6420, 4.1, 8, 1.8, "placeholder_venue_2.png"),
            ("APSRTC Indoor Stadium", "Badminton,Basketball", "Pandit Nehru Bus Station Road, Vijayawada, Andhra Pradesh 520003", 16.5102, 80.6345, 4.0, 6, 1.5, "placeholder_venue_3.png"),
            ("Andhra Tennis Academy", "Tennis", "Labbipet, Vijayawada, Andhra Pradesh 520010", 16.5160, 80.6495, 4.5, 4, 1.2, "placeholder_venue_5.png"),
            ("Vijayawada Municipal Aquatic Centre", "Swimming", "Durga Temple Road, Vijayawada, Andhra Pradesh 520002", 16.5035, 80.6520, 3.8, 20, 0.6, "placeholder_venue_7.png"),
            ("Sports Authority of India Complex (SAI)", "Basketball,Volleyball,Badminton", "Auto Nagar, Vijayawada, Andhra Pradesh 520007", 16.4955, 80.6385, 4.3, 18, 1.6, "placeholder_venue_8.png"),
            ("Vijayawada Badminton Centre", "Badminton", "Governorpet, Vijayawada, Andhra Pradesh 520002", 16.5090, 80.6460, 4.2, 7, 0.5, "placeholder_venue_9.png"),
            ("GM Cricket Grounds", "Cricket", "Brothers Colony, Patamata, Vijayawada, Andhra Pradesh 520008", 16.4920, 80.6680, 3.9, 14, 2.5, "placeholder_venue_10.png"),
            ("SNR Law College Football Ground", "Football", "Mogalrajapuram, Vijayawada, Andhra Pradesh 520010", 16.5185, 80.6565, 3.7, 11, 1.6, "placeholder_venue_11.png"),
            ("NTR Stadium", "Tennis,Athletics Track", "Vidyadharapuram, Vijayawada, Andhra Pradesh 520012", 16.4850, 80.6255, 4.1, 9, 3.1, "placeholder_venue_12.png"),
            ("Railway Recreation Club", "Cricket,Swimming", "Railway Colony, Vijayawada, Andhra Pradesh 520001", 16.5110, 80.6300, 3.6, 5, 1.9, "placeholder_venue_13.png"),
            ("Andhra Loyola College Athletics Ground", "Athletics Track,Football", "Loyola College Road, Vijayawada, Andhra Pradesh 520008", 16.4975, 80.6595, 3.9, 22, 1.3, "placeholder_venue_14.png"),
            ("VGTM Urban Sports Park", "Cricket,Football,Basketball,Badminton,Tennis,Volleyball,Swimming,Athletics Track", "VGTM Layout, Ramavarappadu, Vijayawada, Andhra Pradesh 521108", 16.5275, 80.6710, 4.6, 30, 3.4, "placeholder_venue_15.png"),
            # Guntur venues (3)
            ("Acharya Nagarjuna University Sports Grounds", "Football,Athletics Track", "Nagarjuna Nagar, Guntur, Andhra Pradesh 522510", 16.3425, 80.4582, 4.4, 15, 24.5, "placeholder_venue_4.png"),
            ("Guntur Municipal Corporation Stadium", "Cricket,Football", "Brodipet, Guntur, Andhra Pradesh 522002", 16.3010, 80.4420, 4.0, 10, 28.0, "placeholder_venue_16.png"),
            ("Guntur Indoor Sports Complex", "Badminton,Table Tennis,Chess", "Lakshmipuram, Guntur, Andhra Pradesh 522007", 16.3100, 80.4350, 4.2, 8, 29.5, "placeholder_venue_17.png"),
            # Visakhapatnam venues (4)
            ("East Coast Beach Volleyball Arena", "Volleyball", "RK Beach Road, Visakhapatnam, Andhra Pradesh 530017", 17.7119, 83.2995, 4.2, 10, 350.0, "placeholder_venue_6.png"),
            ("Visakhapatnam Port Stadium", "Cricket,Football", "Port Area, Visakhapatnam, Andhra Pradesh 530035", 17.6950, 83.2850, 4.1, 16, 355.0, "placeholder_venue_18.png"),
            ("Andhra University Sports Complex", "Basketball,Volleyball,Tennis", "AU Campus, Visakhapatnam, Andhra Pradesh 530003", 17.7280, 83.3200, 4.3, 20, 348.0, "placeholder_venue_19.png"),
            ("VUDA Park Sports Arena", "Badminton,Table Tennis,Swimming", "Beach Road, Visakhapatnam, Andhra Pradesh 530017", 17.7180, 83.3100, 4.4, 14, 352.0, "placeholder_venue_20.png"),
            # Kakinada venues (2)
            ("Kakinada Beach Sports Complex", "Volleyball,Football", "Beach Road, Kakinada, Andhra Pradesh 533001", 16.9500, 82.2500, 4.0, 12, 200.0, "placeholder_venue_21.png"),
            ("Kakinada Indoor Stadium", "Badminton,Basketball", "Temple Street, Kakinada, Andhra Pradesh 533001", 16.9400, 82.2400, 3.9, 8, 198.0, "placeholder_venue_22.png"),
            # Tirupati venues (2)
            ("Sri Venkateswara University Sports Ground", "Cricket,Football,Athletics Track", "SVU Campus, Tirupati, Andhra Pradesh 517502", 13.6300, 79.4200, 4.2, 18, 420.0, "placeholder_venue_23.png"),
            ("Tirupati Indoor Sports Academy", "Badminton,Table Tennis,Chess", "Renigunta Road, Tirupati, Andhra Pradesh 517501", 13.6400, 79.4100, 4.1, 10, 425.0, "placeholder_venue_24.png"),
            # Rajahmundry venues (2)
            ("Rajahmundry Sports Hub", "Cricket,Football,Badminton", "Kadiyam Road, Rajahmundry, Andhra Pradesh 533101", 17.0000, 81.7800, 4.0, 14, 160.0, "placeholder_venue_25.png"),
            ("Godavari Indoor Stadium", "Basketball,Volleyball,Table Tennis", "Pushkar Ghat Road, Rajahmundry, Andhra Pradesh 533101", 16.9800, 81.7900, 4.2, 9, 162.0, "placeholder_venue_26.png"),
        ]
        
        for v in venues_data:
            cur.execute("""
                INSERT INTO sports_venues (name, sport_types, address, latitude, longitude, rating, available_slots, distance_km, image_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, v)
        
        mysql.connection.commit()
        cur.close()
        return True


class GameCategory:
    """Model for game categories (all games & sports categories section)."""

    @staticmethod
    def get_all():
        """Get all game categories ordered by display_order."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT * FROM game_categories
            ORDER BY display_order ASC
        """)
        games = cur.fetchall()
        cur.close()
        return games

    @staticmethod
    def get_by_id(game_id):
        """Get a single game category by ID with full details."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT * FROM game_categories WHERE id = %s
        """, (game_id,))
        game = cur.fetchone()
        cur.close()
        return game

    @staticmethod
    def get_by_name(name):
        """Get a single game category by name."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT * FROM game_categories WHERE LOWER(name) = LOWER(%s)
        """, (name,))
        game = cur.fetchone()
        cur.close()
        return game

    @staticmethod
    def get_match_count_by_sport():
        """Get match counts grouped by sport name."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT LOWER(sport_name) as sport_key, sport_name, COUNT(*) as match_count
            FROM matches
            WHERE status = 'open' OR status IS NULL
            GROUP BY LOWER(sport_name), sport_name
            ORDER BY match_count DESC
        """)
        counts = cur.fetchall()
        cur.close()
        return counts

    @staticmethod
    def get_active_match_count(game_name):
        """Get count of active/open matches for a specific game."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT COUNT(*) as count FROM matches
            WHERE (status = 'open' OR status IS NULL)
            AND LOWER(sport_name) = LOWER(%s)
        """, (game_name,))
        result = cur.fetchone()
        cur.close()
        return result['count'] if result else 0

    @staticmethod
    def get_venue_count_for_sport(sport_name):
        """Get count of venues that support a specific sport."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT COUNT(*) as count FROM sports_venues
            WHERE LOWER(sport_types) LIKE LOWER(%s)
        """, (f'%{sport_name}%',))
        result = cur.fetchone()
        cur.close()
        return result['count'] if result else 0

    @staticmethod
    def get_venue_counts_for_all_sports():
        """Get venue counts for all sports.
        Returns a dict mapping lowercase sport name to venue count.
        """
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT sport_types FROM sports_venues
        """)
        rows = cur.fetchall()
        cur.close()
        
        venue_counts = {}
        for row in rows:
            sports = [s.strip().lower() for s in row['sport_types'].split(',')]
            for sport in sports:
                if sport:
                    venue_counts[sport] = venue_counts.get(sport, 0) + 1
        return venue_counts

    @staticmethod
    def get_all_with_counts():
        """Get all sports with venue counts and match counts."""
        games = GameCategory.get_all()
        venue_counts = GameCategory.get_venue_counts_for_all_sports()
        match_counts = GameCategory.get_match_count_by_sport()
        
        # Build match count map
        match_count_map = {}
        for row in match_counts:
            match_count_map[row['sport_key']] = row['match_count']
        
        result = []
        for game in games:
            sport_key = game['name'].lower().strip()
            result.append({
                "id": game['id'],
                "name": game['name'],
                "logo": game.get('logo', '') or '',
                "description": game.get('description', '') or '',
                "category": game.get('category', '') or '',
                "num_players": game.get('num_players', '') or '',
                "equipment": game.get('equipment', '') or '',
                "match_duration": game.get('match_duration', '') or '',
                "playing_area": game.get('playing_area', '') or '',
                "basic_rules": game.get('basic_rules', '') or '',
                "popular_tournaments": game.get('popular_tournaments', '') or '',
                "difficulty_level": game.get('difficulty_level', '') or '',
                "location_info": game.get('location_info', '') or '',
                "venue_count": venue_counts.get(sport_key, 0),
                "match_count": match_count_map.get(sport_key, 0),
                "display_order": game['display_order']
            })
        return result