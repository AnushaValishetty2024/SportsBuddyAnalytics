-- Team Module Stabilization - Database Migration
-- Adds statistics tracking, point history, activity log, and team chat

USE sports_buddy;

-- 1. Add statistics columns to teams table
ALTER TABLE teams ADD COLUMN IF NOT EXISTS points INT DEFAULT 0;
ALTER TABLE teams ADD COLUMN IF NOT EXISTS wins INT DEFAULT 0;
ALTER TABLE teams ADD COLUMN IF NOT EXISTS losses INT DEFAULT 0;
ALTER TABLE teams ADD COLUMN IF NOT EXISTS draws INT DEFAULT 0;
ALTER TABLE teams ADD COLUMN IF NOT EXISTS matches_played INT DEFAULT 0;

-- 2. Create PointHistory table for tracking point adjustments
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
);

-- 3. Create TeamActivityLog table
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
);

-- 4. Create TeamChatMessage table
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
);

-- 5. Initialize existing teams with default values
UPDATE teams SET 
    points = 0,
    wins = 0,
    losses = 0,
    draws = 0,
    matches_played = 0
WHERE points IS NULL OR wins IS NULL OR losses IS NULL OR draws IS NULL OR matches_played IS NULL;