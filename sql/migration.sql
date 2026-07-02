-- Migration script to add leaderboard tables (safe to run on existing database)
USE sports_buddy;

-- Player points table - tracks each player's performance stats
CREATE TABLE IF NOT EXISTS player_points (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    points INT NOT NULL DEFAULT 0,
    wins INT NOT NULL DEFAULT 0,
    losses INT NOT NULL DEFAULT 0,
    draws INT NOT NULL DEFAULT 0,
    matches_played INT NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Match results table - stores each match outcome
CREATE TABLE IF NOT EXISTS match_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    match_id INT NOT NULL UNIQUE,
    winner_id INT DEFAULT NULL COMMENT 'NULL means draw',
    is_draw TINYINT(1) NOT NULL DEFAULT 0,
    submitted_by INT NOT NULL COMMENT 'User who submitted result',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
    FOREIGN KEY (winner_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (submitted_by) REFERENCES users(id) ON DELETE CASCADE
);

-- Admin override log - tracks all manual point modifications
CREATE TABLE IF NOT EXISTS admin_overrides (
    id INT AUTO_INCREMENT PRIMARY KEY,
    target_user_id INT NOT NULL,
    previous_points INT NOT NULL DEFAULT 0,
    new_points INT NOT NULL DEFAULT 0,
    previous_wins INT NOT NULL DEFAULT 0,
    new_wins INT NOT NULL DEFAULT 0,
    previous_losses INT NOT NULL DEFAULT 0,
    new_losses INT NOT NULL DEFAULT 0,
    previous_draws INT NOT NULL DEFAULT 0,
    new_draws INT NOT NULL DEFAULT 0,
    previous_matches_played INT NOT NULL DEFAULT 0,
    new_matches_played INT NOT NULL DEFAULT 0,
    reason VARCHAR(500) DEFAULT NULL,
    overridden_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (target_user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Initialize player_points for all existing users (safe insert, skips if exists)
INSERT IGNORE INTO player_points (user_id, points, wins, losses, draws, matches_played)
SELECT id, 0, 0, 0, 0, 0 FROM users;