# config/config.py
# ============================================
# BOT KONFIGURATSIYASI
# ============================================

import os
from typing import Optional

class Config:
    """Konfiguratsiya"""
    
    # ============ TELEGRAM ============
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN env o'zgaruvchisi o'rnatilishi kerak!")
    
    # ============ DATABASE ============
    DATABASE_PATH = os.getenv("DATABASE_PATH", "reactions_bot.db")
    
    # ============ ADMIN ============
    ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
    
    # ============ BOT ============
    BOT_USERNAME = "reactions_bot"
    REQUEST_TIMEOUT = 60
    
    # ============ BROADCAST ============
    BROADCAST_DELAY = 0.1

# ============================================
# FSM (Finite State Machine) STATES
# ============================================

from aiogram.fsm.state import State, StatesGroup

class UserStates(StatesGroup):
    """Foydalanuvchi FSM holatlari"""
    
    # Til tanlash
    selecting_language = State()
    
    # Kanal boshqarish
    selecting_channel = State()
    add_channel = State()
    add_group = State()
    remove_channel = State()
    
    # Reaksiya boshqarish
    manage_reactions = State()
    selecting_reactions = State()
    
    # Broadcast
    entering_broadcast_message = State()
    selecting_broadcast_language = State()
    
    # Foydalanuvchi tekshirish
    verifying_subscription = State()

class AdminStates(StatesGroup):
    """Admin FSM holatlari"""
    
    # Admin paneli
    admin_menu = State()
    
    # Majburiy obuna
    manage_force_subscribe = State()
    add_force_channel = State()
    remove_force_channel = State()
    
    # Broadcast
    broadcast_message = State()
    broadcast_language_filter = State()
    
    # Foydalanuvchilar boshqarish
    manage_users = State()
    select_user_action = State()
