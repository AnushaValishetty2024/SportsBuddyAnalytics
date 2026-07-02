-- Sports Match Platform - Database Schema & Seed Data
-- Run this in phpMyAdmin or MySQL CLI
-- This file uses the database name 'sports_buddy' (matches db.php config)

CREATE DATABASE IF NOT EXISTS sports_buddy;
USE sports_buddy;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Matches table
CREATE TABLE IF NOT EXISTS matches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    creator_id INT NOT NULL,
    sport_type ENUM('indoor', 'outdoor') NOT NULL,
    sport_name VARCHAR(100) NOT NULL,
    match_date DATE NOT NULL,
    match_time TIME NOT NULL,
    venue_name VARCHAR(200) NOT NULL,
    max_players INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Match participants table
CREATE TABLE IF NOT EXISTS match_participants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    match_id INT NOT NULL,
    user_id INT NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_match_user (match_id, user_id),
    FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ========================================
-- LEADERBOARD SYSTEM TABLES
-- ========================================

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

-- ========================================
-- SEED DATA
-- ========================================

-- Users
INSERT INTO users (id, name, email) VALUES
(1, 'Anusha', 'anusha@gmail.com'),
(2, 'Rahul', 'rahul@gmail.com'),
(3, 'Sneha', 'sneha@gmail.com'),
(4, 'Kiran', 'kiran@gmail.com');

-- Initialize player_points for all existing users
INSERT INTO player_points (user_id, points, wins, losses, draws, matches_played) VALUES
(1, 0, 0, 0, 0, 0),
(2, 0, 0, 0, 0, 0),
(3, 0, 0, 0, 0, 0),
(4, 0, 0, 0, 0, 0);

-- Matches - sport data covering all 4 sports
INSERT INTO matches (id, creator_id, sport_type, sport_name, match_date, match_time, venue_name, max_players) VALUES
(1, 1, 'outdoor', 'Cricket', '2026-06-23', '17:00:00', 'Vijayawada Stadium', 10),
(2, 2, 'indoor', 'Badminton', '2026-06-24', '18:30:00', 'Indoor Sports Complex', 4),
(3, 3, 'outdoor', 'Football', '2026-06-25', '16:00:00', 'City Ground', 14),
(4, 4, 'outdoor', 'Cricket', '2026-06-26', '07:00:00', 'Beach Arena', 10),
(5, 1, 'indoor', 'Basketball', '2026-06-27', '19:00:00', 'YMCA Indoor Court', 10),
(6, 2, 'outdoor', 'Football', '2026-06-28', '15:30:00', 'Sports Park', 10);

-- Match participants
INSERT INTO match_participants (match_id, user_id) VALUES
(1, 2),
(1, 3),
(2, 1),
(3, 4),
(4, 2),
(4, 3),
(5, 3),
(5, 4);