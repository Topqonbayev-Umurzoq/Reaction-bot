# handlers/admin_handlers.py
# ============================================
# ADMIN HANDLERS
# ============================================

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command, StateFilter
from database.db_manager import DatabaseManager
from config.config import AdminStates, Config
from config.localization import get_text
import logging
import asyncio

logger = logging.getLogger(__name__)
router = Router()

# Database instance
db: DatabaseManager = None

def init_admin_handlers(database: DatabaseManager):
    """Admin handlers initialize qilish"""
    global db
    db = database

# ============================================
# PERMISSION CHECK
# ============================================

async def is_admin(user_id: int) -> bool:
    """Foydalanuvchi admin yoki yo'qligini tekshirish"""
    user = await db.get_user(user_id)
    return user.get('is_admin', False) if user else user_id in Config.ADMIN_IDS

# ============================================
# /ADMIN BUYRUGI
# ============================================

@router.message(Command("admin"))
async def admin_command(message: types.Message, state: FSMContext):
    """
    /admin buyrugi - Admin paneli
    Faqat adminlar uchun
    """
    try:
        user_id = message.from_user.id
        
        if not await is_admin(user_id):
            await message.answer(get_text('not_admin', 'uz'))
            return
        
        # Admin paneli
        admin_text = get_text('admin_panel', 'uz')
        
        buttons = [
            [KeyboardButton(text=get_text('btn_statistics', 'uz'))],
            [KeyboardButton(text=get_text('btn_force_subscribe', 'uz'))],
            [KeyboardButton(text=get_text('btn_broadcast', 'uz'))],
            [KeyboardButton(text=get_text('btn_manage_users', 'uz'))],
            [KeyboardButton(text=get_text('btn_back', 'uz'))]
        ]
        
        kb = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
        await message.answer(admin_text, reply_markup=kb)
        await state.set_state(AdminStates.admin_menu)
        
        await db.add_log(user_id, "admin_panel_access", "Admin paneli ochildi")
        
    except Exception as e:
        logger.error(f"Admin command error: {e}")

# ============================================
# STATISTIKA (ADMIN)
# ============================================

@router.message(F.text == "📊 Statistika", StateFilter(AdminStates.admin_menu))
async def admin_statistics(message: types.Message):
    """Admin statistika ko'rsatish"""
    try:
        user_id = message.from_user.id
        
        if not await is_admin(user_id):
            await message.answer(get_text('not_admin', 'uz'))
            return
        
        # Statistikani yangilash
        await db.update_statistics()
        stats = await db.get_statistics()
        
        stats_text = f"""
📊 STATISTIKA

👥 Jami foydalanuvchilar: {stats.get('total_users', 0)}
👥 Jami guruhlar: {stats.get('total_groups', 0)}
📢 Jami kanallar: {stats.get('total_channels', 0)}
📈 Bugun yangi: {stats.get('daily_new_users', 0)}

Chuqur analitika uchun:
- Broadcast: {await count_broadcasts()} ta
- Force Subscribe: {len(await db.get_force_subscribe_channels())} ta kanal
        """
        
        await message.answer(stats_text)
        
    except Exception as e:
        logger.error(f"Admin statistics error: {e}")

async def count_broadcasts() -> int:
    """Broadcast tarixini hisoblash (helper)"""
    # Bu funksiya data bazasida broadcast_history jadvalini hisoblab beradi
    # Hozircha 0 qaytaramiz
    return 0

# ============================================
# MAJBURIY OBUNA (FORCE SUBSCRIBE)
# ============================================

@router.message(F.text == "📌 Majburiy obuna", StateFilter(AdminStates.admin_menu))
async def force_subscribe_menu(message: types.Message, state: FSMContext):
    """Majburiy obuna menyusi"""
    try:
        user_id = message.from_user.id
        
        if not await is_admin(user_id):
            await message.answer(get_text('not_admin', 'uz'))
            return
        
        force_channels = await db.get_force_subscribe_channels()
        
        channels_list = ""
        if force_channels:
            for ch_id in force_channels:
                channel = await db.get_channel(ch_id)
                if channel:
                    channels_list += f"\n• {channel.get('channel_title', 'Unknown')}"
        else:
            channels_list = "\n❌ Hali kanal qo'shilmagan"
        
        text = f"""
📌 MAJBURIY OBUNA SOZLAMALARI

Hozirgi majburiy obuna kanallar:{channels_list}

Yangi kanal qo'shish uchun kanal ID-sini yuboring:
Masalan: -1001234567890
yoki @channel_username
        """
        
        buttons = [
            [KeyboardButton(text="➕ Kanal qo'shish")],
            [KeyboardButton(text="➖ Kanal o'chirish")],
            [KeyboardButton(text=get_text('btn_back', 'uz'))]
        ]
        
        kb = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
        await message.answer(text, reply_markup=kb)
        await state.set_state(AdminStates.manage_force_subscribe)
        
    except Exception as e:
        logger.error(f"Force subscribe menu error: {e}")

@router.message(F.text == "➕ Kanal qo'shish", StateFilter(AdminStates.manage_force_subscribe))
async def add_force_channel(message: types.Message, state: FSMContext):
    """Majburiy obuna kanaliga qo'shish"""
    try:
        await message.answer("Kanal ID-sini yoki @username ni kiriting:")
        await state.set_state(AdminStates.add_force_channel)
    except Exception as e:
        logger.error(f"Add force channel error: {e}")

@router.message(StateFilter(AdminStates.add_force_channel))
async def process_add_force_channel(message: types.Message, state: FSMContext):
    """Kanal qo'shish jarayoni"""
    try:
        user_id = message.from_user.id
        channel_input = message.text
        
        # Channel ID yoki username dan channel ID olish
        try:
            if channel_input.startswith('-'):
                channel_id = int(channel_input)
            elif channel_input.startswith('@'):
                # Bot API orqali channel ID olish
                channel_id = channel_input
            else:
                await message.answer("❌ Noto'g'ri format! -1001234567890 yoki @username kiriting")
                return
        except ValueError:
            await message.answer("❌ Noto'g'ri kanal ID!")
            return
        
        # Kanalni majburiy obunaga qo'shish
        await db.add_force_subscribe_channel(channel_id)
        await message.answer("✅ Kanal majburiy obunaga qo'shildi!")
        await db.add_log(user_id, "add_force_channel", f"Kanal qo'shildi: {channel_id}")
        
        # Menyuga qaytarish
        await state.set_state(AdminStates.manage_force_subscribe)
        await force_subscribe_menu(message, state)
        
    except Exception as e:
        logger.error(f"Process add force channel error: {e}")
        await message.answer(get_text('error', 'uz'))

# ============================================
# BROADCAST (XABAR TARQATISH)
# ============================================

@router.message(F.text == "📢 Xabar tarqatish", StateFilter(AdminStates.admin_menu))
async def broadcast_menu(message: types.Message, state: FSMContext):
    """Broadcast menyusi"""
    try:
        user_id = message.from_user.id
        
        if not await is_admin(user_id):
            await message.answer(get_text('not_admin', 'uz'))
            return
        
        text = """
📢 XABAR TARQATISH

Tarqatmoqchi bo'lgan xabarni kiriting:
        """
        
        await message.answer(text)
        await state.set_state(AdminStates.broadcast_message)
        
    except Exception as e:
        logger.error(f"Broadcast menu error: {e}")

@router.message(StateFilter(AdminStates.broadcast_message))
async def process_broadcast_message(message: types.Message, state: FSMContext):
    """Broadcast xabarini saqlash"""
    try:
        await state.update_data(broadcast_message=message.text)
        
        # Til filtri tanlash
        text = "Til filtrini tanlang:"
        
        buttons = [
            [InlineKeyboardButton(text="🌍 Barcha", callback_data="lang_all")],
            [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz_filter")],
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en_filter")],
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru_filter")]
        ]
        
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer(text, reply_markup=kb)
        await state.set_state(AdminStates.broadcast_language_filter)
        
    except Exception as e:
        logger.error(f"Process broadcast message error: {e}")

@router.callback_query(F.data.startswith("lang_"), StateFilter(AdminStates.broadcast_language_filter))
async def process_broadcast_language(query: types.CallbackQuery, state: FSMContext):
    """Broadcast til filtri tanlash"""
    try:
        user_id = query.from_user.id
        
        if not await is_admin(user_id):
            await query.answer(get_text('not_admin', 'uz'), show_alert=True)
            return
        
        language_filter = None
        if query.data == "lang_all":
            language_filter = None
        elif query.data == "lang_uz_filter":
            language_filter = "uz"
        elif query.data == "lang_en_filter":
            language_filter = "en"
        elif query.data == "lang_ru_filter":
            language_filter = "ru"
        
        # Ma'lumotlarni olish
        data = await state.get_data()
        broadcast_message = data.get('broadcast_message')
        
        # Foydalanuvchilarni olish
        if language_filter:
            users = await db.get_all_users(language=language_filter)
        else:
            users = await db.get_all_users()
        
        if not users:
            await query.message.edit_text("❌ Hech qanday foydalanuvchi topilmadi!")
            await state.clear()
            return
        
        # Broadcast yuborish
        await broadcast_to_users(
            query.message,
            users,
            broadcast_message,
            user_id,
            language_filter
        )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Process broadcast language error: {e}")

async def broadcast_to_users(
    message: types.Message,
    users: list,
    text: str,
    admin_id: int,
    language_filter: str = None
):
    """Foydalanuvchilarga xabar yuborish"""
    try:
        total = len(users)
        successful = 0
        failed = 0
        
        status_message = await message.answer(
            f"📤 Xabar tarqatilmoqda... (0/{total})"
        )
        
        for i, user in enumerate(users):
            try:
                await message.bot.send_message(
                    chat_id=user.get('user_id'),
                    text=text
                )
                successful += 1
            except Exception as e:
                logger.warning(f"Failed to send to user {user.get('user_id')}: {e}")
                failed += 1
            
            # Status yangilash (har 10 ta xabardan so'ng)
            if (i + 1) % 10 == 0:
                await status_message.edit_text(
                    f"📤 Xabar tarqatilmoqda... ({i+1}/{total})"
                )
            
            # Rate limiting
            await asyncio.sleep(0.1)
        
        # Yakuniy natija
        result_text = f"""
✅ Xabar muvaffaqiyatli tarqatildi!

📤 Yuborilgan: {successful}/{total}
❌ Xato: {failed}
        """
        
        await status_message.edit_text(result_text)
        
        # Log qilish
        await db.add_log(
            admin_id,
            "broadcast",
            f"Xabar tarqatildi: {successful} ta foydalanuvchiga, {failed} ta xato"
        )
        
    except Exception as e:
        logger.error(f"Broadcast error: {e}")
        await message.answer(get_text('error', 'uz'))

# ============================================
# ROUTER
# ============================================

def get_admin_router() -> Router:
    """Admin router qaytarish"""
    return router
