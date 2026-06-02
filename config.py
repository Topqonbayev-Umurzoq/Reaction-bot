"""
Bot Configuration Settings
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Bot Token (from .env file)
BOT_TOKEN = os.getenv('BOT_TOKEN', '')

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Debug mode
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Reaction settings
DEFAULT_REACTIONS = [
    '👍',  # Thumbs up
    '❤️',  # Heart
    '🔥',  # Fire
    '😂',  # Laughing
    '😢',  # Sad
    '🎉',  # Celebration
    '👏',  # Clapping
    '✅',  # Check mark
]

# Bot settings
COMMAND_PREFIX = '/'
ADMIN_ONLY = False  # Set to True if only admins can control bot

# Chat configuration - add your groups/channels
MONITORED_CHATS = {
    # -1001234567890: ['👍', '❤️', '🔥'],  # Chat ID: allowed reactions
}

# Features
ENABLE_AUTO_REACTIONS = True
ENABLE_MANUAL_REACTIONS = True
ENABLE_REACTION_STATS = True
