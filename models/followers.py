from flask import current_app
from models import mysql
from datetime import datetime


class Follower:
    """Model for follow/unfollow relationships between users."""

    @staticmethod
    def create_table():
        cur = mysql.connection.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS followers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                follower_id INT NOT NULL,
                following_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (follower_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (following_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY uk_follower_following (follower_id, following_id),
                INDEX idx_follower (follower_id),
                INDEX idx_following (following_id),
                INDEX idx_created (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def follow(follower_id, following_id):
        """Follow a user. Returns True if successful, False if already following."""
        if follower_id == following_id:
            return False
        
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                INSERT IGNORE INTO followers (follower_id, following_id)
                VALUES (%s, %s)
            """, (follower_id, following_id))
            mysql.connection.commit()
            return cur.rowcount > 0
        except Exception as e:
            current_app.logger.error(f"Follow error: {e}")
            return False
        finally:
            cur.close()

    @staticmethod
    def unfollow(follower_id, following_id):
        """Unfollow a user. Returns True if successful."""
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                DELETE FROM followers
                WHERE follower_id = %s AND following_id = %s
            """, (follower_id, following_id))
            mysql.connection.commit()
            return cur.rowcount > 0
        except Exception as e:
            current_app.logger.error(f"Unfollow error: {e}")
            return False
        finally:
            cur.close()

    @staticmethod
    def is_following(follower_id, following_id):
        """Check if follower_id is following following_id."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT COUNT(*) as cnt FROM followers
            WHERE follower_id = %s AND following_id = %s
        """, (follower_id, following_id))
        row = cur.fetchone()
        cur.close()
        return row['cnt'] > 0 if row else False

    @staticmethod
    def get_follower_count(user_id):
        """Get number of followers for a user."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT COUNT(*) as cnt FROM followers
            WHERE following_id = %s
        """, (user_id,))
        row = cur.fetchone()
        cur.close()
        return row['cnt'] if row else 0

    @staticmethod
    def get_following_count(user_id):
        """Get number of users this user is following."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT COUNT(*) as cnt FROM followers
            WHERE follower_id = %s
        """, (user_id,))
        row = cur.fetchone()
        cur.close()
        return row['cnt'] if row else 0

    @staticmethod
    def get_followers(user_id, limit=50):
        """Get list of followers for a user."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT u.id, u.name, u.email, f.created_at as followed_at
            FROM followers f
            JOIN users u ON f.follower_id = u.id
            WHERE f.following_id = %s
            ORDER BY f.created_at DESC
            LIMIT %s
        """, (user_id, limit))
        followers = cur.fetchall()
        cur.close()
        return followers

    @staticmethod
    def get_following(user_id, limit=50):
        """Get list of users this user is following."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT u.id, u.name, u.email, f.created_at as followed_at
            FROM followers f
            JOIN users u ON f.following_id = u.id
            WHERE f.follower_id = %s
            ORDER BY f.created_at DESC
            LIMIT %s
        """, (user_id, limit))
        following = cur.fetchall()
        cur.close()
        return following