-- Migration: Add latitude/longitude aliases and update match locations
-- Run this after schema.sql and migration_day4.sql
-- Use in phpMyAdmin or MySQL CLI

USE sports_buddy;

-- Add latitude and longitude columns as aliases for venue_lat/venue_lng
ALTER TABLE matches
ADD COLUMN IF NOT EXISTS latitude DOUBLE DEFAULT NULL AFTER venue_lng,
ADD COLUMN IF NOT EXISTS longitude DOUBLE DEFAULT NULL AFTER latitude;

-- Copy venue_lat/lng to latitude/longitude for existing records
UPDATE matches SET latitude = venue_lat, longitude = venue_lng
WHERE venue_lat IS NOT NULL AND venue_lng IS NOT NULL;

-- Update matches with real venue names and realistic coordinates
-- Match 1: Cricket at Vijayawada Stadium
UPDATE matches SET 
    venue_name = 'Vijayawada Stadium',
    latitude = 16.5062, 
    longitude = 80.6480 
WHERE id = 1;

-- Match 2: Badminton at Indoor Sports Complex
UPDATE matches SET 
    venue_name = 'Indoor Sports Complex',
    latitude = 16.5200, 
    longitude = 80.6300 
WHERE id = 2;

-- Match 3: Football at City Ground
UPDATE matches SET 
    venue_name = 'City Ground',
    latitude = 16.4900, 
    longitude = 80.6700 
WHERE id = 3;

-- Match 4: Cricket at Beach Arena
UPDATE matches SET 
    venue_name = 'Beach Arena',
    latitude = 16.4800, 
    longitude = 80.7000 
WHERE id = 4;

-- Match 5: Basketball at YMCA Indoor Court
UPDATE matches SET 
    venue_name = 'YMCA Indoor Court',
    latitude = 16.5400, 
    longitude = 80.6200 
WHERE id = 5;

-- Match 6: Football at Sports Park
UPDATE matches SET 
    venue_name = 'Sports Park',
    latitude = 16.5100, 
    longitude = 80.6600 
WHERE id = 6;

-- Add status column if not exists (needed for filtering)
ALTER TABLE matches ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'open';

-- Update all matches to have 'open' status
UPDATE matches SET status = 'open' WHERE status IS NULL;