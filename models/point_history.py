from flask import current_app
from flask_mysqldb import MySQL
from datetime import datetime

mysql = MySQL()


class PointHistory:
    """Model for point_history table operations."""

    @staticmethod
    def create_table():
        """Create point_history table if not exists."""
        cur = mysql.connection.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS point_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                entity_type ENUM('player', 'team') NOT NULL,
                entity_id INT NOT NULL,
                points_changed INT NOT NULL,
                reason TEXT NOT NULL,
                created_by INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_entity (entity_type, entity_id),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def log(entity_type, entity_id, points_changed, reason, created_by):
        """Log a point adjustment.
        
        Args:
            entity_type: 'player' or 'team'
            entity_id: user_id or team_id
            points_changed: positive or negative integer
            reason: explanation for the adjustment
            created_by: user_id of admin/captain making the change
        """
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO point_history (entity_type, entity_id, points_changed, reason, created_by)
            VALUES (%s, %s, %s, %s, %s)
        """, (entity_type, entity_id, points_changed, reason, created_by))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def get_for_entity(entity_type, entity_id, limit=20):
        """Get point history for a specific entity."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT ph.*, u.name as created_by_name
            FROM point_history ph
            JOIN users u ON ph.created_by = u.id
            WHERE ph.entity_type = %s AND ph.entity_id = %s
            ORDER BY ph.created_at DESC
            LIMIT %s
        """, (entity_type, entity_id, limit))
        history = cur.fetchall()
        cur.close()
        return history

    @staticmethod
    def get_recent(limit=50):
        """Get recent point adjustments across all entities."""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT ph.*, u.name as created_by_name
            FROM point_history ph
            JOIN users u ON ph.created_by = u.id
            ORDER BY ph.created_at DESC
            LIMIT %s
        """, (limit,))
        history = cur.fetchall()
        cur.close()
        return history