"""
Team Migration Script
Adds statistics columns to existing teams and populates with sample data
"""

import mysql.connector
from datetime import datetime, timedelta
import random

def migrate_teams():
    try:
        # Connect to database
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='sports_buddy'
        )
        cur = conn.cursor(dictionary=True)

        print("Starting team migration...")

        # 1. Add statistics columns if they don't exist
        print("\n1. Adding statistics columns...")
        try:
            cur.execute("ALTER TABLE teams ADD COLUMN IF NOT EXISTS points INT DEFAULT 0")
            print("  ✓ Added points column")
        except mysql.connector.Error as e:
            if 'Duplicate column name' in str(e):
                print("  ✓ Points column already exists")
            else:
                print(f"  - Points column: {e}")

        try:
            cur.execute("ALTER TABLE teams ADD COLUMN IF NOT EXISTS wins INT DEFAULT 0")
            print("  ✓ Added wins column")
        except mysql.connector.Error as e:
            if 'Duplicate column name' in str(e):
                print("  ✓ Wins column already exists")
            else:
                print(f"  - Wins column: {e}")

        try:
            cur.execute("ALTER TABLE teams ADD COLUMN IF NOT EXISTS losses INT DEFAULT 0")
            print("  ✓ Added losses column")
        except mysql.connector.Error as e:
            if 'Duplicate column name' in str(e):
                print("  ✓ Losses column already exists")
            else:
                print(f"  - Losses column: {e}")

        try:
            cur.execute("ALTER TABLE teams ADD COLUMN IF NOT EXISTS draws INT DEFAULT 0")
            print("  ✓ Added draws column")
        except mysql.connector.Error as e:
            if 'Duplicate column name' in str(e):
                print("  ✓ Draws column already exists")
            else:
                print(f"  - Draws column: {e}")

        try:
            cur.execute("ALTER TABLE teams ADD COLUMN IF NOT EXISTS matches_played INT DEFAULT 0")
            print("  ✓ Added matches_played column")
        except mysql.connector.Error as e:
            if 'Duplicate column name' in str(e):
                print("  ✓ Matches_played column already exists")
            else:
                print(f"  - Matches_played column: {e}")

        # 2. Create new tables if they don't exist
        print("\n2. Creating new tables...")
        
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS team_point_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    team_id INT NOT NULL,
                    change_value INT NOT NULL,
                    reason TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_by INT,
                    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
                    FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
                    INDEX idx_team_id (team_id),
                    INDEX idx_timestamp (timestamp)
                )
            """)
            print("  ✓ Created team_point_history table")
        except mysql.connector.Error as e:
            print(f"  - team_point_history: {e}")

        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS team_activity_log (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    team_id INT NOT NULL,
                    action_type VARCHAR(50) NOT NULL,
                    description TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id INT,
                    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
                    INDEX idx_team_id (team_id),
                    INDEX idx_timestamp (timestamp)
                )
            """)
            print("  ✓ Created team_activity_log table")
        except mysql.connector.Error as e:
            print(f"  - team_activity_log: {e}")

        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS team_chat_messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    team_id INT NOT NULL,
                    user_id INT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_team_id (team_id),
                    INDEX idx_timestamp (timestamp)
                )
            """)
            print("  ✓ Created team_chat_messages table")
        except mysql.connector.Error as e:
            print(f"  - team_chat_messages: {e}")

        # 3. Get existing teams
        print("\n3. Updating existing teams...")
        cur.execute("SELECT id, team_name, captain_id FROM teams")
        teams = cur.fetchall()
        
        if not teams:
            print("  No teams found in database")
            return

        print(f"  Found {len(teams)} teams")

        # 4. Get users for seeding
        cur.execute("SELECT id, name FROM users LIMIT 20")
        users = cur.fetchall()

        if len(users) < 2:
            print("  WARNING: Need at least 2 users for proper seeding")
            return

        # 5. Update teams with statistics
        for team in teams:
            team_id = team['id']
            
            # Generate realistic random stats
            matches_played = random.randint(5, 20)
            wins = random.randint(2, matches_played - 2)
            losses = random.randint(1, matches_played - wins - 1)
            draws = matches_played - wins - losses
            points = (wins * 10) + (draws * 5)
            
            # Update team record
            cur.execute("""
                UPDATE teams 
                SET points = %s, wins = %s, losses = %s, draws = %s, matches_played = %s
                WHERE id = %s
            """, (points, wins, losses, draws, matches_played, team_id))
            
            # Try to update team_statistics table if it exists
            try:
                win_percentage = round((wins / matches_played * 100) if matches_played > 0 else 0, 2)
                avg_points = round(points / matches_played, 2) if matches_played > 0 else 0.0
                
                cur.execute("SELECT team_id FROM team_statistics WHERE team_id = %s", (team_id,))
                if cur.fetchone():
                    cur.execute("""
                        UPDATE team_statistics 
                        SET matches_played = %s, wins = %s, losses = %s, draws = %s,
                            total_points = %s, win_percentage = %s, avg_points_per_match = %s
                        WHERE team_id = %s
                    """, (matches_played, wins, losses, draws, points, win_percentage, avg_points, team_id))
                else:
                    cur.execute("""
                        INSERT INTO team_statistics 
                        (team_id, matches_played, wins, losses, draws, total_points, 
                         win_percentage, avg_points_per_match)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (team_id, matches_played, wins, losses, draws, points, win_percentage, avg_points))
            except mysql.connector.Error:
                pass  # Table might not exist
            
            print(f"  ✓ Updated: {team['team_name']} ({matches_played} matches, {points} pts)")

        # 6. Add members to teams
        print("\n4. Adding members to teams...")
        for team in teams:
            team_id = team['id']
            captain_id = team['captain_id']
            
            # Add captain if not already member
            try:
                cur.execute("""
                    INSERT IGNORE INTO team_members (team_id, user_id)
                    VALUES (%s, %s)
                """, (team_id, captain_id))
            except mysql.connector.Error:
                pass
            
            # Add 1-4 random members
            available_users = [u['id'] for u in users if u['id'] != captain_id]
            if available_users:
                num_members = random.randint(1, min(4, len(available_users)))
                random.shuffle(available_users)
                
                for user_id in available_users[:num_members]:
                    try:
                        cur.execute("""
                            INSERT IGNORE INTO team_members (team_id, user_id)
                            VALUES (%s, %s)
                        """, (team_id, user_id))
                        
                        # Add join activity
                        try:
                            user = next(u for u in users if u['id'] == user_id)
                            cur.execute("""
                                INSERT INTO team_activity_log 
                                (team_id, action_type, description, user_id, timestamp)
                                VALUES (%s, 'member_joined', %s, %s, %s)
                            """, (
                                team_id,
                                f"{user['name']} joined the team",
                                user_id,
                                datetime.now() - timedelta(days=random.randint(1, 30))
                            ))
                        except mysql.connector.Error:
                            pass
                    except mysql.connector.Error:
                        pass

        # 7. Add activity logs
        print("\n5. Adding activity logs...")
        activity_types = [
            'match_won', 'match_won', 'match_won',  # Weighted towards wins
            'match_lost',
            'match_draw',
            'points_adjusted',
            'member_joined'
        ]
        
        for team in teams:
            team_id = team['id']
            for i in range(8):
                activity_type = random.choice(activity_types)
                descriptions = {
                    'match_won': f"Victory in match #{random.randint(100,999)}",
                    'match_lost': f"Defeat in competitive match",
                    'match_draw': f"Tied match against strong opponents",
                    'points_adjusted': f"Points adjusted by administrator",
                    'member_joined': "New player joined the roster"
                }
                description = descriptions.get(activity_type, 'Team activity')
                
                try:
                    cur.execute("""
                        INSERT INTO team_activity_log 
                        (team_id, action_type, description, user_id, timestamp)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        team_id,
                        activity_type,
                        description,
                        team['captain_id'],
                        datetime.now() - timedelta(days=random.randint(0, 60))
                    ))
                except mysql.connector.Error:
                    pass

        # 8. Add chat messages
        print("\n6. Adding chat messages...")
        messages = [
            "Great practice session today! 💪",
            "Who's available for the weekend match?",
            "We need to work on our defense",
            "Amazing teamwork everyone! 🏆",
            "Don't forget about the tournament next week",
            "Let's schedule a training session",
            "Good luck in the finals! 🎉",
            "That was an incredible save!",
            "We should practice more on set pieces",
            "Proud of this team! 👏"
        ]

        for team in teams:
            team_id = team['id']
            # Get team members
            try:
                cur.execute("SELECT user_id FROM team_members WHERE team_id = %s", (team_id,))
                members = [row['user_id'] for row in cur.fetchall()]
                
                if not members:
                    members = [team['captain_id']]
                
                for i in range(10):
                    cur.execute("""
                        INSERT INTO team_chat_messages 
                        (team_id, user_id, message, timestamp)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        team_id,
                        random.choice(members),
                        random.choice(messages),
                        datetime.now() - timedelta(hours=random.randint(0, 72))
                    ))
            except mysql.connector.Error:
                pass

        # 9. Add point history
        print("\n7. Adding point history...")
        point_changes = [
            ("Won tournament match", 15),
            ("Sportsmanship bonus", 10),
            ("Fair play award", 5),
            ("Regular match win", 10),
            ("Draw match", 5),
            ("Participation reward", 3),
        ]

        for team in teams:
            team_id = team['id']
            for i in range(5):
                reason, change = random.choice(point_changes)
                try:
                    cur.execute("""
                        INSERT INTO team_point_history 
                        (team_id, change_value, reason, updated_by, timestamp)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        team_id,
                        change,
                        reason,
                        team['captain_id'],
                        datetime.now() - timedelta(days=random.randint(1, 45))
                    ))
                except mysql.connector.Error:
                    pass

        conn.commit()
        cur.close()
        conn.close()

        print(f"\n✅ Migration complete!")
        print(f"   Updated {len(teams)} teams with statistics, members, activities, chat, and point history")
        print("\nDatabase is ready!")

    except mysql.connector.Error as e:
        print(f"\n❌ Database error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == '__main__':
    migrate_teams()