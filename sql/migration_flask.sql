-- Migration: Align matches table with Flask app requirements
-- Run this AFTER schema.sql to add missing columns and support the create-match flow

-- The Flask route inserts: creator_id, sport_type, location, match_time, max_players
-- The original schema has: creator_id, sport_type, sport_name, match_date, match_time, venue_name, max_players

-- Step 1: Add `location` column as an alias/alternative to venue_name
-- (so both the Flask app and the PHP backend can co-exist)
ALTER TABLE matches
  ADD COLUMN IF NOT EXISTS location VARCHAR(200) DEFAULT NULL AFTER venue_name;

-- Step 2: Add `sport_name` if missing
-- (already exists in original schema, but ensuring compatibility)
-- ALTER TABLE matches ADD COLUMN IF NOT EXISTS sport_name VARCHAR(100) NOT NULL DEFAULT '' AFTER sport_type;

-- Step 3: Ensure match_date column exists
-- ALTER TABLE matches ADD COLUMN IF NOT EXISTS match_date DATE DEFAULT NULL AFTER sport_name;

-- Note: If your `matches` table was created WITHOUT sport_name, match_date, venue_name
-- and instead has `location`, run this instead:
-- ALTER TABLE matches
--   ADD COLUMN sport_name VARCHAR(100) NOT NULL DEFAULT 'General' AFTER sport_type,
--   ADD COLUMN match_date DATE DEFAULT NULL AFTER sport_name,
--   CHANGE COLUMN location venue_name VARCHAR(200) NOT NULL DEFAULT 'Unknown';