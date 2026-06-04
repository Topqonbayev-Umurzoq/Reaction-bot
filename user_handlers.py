# handlers/user_handlers.py
# ============================================
# FOYDALANUVCHI HANDLERS
# ============================================

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
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

def get_main_menu_keyboard(language: str) -> InlineKeyboardMarkup:
    """Asosiy menyu klaviaturas"""
    buttons = [
        [InlineKeyboardButton(text="🔗 " + get_text('btn_channels', language), callback_data="menu_channels")],
        [InlineKeyboardButton(text="👥 " + get_text('btn_groups', language), callback_data="menu_groups")],
        [InlineKeyboardButton(text="📹 " + get_text('btn_guide', language), callback_data="menu_guide")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

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

@router.callback_query(F.data == "lang_uz")
async def select_language_uz(query: types.CallbackQuery, state: FSMContext):
    """Uzbek tili tanlash"""
    await process_language_selection(query, state, "uz")

@router.callback_query(F.data == "lang_en")
async def select_language_en(query: types.CallbackQuery, state: FSMContext):
    """English tili tanlash"""
    await process_language_selection(query, state, "en")

@router.callback_query(F.data == "lang_ru")
async def select_language_ru(query: types.CallbackQuery, state: FSMContext):
    """Russian tili tanlash"""
    await process_language_selection(query, state, "ru")

async def process_language_selection(query: types.CallbackQuery, state: FSMContext, language: str):
    """Til tanlash jarayoni"""
    try:
        user_id = query.from_user.id
        
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
        await query.answer("❌ Xato yuz berdi", show_alert=True)

# ============================================
# MAIN MENU CALLBACKS
# ============================================

@router.callback_query(F.data == "menu_channels")
async def menu_channels_callback(query: types.CallbackQuery, state: FSMContext):
    """Kanallar menyu callback"""
    try:
        user_id = query.from_user.id
        user = await db.get_user(user_id)
        
        if not user:
            await query.answer("❌ Foydalanuvchi topilmadi", show_alert=True)
            return
        
        language = user.get('language_code', 'uz')
        await handle_channels_menu(query, language, state)
        
    except Exception as e:
        logger.error(f"Menu channels callback error: {e}")
        await query.answer("❌ Xato yuz berdi", show_alert=True)

@router.callback_query(F.data == "menu_groups")
async def menu_groups_callback(query: types.CallbackQuery, state: FSMContext):
    """Guruhlar menyu callback"""
    try:
        user_id = query.from_user.id
        user = await db.get_user(user_id)
        
        if not user:
            await query.answer("❌ Foydalanuvchi topilmadi", show_alert=True)
            return
        
        language = user.get('language_code', 'uz')
        await handle_groups_menu(query, language, state)
        
    except Exception as e:
        logger.error(f"Menu groups callback error: {e}")
        await query.answer("❌ Xato yuz berdi", show_alert=True)

@router.callback_query(F.data == "menu_guide")
async def menu_guide_callback(query: types.CallbackQuery):
    """Qo'llanma callback"""
    try:
        user_id = query.from_user.id
        user = await db.get_user(user_id)
        
        if not user:
            await query.answer("❌ Foydalanuvchi topilmadi", show_alert=True)
            return
        
        language = user.get('language_code', 'uz')
        await handle_guide(query, language)
        
    except Exception as e:
        logger.error(f"Menu guide callback error: {e}")
        await query.answer("❌ Xato yuz berdi", show_alert=True)

@router.message(F.text)
async def handle_text_messages(message: types.Message, state: FSMContext):
    """Boshqa barcha text xabarlarni qayta ishlash (fallback)"""
    try:
        user_id = message.from_user.id
        user = await db.get_user(user_id)
        
        if not user:
            await message.answer("❌ Foydalanuvchi topilmadi. /start buyrug'idan boshlang.")
            return
        
        language = user.get('language_code', 'uz')
        
        # Noto'g'ri xabar - bosh menyuni ko'rsatish
        main_menu_text = get_text('main_menu', language)
        await message.answer(
            main_menu_text,
            reply_markup=get_main_menu_keyboard(language)
        )
        
    except Exception as e:
        logger.error(f"Text handler error: {e}")

# ============================================
# KANALLAR MENYUSI
# ============================================

async def handle_channels_menu(query: types.CallbackQuery, language: str, state: FSMContext):
    """Kanallar menyusi - Faqat tanlash"""
    try:
        # Admin qo'shgan barcha kanallarni olish
        all_channels = await db.get_all_channels()
        
        if all_channels:
            text = "🔗 KANALLAR\n\nBir kanalni tanlang:"
            
            buttons = []
            for channel in all_channels:
                channel_id = channel.get('channel_id')
                channel_title = channel.get('channel_title', 'Nomalum kanal')
                buttons.append([
                    InlineKeyboardButton(
                        text=f"✓ {channel_title}",
                        callback_data=f"view_channel_{channel_id}"
                    )
                ])
            
            # Orqaga tugmasi
            buttons.append([
                InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_main_menu")
            ])
            
            kb = InlineKeyboardMarkup(inline_keyboard=buttons)
            await query.message.edit_text(text, reply_markup=kb)
        else:
            # Hech qanday kanal yo'q
            text = "❌ Hali kanallar qo'shilmagan"
            
            buttons = [
                [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_main_menu")]
            ]
            
            kb = InlineKeyboardMarkup(inline_keyboard=buttons)
            await query.message.edit_text(text, reply_markup=kb)
        
        await state.set_state(UserStates.selecting_channel)
        
    except Exception as e:
        logger.error(f"Channels menu error: {e}")
        await query.answer("❌ Xato yuz berdi", show_alert=True)

@router.callback_query(F.data.startswith("view_channel_"))
async def view_channel_callback(query: types.CallbackQuery, state: FSMContext):
    """Kanal ma'lumotlarini ko'rsatish"""
    try:
        channel_id = query.data.replace("view_channel_", "")
        user_id = query.from_user.id
        user = await db.get_user(user_id)
        language = user.get('language_code', 'uz') if user else 'uz'
        
        channel = await db.get_channel(int(channel_id))
        if not channel:
            await query.answer("❌ Kanal topilmadi", show_alert=True)
            return
        
        channel_title = channel.get('channel_title', 'Nomalum')
        channel_username = channel.get('channel_username', '—')
        
        text = f"""
🔗 KANAL MA'LUMOTLARI

📌 Nomi: {channel_title}
👤 Username: {channel_username}

Qanaqa qilmasiz?
        """
        
        buttons = [
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_channels")]
        ]
        
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await query.message.edit_text(text, reply_markup=kb)
        
    except Exception as e:
        logger.error(f"View channel error: {e}")
        await query.answer("❌ Xato yuz berdi", show_alert=True)

@router.callback_query(F.data == "back_to_channels")
async def back_to_channels_callback(query: types.CallbackQuery, state: FSMContext):
    """Kanallar ro'yxatiga qaytarish"""
    try:
        user = await db.get_user(query.from_user.id)
        language = user.get('language_code', 'uz') if user else 'uz'
        
        # Kanallar menyusiga qaytarish
        all_channels = await db.get_all_channels()
        
        if all_channels:
            text = "🔗 KANALLAR\n\nBir kanalni tanlang:"
            
            buttons = []
            for channel in all_channels:
                channel_id = channel.get('channel_id')
                channel_title = channel.get('channel_title', 'Nomalum kanal')
                buttons.append([
                    InlineKeyboardButton(
                        text=f"✓ {channel_title}",
                        callback_data=f"view_channel_{channel_id}"
                    )
                ])
            
            buttons.append([
                InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_main_menu")
            ])
            
            kb = InlineKeyboardMarkup(inline_keyboard=buttons)
            await query.message.edit_text(text, reply_markup=kb)
        
    except Exception as e:
        logger.error(f"Back to channels error: {e}")

# ============================================
# GURUH REAKSIYALARI MENYUSI
# ============================================

async def handle_groups_menu(query: types.CallbackQuery, language: str, state: FSMContext):
    """Guruh reaksiyalari menyusi - Faqat tanlash"""
    try:
        # Barcha guruhlarni olish
        all_groups = await db.get_all_groups()
        
        if all_groups:
            text = "👥 GURUHLAR\n\nBir guruhni tanlang:"
            
            buttons = []
            for group in all_groups:
                group_id = group.get('group_id')
                group_title = group.get('group_title', 'Nomalum guruh')
                buttons.append([
                    InlineKeyboardButton(
                        text=f"📌 {group_title}",
                        callback_data=f"manage_group_{group_id}"
                    )
                ])
            
            buttons.append([
                InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_main_menu")
            ])
            
            kb = InlineKeyboardMarkup(inline_keyboard=buttons)
            await query.message.edit_text(text, reply_markup=kb)
        else:
            text = "❌ Hali guruhlar qo'shilmagan\n\nBotni guruhga qo'shing va reaksiyalarni yoqing"
            
            buttons = [
                [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_main_menu")]
            ]
            
            kb = InlineKeyboardMarkup(inline_keyboard=buttons)
            await query.message.edit_text(text, reply_markup=kb)
        
        await state.set_state(UserStates.manage_reactions)
        
    except Exception as e:
        logger.error(f"Groups menu error: {e}")
        await query.answer("❌ Xato yuz berdi", show_alert=True)

@router.callback_query(F.data.startswith("manage_group_"))
async def manage_group_callback(query: types.CallbackQuery, state: FSMContext):
    """Guruhni boshqarish"""
    try:
        group_id = query.data.replace("manage_group_", "")
        user = await db.get_user(query.from_user.id)
        language = user.get('language_code', 'uz') if user else 'uz'
        
        group = await db.get_group(int(group_id))
        if not group:
            await query.answer("❌ Guruh topilmadi", show_alert=True)
            return
        
        group_title = group.get('group_title', 'Nomalum')
        
        text = f"""
👥 GURUH: {group_title}

Reaksiyalarni boshqarish:
        """
        
        buttons = [
            [InlineKeyboardButton(text="✅ Yoqish", callback_data=f"reactions_on_{group_id}")],
            [InlineKeyboardButton(text="❌ O'chirish", callback_data=f"reactions_off_{group_id}")],
            [InlineKeyboardButton(text="🎨 Emoji-larni tanlash", callback_data=f"select_emoji_{group_id}")],
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_groups")]
        ]
        
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await query.message.edit_text(text, reply_markup=kb)
        
    except Exception as e:
        logger.error(f"Manage group error: {e}")
        await query.answer("❌ Xato yuz berdi", show_alert=True)

@router.callback_query(F.data == "back_to_groups")
async def back_to_groups_callback(query: types.CallbackQuery, state: FSMContext):
    """Guruhlar ro'yxatiga qaytarish"""
    try:
        user = await db.get_user(query.from_user.id)
        language = user.get('language_code', 'uz') if user else 'uz'
        
        # Guruhlar menyusiga qaytarish
        all_groups = await db.get_all_groups()
        
        if all_groups:
            text = "👥 GURUHLAR\n\nBir guruhni tanlang:"
            
            buttons = []
            for group in all_groups:
                group_id = group.get('group_id')
                group_title = group.get('group_title', 'Nomalum guruh')
                buttons.append([
                    InlineKeyboardButton(
                        text=f"📌 {group_title}",
                        callback_data=f"manage_group_{group_id}"
                    )
                ])
            
            buttons.append([
                InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_main_menu")
            ])
            
            kb = InlineKeyboardMarkup(inline_keyboard=buttons)
            await query.message.edit_text(text, reply_markup=kb)
        
    except Exception as e:
        logger.error(f"Back to groups error: {e}")

# ============================================
# QOLLANMA
# ============================================

async def handle_guide(query: types.CallbackQuery, language: str):
    """Qo'llanma ko'rsatish"""
    try:
        guides = {
            'uz': """
📖 QOLLANMA

🤖 BOT HAQIDA:
Reaksiyalar Bot - Telegram guruhlaringizda emoji reaksiyalarini yoqish uchun bot.

📌 KANALLAR:
Barcha mavjud kanallarni ko'rish va boshqarish

👥 GURUHLAR:
Guruhlaringizda reaksiyalarni sozlash

🎨 EMOJI-LAR:
70+ emoji reaksiyalari mavjud

✨ PREMIUM:
Qo'shimcha emoji va funksiyalar uchun
            """,
            'en': """
📖 GUIDE

🤖 ABOUT BOT:
Reactions Bot - Add emoji reactions to your Telegram groups.

📌 CHANNELS:
View and manage all available channels

👥 GROUPS:
Configure reactions in your groups

🎨 EMOJIS:
70+ emoji reactions available

✨ PREMIUM:
Extra emojis and features
            """,
            'ru': """
📖 РУКОВОДСТВО

🤖 О БОТЕ:
Reactions Bot - Добавьте эмоджи реакции в ваши Telegram группы.

📌 КАНАЛЫ:
Просмотр и управление всеми доступными каналами

👥 ГРУППЫ:
Настройка реакций в ваших группах

🎨 ЭМОДЖИ:
70+ эмоджи реакций доступно

✨ ПРЕМИУМ:
Дополнительные эмоджи и функции
            """
        }
        
        guide_text = guides.get(language, guides['uz'])
        
        buttons = [
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_main_menu")]
        ]
        
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await query.message.edit_text(guide_text, reply_markup=kb)
        
    except Exception as e:
        logger.error(f"Guide error: {e}")
        await query.answer("❌ Xato yuz berdi", show_alert=True)

# ============================================
# STATISTIKA (OLIB TASHLANDI - FOYDALANUVCHILARGA KERAK EMASá)
# ============================================

async def handle_statistics(query: types.CallbackQuery, language: str):
    """DEPRECATED - Statistika (foydalanuvchilarga kerak emas)"""
    pass

# ============================================
# BACK TO MAIN MENU
# ============================================

@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu_callback(query: types.CallbackQuery, state: FSMContext):
    """Bosh menyuga qaytarish"""
    try:
        user_id = query.from_user.id
        user = await db.get_user(user_id)
        
        if not user:
            await query.answer("❌ Foydalanuvchi topilmadi", show_alert=True)
            return
        
        language = user.get('language_code', 'uz')
        main_menu_text = get_text('main_menu', language)
        
        await state.clear()
        await query.message.edit_text(
            main_menu_text,
            reply_markup=get_main_menu_keyboard(language)
        )
        
    except Exception as e:
        logger.error(f"Back to main menu error: {e}")
        await query.answer("❌ Xato yuz berdi", show_alert=True)

# ============================================
# ASOSIY ROUTER
# ============================================

def get_router() -> Router:
    """Router qaytarish"""
    return router
