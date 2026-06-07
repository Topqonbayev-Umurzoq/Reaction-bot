from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8789443133"))
DB_NAME = "bot.db"

LANGUAGES = ["uz", "ru", "en"]
DEFAULT_LANG = "uz"
