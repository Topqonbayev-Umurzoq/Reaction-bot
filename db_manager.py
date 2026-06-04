# database/db_manager.py
# ============================================
# MA'LUMOTLAR BAZASI MENEJERI
# ============================================

import asyncio
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import aiosqlite
from contextlib import asynccontextmanager

class DatabaseManager:
    """
    Ma'lumotlar bazasini boshqarish uchun asosiy sinf
    SQLite va PostgreSQL uchun mos
    """
    
    def __init__(self, db_path: str = "reactions_bot.db"):
        self.db_path = db_path
        self.connection: Optional[aiosqlite.Connection] = None
    
    async def initialize(self):
        """Bazani initsializatsiya qilish"""
        self.connection = await aiosqlite.connect(self.db_path)
        self.connection.row_factory = aiosqlite.Row
        await self.create_tables()
    
    async def close(self):
        """Bazani yopish"""
        if self.connection:
            await self.connection.close()
    
    @asynccontextmanager
    async def get_connection(self):
        """Connection kontekst menejeri"""
        if not self.connection:
            await self.initialize()
        yield self.connection
    
    # ============ USERS ============
    
    async def add_or_update_user(self, user_id: int, username: str, first_name: str, 
                                 last_name: str, language: str = 'uz', is_bot: bool = False):
        """Foydalanuvchini qo'shish yoki yangilash"""
        async with self.get_connection() as conn:
            await conn.execute(
                """INSERT INTO users (user_id, username, first_name, last_name, language_code, is_bot)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ON CONFLICT(user_id) DO UPDATE SET
                   username=excluded.username,
                   first_name=excluded.first_name,
                   last_name=excluded.last_name,
                   language_code=excluded.language_code,
                   updated_at=CURRENT_TIMESTAMP""",
                (user_id, username, first_name, last_name, language, is_bot)
            )
            await conn.commit()
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Foydalanuvchi ma'lumotlarini olish"""
        async with self.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def set_user_language(self, user_id: int, language: str):
        """Foydalanuvchi tilini o'rnatish"""
        async with self.get_connection() as conn:
            await conn.execute(
                "UPDATE users SET language_code = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                (language, user_id)
            )
            await conn.commit()
    
    async def set_admin(self, user_id: int, is_admin: bool = True):
        """Foydalanuvchini admin qilish"""
        async with self.get_connection() as conn:
            await conn.execute(
                "UPDATE users SET is_admin = ? WHERE user_id = ?",
                (is_admin, user_id)
            )
            await conn.commit()
    
    async def get_all_users(self, language: Optional[str] = None) -> List[Dict]:
        """Barcha foydalanuvchilarni olish (ixtiyoriy til filtri)"""
        async with self.get_connection() as conn:
            if language:
                cursor = await conn.execute(
                    "SELECT * FROM users WHERE language_code = ? AND is_bot = False ORDER BY created_at DESC",
                    (language,)
                )
            else:
                cursor = await conn.execute(
                    "SELECT * FROM users WHERE is_bot = False ORDER BY created_at DESC"
                )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_admin_ids(self) -> List[int]:
        """Admin IDlarini olish"""
        async with self.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT user_id FROM users WHERE is_admin = True"
            )
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
    
    async def count_users(self) -> int:
        """Foydalanuvchilar sonini olish"""
        async with self.get_connection() as conn:
            cursor = await conn.execute("SELECT COUNT(*) FROM users WHERE is_bot = False")
            return (await cursor.fetchone())[0]
    
    # ============ GROUPS ============
    
    async def add_or_update_group(self, group_id: int, group_title: str, group_type: str):
        """Guruhni qo'shish yoki yangilash"""
        async with self.get_connection() as conn:
            await conn.execute(
                """INSERT INTO groups (group_id, group_title, group_type)
                   VALUES (?, ?, ?)
                   ON CONFLICT(group_id) DO UPDATE SET
                   group_title=excluded.group_title,
                   updated_at=CURRENT_TIMESTAMP""",
                (group_id, group_title, group_type)
            )
            await conn.commit()
    
    async def get_group(self, group_id: int) -> Optional[Dict]:
        """Guruh ma'lumotlarini olish"""
        async with self.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT * FROM groups WHERE group_id = ?", (group_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def count_groups(self) -> int:
        """Guruhlar sonini olish"""
        async with self.get_connection() as conn:
            cursor = await conn.execute("SELECT COUNT(*) FROM groups WHERE is_active = True")
            return (await cursor.fetchone())[0]
    
    async def get_all_groups(self) -> List[Dict]:
        """Barcha faol guruhlarni olish"""
        async with self.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT * FROM groups WHERE is_active = True ORDER BY group_title ASC"
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_user_groups(self, user_id: int) -> List[Dict]:
        """Foydalanuvchining guruhlarini olish"""
        async with self.get_connection() as conn:
            cursor = await conn.execute(
                """SELECT DISTINCT g.* FROM groups g 
                   WHERE g.is_active = True 
                   ORDER BY g.group_title ASC""",
                ()
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    # ============ CHANNELS ============
    
    async def add_channel(self, channel_id: int, channel_title: str, 
                         channel_username: str, user_id: int):
        """Kanalni qo'shish"""
        async with self.get_connection() as conn:
            await conn.execute(
                """INSERT OR IGNORE INTO channels 
                   (channel_id, channel_title, channel_username, added_by_user)
                   VALUES (?, ?, ?, ?)""",
                (channel_id, channel_title, channel_username, user_id)
            )
            await conn.commit()
    
    async def remove_channel(self, channel_id: int):
        """Kanalni o'chirish"""
        async with self.get_connection() as conn:
            await conn.execute(
                "UPDATE channels SET is_active = False WHERE channel_id = ?",
                (channel_id,)
            )
            await conn.commit()
    
    async def get_channel(self, channel_id: int) -> Optional[Dict]:
        """Kanal ma'lumotlarini olish"""
        async with self.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT * FROM channels WHERE channel_id = ? AND is_active = True",
                (channel_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def get_all_channels(self) -> List[Dict]:
        """Barcha faol kanallarni olish"""
        async with self.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT * FROM channels WHERE is_active = True ORDER BY created_at DESC"
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_user_channels(self, user_id: int) -> List[Dict]:
        """Foydalanuvchi qo'shgan kanallarni olish"""
        async with self.get_connection() as conn:
            cursor = await conn.execute(
                """SELECT * FROM channels 
                   WHERE added_by_user = ? AND is_active = True 
                   ORDER BY created_at DESC""",
                (user_id,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def count_channels(self) -> int:
        """Kanallar sonini olish"""
        async with self.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT COUNT(*) FROM channels WHERE is_active = True"
            )
            return (await cursor.fetchone())[0]
    
    # ============ FORCE SUBSCRIBE ============
    
    async def add_force_subscribe_channel(self, channel_id: int):
        """Majburiy obuna kanaliga qo'shish"""
        async with self.get_connection() as conn:
            await conn.execute(
                "INSERT OR IGNORE INTO force_subscribe_channels (channel_id) VALUES (?)",
                (channel_id,)
            )
            await conn.commit()
    
    async def remove_force_subscribe_channel(self, channel_id: int):
        """Majburiy obuna kanalidan o'chirish"""
        async with self.get_connection() as conn:
            await conn.execute(
                "DELETE FROM force_subscribe_channels WHERE channel_id = ?",
                (channel_id,)
            )
            await conn.commit()
    
    async def get_force_subscribe_channels(self) -> List[int]:
        """Majburiy obuna kanallarini olish"""
        async with self.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT channel_id FROM force_subscribe_channels"
            )
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
    
    async def is_user_subscribed(self, user_id: int, channel_id: int) -> bool:
        """Foydalanuvchi kanuga obunalangan yoki yo'qligini tekshirish"""
        async with self.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT 1 FROM user_subscriptions WHERE user_id = ? AND channel_id = ?",
                (user_id, channel_id)
            )
            return (await cursor.fetchone()) is not None
    
    async def add_subscription(self, user_id: int, channel_id: int):
        """Obunani qo'shish"""
        async with self.get_connection() as conn:
            await conn.execute(
                "INSERT OR IGNORE INTO user_subscriptions (user_id, channel_id) VALUES (?, ?)",
                (user_id, channel_id)
            )
            await conn.commit()
    
    # ============ REACTIONS ============
    
    async def get_all_reactions(self, include_premium: bool = False) -> List[str]:
        """Barcha reaksiyalarni olish"""
        async with self.get_connection() as conn:
            if include_premium:
                cursor = await conn.execute(
                    "SELECT emoji FROM reactions ORDER BY reaction_id"
                )
            else:
                cursor = await conn.execute(
                    "SELECT emoji FROM reactions WHERE is_premium = False ORDER BY reaction_id"
                )
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
    
    async def get_group_reaction_settings(self, group_id: int) -> Optional[Dict]:
        """Guruh reaksiya sozlamalarini olish"""
        async with self.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT * FROM group_reaction_settings WHERE group_id = ?",
                (group_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def update_group_reactions(self, group_id: int, is_enabled: bool, 
                                     reactions: Optional[str] = None):
        """Guruh reaksiyalarini yangilash"""
        async with self.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT id FROM group_reaction_settings WHERE group_id = ?",
                (group_id,)
            )
            exists = await cursor.fetchone()
            
            if exists:
                await conn.execute(
                    """UPDATE group_reaction_settings 
                       SET is_reactions_enabled = ?, allowed_reactions = ?, updated_at = CURRENT_TIMESTAMP
                       WHERE group_id = ?""",
                    (is_enabled, reactions, group_id)
                )
            else:
                await conn.execute(
                    """INSERT INTO group_reaction_settings 
                       (group_id, is_reactions_enabled, allowed_reactions)
                       VALUES (?, ?, ?)""",
                    (group_id, is_enabled, reactions)
                )
            
            await conn.commit()
    
    # ============ BROADCAST ============
    
    async def add_broadcast_history(self, admin_id: int, message_text: str, 
                                   total_recipients: int, language_filter: Optional[str] = None):
        """Broadcast tarixini qo'shish"""
        async with self.get_connection() as conn:
            await conn.execute(
                """INSERT INTO broadcast_history 
                   (admin_id, message_text, total_recipients, language_filter)
                   VALUES (?, ?, ?, ?)""",
                (admin_id, message_text, total_recipients, language_filter)
            )
            await conn.commit()
    
    async def update_broadcast_result(self, broadcast_id: int, successful: int, failed: int):
        """Broadcast natijalarini yangilash"""
        async with self.get_connection() as conn:
            await conn.execute(
                """UPDATE broadcast_history 
                   SET successful = ?, failed = ?
                   WHERE id = ?""",
                (successful, failed, broadcast_id)
            )
            await conn.commit()
    
    # ============ STATISTICS ============
    
    async def get_statistics(self) -> Dict:
        """Statistika ma'lumotlarini olish"""
        async with self.get_connection() as conn:
            cursor = await conn.execute("SELECT * FROM statistics LIMIT 1")
            row = await cursor.fetchone()
            return dict(row) if row else {}
    
    async def update_statistics(self):
        """Statistikani yangilash"""
        total_users = await self.count_users()
        total_groups = await self.count_groups()
        total_channels = await self.count_channels()
        
        async with self.get_connection() as conn:
            await conn.execute(
                """UPDATE statistics 
                   SET total_users = ?, total_groups = ?, total_channels = ?,
                       updated_at = CURRENT_TIMESTAMP
                   WHERE stat_id = 1""",
                (total_users, total_groups, total_channels)
            )
            await conn.commit()
    
    # ============ LOGS ============
    
    async def add_log(self, user_id: int, action: str, details: Optional[str] = None):
        """Log qo'shish"""
        async with self.get_connection() as conn:
            await conn.execute(
                "INSERT INTO bot_logs (user_id, action, details) VALUES (?, ?, ?)",
                (user_id, action, details)
            )
            await conn.commit()
    
    async def create_tables(self):
        """Jadvallarni yaratish (agar mavjud bo'lmasa)"""
        async with self.get_connection() as conn:
            # Jadvallar yaratish SQL skripti
            create_tables_sql = """
            -- USERS
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                language_code TEXT DEFAULT 'uz',
                is_bot BOOLEAN DEFAULT 0,
                is_admin BOOLEAN DEFAULT 0,
                is_blocked BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- GROUPS
            CREATE TABLE IF NOT EXISTS groups (
                group_id INTEGER PRIMARY KEY,
                group_title TEXT,
                group_type TEXT,
                member_count INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- CHANNELS
            CREATE TABLE IF NOT EXISTS channels (
                channel_id INTEGER PRIMARY KEY,
                channel_title TEXT,
                channel_username TEXT,
                is_force_subscribe BOOLEAN DEFAULT 0,
                added_by_user INTEGER,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- FORCE_SUBSCRIBE_CHANNELS
            CREATE TABLE IF NOT EXISTS force_subscribe_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- USER_SUBSCRIPTIONS
            CREATE TABLE IF NOT EXISTS user_subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                channel_id INTEGER,
                subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, channel_id)
            );
            
            -- REACTIONS
            CREATE TABLE IF NOT EXISTS reactions (
                reaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                emoji TEXT UNIQUE,
                is_premium BOOLEAN DEFAULT 0,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- GROUP_REACTION_SETTINGS
            CREATE TABLE IF NOT EXISTS group_reaction_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER UNIQUE,
                is_reactions_enabled BOOLEAN DEFAULT 1,
                allowed_reactions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- BROADCAST_HISTORY
            CREATE TABLE IF NOT EXISTS broadcast_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER,
                message_text TEXT,
                total_recipients INTEGER,
                successful INTEGER DEFAULT 0,
                failed INTEGER DEFAULT 0,
                language_filter TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- STATISTICS
            CREATE TABLE IF NOT EXISTS statistics (
                stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_users INTEGER DEFAULT 0,
                total_groups INTEGER DEFAULT 0,
                total_channels INTEGER DEFAULT 0,
                daily_new_users INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- BOT_LOGS
            CREATE TABLE IF NOT EXISTS bot_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            for statement in create_tables_sql.split(';'):
                if statement.strip():
                    await conn.execute(statement)
            
            # Default reaksiyalarni qo'shish
            default_emojis = [
                '❤️', '👍', '😂', '😮', '😢', '🔥', '👏', '🙏',
                '💯', '✨', '🎉', '😍', '🤔', '😤', '🤮', '⚡',
                '🌟', '💪', '🚀', '🎯', '💔', '🤝', '👌', '🤙',
                '💥', '📱', '💻', '🎮', '🏆', '🥇', '⭐', '🌈',
                '🍕', '🍰', '😋', '🍻', '🎵', '📚', '🎓', '🏠',
                '🌍', '✈️', '🚗', '⚽', '🏀', '🎾', '🏐', '🎳',
                '🎬', '📸', '🎨', '🖼️', '🌺', '🌸', '🌼', '🌻',
                '🦋', '🐢', '🐻', '🦊', '🐱', '🐶', '🐭', '🦁',
                '🐲', '🦕', '🤖', '👽', '👻', '💀', '🎃'
            ]
            
            for emoji in default_emojis:
                await conn.execute(
                    "INSERT OR IGNORE INTO reactions (emoji, is_premium) VALUES (?, 0)",
                    (emoji,)
                )
            
            # Statistika jadvali
            await conn.execute(
                "INSERT OR IGNORE INTO statistics (stat_id, total_users, total_groups, total_channels, daily_new_users) VALUES (1, 0, 0, 0, 0)"
            )
            
            await conn.commit()
