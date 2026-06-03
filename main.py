# main.py
# ============================================
# REAKSIYALAR BOT - ASOSIY FAYL
# Aiogram 3.x
# ============================================

import asyncio
import logging
from aiogram import Dispatcher, Bot, F, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.types import BotCommand, BotCommandScopeDefault
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Konfiguratsiya va modullar import
from config.config import Config
from database.db_manager import DatabaseManager
from handlers import user_handlers, admin_handlers

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variables
load_dotenv()

# ============================================
# GLOBAL VARIABLES
# ============================================

bot: Bot = None
dp: Dispatcher = None
db: DatabaseManager = None

# ============================================
# BOT COMMANDS SETUP
# ============================================

async def set_commands(bot: Bot):
    """Bot buyruqlarini o'rnatish"""
    commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="admin", description="Admin paneli"),
        BotCommand(command="help", description="Yordam"),
        BotCommand(command="settings", description="Sozlamalar"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
    logger.info("Bot commands set successfully")

# ============================================
# INITIALIZATION
# ============================================

async def initialize():
    """Botni initialize qilish"""
    global bot, dp, db
    
    try:
        # Bot tokeni tekshirish
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token:
            raise ValueError("BOT_TOKEN environment variable not set!")
        
        # Bot va Dispatcher yaratish
        bot = Bot(token=bot_token)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        
        # Database initsializatsiya
        db = DatabaseManager()
        await db.initialize()
        logger.info("Database initialized successfully")
        
        # Handlers initializatsiya
        user_handlers.init_handlers(db)
        admin_handlers.init_admin_handlers(db)
        
        # Bot commands o'rnatish
        await set_commands(bot)
        
        # Routerlarni registratsiya qilish
        dp.include_router(user_handlers.router)
        dp.include_router(admin_handlers.router)
        
        logger.info("Bot initialized successfully")
        
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        raise

# ============================================
# SHUTDOWN
# ============================================

async def shutdown():
    """Botni to'xtattish"""
    global bot, db
    
    try:
        if db:
            await db.close()
            logger.info("Database closed")
        
        if bot:
            await bot.session.close()
            logger.info("Bot session closed")
    
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

# ============================================
# ERROR HANDLER
# ============================================

async def handle_error(update: types.Update, error: Exception):
    """Xatoliklarni qayta ishlash"""
    logger.error(f"Error occurred: {error}")
    logger.error(f"Update: {update}")

# ============================================
# POLLING
# ============================================

async def polling():
    """Bot polling orqali ishga tushirish"""
    try:
        logger.info("Bot polling started...")
        await dp.start_polling(bot, handle_updates=True)
    
    except Exception as e:
        logger.error(f"Polling error: {e}")
    
    finally:
        await shutdown()

# ============================================
# WEBHOOK (OPSIONAL)
# ============================================

async def webhook_setup():
    """Webhook setupi (production uchun)"""
    try:
        webhook_url = os.getenv("WEBHOOK_URL")
        if webhook_url:
            await bot.set_webhook(webhook_url)
            logger.info(f"Webhook set: {webhook_url}")
    except Exception as e:
        logger.error(f"Webhook setup error: {e}")

# ============================================
# MAIN
# ============================================

async def main():
    """Asosiy funksiya"""
    try:
        # Initializing
        await initialize()
        
        # Polling orqali ishga tushirish
        await polling()
    
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        await shutdown()

# ============================================
# ENTRY POINT
# ============================================

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
