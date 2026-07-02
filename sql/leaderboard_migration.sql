-- ============================================================
-- Leaderboard System Migration
-- Restructures match_results for dynamic leaderboard aggregation
-- ============================================================

-- 1. Add status column to matches if not exists
ALTER TABLE matches
  ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'open'
  COMMENT 'open, in_progress, completed, cancelled';

-- 2. Restructure match_results table
-- Drop old match_results if exists and recreate with proper structure
-- We use a temp approach: create new table, migrate data, swap

CREATE TABLE IF NOT EXISTS match_results_new (
    id INT AUTO_INCREMENT PRIMARY KEY,
    match_id INT NOT NULL UNIQUE,
    user_id INT NOT NULL COMMENT 'Player who earned points',
    points_awarded INT NOT NULL DEFAULT 0 COMMENT 'Points earned from match outcome',
    admin_adjustment INT NOT NULL DEFAULT 0 COMMENT 'Manual adjustment by admin (can be negative)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_match_id (match_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Create user_stats table (optional but recommended)
CREATE TABLE IF NOT EXISTS user_stats (
    user_id INT NOT NULL PRIMARY KEY,
    total_points INT NOT NULL DEFAULT 0,
    wins INT NOT NULL DEFAULT 0,
    losses INT NOT NULL DEFAULT 0,
    draws INT NOT NULL DEFAULT 0,
    matches_played INT NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Migrate existing data from old match_results to new structure
-- For each existing match result, create entries for all participants
INSERT IGNORE INTO match_results_new (match_id, user_id, points_awarded, admin_adjustment, created_at)
SELECT 
    mr.match_id,
    mp.user_id,
    CASE 
        WHEN mr.is_draw = 1 THEN 5
        WHEN mp.user_id = mr.winner_id THEN 10
        ELSE 0
    END AS points_awarded,
    0 AS admin_adjustment,
    mr.created_at
FROM match_results mr
JOIN match_participants mp ON mr.match_id = mp.match_id
WHERE mr.match_id IS NOT NULL;

-- 5. Populate user_stats from existing data
INSERT IGNORE INTO user_stats (user_id, total_points, wins, losses, draws, matches_played)
SELECT 
    u.id,
    COALESCE(SUM(mr_new.points_awarded + mr_new.admin_adjustment), 0) AS total_points,
    COALESCE(w.wins, 0) AS wins,
    COALESCE(l.losses, 0) AS losses,
    COALESCE(d.draws, 0) AS draws,
    COALESCE(mp_cnt.match_count, 0) AS matches_played
FROM users u
LEFT JOIN match_results_new mr_new ON u.id = mr_new.user_id
LEFT JOIN (
    SELECT mr.match_id, mr.winner_id, COUNT(*) AS wins
    FROM match_results mr
    WHERE mr.winner_id IS NOT NULL AND mr.is_draw = 0
    GROUP BY mr.winner_id
) w ON u.id = w.winner_id
LEFT JOIN (
    SELECT mr.match_id, mp.user_id, COUNT(*) AS losses
    FROM match_results mr
    JOIN match_participants mp ON mr.match_id = mp.match_id
    WHERE mr.is_draw = 0 AND mp.user_id != mr.winner_id
    GROUP BY mp.user_id
) l ON u.id = l.user_id
LEFT JOIN (
    SELECT mp.user_id, COUNT(DISTINCT mp.match_id) AS draw_count
    FROM match_results mr
    JOIN match_participants mp ON mr.match_id = mp.match_id
    WHERE mr.is_draw = 1
    GROUP BY mp.user_id
) d ON u.id = d.user_id
LEFT JOIN (
    SELECT user_id, COUNT(DISTINCT match_id) AS match_count
    FROM match_participants
    GROUP BY user_id
) mp_cnt ON u.id = mp_cnt.user_id
GROUP BY u.id;

-- 6. Swap tables (keep old for backup)
-- Uncomment to swap:
-- RENAME TABLE match_results TO match_results_old, match_results_new TO match_results;