"""
Telegram Reaction Bot
Adds reactions to messages in groups and channels
"""

import logging
import random
from telegram import Update, BotCommand, ReactionTypeEmoji
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from config import BOT_TOKEN, LOG_LEVEL, DEFAULT_REACTIONS, ENABLE_AUTO_REACTIONS
from database import (
    add_group, remove_group, add_channel, remove_channel,
    get_groups, get_channels, increment_reactions, increment_messages, get_stats
)

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
        self.app.add_handler(CommandHandler("add_group", self.add_group_command))
        self.app.add_handler(CommandHandler("remove_group", self.remove_group_command))
        self.app.add_handler(CommandHandler("add_channel", self.add_channel_command))
        self.app.add_handler(CommandHandler("remove_channel", self.remove_channel_command))
        self.app.add_handler(CommandHandler("list_groups", self.list_groups_command))
        self.app.add_handler(CommandHandler("list_channels", self.list_channels_command))
        
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
            "📋 Buyruqlar:\n\n"
            "📊 /stats - Bot statistikasi\n"
            "/reactions - Reaksiyalar ro'yxati\n\n"
            "👥 Guruh sozlamalari:\n"
            "/add_group - Guruhni qo'shish\n"
            "/remove_group - Guruhni o'chirish\n"
            "/list_groups - Guruhlarn ro'yxati\n\n"
            "📢 Kanal sozlamalari:\n"
            "/add_channel - Kanalini qo'shish\n"
            "/remove_channel - Kanalini o'chirish\n"
            "/list_channels - Kanallarning ro'yxati\n\n"
            "⚙️ Bot funksiyalari:\n"
            "- Xabarlarga avtomatik reaksiya qo'shish\n"
            "- Guruhlarda va kanallarda ishlash\n"
            "- Admin ruxsati kerak"
        )
        await update.message.reply_text(message)

    async def reactions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show available reactions"""
        reactions_text = "😊 Mavjud reaksiyalar:\n\n" + ", ".join(DEFAULT_REACTIONS)
        await update.message.reply_text(reactions_text)

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show bot statistics"""
        stats = get_stats()
        stats_message = (
            f"📊 Bot statistikasi:\n\n"
            f"✨ Qo'shilgan reaksiyalar: {stats['reactions_added']}\n"
            f"💬 Qayta ishlangan xabarlar: {stats['messages_processed']}\n"
            f"👥 Faol guruhlar: {stats['groups_count']}\n"
            f"📢 Faol kanallar: {stats['channels_count']}"
        )
        await update.message.reply_text(stats_message)

    async def auto_react(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Automatically add reactions to messages"""
        try:
            # Skip if message is from the bot itself
            if update.message.from_user.id == context.bot.id:
                return
            
            increment_messages()
            
            # Choose random reaction
            reaction = random.choice(DEFAULT_REACTIONS)
            
            # Add reaction with proper error handling
            try:
                await context.bot.set_message_reaction(
                    chat_id=update.effective_chat.id,
                    message_id=update.message.message_id,
                    reaction=[ReactionTypeEmoji(emoji=reaction)]
                )
                increment_reactions()
                logger.info(
                    f"✅ Reaksiya qo'shildi: {reaction} | "
                    f"Chat: {update.effective_chat.id} | "
                    f"Message: {update.message.message_id}"
                )
            except Exception as react_error:
                logger.error(
                    f"❌ Reaksiya qo'shib bo'lmadi: {str(react_error)} | "
                    f"Reaction: {reaction}"
                )
        except Exception as e:
            logger.error(f"❌ Xatolik auto_react'da: {str(e)}")

    async def add_group_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add current group to monitor"""
        if update.effective_chat.type not in ['group', 'supergroup']:
            await update.message.reply_text("❌ Bu buyruq faqat guruhlarda ishlaydi!")
            return
        
        chat_id = update.effective_chat.id
        chat_name = update.effective_chat.title
        
        if add_group(chat_id, chat_name):
            await update.message.reply_text(
                f"✅ Guruh qo'shildi: {chat_name}\n"
                f"ID: {chat_id}\n"
                f"Endi bot reaksiya qo'shishni boshlaydi!"
            )
            logger.info(f"✅ Guruh qo'shildi: {chat_name} ({chat_id})")
        else:
            await update.message.reply_text("⚠️ Bu guruh allaqachon qo'shilgan!")

    async def remove_group_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Remove current group from monitoring"""
        if update.effective_chat.type not in ['group', 'supergroup']:
            await update.message.reply_text("❌ Bu buyruq faqat guruhlarda ishlaydi!")
            return
        
        chat_id = update.effective_chat.id
        if remove_group(chat_id):
            await update.message.reply_text("✅ Guruh o'chirildi. Bot reaksiya qo'shishni to'xtatadi.")
            logger.info(f"✅ Guruh o'chirildi: {chat_id}")
        else:
            await update.message.reply_text("❌ Bu guruh ro'yxatda yo'q")

    async def add_channel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add current channel to monitor"""
        if update.effective_chat.type not in ['channel']:
            await update.message.reply_text("❌ Bu buyruq faqat kanallarda ishlaydi!")
            return
        
        chat_id = update.effective_chat.id
        chat_name = update.effective_chat.title
        
        if add_channel(chat_id, chat_name):
            await update.message.reply_text(
                f"✅ Kanal qo'shildi: {chat_name}\n"
                f"ID: {chat_id}"
            )
            logger.info(f"✅ Kanal qo'shildi: {chat_name} ({chat_id})")
        else:
            await update.message.reply_text("⚠️ Bu kanal allaqachon qo'shilgan!")

    async def remove_channel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Remove current channel from monitoring"""
        if update.effective_chat.type not in ['channel']:
            await update.message.reply_text("❌ Bu buyruq faqat kanallarda ishlaydi!")
            return
        
        chat_id = update.effective_chat.id
        if remove_channel(chat_id):
            await update.message.reply_text("✅ Kanal o'chirildi.")
            logger.info(f"✅ Kanal o'chirildi: {chat_id}")
        else:
            await update.message.reply_text("❌ Bu kanal ro'yxatda yo'q")

    async def list_groups_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all monitored groups"""
        groups = get_groups()
        if not groups:
            await update.message.reply_text("📭 Hech qanday guruh qo'shilmagan")
            return
        
        message = "👥 Faol guruhllar:\n\n"
        for chat_id, info in groups.items():
            message += f"• {info['name']} (ID: {chat_id})\n"
        
        await update.message.reply_text(message)

    async def list_channels_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all monitored channels"""
        channels = get_channels()
        if not channels:
            await update.message.reply_text("📭 Hech qanday kanal qo'shilmagan")
            return
        
        message = "📢 Faol kanallar:\n\n"
        for chat_id, info in channels.items():
            message += f"• {info['name']} (ID: {chat_id})\n"
        
        await update.message.reply_text(message)

    async def setup_commands(self):
        """Setup bot commands"""
        commands = [
            BotCommand("start", "Botni boshlash"),
            BotCommand("help", "Yordam"),
            BotCommand("reactions", "Reaksiyalar ro'yxati"),
            BotCommand("stats", "Statistika"),
            BotCommand("add_group", "Guruhni qo'shish"),
            BotCommand("remove_group", "Guruhni o'chirish"),
            BotCommand("list_groups", "Guruhlarn ro'yxati"),
            BotCommand("add_channel", "Kanalini qo'shish"),
            BotCommand("remove_channel", "Kanalini o'chirish"),
            BotCommand("list_channels", "Kanallarning ro'yxati"),
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
