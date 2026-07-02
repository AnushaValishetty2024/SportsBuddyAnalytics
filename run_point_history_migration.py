import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='sports_buddy'
)
cursor = conn.cursor()

# Create point_history table
cursor.execute("""
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

conn.commit()
cursor.close()
conn.close()

print("point_history table created/verified successfully.")