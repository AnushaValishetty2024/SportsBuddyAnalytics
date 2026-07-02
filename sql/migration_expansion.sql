-- Migration: Fix friend_requests table UNIQUE constraint
-- The original UNIQUE KEY on (sender_id, receiver_id) prevents
-- reverse-direction requests. We need to drop and recreate it properly.
-- Run this in phpMyAdmin or MySQL CLI

USE sports_buddy;

-- 1. Drop the restrictive unique key
ALTER TABLE friend_requests DROP INDEX unique_friendship;

-- 2. Add a more flexible unique key (allows both directions)
-- Note: We handle duplicate prevention in PHP code instead
-- Just keep a regular index for performance
ALTER TABLE friend_requests ADD INDEX idx_sender_receiver (sender_id, receiver_id);
ALTER TABLE friend_requests ADD INDEX idx_receiver_sender (receiver_id, sender_id);