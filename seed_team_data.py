"""
Seed Team Data Script
Creates 5 sample teams with statistics, activity logs, chat messages, and point history
Run this after applying the database migrations.
"""

import mysql.connector
from datetime import datetime, timedelta
import random

def seed_team_data():
    try:
        # Connect to database
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='sports_buddy'
        )
        cur = conn.cursor(dictionary=True)

        # Check if teams already exist
        cur.execute("SELECT COUNT(*) as cnt FROM teams")
        result = cur.fetchone()
        
        if result['cnt'] > 0:
            print(f"Database already has {result['cnt']} teams. Skipping seed.")
            return

        print("Seeding team data...")

        # Get some users to be captains and members
        cur.execute("SELECT id, name FROM users LIMIT 10")
        users = cur.fetchall()
        
        if len(users) < 5:
            print("ERROR: Need at least 5 users in database to seed teams.")
            print(f"Found {len(users)} users. Please create users first.")
            return

        # Sample team data
        teams_data = [
            {
                'team_name': 'Phoenix Rising',
                'description': 'Competitive basketball team looking for talented players',
                'sport_type': 'Basketball',
                'location': 'Mumbai',
                'captain_id': users[0]['id'],
                'points': 150,
                'wins': 12,
                'losses': 3,
                'draws': 1,
                'matches_played': 16
            },
            {
                'team_name': 'Thunder Strikers',
                'description': 'Cricket enthusiasts playing weekend matches',
                'sport_type': 'Cricket',
                'location': 'Delhi',
                'captain_id': users[1]['id'],
                'points': 120,
                'wins': 10,
                'losses': 4,
                'draws': 2,
                'matches_played': 16
            },
            {
                'team_name': 'Goal Machines',
                'description': 'Football club with professional training sessions',
                'sport_type': 'Football',
                'location': 'Bangalore',
                'captain_id': users[2]['id'],
                'points': 95,
                'wins': 8,
                'losses': 5,
                'draws': 2,
                'matches_played': 15
            },
            {
                'team_name': 'Smash Masters',
                'description': 'Badminton doubles specialists',
                'sport_type': 'Badminton',
                'location': 'Chennai',
                'captain_id': users[3]['id'],
                'points': 75,
                'wins': 6,
                'losses': 5,
                'draws': 3,
                'matches_played': 14
            },
            {
                'team_name': 'Net Warriors',
                'description': 'Volleyball team for beginners and intermediates',
                'sport_type': 'Volleyball',
                'location': 'Hyderabad',
                'captain_id': users[4]['id'],
                'points': 45,
                'wins': 4,
                'losses': 6,
                'draws': 1,
                'matches_played': 11
            }
        ]

        created_teams = []

        # Create teams
        for team_data in teams_data:
            try:
                cur.execute("""
                    INSERT INTO teams 
                    (team_name, description, sport_type, location, captain_id, max_members, 
                     points, wins, losses, draws, matches_played)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    team_data['team_name'],
                    team_data['description'],
                    team_data['sport_type'],
                    team_data['location'],
                    team_data['captain_id'],
                    10,
                    team_data['points'],
                    team_data['wins'],
                    team_data['losses'],
                    team_data['draws'],
                    team_data['matches_played']
                ))
                
                team_id = cur.lastrowid
                created_teams.append({
                    'id': team_id,
                    'name': team_data['team_name'],
                    'captain_id': team_data['captain_id'],
                    'points': team_data['points']
                })
                
                # Add captain as member
                cur.execute("""
                    INSERT INTO team_members (team_id, user_id)
                    VALUES (%s, %s)
                """, (team_id, team_data['captain_id']))
                
                # Create statistics record if table exists
                try:
                    win_percentage = round((team_data['wins'] / team_data['matches_played'] * 100) 
                                           if team_data['matches_played'] > 0 else 0, 2)
                    avg_points = round(team_data['points'] / team_data['matches_played'], 2) \
                                 if team_data['matches_played'] > 0 else 0.0
                    
                    cur.execute("""
                        INSERT INTO team_statistics 
                        (team_id, matches_played, wins, losses, draws, total_points, 
                         win_percentage, avg_points_per_match)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        team_id,
                        team_data['matches_played'],
                        team_data['wins'],
                        team_data['losses'],
                        team_data['draws'],
                        team_data['points'],
                        win_percentage,
                        avg_points
                    ))
                except mysql.connector.Error:
                    pass  # Table might not exist yet
                
                print(f"✓ Created team: {team_data['team_name']}")
                
            except mysql.connector.Error as e:
                print(f"✗ Error creating team {team_data['team_name']}: {e}")

        # Add members to teams (1-4 members per team besides captain)
        for team in created_teams:
            num_members = random.randint(1, 4)
            available_users = [u for u in users if u['id'] != team['captain_id']]
            random.shuffle(available_users)
            
            for i in range(min(num_members, len(available_users))):
                try:
                    cur.execute("""
                        INSERT INTO team_members (team_id, user_id)
                        VALUES (%s, %s)
                    """, (team['id'], available_users[i]['id']))
                    
                    # Log activity
                    try:
                        cur.execute("""
                            INSERT INTO team_activity_log 
                            (team_id, action_type, description, user_id, timestamp)
                            VALUES (%s, 'member_joined', %s, %s, %s)
                        """, (
                            team['id'],
                            f"{available_users[i]['name']} joined the team",
                            available_users[i]['id'],
                            datetime.now() - timedelta(days=random.randint(1, 30))
                        ))
                    except mysql.connector.Error:
                        pass
                        
                except mysql.connector.Error as e:
                    print(f"  Error adding member: {e}")

        # Add activity logs for each team
        activity_templates = [
            ("match_won", "won a match against Team X"),
            ("match_won", "victorious in tournament semi-final"),
            ("match_draw", "tied with opponents in intense match"),
            ("points_adjusted", "bonus points awarded for sportsmanship"),
            ("member_joined", "new member joined the roster"),
        ]

        for team in created_teams:
            for i in range(5):
                try:
                    activity_type, description = random.choice(activity_templates)
                    cur.execute("""
                        INSERT INTO team_activity_log 
                        (team_id, action_type, description, user_id, timestamp)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        team['id'],
                        activity_type,
                        description,
                        team['captain_id'],
                        datetime.now() - timedelta(days=random.randint(0, 60))
                    ))
                except mysql.connector.Error:
                    pass

        # Add chat messages
        chat_messages = [
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

        for team in created_teams:
            members = [team['captain_id']] + [u['id'] for u in random.sample(users, min(3, len(users)))]
            
            for i in range(10):
                try:
                    cur.execute("""
                        INSERT INTO team_chat_messages 
                        (team_id, user_id, message, timestamp)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        team['id'],
                        random.choice(members),
                        random.choice(chat_messages),
                        datetime.now() - timedelta(hours=random.randint(0, 72))
                    ))
                except mysql.connector.Error:
                    pass

        # Add point history entries
        point_changes = [
            ("Won tournament match", 15),
            ("Sportsmanship bonus", 10),
            ("Fair play award", 5),
            ("Regular match win", 10),
            ("Draw match", 5),
            ("Participation reward", 3),
        ]

        for team in created_teams:
            for i in range(5):
                try:
                    reason, change = random.choice(point_changes)
                    cur.execute("""
                        INSERT INTO team_point_history 
                        (team_id, change_value, reason, updated_by, timestamp)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        team['id'],
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

        print(f"\n✅ Successfully seeded {len(created_teams)} teams with:")
        print("  - Team members")
        print("  - Activity logs")
        print("  - Chat messages")
        print("  - Point history")
        print("\nDatabase is now ready with test data!")

    except mysql.connector.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == '__main__':
    seed_team_data()