-- Migration: Create sports_venues table for Nearby Sports Venues feature
CREATE TABLE IF NOT EXISTS sports_venues (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    sport_types VARCHAR(500) NOT NULL COMMENT 'Comma-separated list of sports',
    address TEXT,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    rating DECIMAL(2, 1) DEFAULT 0.0,
    available_slots INT DEFAULT 0,
    distance_km DECIMAL(6, 2) DEFAULT 0.00,
    image_url VARCHAR(500) DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;