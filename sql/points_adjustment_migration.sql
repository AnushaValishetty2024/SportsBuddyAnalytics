-- Points Adjustment System Migration
-- Creates table for tracking point changes
-- Date: 2026-07-02

-- Create match_result_point_changes table for tracking individual point changes
CREATE TABLE IF NOT EXISTS match_result_point_changes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    match_id INT NOT NULL,
    user_id INT NOT NULL,
    points_change INT NOT NULL,
    change_type ENUM('win', 'draw', 'loss', 'admin_adjustment', 'manual_adjustment') NOT NULL,
    reason TEXT,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_match_id (match_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;