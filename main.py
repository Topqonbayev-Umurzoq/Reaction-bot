"""
Telegram Reaction Bot
Adds reactions to messages in groups and channels
"""

import logging
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from config import BOT_TOKEN, LOG_LEVEL, DEFAULT_REACTIONS, ENABLE_AUTO_REACTIONS

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=LOG_LEVEL
)
logger = logging.getLogger(__name__)


class ReactionBot:
    def __init__(self, token: str):
        self.token = token
        self.app = Application.builder().token(token).build()
        self.setup_handlers()

    def setup_handlers(self):
        """Setup all command and message handlers"""
        # Commands
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("reactions", self.reactions_command))
        self.app.add_handler(CommandHandler("stats", self.stats_command))
        
        # Message handlers
        if ENABLE_AUTO_REACTIONS:
            self.app.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.auto_react)
            )

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        message = (
            "👋 Assalomu alaikum! Men Reaction Bot.\n\n"
            "Men guruh va kanallarda xabar gaplarga reaksiya qo'shaaman.\n\n"
            "Buyruqlarni bilish uchun /help yozing."
        )
        await update.message.reply_text(message)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        message = (
            "📋 Dostupnye komandy:\n\n"
            "/start - Boshlash\n"
            "/help - Yordam\n"
            "/reactions - Reaksiyalar ro'yxati\n"
            "/stats - Statistika\n\n"
            "🤖 Bot funksiyalari:\n"
            "- Xabarlarga avtomatik reaksiya qo'shish\n"
            "- Reaksiya statistikasini ko'rish\n"
            "- Guruh va kanallarda to'full sozlamalar"
        )
        await update.message.reply_text(message)

    async def reactions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show available reactions"""
        reactions_text = "😊 Mavjud reaksiyalar:\n\n" + ", ".join(DEFAULT_REACTIONS)
        await update.message.reply_text(reactions_text)

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show bot statistics"""
        stats_message = (
            "📊 Bot statistikasi:\n\n"
            "Qo'shilgan reaksiyalar: 0\n"
            "Faol guruhlar: 0\n"
            "Faol kanallar: 0\n\n"
            "(Statistika hali yozilmagan)"
        )
        await update.message.reply_text(stats_message)

    async def auto_react(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Automatically add reactions to messages"""
        try:
            # Add a random reaction to the message
            import random
            reaction = random.choice(DEFAULT_REACTIONS)
            
            # Add reaction (requires Bot API 5.4+)
            await context.bot.set_message_reaction(
                chat_id=update.effective_chat.id,
                message_id=update.message.message_id,
                reaction=reaction
            )
            logger.info(
                f"Added reaction {reaction} to message in chat {update.effective_chat.id}"
            )
        except Exception as e:
            logger.error(f"Error adding reaction: {e}")

    async def setup_commands(self):
        """Setup bot commands"""
        commands = [
            BotCommand("start", "Botni boshlash"),
            BotCommand("help", "Yordam olish"),
            BotCommand("reactions", "Reaksiyalar ro'yxati"),
            BotCommand("stats", "Statistika"),
        ]
        await self.app.bot.set_my_commands(commands)

    async def post_init(self, app: Application):
        """Run after bot initialization"""
        await self.setup_commands()
        logger.info("Bot successfully started!")

    def run(self):
        """Start the bot"""
        self.app.post_init = self.post_init
        logger.info("Starting Reaction Bot...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point"""
    if not BOT_TOKEN:
        raise ValueError(
            "BOT_TOKEN not found in .env file. "
            "Please add your token to the .env file."
        )
    
    bot = ReactionBot(BOT_TOKEN)
    bot.run()


if __name__ == "__main__":
    main()
