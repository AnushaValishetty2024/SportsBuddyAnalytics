-- Team Analytics & Statistics Migration
-- Adds support for team matches, statistics, and leaderboard
-- Run this AFTER the teams migration

USE sports_buddy;

-- ========================================
-- TEAM MATCHES TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS team_matches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    team1_id INT NOT NULL,
    team2_id INT NOT NULL,
    sport_type VARCHAR(50) NOT NULL,
    venue_name VARCHAR(200) NOT NULL,
    match_date DATE NOT NULL,
    match_time TIME NOT NULL,
    team1_score INT DEFAULT NULL,
    team2_score INT DEFAULT NULL,
    winner_team_id INT DEFAULT NULL,
    is_draw TINYINT(1) NOT NULL DEFAULT 0,
    status ENUM('scheduled', 'completed', 'cancelled') DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (team1_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (team2_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (winner_team_id) REFERENCES teams(id) ON DELETE SET NULL,
    CHECK (team1_id != team2_id)
);

-- ========================================
-- TEAM STATISTICS TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS team_statistics (
    team_id INT NOT NULL PRIMARY KEY,
    matches_played INT NOT NULL DEFAULT 0,
    wins INT NOT NULL DEFAULT 0,
    losses INT NOT NULL DEFAULT 0,
    draws INT NOT NULL DEFAULT 0,
    total_points INT NOT NULL DEFAULT 0,
    win_percentage DECIMAL(5,2) DEFAULT 0.00,
    avg_points_per_match DECIMAL(6,2) DEFAULT 0.00,
    current_rank INT DEFAULT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
);

-- ========================================
-- INDEXES FOR PERFORMANCE
-- ========================================
CREATE INDEX idx_team_matches_team1 ON team_matches(team1_id);
CREATE INDEX idx_team_matches_team2 ON team_matches(team2_id);
CREATE INDEX idx_team_matches_status ON team_matches(status);
CREATE INDEX idx_team_matches_date ON team_matches(match_date);
CREATE INDEX idx_team_statistics_rank ON team_statistics(current_rank);
CREATE INDEX idx_team_statistics_points ON team_statistics(total_points DESC);

-- ========================================
-- ACTIVITY LOG TABLE (for recent activity feed)
-- ========================================
CREATE TABLE IF NOT EXISTS team_activity_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    team_id INT NOT NULL,
    activity_type ENUM('created', 'member_joined', 'member_left', 'match_won', 'match_lost', 'match_draw', 'match_completed') NOT NULL,
    description TEXT NOT NULL,
    related_user_id INT DEFAULT NULL,
    related_match_id INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (related_user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (related_match_id) REFERENCES team_matches(id) ON DELETE SET NULL
);

CREATE INDEX idx_team_activity_team ON team_activity_log(team_id);
CREATE INDEX idx_team_activity_created ON team_activity_log(created_at DESC);