-- Day 4 Migration: Social + Geolocation Discovery
-- Run this in phpMyAdmin or MySQL CLI
USE sports_buddy;

-- 1. Add latitude and longitude columns to users table
ALTER TABLE users
ADD COLUMN latitude DOUBLE DEFAULT NULL AFTER email,
ADD COLUMN longitude DOUBLE DEFAULT NULL AFTER latitude;

-- 2. Create friend_requests table
CREATE TABLE IF NOT EXISTS friend_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    status ENUM('pending', 'accepted', 'rejected') NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_friendship (sender_id, receiver_id),
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Add venue_lat and venue_lng to matches for map markers
ALTER TABLE matches
ADD COLUMN venue_lat DOUBLE DEFAULT NULL AFTER venue_name,
ADD COLUMN venue_lng DOUBLE DEFAULT NULL AFTER venue_lat;

-- Update existing matches with approximate Vijayawada locations
UPDATE matches SET venue_lat = 16.5062, venue_lng = 80.6480 WHERE id = 1;
UPDATE matches SET venue_lat = 16.5200, venue_lng = 80.6300 WHERE id = 2;
UPDATE matches SET venue_lat = 16.4900, venue_lng = 80.6700 WHERE id = 3;
UPDATE matches SET venue_lat = 16.4800, venue_lng = 80.7000 WHERE id = 4;
UPDATE matches SET venue_lat = 16.5400, venue_lng = 80.6200 WHERE id = 5;
UPDATE matches SET venue_lat = 16.5100, venue_lng = 80.6600 WHERE id = 6;