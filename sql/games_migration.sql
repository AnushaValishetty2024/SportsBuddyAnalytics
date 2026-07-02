-- Migration: Create game_categories table with logo support and seed data
-- Run this after schema.sql

USE sports_buddy;

-- Create game_categories table if not exists
CREATE TABLE IF NOT EXISTS game_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    logo VARCHAR(255) DEFAULT NULL COMMENT 'Path to game logo image',
    description TEXT DEFAULT NULL,
    rules TEXT DEFAULT NULL,
    location_info VARCHAR(255) DEFAULT NULL,
    display_order INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Seed data: popular sports with logos and descriptions
INSERT INTO game_categories (name, logo, description, rules, location_info, display_order) VALUES
('Cricket', '/static/logos/cricket.png', 'A bat-and-ball game played between two teams of eleven players on a field. One team bats while the other bowls and fields, trying to dismiss the batsmen and limit scoring.', 'Each team has 11 players. The batting team tries to score runs by hitting the ball and running between wickets. The bowling team tries to dismiss batsmen by hitting the stumps or catching the ball. Matches can be Test (5 days), ODI (50 overs), or T20 (20 overs) format.', 'Cricket grounds, stadiums, or open fields with a pitch', 1),
('Football', '/static/logos/football.png', 'A team sport played between two teams of eleven players with a spherical ball. Players use their feet to kick the ball into the opposing goal.', 'Two teams of 11 players each. The objective is to score goals by getting the ball into the opposing goal. Players cannot use their hands or arms (except the goalkeeper). Matches last 90 minutes (two 45-minute halves).', 'Football fields, stadiums, or open grounds with goalposts', 2),
('Badminton', '/static/logos/badminton.png', 'A racket sport played with shuttlecocks across a net. Can be played as singles or doubles, requiring agility, speed, and precision.', 'Played on a rectangular court divided by a net. Players hit a shuttlecock over the net using rackets. A rally ends when the shuttlecock hits the ground or goes out of bounds. Matches are best of 3 games, each played to 21 points.', 'Indoor badminton courts or outdoor marked courts with a net', 3),
('Basketball', '/static/logos/basketball.png', 'A team sport where two teams of five players try to score points by throwing a ball through the opposing team hoop.', 'Two teams of 5 players each. Points are scored by shooting the ball through the opponents hoop (2 or 3 points). Players dribble and pass to advance the ball. Physical contact is limited. Games consist of 4 quarters of 10-12 minutes.', 'Indoor basketball courts with hoops at each end', 4),
('Tennis', '/static/logos/tennis.png', 'A racket sport played individually (singles) or in pairs (doubles). Players hit a ball over a net into the opponent court.', 'Played on a rectangular court divided by a net. Players use rackets to hit a ball over the net into the opponent half. Points: 15, 30, 40, game. Matches are best of 3 or 5 sets. The ball must land within the court boundaries.', 'Tennis courts (clay, grass, or hard court) with a net', 5),
('Volleyball', '/static/logos/volleyball.png', 'A team sport where two teams of six players are separated by a net. Each team tries to score points by grounding a ball on the other team court.', 'Two teams of 6 players each. Teams hit a ball over a net using their hands/arms. Each team has 3 touches to return the ball. Points are scored when the ball touches the ground on the opponent side. Matches are best of 5 sets, each played to 25 points.', 'Indoor or beach volleyball courts with a net', 6),
('Table Tennis', '/static/logos/table-tennis.png', 'Also known as ping pong, a sport where two or four players hit a lightweight ball back and forth across a table using small rackets.', 'Played on a table divided by a net. Players use paddles to hit a lightweight ball back and forth. A point is scored when a player fails to return the ball properly. Games are played to 11 points. Matches are typically best of 5 or 7 games.', 'Indoor table tennis tables in sports centers', 7),
('Kabaddi', '/static/logos/kabaddi.png', 'A contact team sport played between two teams of seven players. A raider enters the opponent half, tries to tag defenders, and return without being caught.', 'Two teams of 7 players each. A raider enters the opponent half chanting kabaddi and tries to tag defenders. Defenders try to catch the raider. Points are scored for successful raids or tackles. Matches have two halves of 20 minutes.', 'Kabaddi courts, usually indoor in professional settings', 8);

-- Add logo column if game_categories already exists but without it
ALTER TABLE game_categories ADD COLUMN IF NOT EXISTS logo VARCHAR(255) DEFAULT NULL AFTER name;
ALTER TABLE game_categories ADD COLUMN IF NOT EXISTS description TEXT DEFAULT NULL AFTER logo;
ALTER TABLE game_categories ADD COLUMN IF NOT EXISTS rules TEXT DEFAULT NULL AFTER description;
ALTER TABLE game_categories ADD COLUMN IF NOT EXISTS location_info VARCHAR(255) DEFAULT NULL AFTER rules;