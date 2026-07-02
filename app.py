from flask import Flask
from flask_cors import CORS
from config import Config
from models import mysql, User, Leaderboard, SportsVenue, Conversation, Message, Notification, UserBadge, Team, TeamMember, TeamMatch, TeamStatistics, TeamActivityLog, Follower, EventLog
from routes.backend import backend_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    print(app.url_map)
    app.register_blueprint(backend_bp)
    
    # Enable CORS for all routes (frontend runs on different port)
    CORS(app)

    # Initialize MySQL
    mysql.init_app(app)

    # Create database on startup
    with app.app_context():
        try:
            import pymysql
            conn = pymysql.connect(
                host=app.config['MYSQL_HOST'],
                user=app.config['MYSQL_USER'],
                password=app.config['MYSQL_PASSWORD']
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {app.config['MYSQL_DB']}")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Warning: Could not create database: {e}")

        # Register blueprints
        from routes.auth import auth_bp
        app.register_blueprint(auth_bp)

        from routes.dashboard import dashboard_bp
        app.register_blueprint(dashboard_bp)

        # Day 5: Register chat/notification/AI blueprint
        from routes.chat import chat_bp
        app.register_blueprint(chat_bp)

        # Register Team blueprint
        from routes.team import team_bp
        app.register_blueprint(team_bp)

        # Day 7: Register social blueprint (profiles, followers, seasonal leaderboard)
        from routes.social import social_bp
        app.register_blueprint(social_bp)

        # Create tables
        try:
            User.create_table()
            Leaderboard.create_tables()
            SportsVenue.create_table()
            Conversation.create_table()
            Message.create_table()
            Notification.create_table()
            UserBadge.create_table()
            Follower.create_table()
            EventLog.create_table()
            
            # Create team tables
            Team.create_table()
            TeamMember.create_table()
            TeamMatch.create_table()
            TeamStatistics.create_table()
            TeamActivityLog.create_table()
            
            # Auto-seed team demo data if tables are empty
            from seed_team_data import seed_team_data
            seeded = seed_team_data()
            if seeded:
                print("Team demo data seeded successfully.")
            
            # Auto-seed venues data if table is empty
            seeded = SportsVenue.seed_default_data()
            if seeded:
                print("Sports venues seeded with default data.")
            
            # Auto-seed matches data if fewer than 15 matches exist
            from models import Match
            matches_seeded = Match.seed_match_data()
            if matches_seeded:
                print("Match locations seeded with sample data.")
            
            print("Database tables created successfully.")
        except Exception as e:
            print(f"Warning: Could not create tables: {e}")

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)