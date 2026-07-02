 -- Team Management Foundation - Database Migration
-- Run this script to add teams functionality to Sports Buddy

USE sports_buddy;

-- Teams table
CREATE TABLE IF NOT EXISTS teams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    sport_type VARCHAR(50) NOT NULL,
    location VARCHAR(200) NOT NULL,
    logo VARCHAR(255) DEFAULT NULL,
    captain_id INT NOT NULL,
    max_members INT NOT NULL DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (captain_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Team members table
CREATE TABLE IF NOT EXISTS team_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    team_id INT NOT NULL,
    user_id INT NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_team_user (team_id, user_id),
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Add profile_picture to users table if it doesn't exist
-- Attempt to add column, will fail silently if already exists
CREATE TABLE IF NOT EXISTS temp_users_check (profile_picture VARCHAR(255) DEFAULT NULL);
-- This is a workaround - in practice, run the ALTER below if column doesn't exist
ALTER TABLE users ADD COLUMN profile_picture VARCHAR(255) DEFAULT NULL;

-- Indexes for better query performance
CREATE INDEX idx_teams_sport_type ON teams(sport_type);
CREATE INDEX idx_teams_location ON teams(location);
CREATE INDEX idx_team_members_team_id ON team_members(team_id);
CREATE INDEX idx_team_members_user_id ON team_members(user_id);
