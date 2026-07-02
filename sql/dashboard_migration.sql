-- Migration: Add dashboard support columns and tables
-- Run this AFTER schema.sql

USE sports_buddy;

-- Add latitude/longitude columns to matches for map display
ALTER TABLE matches
  ADD COLUMN IF NOT EXISTS latitude DECIMAL(10, 8) DEFAULT NULL AFTER venue_name,
  ADD COLUMN IF NOT EXISTS longitude DECIMAL(11, 8) DEFAULT NULL AFTER latitude,
  ADD COLUMN IF NOT EXISTS status ENUM('upcoming', 'ongoing', 'completed', 'cancelled') DEFAULT 'upcoming' AFTER max_players;

-- Index for match filtering by sport
ALTER TABLE matches
  ADD INDEX IF NOT EXISTS idx_sport_name (sport_name),
  ADD INDEX IF NOT EXISTS idx_match_date (match_date),
  ADD INDEX IF NOT EXISTS idx_status (status);

-- Nearby sports venues/businesses table
CREATE TABLE IF NOT EXISTS nearby_businesses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    business_type ENUM('ground', 'turf', 'stadium', 'indoor_court', 'sports_club') NOT NULL,
    description TEXT,
    address VARCHAR(300) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    contact_phone VARCHAR(20) DEFAULT NULL,
    sport_types VARCHAR(200) DEFAULT NULL COMMENT 'Comma-separated list of sports available',
    rating DECIMAL(2,1) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_business_type (business_type),
    INDEX idx_location (latitude, longitude)
);

-- Seed nearby businesses
INSERT INTO nearby_businesses (name, business_type, description, address, latitude, longitude, sport_types, rating) VALUES
('Vijayawada Cricket Stadium', 'stadium', 'Full-size cricket stadium with practice nets', 'IGMC Stadium Road, Vijayawada', 16.5062, 80.6480, 'cricket', 4.5),
('Indoor Sports Complex', 'indoor_court', 'Multi-purpose indoor courts for badminton, basketball', 'MG Road, Vijayawada', 16.5085, 80.6450, 'badminton,basketball,table_tennis', 4.2),
('City Football Ground', 'ground', 'Professional football ground with floodlights', 'Benz Circle, Vijayawada', 16.5100, 80.6400, 'football', 4.0),
('Beach Arena Turf', 'turf', 'Synthetic turf for cricket and football', 'Beach Road, Vijayawada', 16.5200, 80.6550, 'cricket,football', 4.3),
('SMART Badminton Academy', 'indoor_court', 'Professional badminton coaching and courts', 'Auto Nagar, Vijayawada', 16.4985, 80.6380, 'badminton', 4.6),
('Tennis Academy Vijayawada', 'indoor_court', 'Clay and hard court tennis facilities', 'Gurunanak Colony, Vijayawada', 16.5150, 80.6520, 'tennis', 4.1),
('Railway Stadium', 'stadium', 'Multi-sport stadium with athletics track', 'Railway Station Road, Vijayawada', 16.5120, 80.6440, 'cricket,football,athletics', 4.0),
('NTR Stadium Turf', 'turf', 'Synthetic turf for 5-a-side football and cricket', 'NTR Stadium, Vijayawada', 16.5140, 80.6430, 'football,cricket', 4.4);

-- Create games_sports table for the all-games section
CREATE TABLE IF NOT EXISTS game_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    icon_path VARCHAR(255) DEFAULT NULL,
    display_order INT DEFAULT 0
);

INSERT INTO game_categories (name, display_order) VALUES
('Cricket', 1),
('Football', 2),
('Badminton', 3),
('Tennis', 4),
('Basketball', 5),
('Volleyball', 6);

-- Update existing matches with sample coordinates if null
UPDATE matches SET latitude = 16.5062, longitude = 80.6480 WHERE latitude IS NULL AND id = 1;
UPDATE matches SET latitude = 16.5085, longitude = 80.6450 WHERE latitude IS NULL AND id = 2;
UPDATE matches SET latitude = 16.5100, longitude = 80.6400 WHERE latitude IS NULL AND id = 3;
UPDATE matches SET latitude = 16.5200, longitude = 80.6550 WHERE latitude IS NULL AND id = 4;
UPDATE matches SET latitude = 16.4985, longitude = 80.6380 WHERE latitude IS NULL AND id = 5;
UPDATE matches SET latitude = 16.5150, longitude = 80.6520 WHERE latitude IS NULL AND id = 6;