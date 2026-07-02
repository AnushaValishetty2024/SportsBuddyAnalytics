-- ============================================================
-- Sports Buddy Chat System Migration
-- Adds conversation_members table for group/match chats
-- ============================================================

-- Create conversation_members table if not exists
CREATE TABLE IF NOT EXISTS conversation_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT NULL,
    match_id INT NULL,
    user_id INT NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
    UNIQUE KEY uk_unique_membership (conversation_id, user_id),
    UNIQUE KEY uk_unique_match_membership (match_id, user_id),
    INDEX idx_user (user_id),
    INDEX idx_match (match_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Verify conversations table has user1_id < user2_id unique constraint
-- (Already exists from models/chat.py: UNIQUE KEY uk_conversation_pair (user1_id, user2_id))

-- Verify messages table supports both private and group chat
-- (Already exists from models/chat.py with conversation_id and match_id columns)

-- Verify notifications table exists for chat notifications
-- (Already exists from models/chat.py)