from flask import current_app
from models import mysql
from datetime import datetime
import json


class EventLog:
    """Lightweight event handling service for triggering notifications, badge checks, and leaderboard updates."""

    @staticmethod
    def create_table():
        cur = mysql.connection.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS event_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                event_type VARCHAR(50) NOT NULL,
                user_id INT NULL,
                entity_type VARCHAR(50) NULL,
                entity_id INT NULL,
                event_data JSON NULL,
                processed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
                INDEX idx_event_type (event_type),
                INDEX idx_processed (processed),
                INDEX idx_created (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def log(event_type, user_id=None, entity_type=None, entity_id=None, event_data=None):
        """Log an event for async processing.
        
        Args:
            event_type: Type of event (match_created, match_completed, tournament_joined, badge_earned, player_followed, ai_report_generated)
            user_id: User associated with event
            entity_type: Type of entity (match, tournament, badge, etc.)
            entity_id: ID of the entity
            event_data: Additional data as dict
        """
        cur = mysql.connection.cursor()
        try:
            event_data_json = json.dumps(event_data) if event_data else None
            cur.execute("""
                INSERT INTO event_log (event_type, user_id, entity_type, entity_id, event_data)
                VALUES (%s, %s, %s, %s, %s)
            """, (event_type, user_id, entity_type, entity_id, event_data_json))
            mysql.connection.commit()
            return True
        except Exception as e:
            current_app.logger.error(f"Event log error: {e}")
            return False
        finally:
            cur.close()

    @staticmethod
    def get_unprocessed_events(limit=100):
        """Get unprocessed events for batch processing."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT * FROM event_log
            WHERE processed = FALSE
            ORDER BY created_at ASC
            LIMIT %s
        """, (limit,))
        events = cur.fetchall()
        cur.close()
        return events

    @staticmethod
    def mark_processed(event_id):
        """Mark an event as processed."""
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                UPDATE event_log SET processed = TRUE WHERE id = %s
            """, (event_id,))
            mysql.connection.commit()
            return True
        except Exception as e:
            current_app.logger.error(f"Mark processed error: {e}")
            return False
        finally:
            cur.close()

    @staticmethod
    def process_events():
        """Process unprocessed events and trigger appropriate actions.
        
        This should be called periodically or after events are logged.
        """
        events = EventLog.get_unprocessed_events()
        
        for event in events:
            try:
                event_type = event['event_type']
                user_id = event['user_id']
                entity_type = event['entity_type']
                entity_id = event['entity_id']
                event_data = json.loads(event['event_data']) if event['event_data'] else {}
                
                # Process based on event type
                if event_type == 'match_completed':
                    EventLog._handle_match_completed(user_id, entity_id, event_data)
                elif event_type == 'match_created':
                    EventLog._handle_match_created(user_id, entity_id, event_data)
                elif event_type == 'tournament_joined':
                    EventLog._handle_tournament_joined(user_id, entity_id, event_data)
                elif event_type == 'badge_earned':
                    EventLog._handle_badge_earned(user_id, entity_id, event_data)
                elif event_type == 'player_followed':
                    EventLog._handle_player_followed(user_id, entity_id, event_data)
                elif event_type == 'ai_report_generated':
                    EventLog._handle_ai_report_generated(user_id, entity_id, event_data)
                
                # Mark as processed
                EventLog.mark_processed(event['id'])
                
            except Exception as e:
                current_app.logger.error(f"Error processing event {event['id']}: {e}")

    @staticmethod
    def _handle_match_completed(user_id, match_id, event_data):
        """Handle match completion - update seasonal leaderboard and check badges."""
        from models import Leaderboard, UserBadge, Notification
        
        # Update seasonal leaderboard
        Leaderboard.update_seasonal_leaderboard(user_id)
        
        # Check and award badges
        user_badges = UserBadge.get_user_badges(user_id)
        badge_codes = [b['badge_code'] for b in user_badges]
        
        # Get user stats
        stats = Leaderboard.get_dynamic_leaderboard()
        user_stat = next((s for s in stats if s['user_id'] == user_id), None)
        
        if user_stat:
            matches_played = user_stat.get('matches_played', 0)
            wins = user_stat.get('wins', 0)
            
            # Check matches milestones
            for milestone in [1, 5, 10, 25, 50]:
                badge_code = f'matches_{milestone}'
                if matches_played >= milestone and badge_code not in badge_codes:
                    UserBadge.award_badge(user_id, f'matches_{milestone}', 
                        f'{milestone} Matches Played', f'Played {milestone} matches',
                        'bi-trophy-fill')
                    Notification.create(
                        user_id=user_id,
                        type='badge_unlocked',
                        title='Badge Unlocked!',
                        message=f'You earned the "{milestone} Matches Played" badge!',
                        related_badge_id=None
                    )
            
            # Check wins milestones
            for milestone in [1, 5, 10, 25]:
                badge_code = f'wins_{milestone}'
                if wins >= milestone and badge_code not in badge_codes:
                    UserBadge.award_badge(user_id, f'wins_{milestone}',
                        f'{milestone} Wins', f'Won {milestone} matches',
                        'bi-star-fill')
                    Notification.create(
                        user_id=user_id,
                        type='badge_unlocked',
                        title='Badge Unlocked!',
                        message=f'You earned the "{milestone} Wins" badge!',
                        related_badge_id=None
                    )

    @staticmethod
    def _handle_match_created(user_id, match_id, event_data):
        """Handle match creation - could notify followers in the future."""
        pass

    @staticmethod
    def _handle_tournament_joined(user_id, tournament_id, event_data):
        """Handle tournament join."""
        pass

    @staticmethod
    def _handle_badge_earned(user_id, badge_id, event_data):
        """Handle badge earned event."""
        from models import Notification
        Notification.create(
            user_id=user_id,
            type='badge_unlocked',
            title='Badge Unlocked!',
            message=event_data.get('message', 'You earned a new badge!'),
            related_badge_id=badge_id
        )

    @staticmethod
    def _handle_player_followed(user_id, followed_user_id, event_data):
        """Handle new follower - notify the followed user."""
        from models import User, Notification
        
        followed_user = User.get_by_id(followed_user_id)
        follower_user = User.get_by_id(user_id)
        
        if followed_user and follower_user:
            Notification.create(
                user_id=followed_user_id,
                type='new_follower',
                title='New Follower',
                message=f'{follower_user["name"]} started following you!',
                related_user_id=user_id
            )

    @staticmethod
    def _handle_ai_report_generated(user_id, report_id, event_data):
        """Handle AI report generation."""
        from models import Notification
        
        Notification.create(
            user_id=user_id,
            type='ai_report_ready',
            title='AI Match Report Ready',
            message='Your AI match analysis report is now available. Check it out!',
            related_ai_report_id=report_id
        )