from flask import current_app
from models import mysql
from datetime import datetime


class Conversation:
    """Model for private conversations (one-to-one chat)."""

    @staticmethod
    def create_table():
        cur = mysql.connection.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user1_id INT NOT NULL,
                user2_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user1_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (user2_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY uk_conversation_pair (user1_id, user2_id),
                INDEX idx_user1 (user1_id),
                INDEX idx_user2 (user2_id),
                INDEX idx_updated (updated_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # Create conversation_members table for group/match chats
        cur.execute("""
            CREATE TABLE IF NOT EXISTS conversation_members (
                id INT AUTO_INCREMENT PRIMARY KEY,
                conversation_id INT NULL,
                match_id INT NULL,
                user_id INT NOT NULL,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
                FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
                UNIQUE KEY uk_unique_membership (conversation_id, user_id),
                UNIQUE KEY uk_unique_match_membership (match_id, user_id),
                INDEX idx_user (user_id),
                INDEX idx_match (match_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def get_or_create(user1_id, user2_id):
        """Get existing conversation or create a new one.
        Always stores with user1_id < user2_id to ensure uniqueness.
        """
        if user1_id > user2_id:
            user1_id, user2_id = user2_id, user1_id

        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT * FROM conversations
            WHERE user1_id = %s AND user2_id = %s
        """, (user1_id, user2_id))
        convo = cur.fetchone()

        if convo:
            cur.close()
            return convo

        cur.execute("""
            INSERT INTO conversations (user1_id, user2_id) VALUES (%s, %s)
        """, (user1_id, user2_id))
        mysql.connection.commit()
        convo_id = cur.lastrowid
        cur.close()
        return {"id": convo_id, "user1_id": user1_id, "user2_id": user2_id}

    @staticmethod
    def get_by_id(conversation_id):
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT c.*, u1.name as user1_name, u2.name as user2_name
            FROM conversations c
            JOIN users u1 ON c.user1_id = u1.id
            JOIN users u2 ON c.user2_id = u2.id
            WHERE c.id = %s
        """, (conversation_id,))
        convo = cur.fetchone()
        cur.close()
        return convo

    @staticmethod
    def get_user_conversations(user_id):
        """Get all conversations for a user with the other participant's info."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT c.*, u1.id as other_user_id, u1.name as other_user_name,
                   (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id AND is_read = FALSE AND sender_id != %s) as unread_count
            FROM conversations c
            JOIN users u1 ON ((c.user1_id = u1.id AND c.user2_id = %s) OR (c.user2_id = u1.id AND c.user1_id = %s))
            WHERE c.user1_id = %s OR c.user2_id = %s
            ORDER BY c.updated_at DESC
        """, (user_id, user_id, user_id, user_id, user_id))
        convos = cur.fetchall()
        cur.close()
        return convos


class Message:
    """Model for messages (both private and group/match chat)."""

    @staticmethod
    def create_table():
        cur = mysql.connection.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                conversation_id INT NULL,
                match_id INT NULL,
                sender_id INT NOT NULL,
                message_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_read BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
                FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
                FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_conversation (conversation_id),
                INDEX idx_match (match_id),
                INDEX idx_sender (sender_id),
                INDEX idx_created (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def send(conversation_id=None, match_id=None, sender_id=None, message_text=''):
        if not message_text or not message_text.strip():
            return None
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO messages (conversation_id, match_id, sender_id, message_text)
            VALUES (%s, %s, %s, %s)
        """, (conversation_id, match_id, sender_id, message_text.strip()))
        mysql.connection.commit()
        msg_id = cur.lastrowid
        cur.close()

        # Update conversation updated_at
        if conversation_id:
            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE conversations SET updated_at = NOW() WHERE id = %s
            """, (conversation_id,))
            mysql.connection.commit()
            cur.close()

        return {"id": msg_id, "conversation_id": conversation_id, "match_id": match_id, "sender_id": sender_id}

    @staticmethod
    def get_conversation_messages(conversation_id, limit=50):
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT m.*, u.name as sender_name
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE m.conversation_id = %s
            ORDER BY m.created_at ASC
            LIMIT %s
        """, (conversation_id, limit))
        messages = cur.fetchall()
        cur.close()
        return messages

    @staticmethod
    def get_match_messages(match_id, limit=50):
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT m.*, u.name as sender_name
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE m.match_id = %s
            ORDER BY m.created_at ASC
            LIMIT %s
        """, (match_id, limit))
        messages = cur.fetchall()
        cur.close()
        return messages

    @staticmethod
    def mark_conversation_read(conversation_id, user_id):
        """Mark all messages in a conversation as read for a user."""
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE messages
            SET is_read = TRUE
            WHERE conversation_id = %s AND sender_id != %s AND is_read = FALSE
        """, (conversation_id, user_id))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def mark_match_read(match_id, user_id):
        """Mark all messages in a match chat as read for a user."""
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE messages
            SET is_read = TRUE
            WHERE match_id = %s AND sender_id != %s AND is_read = FALSE
        """, (match_id, user_id))
        mysql.connection.commit()
        cur.close()


class Notification:
    """Model for notifications."""

    @staticmethod
    def create_table():
        cur = mysql.connection.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                type VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                related_user_id INT NULL,
                related_match_id INT NULL,
                related_conversation_id INT NULL,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (related_user_id) REFERENCES users(id) ON DELETE SET NULL,
                FOREIGN KEY (related_match_id) REFERENCES matches(id) ON DELETE SET NULL,
                FOREIGN KEY (related_conversation_id) REFERENCES conversations(id) ON DELETE SET NULL,
                INDEX idx_user (user_id),
                INDEX idx_is_read (is_read),
                INDEX idx_created (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def create(user_id, type, title, message, related_user_id=None, related_match_id=None, related_conversation_id=None):
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO notifications (user_id, type, title, message, related_user_id, related_match_id, related_conversation_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, type, title, message, related_user_id, related_match_id, related_conversation_id))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def get_user_notifications(user_id, limit=20):
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT * FROM notifications
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (user_id, limit))
        notifications = cur.fetchall()
        cur.close()
        return notifications

    @staticmethod
    def get_unread_count(user_id):
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT COUNT(*) as cnt FROM notifications
            WHERE user_id = %s AND is_read = FALSE
        """, (user_id,))
        row = cur.fetchone()
        cur.close()
        return row['cnt'] if row else 0

    @staticmethod
    def mark_as_read(notification_id, user_id):
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE notifications SET is_read = TRUE
            WHERE id = %s AND user_id = %s
        """, (notification_id, user_id))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def mark_all_as_read(user_id):
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE notifications SET is_read = TRUE
            WHERE user_id = %s AND is_read = FALSE
        """, (user_id,))
        mysql.connection.commit()
        cur.close()


class UserBadge:
    """Model for user badges/achievements."""

    @staticmethod
    def create_table():
        cur = mysql.connection.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_badges (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                badge_code VARCHAR(50) NOT NULL,
                badge_name VARCHAR(100) NOT NULL,
                description TEXT,
                icon VARCHAR(100) DEFAULT 'bi-trophy-fill',
                awarded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY uk_user_badge (user_id, badge_code),
                INDEX idx_user (user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def get_user_badges(user_id):
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT ub.*, b.badge_name, b.description, b.icon
            FROM user_badges ub
            JOIN badges b ON ub.badge_code = b.badge_code
            WHERE ub.user_id = %s
            ORDER BY ub.awarded_at DESC
        """, (user_id,))
        badges = cur.fetchall()
        cur.close()
        return badges

    @staticmethod
    def award_badge(user_id, badge_code, badge_name='', description='', icon='bi-trophy-fill'):
        cur = mysql.connection.cursor()
        try:
            # Try to get badge details from badges table
            cur.execute("SELECT badge_name, description, icon FROM badges WHERE badge_code = %s", (badge_code,))
            badge_row = cur.fetchone()
            
            if badge_row:
                badge_name = badge_row['badge_name']
                description = badge_row['description']
                icon = badge_row['icon']
            
            cur.execute("""
                INSERT IGNORE INTO user_badges (user_id, badge_code, badge_name, description, icon)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, badge_code, badge_name, description, icon))
            mysql.connection.commit()
            return cur.rowcount > 0
        finally:
            cur.close()
