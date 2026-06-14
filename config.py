import os
from dotenv import load_dotenv

# .env faylini yuklaydi
load_dotenv()

# Tokenni .env fayldan o'qiydi
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8789443133"))
SUBSCRIBE_CHANNEL = os.getenv("SUBSCRIBE_CHANNEL", "")
DB_NAME = "bot.db"

LANGUAGES = ["uz", "ru", "en"]
DEFAULT_LANG = "en"
