-- ============================================
-- REAKSIYALAR BOT - MA'LUMOTLAR BAZASI
-- PostgreSQL / SQLite
-- ============================================

-- 1. FOYDALANUVCHILAR JADVALI
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    language_code VARCHAR(10) DEFAULT 'uz',  -- 'uz', 'en', 'ru'
    is_bot BOOLEAN DEFAULT FALSE,
    is_admin BOOLEAN DEFAULT FALSE,
    is_blocked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. GURUHLAR JADVALI
CREATE TABLE groups (
    group_id BIGINT PRIMARY KEY,
    group_title VARCHAR(255),
    group_type VARCHAR(50),  -- 'supergroup', 'group'
    member_count INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. KANALLAR JADVALI
CREATE TABLE channels (
    channel_id BIGINT PRIMARY KEY,
    channel_title VARCHAR(255),
    channel_username VARCHAR(255),
    is_force_subscribe BOOLEAN DEFAULT FALSE,
    added_by_user BIGINT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (added_by_user) REFERENCES users(user_id)
);

-- 4. MAJBURIY OBUNA KANALLARI
CREATE TABLE force_subscribe_channels (
    id SERIAL PRIMARY KEY,
    channel_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE,
    UNIQUE(channel_id)
);

-- 5. FOYDALANUVCHI-KANAL A'ZOLIGI
CREATE TABLE user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE,
    UNIQUE(user_id, channel_id)
);

-- 6. EMOJI REAKSIYALARI
CREATE TABLE reactions (
    reaction_id SERIAL PRIMARY KEY,
    emoji VARCHAR(50) NOT NULL,
    is_premium BOOLEAN DEFAULT FALSE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(emoji)
);

-- 7. GURUH REAKSIYA SOZLAMALARI
CREATE TABLE group_reaction_settings (
    id SERIAL PRIMARY KEY,
    group_id BIGINT NOT NULL,
    is_reactions_enabled BOOLEAN DEFAULT TRUE,
    allowed_reactions TEXT,  -- JSON array: ["❤️", "👍", "😂"]
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups(group_id) ON DELETE CASCADE,
    UNIQUE(group_id)
);

-- 8. XABAR TARQATISH (BROADCAST) TARIX
CREATE TABLE broadcast_history (
    id SERIAL PRIMARY KEY,
    admin_id BIGINT NOT NULL,
    message_text TEXT,
    total_recipients INT,
    successful INT DEFAULT 0,
    failed INT DEFAULT 0,
    language_filter VARCHAR(10),  -- NULL = barcha, 'uz'/'en'/'ru'
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(user_id)
);

-- 9. STATISTIKA JADVALI
CREATE TABLE statistics (
    stat_id SERIAL PRIMARY KEY,
    total_users INT DEFAULT 0,
    total_groups INT DEFAULT 0,
    total_channels INT DEFAULT 0,
    daily_new_users INT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. LOG JADVALI
CREATE TABLE bot_logs (
    log_id SERIAL PRIMARY KEY,
    user_id BIGINT,
    action VARCHAR(100),
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- ============================================
-- INDEXLAR (PERFORMANCE UCHUN)
-- ============================================
CREATE INDEX idx_users_language ON users(language_code);
CREATE INDEX idx_users_is_admin ON users(is_admin);
CREATE INDEX idx_groups_is_active ON groups(is_active);
CREATE INDEX idx_channels_force_subscribe ON channels(is_force_subscribe);
CREATE INDEX idx_force_subscribe_channel ON force_subscribe_channels(channel_id);
CREATE INDEX idx_subscriptions_user ON user_subscriptions(user_id);
CREATE INDEX idx_group_reactions_group ON group_reaction_settings(group_id);
CREATE INDEX idx_broadcast_admin ON broadcast_history(admin_id);
CREATE INDEX idx_logs_user ON bot_logs(user_id);
CREATE INDEX idx_logs_action ON bot_logs(action);

-- ============================================
-- DEFAULT EMOJI REAKSIYALARI
-- ============================================
INSERT INTO reactions (emoji, is_premium) VALUES
('❤️', FALSE), ('👍', FALSE), ('😂', FALSE), ('😮', FALSE),
('😢', FALSE), ('🔥', FALSE), ('👏', FALSE), ('🙏', FALSE),
('💯', FALSE), ('✨', FALSE), ('🎉', FALSE), ('😍', FALSE),
('🤔', FALSE), ('😤', FALSE), ('🤮', FALSE), ('⚡', FALSE),
('🌟', FALSE), ('💪', FALSE), ('🚀', FALSE), ('🎯', FALSE),
('💔', FALSE), ('🤝', FALSE), ('👌', FALSE), ('🤙', FALSE),
('💥', FALSE), ('📱', FALSE), ('💻', FALSE), ('🎮', FALSE),
('🏆', FALSE), ('🥇', FALSE), ('⭐', FALSE), ('🌈', FALSE),
('🍕', FALSE), ('🍰', FALSE), ('😋', FALSE), ('🍻', FALSE),
('🎵', FALSE), ('📚', FALSE), ('🎓', FALSE), ('🏠', FALSE),
('🌍', FALSE), ('✈️', FALSE), ('🚗', FALSE), ('⚽', FALSE),
('🏀', FALSE), ('🎾', FALSE), ('🏐', FALSE), ('🎳', FALSE),
('🎬', FALSE), ('📸', FALSE), ('🎨', FALSE), ('🖼️', FALSE),
('🌺', FALSE), ('🌸', FALSE), ('🌼', FALSE), ('🌻', FALSE),
('🦋', FALSE), ('🐢', FALSE), ('🐻', FALSE), ('🦊', FALSE),
('🐱', FALSE), ('🐶', FALSE), ('🐭', FALSE), ('🦁', FALSE),
('🐲', FALSE), ('🦕', FALSE), ('🤖', FALSE), ('👽', FALSE),
('👻', FALSE), ('💀', FALSE), ('🎃', FALSE);

-- PREMIUM EMOJI (faqat premium users uchun)
INSERT INTO reactions (emoji, is_premium) VALUES
('🌟💎', TRUE), ('✨🎆', TRUE), ('🎪🎭', TRUE), ('🏰🗼', TRUE);

-- ============================================
-- INITIAL STATISTIKA
-- ============================================
INSERT INTO statistics (total_users, total_groups, total_channels, daily_new_users)
VALUES (0, 0, 0, 0);
