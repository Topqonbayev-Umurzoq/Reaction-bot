# handlers/user_handlers.py
# ============================================
# FOYDALANUVCHI HANDLERS
# ============================================

import re
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command, StateFilter
from db_manager import DatabaseManager
from config import UserStates
from localization import get_text, LANGUAGES
import logging

logger = logging.getLogger(__name__)
router = Router()

# Database instance (global)
db: DatabaseManager = None

def init_handlers(database: DatabaseManager):
    """Handlerlari initialize qilish"""
    global db
    db = database

# ============================================
# KEYBOARD FUNKSIYALARI
# ============================================

def get_language_keyboard() -> InlineKeyboardMarkup:
    """Til tanlash klaviaturas"""
    buttons = [
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_main_menu_keyboard(language: str) -> ReplyKeyboardMarkup:
    """Asosiy menyu klaviaturas"""
    buttons = [
        [KeyboardButton(text="📢 KANAL UCHUN"), KeyboardButton(text="👥 GURUH UCHUN")],
        [KeyboardButton(text=get_text('btn_guide', language)), KeyboardButton(text=get_text('btn_stats', language))]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_back_keyboard(language: str) -> ReplyKeyboardMarkup:
    """Orqaga qaytish klaviaturas"""
    buttons = [
        [KeyboardButton(text=get_text('btn_back', language))]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# ============================================
# /START BUYRUGI
# ============================================

@router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    """
    /start buyrugi
    Til tanlash ekrani ko'rsatadi
    """
    try:
        user_id = message.from_user.id
        
        # Foydalanuvchini bazaga qo'shish
        await db.add_or_update_user(
            user_id=user_id,
            username=message.from_user.username or "Unknown",
            first_name=message.from_user.first_name or "",
            last_name=message.from_user.last_name or "",
            language="uz",  # Default
            is_bot=message.from_user.is_bot
        )
        
        # Mavcut foydalanuvchini tekshirish
        user = await db.get_user(user_id)
        
        if user:
            current_language = user.get('language_code', 'uz')
            
            # Agar til allaqachon tanlangan bo'lsa, asosiy menyuni ko'rsatish
            if current_language and current_language != 'uz':
                welcome_text = get_text('main_menu', current_language)
                await message.answer(
                    welcome_text,
                    reply_markup=get_main_menu_keyboard(current_language)
                )
            else:
                # Til tanlash ekrani
                welcome_text = get_text('start_welcome', 'uz')
                await message.answer(
                    welcome_text,
                    reply_markup=get_language_keyboard()
                )
                await state.set_state(UserStates.selecting_language)
        
        # Log qilish
        await db.add_log(user_id, "start_command", "Bot ishga tushdi")
        
    except Exception as e:
        logger.error(f"Start command error: {e}")
        await message.answer("❌ Xato yuz berdi")

# ============================================
# TIL TANLASH
# ============================================

@router.callback_query(F.data.startswith("lang_"), UserStates.selecting_language)
async def select_language(query: types.CallbackQuery, state: FSMContext):
    """Til tanlash callback"""
    try:
        user_id = query.from_user.id
        language = query.data.split("_")[1]  # "lang_uz" -> "uz"
        
        # Tilni bazaga saqlash
        await db.set_user_language(user_id, language)
        
        # Holatni tozalash
        await state.clear()
        
        # Asosiy menyuni ko'rsatish
        welcome_text = get_text('language_selected', language)
        main_menu_text = get_text('main_menu', language)
        
        await query.message.edit_text(welcome_text)
        await query.message.answer(
            main_menu_text,
            reply_markup=get_main_menu_keyboard(language)
        )
        
        await db.add_log(user_id, "language_selection", f"Til tanlandi: {language}")
        
    except Exception as e:
        logger.error(f"Language selection error: {e}")
        await query.answer("❌ Xato yuz berdi")

# ============================================
# MAIN MENU TUGMALARI
# ============================================


# ============================================
# KANALLAR MENYUSI
# ============================================

async def handle_channels_menu(message: types.Message, language: str, state: FSMContext):
    """Kanallar menyusi"""
    try:
        channels_text = get_text('channels_menu', language)
        
        buttons = [
            [KeyboardButton(text=get_text('btn_add_channel', language))],
            [KeyboardButton(text=get_text('btn_remove_channel', language))],
            [KeyboardButton(text=get_text('btn_back', language))]
        ]
        
        kb = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
        await message.answer(channels_text, reply_markup=kb)
        await state.set_state(UserStates.selecting_channel)
        
    except Exception as e:
        logger.error(f"Channels menu error: {e}")

# ============================================
# CHANNEL INPUT PARSING

def parse_channel_input(channel_input: str):
    """Kanal identifikatorini tahlil qiladi"""
    if not channel_input:
        return None
    channel_input = channel_input.strip()
    # Support t.me links and @username formats
    url_match = re.match(r'^(?:https?://)?t\.me/(@?[A-Za-z0-9_]{5,})$', channel_input, re.IGNORECASE)
    if url_match:
        username = url_match.group(1)
        return username if username.startswith('@') else f'@{username}'
    if re.match(r'^@[A-Za-z0-9_]{5,}$', channel_input):
        return channel_input
    if re.match(r'^-?\d+$', channel_input):
        try:
            return int(channel_input)
        except ValueError:
            return None
    return None

@router.message(StateFilter(UserStates.selecting_channel), F.text)
async def handle_channel_menu_choice(message: types.Message, state: FSMContext):
    """Kanal boshqarish menyusi tanlovlarini qayta ishlaydi"""
    try:
        user = await db.get_user(message.from_user.id)
        language = user.get('language_code', 'uz') if user else 'uz'
        text = message.text

        if text == get_text('btn_add_channel', language):
            await message.answer(get_text('enter_channel_id', language))
            await state.set_state(UserStates.add_channel)
            return

        if text == get_text('btn_remove_channel', language):
            await message.answer(get_text('enter_channel_id', language))
            await state.set_state(UserStates.remove_channel)
            return

        if text == get_text('btn_back', language):
            await state.clear()
            await message.answer(get_text('main_menu', language), reply_markup=get_main_menu_keyboard(language))
            return

        await message.answer(get_text('error', language), reply_markup=ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text=get_text('btn_add_channel', language))],
            [KeyboardButton(text=get_text('btn_remove_channel', language))],
            [KeyboardButton(text=get_text('btn_back', language))]
        ], resize_keyboard=True))

    except Exception as e:
        logger.error(f"Channel menu choice error: {e}")

@router.message(StateFilter(UserStates.add_channel))
async def process_add_channel(message: types.Message, state: FSMContext):
    """Kanal qo'shish jarayoni"""
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    language = user.get('language_code', 'uz') if user else 'uz'
    channel_input = message.text.strip()

    channel_identifier = parse_channel_input(channel_input)
    if not channel_identifier:
        await message.answer(get_text('invalid_channel', language))
        return

    try:
        chat = await message.bot.get_chat(channel_identifier)
        bot_user = await message.bot.get_me()
        await message.bot.get_chat_member(chat.id, bot_user.id)
    except Exception as e:
        logger.error(f"Channel verification failed: {e}")
        await message.answer(get_text('invalid_channel', language))
        return

    try:
        await db.add_channel(
            channel_id=chat.id,
            channel_title=chat.title or chat.username or 'Unknown',
            channel_username=f'@{chat.username}' if chat.username else '',
            user_id=user_id
        )
        await db.add_log(user_id, 'add_channel', f'Added channel: {chat.id}')
        await message.answer(get_text('channel_added', language), reply_markup=get_main_menu_keyboard(language))
        await state.clear()
    except Exception as e:
        logger.error(f"Add channel failed: {e}")
        await message.answer(get_text('error', language))
        await state.clear()

@router.message(StateFilter(UserStates.remove_channel))
async def process_remove_channel(message: types.Message, state: FSMContext):
    """Kanal o'chirish jarayoni"""
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    language = user.get('language_code', 'uz') if user else 'uz'
    channel_input = message.text.strip()

    channel_identifier = parse_channel_input(channel_input)
    if not channel_identifier:
        await message.answer(get_text('invalid_channel', language))
        return

    try:
        if isinstance(channel_identifier, str):
            chat = await message.bot.get_chat(channel_identifier)
            channel_id = chat.id
        else:
            channel_id = channel_identifier
        await db.remove_channel(channel_id)
        await message.answer(get_text('channel_removed', language), reply_markup=get_main_menu_keyboard(language))
        await state.clear()
    except Exception as e:
        logger.error(f"Remove channel failed: {e}")
        await message.answer(get_text('invalid_channel', language))
        await state.clear()

# ============================================
# MAIN MENU TUGMALARI

@router.message(F.text)
async def handle_main_menu(message: types.Message, state: FSMContext):
    """Asosiy menyu tugmalarini qayta ishlash"""
    try:
        user_id = message.from_user.id
        user = await db.get_user(user_id)
        
        if not user:
            await message.answer("❌ Foydalanuvchi topilmadi. /start buyrug'idan boshlang.")
            return
        
        language = user.get('language_code', 'uz')
        text = message.text
        
        # Kanallar tugmasi
        if text == "📢 KANAL UCHUN":
            await handle_channels_menu(message, language, state)
        
        # Guruhlar tugmasi
        elif text == "👥 GURUH UCHUN":
            await handle_groups_menu(message, language, state)
        
        # Qo'llanma tugmasi
        elif text == get_text('btn_guide', language):
            await handle_guide(message, language)
        
        # Statistika tugmasi
        elif text == get_text('btn_stats', language):
            await handle_statistics(message, language)
        
        # Orqaga tugmasi
        elif text == get_text('btn_back', language):
            menu_text = get_text('main_menu', language)
            await message.answer(
                menu_text,
                reply_markup=get_main_menu_keyboard(language)
            )
        
        else:
            await message.answer(
                get_text('error', language),
                reply_markup=get_main_menu_keyboard(language)
            )
    
    except Exception as e:
        logger.error(f"Main menu handler error: {e}")

# ============================================
# GURUH REAKSIYALARI MENYUSI
# ============================================

async def handle_groups_menu(message: types.Message, language: str, state: FSMContext):
    """Guruh reaksiyalari menyusi"""
    try:
        groups_text = get_text('groups_menu', language)
        
        buttons = [
            [KeyboardButton(text=get_text('btn_reactions_on', language))],
            [KeyboardButton(text=get_text('btn_reactions_off', language))],
            [KeyboardButton(text=get_text('btn_select_reactions', language))],
            [KeyboardButton(text=get_text('btn_back', language))]
        ]
        
        kb = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
        await message.answer(groups_text, reply_markup=kb)
        await state.set_state(UserStates.manage_reactions)
        
    except Exception as e:
        logger.error(f"Groups menu error: {e}")

# ============================================
# QOLLANMA
# ============================================

async def handle_guide(message: types.Message, language: str):
    """Qo'llanma ko'rsatish"""
    guides = {
        'uz': """
📖 QOLLANMA

/reaksiya - Guruhda reaksiyalarni yoqish
/reaksiya_on - Reaksiyalarni yoqish
/reaksiya_off - Reaksiyalarni o'chirish
/settings - Sozlamalar

🎯 Reaksiyalar botdan foydalanish:
1. Botni guruhga qo'shing
2. Xabarlarning ostiga reaksiya emoji-lari chiqadi
3. Foydalanuvchilar emoji-larni bosib reaksiya berishi mumkin
        """,
        'en': """
📖 GUIDE

/reaction - Enable reactions in group
/reaction_on - Turn on reactions
/reaction_off - Turn off reactions
/settings - Settings

🎯 How to use Reactions Bot:
1. Add the bot to your group
2. Reaction emojis will appear below messages
3. Users can click on emojis to react
        """,
        'ru': """
📖 РУКОВОДСТВО

/reaction - Включить реакции в группе
/reaction_on - Включить реакции
/reaction_off - Отключить реакции
/settings - Настройки

🎯 Как использовать бота реакций:
1. Добавьте бота в вашу группу
2. Эмодзи реакций появятся под сообщениями
3. Пользователи смогут нажимать на эмодзи, чтобы реагировать
        """
    }
    
    guide_text = guides.get(language, guides['uz'])
    user = await db.get_user(message.from_user.id)
    lang = user.get('language_code', 'uz') if user else 'uz'
    
    await message.answer(guide_text, reply_markup=get_main_menu_keyboard(lang))

# ============================================
# STATISTIKA
# ============================================

async def handle_statistics(message: types.Message, language: str):
    """Statistika ko'rsatish"""
    try:
        stats = await db.get_statistics()
        
        stats_text = get_text('statistics', language,
            total_users=stats.get('total_users', 0),
            total_groups=stats.get('total_groups', 0),
            total_channels=stats.get('total_channels', 0),
            daily_new_users=stats.get('daily_new_users', 0)
        )
        
        await message.answer(stats_text, reply_markup=get_main_menu_keyboard(language))
        
    except Exception as e:
        logger.error(f"Statistics error: {e}")
        await message.answer(get_text('error', language))

# ============================================
# ASOSIY ROUTER
# ============================================

def get_router() -> Router:
    """Router qaytarish"""
    return router
