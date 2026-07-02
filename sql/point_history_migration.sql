-- ============================================
-- Point History Table for Audit Trail
-- ============================================
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Add adjustment tracking columns if they don't exist
ALTER TABLE match_results_new
    ADD COLUMN IF NOT EXISTS adjustment_reason TEXT DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS adjusted_at TIMESTAMP NULL DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS adjusted_by INT DEFAULT NULL;

-- Add points field to users table if not exists
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS points INT NOT NULL DEFAULT 0;

-- Add manual_adjustments column to team_statistics
ALTER TABLE team_statistics
    ADD COLUMN IF NOT EXISTS manual_adjustments INT NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS adjustment_reason TEXT DEFAULT NULL;