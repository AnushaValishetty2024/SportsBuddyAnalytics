-- Day 7: Smart Notification System, Seasonal Leaderboard, Follow System, Enhanced Profiles, Badges
-- Run this migration to add all new tables and enhancements

-- ========================================
-- 1. ENHANCE NOTIFICATIONS TABLE
-- ========================================
-- Add related entity fields for matches, tournaments, badges, AI reports
ALTER TABLE notifications
    ADD COLUMN IF NOT EXISTS related_tournament_id INT NULL AFTER related_match_id,
    ADD COLUMN IF NOT EXISTS related_badge_id INT NULL AFTER related_tournament_id,
    ADD COLUMN IF NOT EXISTS related_ai_report_id INT NULL AFTER related_badge_id,
    ADD INDEX IF NOT EXISTS idx_notification_type (type),
    ADD INDEX IF NOT EXISTS idx_notification_user_created (user_id, created_at DESC);

-- ========================================
-- 2. BADGES DEFINITION TABLE (for badge catalog)
-- ========================================
CREATE TABLE IF NOT EXISTS badges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    badge_code VARCHAR(50) NOT NULL UNIQUE,
    badge_name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(100) DEFAULT 'bi-trophy-fill',
    criteria_type ENUM('matches_played', 'wins', 'tournaments_won', 'weekly_top', 'monthly_top', 'mvp', 'custom') NOT NULL,
    criteria_value INT DEFAULT 0,
    points_required INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_badge_code (badge_code),
    INDEX idx_criteria_type (criteria_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ========================================
-- 3. USER BADGES (already exists, enhance with foreign key)
-- ========================================
-- Add foreign key to badges table if not exists
ALTER TABLE user_badges
    ADD COLUMN IF NOT EXISTS badge_id INT NULL AFTER id;

-- ========================================
-- 4. FOLLOWERS TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS followers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    follower_id INT NOT NULL,
    following_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_follower_following (follower_id, following_id),
    INDEX idx_follower (follower_id),
    INDEX idx_following (following_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ========================================
-- 5. ENHANCE USERS TABLE WITH PROFILE FIELDS
-- ========================================
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS bio TEXT DEFAULT NULL AFTER email,
    ADD COLUMN IF NOT EXISTS profile_picture VARCHAR(500) DEFAULT NULL AFTER bio,
    ADD COLUMN IF NOT EXISTS favorite_sport VARCHAR(100) DEFAULT NULL AFTER profile_picture,
    ADD COLUMN IF NOT EXISTS location VARCHAR(200) DEFAULT NULL AFTER favorite_sport,
    ADD COLUMN IF NOT EXISTS show_profile_publicly BOOLEAN DEFAULT TRUE AFTER location;

-- ========================================
-- 6. SEASONAL LEADERBOARD TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS seasonal_leaderboard (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    period_type ENUM('weekly', 'monthly', 'lifetime') NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    points INT NOT NULL DEFAULT 0,
    matches_played INT NOT NULL DEFAULT 0,
    wins INT NOT NULL DEFAULT 0,
    losses INT NOT NULL DEFAULT 0,
    draws INT NOT NULL DEFAULT 0,
    win_rate DECIMAL(5,2) DEFAULT 0.00,
    rank_position INT DEFAULT 0,
    is_current BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_period (user_id, period_type, period_start, period_end),
    INDEX idx_period_type_start (period_type, period_start),
    INDEX idx_user_period (user_id, period_type),
    INDEX idx_is_current (is_current)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ========================================
-- 7. AI MATCH REPORTS TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS ai_match_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    match_id INT NOT NULL,
    user_id INT NOT NULL,
    report_data JSON NOT NULL,
    summary TEXT,
    mvp_user_id INT NULL,
    team_performance TEXT,
    key_statistics TEXT,
    strengths TEXT,
    improvements TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_match_report (match_id, user_id),
    INDEX idx_match (match_id),
    INDEX idx_user (user_id),
    INDEX idx_generated (generated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ========================================
-- 7B. TEAM FOLLOWERS TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS team_followers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    team_id INT NOT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_team_follower (team_id, user_id),
    INDEX idx_team (team_id),
    INDEX idx_user (user_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ========================================
-- 8. EVENT LOG TABLE (for event system)
-- ========================================
CREATE TABLE IF NOT EXISTS event_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    user_id INT NULL,
    entity_type VARCHAR(50) NULL,
    entity_id INT NULL,
    event_data JSON NULL,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_event_type (event_type),
    INDEX idx_processed (processed),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ========================================
-- 9. SEED BADGES DATA
-- ========================================
INSERT IGNORE INTO badges (badge_code, badge_name, description, icon, criteria_type, criteria_value) VALUES
('first_match', 'First Match', 'Completed your first match', 'bi-trophy-fill', 'matches_played', 1),
('matches_5', '5 Matches Played', 'Played 5 matches', 'bi-trophy-fill', 'matches_played', 5),
('matches_10', '10 Matches Played', 'Played 10 matches', 'bi-trophy-fill', 'matches_played', 10),
('matches_25', '25 Matches Played', 'Played 25 matches', 'bi-trophy-fill', 'matches_played', 25),
('matches_50', '50 Matches Played', 'Played 50 matches', 'bi-trophy-fill', 'matches_played', 50),
('first_win', 'First Victory', 'Won your first match', 'bi-star-fill', 'wins', 1),
('wins_5', '5 Wins', 'Won 5 matches', 'bi-star-fill', 'wins', 5),
('wins_10', '10 Wins', 'Won 10 matches', 'bi-star-fill', 'wins', 10),
('wins_25', '25 Wins', 'Won 25 matches', 'bi-star-fill', 'wins', 25),
('tournament_champion', 'Tournament Champion', 'Won a tournament', 'bi-trophy-fill', 'tournaments_won', 1),
('mvp', 'Most Valuable Player', 'Earned MVP in a match', 'bi-award-fill', 'custom', 1),
('weekly_top', 'Weekly Top Player', 'Ranked #1 this week', 'bi-calendar-week-fill', 'weekly_top', 1),
('monthly_top', 'Monthly Top Player', 'Ranked #1 this month', 'bi-calendar-month-fill', 'monthly_top', 1);

-- ========================================
-- 10. CREATE INITIAL SEASONAL RANKINGS
-- ========================================
-- Populate with current data
INSERT INTO seasonal_leaderboard (user_id, period_type, period_start, period_end, points, matches_played, wins, losses, draws, win_rate, rank_position, is_current)
SELECT
    u.id,
    'lifetime' as period_type,
    '2000-01-01' as period_start,
    '2099-12-31' as period_end,
    COALESCE(SUM(mr.points_awarded + COALESCE(mr.admin_adjustment, 0)), 0) + COALESCE(u.points, 0) as points,
    COUNT(DISTINCT mr.match_id) as matches_played,
    COUNT(DISTINCT CASE WHEN (mr.points_awarded + COALESCE(mr.admin_adjustment, 0)) >= 10 THEN mr.match_id END) as wins,
    COUNT(DISTINCT CASE WHEN (mr.points_awarded + COALESCE(mr.admin_adjustment, 0)) = 0 AND mr.match_id IS NOT NULL THEN mr.match_id END) as losses,
    COUNT(DISTINCT CASE WHEN (mr.points_awarded + COALESCE(mr.admin_adjustment, 0)) = 5 AND mr.match_id IS NOT NULL THEN mr.match_id END) as draws,
    CASE
        WHEN COUNT(DISTINCT mr.match_id) > 0 THEN
            ROUND(COUNT(DISTINCT CASE WHEN (mr.points_awarded + COALESCE(mr.admin_adjustment, 0)) >= 10 THEN mr.match_id END) * 100.0 / COUNT(DISTINCT mr.match_id), 2)
        ELSE 0.00
    END as win_rate,
    0 as rank_position,
    TRUE as is_current
FROM users u
LEFT JOIN match_results_new mr ON u.id = mr.user_id
GROUP BY u.id, u.name
ORDER BY points DESC;

-- Set rank positions
SET @rank = 0;
UPDATE seasonal_leaderboard
SET rank_position = (@rank := @rank + 1)
WHERE period_type = 'lifetime' AND is_current = TRUE
ORDER BY points DESC, wins DESC;

-- Create weekly and monthly entries (for current period)
-- Weekly: Monday to Sunday of current week
-- Monthly: 1st to last day of current month
INSERT INTO seasonal_leaderboard (user_id, period_type, period_start, period_end, points, matches_played, wins, losses, draws, win_rate, rank_position, is_current)
SELECT
    u.id,
    'weekly' as period_type,
    DATE_SUB(CURDATE(), INTERVAL (WEEKDAY(CURDATE())) DAY) as period_start,
    DATE_ADD(DATE_SUB(CURDATE(), INTERVAL (WEEKDAY(CURDATE())) DAY), INTERVAL 6 DAY) as period_end,
    0 as points,
    0 as matches_played,
    0 as wins,
    0 as losses,
    0 as draws,
    0.00 as win_rate,
    0 as rank_position,
    TRUE as is_current
FROM users u;

INSERT INTO seasonal_leaderboard (user_id, period_type, period_start, period_end, points, matches_played, wins, losses, draws, win_rate, rank_position, is_current)
SELECT
    u.id,
    'monthly' as period_type,
    DATE_FORMAT(CURDATE(), '%Y-%m-01') as period_start,
    LAST_DAY(CURDATE()) as period_end,
    0 as points,
    0 as matches_played,
    0 as wins,
    0 as losses,
    0 as draws,
    0.00 as win_rate,
    0 as rank_position,
    TRUE as is_current
FROM users u;

-- ========================================
-- MIGRATION COMPLETE
-- ========================================