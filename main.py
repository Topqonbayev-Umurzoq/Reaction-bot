import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db
from handlers import start, settings, group_commands, admin

logging.basicConfig(level=logging.INFO)

async def main():
    init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Handlerlarni ro'yxatga olish
    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(settings.router)
    dp.include_router(group_commands.router)

    print("✅ Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
