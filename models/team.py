from flask import current_app
from flask_mysqldb import MySQL
from datetime import datetime

mysql = MySQL()


class Team:
    """Model for teams table operations."""

    @staticmethod
    def create_table():
        """Create teams table if not exists."""
        cur = mysql.connection.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                id INT AUTO_INCREMENT PRIMARY KEY,
                team_name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT,
                sport_type VARCHAR(50) NOT NULL,
                location VARCHAR(200) NOT NULL,
                logo VARCHAR(255) DEFAULT NULL,
                captain_id INT NOT NULL,
                max_members INT NOT NULL DEFAULT 10,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (captain_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def create(team_name, description, sport_type, location, captain_id, max_members=10, logo=None):
        """Create a new team."""
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO teams (team_name, description, sport_type, location, logo, captain_id, max_members)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (team_name, description, sport_type, location, logo, captain_id, max_members))
        mysql.connection.commit()
        team_id = cur.lastrowid
        cur.close()
        return team_id

    @staticmethod
    def get_all():
        """Get all teams with captain name and member count."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT t.*, u.name as captain_name,
                   COUNT(tm.user_id) as current_members
            FROM teams t
            JOIN users u ON t.captain_id = u.id
            LEFT JOIN team_members tm ON t.id = tm.team_id
            GROUP BY t.id
            ORDER BY t.created_at DESC
        """)
        teams = cur.fetchall()
        cur.close()
        return teams

    @staticmethod
    def get_by_id(team_id):
        """Get a single team by ID."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT t.*, u.name as captain_name
            FROM teams t
            JOIN users u ON t.captain_id = u.id
            WHERE t.id = %s
        """, (team_id,))
        team = cur.fetchone()
        cur.close()
        return team

    @staticmethod
    def get_by_user(user_id):
        """Get teams that a user is a member of."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT t.*, u.name as captain_name,
                   COUNT(tm.user_id) as current_members
            FROM teams t
            JOIN users u ON t.captain_id = u.id
            JOIN team_members tm ON t.id = tm.team_id
            WHERE tm.user_id = %s
            GROUP BY t.id
            ORDER BY t.created_at DESC
        """, (user_id,))
        teams = cur.fetchall()
        cur.close()
        return teams

    @staticmethod
    def get_filtered(sport_type=None, location=None):
        """Get teams with optional filters."""
        query = """
            SELECT t.*, u.name as captain_name,
                   COUNT(tm.user_id) as current_members
            FROM teams t
            JOIN users u ON t.captain_id = u.id
            LEFT JOIN team_members tm ON t.id = tm.team_id
            WHERE 1=1
        """
        params = []

        if sport_type:
            query += " AND LOWER(t.sport_type) = LOWER(%s)"
            params.append(sport_type)

        if location:
            query += " AND LOWER(t.location) LIKE LOWER(%s)"
            params.append(f'%{location}%')

        query += " GROUP BY t.id ORDER BY t.created_at DESC"

        cur = mysql.connection.cursor()
        cur.execute(query, tuple(params))
        teams = cur.fetchall()
        cur.close()
        return teams

    @staticmethod
    def search(search_term):
        """Search teams by name."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT t.*, u.name as captain_name,
                   COUNT(tm.user_id) as current_members
            FROM teams t
            JOIN users u ON t.captain_id = u.id
            LEFT JOIN team_members tm ON t.id = tm.team_id
            WHERE LOWER(t.team_name) LIKE LOWER(%s)
            GROUP BY t.id
            ORDER BY t.created_at DESC
        """, (f'%{search_term}%',))
        teams = cur.fetchall()
        cur.close()
        return teams

    @staticmethod
    def update(team_id, team_name, description, sport_type, location, max_members, logo=None):
        """Update team details."""
        cur = mysql.connection.cursor()
        if logo:
            cur.execute("""
                UPDATE teams
                SET team_name = %s, description = %s, sport_type = %s,
                    location = %s, max_members = %s, logo = %s
                WHERE id = %s
            """, (team_name, description, sport_type, location, max_members, logo, team_id))
        else:
            cur.execute("""
                UPDATE teams
                SET team_name = %s, description = %s, sport_type = %s,
                    location = %s, max_members = %s
                WHERE id = %s
            """, (team_name, description, sport_type, location, max_members, team_id))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def delete(team_id):
        """Delete a team."""
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM teams WHERE id = %s", (team_id,))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def is_captain(team_id, user_id):
        """Check if user is the captain of the team."""
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM teams WHERE id = %s AND captain_id = %s", (team_id, user_id))
        result = cur.fetchone()
        cur.close()
        return result is not None

    @staticmethod
    def count_teams():
        """Count total teams in the database."""
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM teams")
        row = cur.fetchone()
        cur.close()
        return row['cnt'] if row else 0


class TeamMember:
    """Model for team_members table operations."""

    @staticmethod
    def create_table():
        """Create team_members table if not exists."""
        cur = mysql.connection.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS team_members (
                id INT AUTO_INCREMENT PRIMARY KEY,
                team_id INT NOT NULL,
                user_id INT NOT NULL,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_team_user (team_id, user_id),
                FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def add_member(team_id, user_id):
        """Add a member to a team."""
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                INSERT INTO team_members (team_id, user_id)
                VALUES (%s, %s)
            """, (team_id, user_id))
            mysql.connection.commit()
            
            # Log activity
            try:
                user = User.get_by_id(user_id)
                TeamActivityLog.log(team_id, 'member_joined', 
                                   f'{user["name"]} joined the team', 
                                   related_user_id=user_id)
            except Exception:
                pass  # Non-critical
            
            cur.close()
            return True
        except Exception as e:
            mysql.connection.rollback()
            cur.close()
            raise e

    @staticmethod
    def remove_member(team_id, user_id):
        """Remove a member from a team."""
        cur = mysql.connection.cursor()
        try:
            # Get user name before removal
            user = User.get_by_id(user_id)
            
            cur.execute("""
                DELETE FROM team_members
                WHERE team_id = %s AND user_id = %s
            """, (team_id, user_id))
            mysql.connection.commit()
            
            # Log activity
            try:
                TeamActivityLog.log(team_id, 'member_left', 
                                   f'{user["name"]} left the team', 
                                   related_user_id=user_id)
            except Exception:
                pass  # Non-critical
            
            cur.close()
            return True
        except Exception as e:
            mysql.connection.rollback()
            cur.close()
            raise e

    @staticmethod
    def is_member(team_id, user_id):
        """Check if user is a member of the team."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id FROM team_members
            WHERE team_id = %s AND user_id = %s
        """, (team_id, user_id))
        result = cur.fetchone()
        cur.close()
        return result is not None

    @staticmethod
    def get_members(team_id):
        """Get all members of a team with user details."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT u.id, u.name, u.email, tm.joined_at
            FROM team_members tm
            LEFT JOIN users u ON tm.user_id = u.id
            WHERE tm.team_id = %s
            ORDER BY tm.joined_at ASC
        """, (team_id,))
        members = cur.fetchall()
        cur.close()
        return members

    @staticmethod
    def get_member_count(team_id):
        """Get the number of members in a team."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT COUNT(*) as count FROM team_members
            WHERE team_id = %s
        """, (team_id,))
        row = cur.fetchone()
        cur.close()
        return row['count'] if row else 0


class TeamMatch:
    """Model for team_matches table operations."""

    @staticmethod
    def create_table():
        """Create team_matches table if not exists."""
        cur = mysql.connection.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS team_matches (
                id INT AUTO_INCREMENT PRIMARY KEY,
                team1_id INT NOT NULL,
                team2_id INT NOT NULL,
                sport_type VARCHAR(50) NOT NULL,
                venue_name VARCHAR(200) NOT NULL,
                match_date DATE NOT NULL,
                match_time TIME NOT NULL,
                team1_score INT DEFAULT NULL,
                team2_score INT DEFAULT NULL,
                winner_team_id INT DEFAULT NULL,
                is_draw TINYINT(1) NOT NULL DEFAULT 0,
                status ENUM('scheduled', 'completed', 'cancelled') DEFAULT 'scheduled',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (team1_id) REFERENCES teams(id) ON DELETE CASCADE,
                FOREIGN KEY (team2_id) REFERENCES teams(id) ON DELETE CASCADE,
                FOREIGN KEY (winner_team_id) REFERENCES teams(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def get_by_team(team_id):
        """Get all matches for a team (both as team1 and team2)."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT tm.*, 
                   t1.team_name as team1_name,
                   t2.team_name as team2_name
            FROM team_matches tm
            JOIN teams t1 ON tm.team1_id = t1.id
            JOIN teams t2 ON tm.team2_id = t2.id
            WHERE tm.team1_id = %s OR tm.team2_id = %s
            ORDER BY tm.match_date DESC, tm.match_time DESC
        """, (team_id, team_id))
        matches = cur.fetchall()
        cur.close()
        return matches

    @staticmethod
    def create(team1_id, team2_id, sport_type, venue_name, match_date, match_time):
        """Create a new team match."""
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO team_matches (team1_id, team2_id, sport_type, venue_name, match_date, match_time)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (team1_id, team2_id, sport_type, venue_name, match_date, match_time))
        mysql.connection.commit()
        match_id = cur.lastrowid
        cur.close()
        return match_id

    @staticmethod
    def record_result(match_id, team1_score, team2_score, winner_team_id=None, is_draw=False):
        """Record match result and update statistics."""
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE team_matches
            SET team1_score = %s, team2_score = %s, winner_team_id = %s, is_draw = %s, status = 'completed'
            WHERE id = %s
        """, (team1_score, team2_score, winner_team_id, 1 if is_draw else 0, match_id))
        mysql.connection.commit()
        
        # Get match details for logging
        cur.execute("SELECT team1_id, team2_id, sport_type FROM team_matches WHERE id = %s", (match_id,))
        match = cur.fetchone()
        cur.close()
        
        # Update statistics for both teams
        if match:
            try:
                team1_id = match['team1_id']
                team2_id = match['team2_id']
                
                # Update statistics
                TeamStatistics.update_from_match(team1_id, team2_id, winner_team_id, is_draw)
                
                # Log activities
                if is_draw:
                    TeamActivityLog.log(team1_id, 'match_draw', 
                        f'Drew {team1_score}-{team2_score} against team {team2_id}', 
                        related_match_id=match_id)
                    TeamActivityLog.log(team2_id, 'match_draw', 
                        f'Drew {team2_score}-{team1_score} against team {team1_id}', 
                        related_match_id=match_id)
                elif winner_team_id == team1_id:
                    TeamActivityLog.log(team1_id, 'match_won', 
                        f'Won {team1_score}-{team2_score} against team {team2_id}', 
                        related_match_id=match_id)
                    TeamActivityLog.log(team2_id, 'match_lost', 
                        f'Lost {team2_score}-{team1_score} against team {team1_id}', 
                        related_match_id=match_id)
                else:
                    TeamActivityLog.log(team1_id, 'match_lost', 
                        f'Lost {team1_score}-{team2_score} against team {team2_id}', 
                        related_match_id=match_id)
                    TeamActivityLog.log(team2_id, 'match_won', 
                        f'Won {team2_score}-{team1_score} against team {team1_id}', 
                        related_match_id=match_id)
            except Exception:
                pass  # Non-critical

    @staticmethod
    def get_with_teams(match_id):
        """Get match details with team information."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT tm.*, 
                   t1.team_name as team1_name,
                   t1.logo as team1_logo,
                   t2.team_name as team2_name,
                   t2.logo as team2_logo
            FROM team_matches tm
            JOIN teams t1 ON tm.team1_id = t1.id
            JOIN teams t2 ON tm.team2_id = t2.id
            WHERE tm.id = %s
        """, (match_id,))
        match = cur.fetchone()
        cur.close()
        return match


class TeamStatistics:
    """Model for team_statistics table operations."""

    @staticmethod
    def create_table():
        """Create team_statistics table if not exists."""
        cur = mysql.connection.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS team_statistics (
                team_id INT NOT NULL PRIMARY KEY,
                matches_played INT NOT NULL DEFAULT 0,
                wins INT NOT NULL DEFAULT 0,
                losses INT NOT NULL DEFAULT 0,
                draws INT NOT NULL DEFAULT 0,
                total_points INT NOT NULL DEFAULT 0,
                manual_adjustments INT NOT NULL DEFAULT 0,
                win_percentage DECIMAL(5,2) DEFAULT 0.00,
                avg_points_per_match DECIMAL(6,2) DEFAULT 0.00,
                current_rank INT DEFAULT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def get_by_team(team_id):
        """Get statistics for a team."""
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM team_statistics WHERE team_id = %s", (team_id,))
        stats = cur.fetchone()
        cur.close()
        return stats

    @staticmethod
    def initialize_for_team(team_id):
        """Initialize statistics record for a new team."""
        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO team_statistics (team_id) VALUES (%s)", (team_id,))
            mysql.connection.commit()
            cur.close()
            return True
        except Exception:
            cur.close()
            return False

    @staticmethod
    def add_team_points(team_id, points, reason, created_by):
        """Add points to a team directly (not from match).
        
        Args:
            team_id: team to adjust
            points: positive integer to add
            reason: explanation
            created_by: user_id of admin/captain making change
        """
        from models.point_history import PointHistory
        cur = mysql.connection.cursor()
        try:
            # Ensure team has stats record
            stats = TeamStatistics.get_by_team(team_id)
            if not stats:
                TeamStatistics.initialize_for_team(team_id)
            
            # Update team statistics
            cur.execute("""
                UPDATE team_statistics 
                SET total_points = total_points + %s,
                    manual_adjustments = manual_adjustments + %s
                WHERE team_id = %s
            """, (points, points, team_id))
            
            # Log in history
            PointHistory.log('team', team_id, points, reason, created_by)
            
            mysql.connection.commit()
            
            # Recalculate ranks
            TeamStatistics.recalculate_ranks()
            
            return True
        except Exception as e:
            mysql.connection.rollback()
            raise e
        finally:
            cur.close()

    @staticmethod
    def adjust_team_points(team_id, delta, reason, created_by):
        """Adjust team points (add or subtract).
        
        Args:
            team_id: team to adjust
            delta: positive or negative integer
            reason: explanation
            created_by: user_id of admin/captain making change
        """
        from models.point_history import PointHistory
        cur = mysql.connection.cursor()
        try:
            # Ensure team has stats record
            stats = TeamStatistics.get_by_team(team_id)
            if not stats:
                TeamStatistics.initialize_for_team(team_id)
            
            # Update team statistics
            cur.execute("""
                UPDATE team_statistics 
                SET total_points = total_points + %s,
                    manual_adjustments = manual_adjustments + %s
                WHERE team_id = %s
            """, (delta, delta, team_id))
            
            # Log in history
            PointHistory.log('team', team_id, delta, reason, created_by)
            
            mysql.connection.commit()
            
            # Recalculate ranks
            TeamStatistics.recalculate_ranks()
            
            return True
        except Exception as e:
            mysql.connection.rollback()
            raise e
        finally:
            cur.close()

    @staticmethod
    def get_team_points(team_id):
        """Get a team's current total points (match-based + manual)."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT 
                ts.total_points,
                ts.manual_adjustments,
                ts.matches_played,
                ts.wins,
                ts.losses,
                ts.draws
            FROM team_statistics ts
            WHERE ts.team_id = %s
        """, (team_id,))
        row = cur.fetchone()
        cur.close()
        if row:
            return {
                'total_points': int(row['total_points']),
                'manual_adjustments': int(row['manual_adjustments']),
                'match_points': int(row['total_points']) - int(row['manual_adjustments']),
                'matches_played': int(row['matches_played']),
                'wins': int(row['wins']),
                'losses': int(row['losses']),
                'draws': int(row['draws'])
            }
        return {
            'total_points': 0,
            'manual_adjustments': 0,
            'match_points': 0,
            'matches_played': 0,
            'wins': 0,
            'losses': 0,
            'draws': 0
        }

    @staticmethod
    def update_from_match(team1_id, team2_id, winner_team_id=None, is_draw=False):
        """Update statistics for both teams after a match."""
        cur = mysql.connection.cursor()
        try:
            # Get current stats
            cur.execute("SELECT * FROM team_statistics WHERE team_id IN (%s, %s)", (team1_id, team2_id))
            rows = cur.fetchall()
            stats_map = {row['team_id']: row for row in rows}
            
            # Ensure both teams have stats records
            for tid in [team1_id, team2_id]:
                if tid not in stats_map:
                    cur.execute("INSERT INTO team_statistics (team_id) VALUES (%s)", (tid,))
                    mysql.connection.commit()
                    stats_map[tid] = {'team_id': tid, 'matches_played': 0, 'wins': 0, 'losses': 0, 
                                      'draws': 0, 'total_points': 0, 'manual_adjustments': 0,
                                      'win_percentage': 0.0, 'avg_points_per_match': 0.0}
            
            # Update team 1
            t1_stats = stats_map[team1_id]
            t1_matches = t1_stats['matches_played'] + 1
            t1_wins = t1_stats['wins'] + (1 if not is_draw and winner_team_id == team1_id else 0)
            t1_losses = t1_stats['losses'] + (1 if not is_draw and winner_team_id != team1_id else 0)
            t1_draws = t1_stats['draws'] + (1 if is_draw else 0)
            t1_points = t1_stats['total_points'] + (10 if not is_draw and winner_team_id == team1_id else (5 if is_draw else 0))
            t1_win_pct = round((t1_wins / t1_matches * 100) if t1_matches > 0 else 0, 2)
            t1_avg_points = round((t1_points / t1_matches), 2) if t1_matches > 0 else 0.0
            
            cur.execute("""
                UPDATE team_statistics
                SET matches_played = %s, wins = %s, losses = %s, draws = %s,
                    total_points = %s, win_percentage = %s, avg_points_per_match = %s
                WHERE team_id = %s
            """, (t1_matches, t1_wins, t1_losses, t1_draws, t1_points, t1_win_pct, t1_avg_points, team1_id))
            
            # Update team 2
            t2_stats = stats_map[team2_id]
            t2_matches = t2_stats['matches_played'] + 1
            t2_wins = t2_stats['wins'] + (1 if not is_draw and winner_team_id == team2_id else 0)
            t2_losses = t2_stats['losses'] + (1 if not is_draw and winner_team_id != team2_id else 0)
            t2_draws = t2_stats['draws'] + (1 if is_draw else 0)
            t2_points = t2_stats['total_points'] + (10 if not is_draw and winner_team_id == team2_id else (5 if is_draw else 0))
            t2_win_pct = round((t2_wins / t2_matches * 100) if t2_matches > 0 else 0, 2)
            t2_avg_points = round((t2_points / t2_matches), 2) if t2_matches > 0 else 0.0
            
            cur.execute("""
                UPDATE team_statistics
                SET matches_played = %s, wins = %s, losses = %s, draws = %s,
                    total_points = %s, win_percentage = %s, avg_points_per_match = %s
                WHERE team_id = %s
            """, (t2_matches, t2_wins, t2_losses, t2_draws, t2_points, t2_win_pct, t2_avg_points, team2_id))
            
            mysql.connection.commit()
            cur.close()
            
            # Recalculate all ranks
            TeamStatistics.recalculate_ranks()
            
            return True
        except Exception as e:
            mysql.connection.rollback()
            cur.close()
            raise e

    @staticmethod
    def recalculate_ranks():
        """Recalculate rankings for all teams based on points."""
        cur = mysql.connection.cursor()
        try:
            # Reset all ranks
            cur.execute("UPDATE team_statistics SET current_rank = NULL")
            
            # Assign ranks based on total_points DESC, then wins DESC
            cur.execute("""
                UPDATE team_statistics ts
                JOIN (
                    SELECT team_id, 
                           RANK() OVER (ORDER BY total_points DESC, wins DESC) as new_rank
                    FROM team_statistics
                ) ranked ON ts.team_id = ranked.team_id
                SET ts.current_rank = ranked.new_rank
            """)
            mysql.connection.commit()
            cur.close()
        except Exception as e:
            mysql.connection.rollback()
            cur.close()
            raise e

    @staticmethod
    def get_leaderboard(limit=50):
        """Get all teams ranked by points."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT ts.*, t.team_name, t.logo, t.sport_type, t.location,
                   u.name as captain_name,
                   COUNT(tm.user_id) as member_count
            FROM team_statistics ts
            JOIN teams t ON ts.team_id = t.id
            JOIN users u ON t.captain_id = u.id
            LEFT JOIN team_members tm ON t.id = tm.team_id
            GROUP BY ts.team_id
            ORDER BY ts.current_rank ASC
            LIMIT %s
        """, (limit,))
        teams = cur.fetchall()
        cur.close()
        return teams

    @staticmethod
    def get_by_user_summary(user_id):
        """Get summary stats for a user across all their teams."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT 
                COALESCE(SUM(ts.wins), 0) as wins,
                COALESCE(SUM(ts.losses), 0) as losses,
                COALESCE(SUM(ts.draws), 0) as draws,
                COALESCE(SUM(ts.total_points), 0) as total_points,
                MIN(ts.current_rank) as rank
            FROM team_statistics ts
            JOIN team_members tm ON ts.team_id = tm.team_id
            WHERE tm.user_id = %s
        """, (user_id,))
        stats = cur.fetchone()
        cur.close()
        if not stats:
            return {'wins': 0, 'losses': 0, 'draws': 0, 'total_points': 0, 'rank': 0}
        return stats


class TeamActivityLog:
    """Model for team_activity_log table operations."""

    @staticmethod
    def create_table():
        """Create team_activity_log table if not exists."""
        cur = mysql.connection.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS team_activity_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                team_id INT NOT NULL,
                activity_type ENUM('created', 'member_joined', 'member_left', 'match_won', 'match_lost', 'match_draw', 'match_completed', 'points_adjusted') NOT NULL,
                description TEXT NOT NULL,
                related_user_id INT DEFAULT NULL,
                related_match_id INT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
                FOREIGN KEY (related_user_id) REFERENCES users(id) ON DELETE SET NULL,
                FOREIGN KEY (related_match_id) REFERENCES team_matches(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def log(team_id, activity_type, description, related_user_id=None, related_match_id=None):
        """Log an activity for a team."""
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO team_activity_log 
                (team_id, activity_type, description, related_user_id, related_match_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (team_id, activity_type, description, related_user_id, related_match_id))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def get_recent_for_team(team_id, limit=10):
        """Get recent activity for a team."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT * FROM team_activity_log
            WHERE team_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (team_id, limit))
        activities = cur.fetchall()
        cur.close()
        return activities