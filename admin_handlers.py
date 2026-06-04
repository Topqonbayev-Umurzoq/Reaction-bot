# handlers/admin_handlers.py
# ============================================
# ADMIN HANDLERS
# ============================================

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command, StateFilter
from db_manager import DatabaseManager
from config import AdminStates, Config
from localization import get_text
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
            await message.answer("❌ Siz admin emassiz!")
            return
        
        # Admin paneli - InlineKeyboard
        admin_text = """
⚙️ ADMIN PANELI

Admin funksiyalarini tanlang:
        """
        
        buttons = [
            [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_statistics")],
            [InlineKeyboardButton(text="📌 Majburiy obuna", callback_data="admin_force_subscribe")],
            [InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast")],
            [InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_manage_users")]
        ]
        
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer(admin_text, reply_markup=kb)
        await state.set_state(AdminStates.admin_menu)
        
        await db.add_log(user_id, "admin_panel_access", "Admin paneli ochildi")
        
    except Exception as e:
        logger.error(f"Admin command error: {e}")

# ============================================
# STATISTIKA (ADMIN)
# ============================================

@router.callback_query(F.data == "admin_statistics")
async def admin_statistics_callback(query: types.CallbackQuery):
    """Admin statistika ko'rsatish"""
    try:
        user_id = query.from_user.id
        
        if not await is_admin(user_id):
            await query.answer("❌ Siz admin emassiz!", show_alert=True)
            return
        
        # Statistikani yangilash
        await db.update_statistics()
        stats = await db.get_statistics()
        
        stats_text = f"""
📊 ADMIN STATISTIKA

👥 Jami foydalanuvchilar: {stats.get('total_users', 0)}
👥 Jami guruhlar: {stats.get('total_groups', 0)}
📢 Jami kanallar: {stats.get('total_channels', 0)}
📈 Bugun yangi: {stats.get('daily_new_users', 0)}

📊 Broadcast yuborilgan: {await count_broadcasts()} ta
📌 Force Subscribe kanallar: {len(await db.get_force_subscribe_channels())} ta
        """
        
        buttons = [
            [InlineKeyboardButton(text="🔄 Yangilash", callback_data="admin_statistics")],
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_back_to_menu")]
        ]
        
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await query.message.edit_text(stats_text, reply_markup=kb)
        
    except Exception as e:
        logger.error(f"Admin statistics error: {e}")
        await query.answer("❌ Xato yuz berdi", show_alert=True)
        
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

@router.callback_query(F.data == "admin_force_subscribe")
async def force_subscribe_menu_callback(query: types.CallbackQuery, state: FSMContext):
    """Majburiy obuna menyusi"""
    try:
        user_id = query.from_user.id
        
        if not await is_admin(user_id):
            await query.answer("❌ Siz admin emassiz!", show_alert=True)
            return
        
        force_channels = await db.get_force_subscribe_channels()
        
        channels_list = ""
        if force_channels:
            for idx, ch_id in enumerate(force_channels, 1):
                channels_list += f"\n{idx}. {ch_id}"
        else:
            channels_list = "\n❌ Hali kanal qo'shilmagan"
        
        text = f"""
📌 MAJBURIY OBUNA SOZLAMALARI

Hozirgi kanallar:{channels_list}

Yangi kanal qo'shish yoki mavjudlarni boshqarish:
        """
        
        buttons = [
            [InlineKeyboardButton(text="➕ Kanal qo'shish", callback_data="admin_add_force_channel")],
            [InlineKeyboardButton(text="➖ Kanal o'chirish", callback_data="admin_remove_force_channel")],
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_back_to_menu")]
        ]
        
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await query.message.edit_text(text, reply_markup=kb)
        await state.set_state(AdminStates.manage_force_subscribe)
        
    except Exception as e:
        logger.error(f"Force subscribe menu error: {e}")
        await query.answer("❌ Xato yuz berdi", show_alert=True)

@router.callback_query(F.data == "admin_add_force_channel")
async def admin_add_force_channel_callback(query: types.CallbackQuery, state: FSMContext):
    """Majburiy obuna kanaliga qo'shish"""
    try:
        await query.message.edit_text("Kanal ID-sini yoki @username ni kiriting:\n\nMasalan: -1001234567890 yoki @mychannel")
        await state.set_state(AdminStates.add_force_channel)
    except Exception as e:
        logger.error(f"Add force channel error: {e}")
        await query.answer("❌ Xato yuz berdi", show_alert=True)

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
        await db.add_log(user_id, "add_force_channel", f"Kanal qo'shildi: {channel_input}")
        
        # Menyuga qaytarish
        await state.clear()
        
    except Exception as e:
        logger.error(f"Process add force channel error: {e}")
        await message.answer("❌ Xato yuz berdi")

@router.callback_query(F.data == "admin_remove_force_channel")
async def admin_remove_force_channel_callback(query: types.CallbackQuery, state: FSMContext):
    """Majburiy obuna kanalidan o'chirish"""
    try:
        force_channels = await db.get_force_subscribe_channels()
        
        if not force_channels:
            await query.message.edit_text("❌ O'chirish uchun kanal yo'q!")
            return
        
        text = "O'chirish uchun kanal tanlang:"
        buttons = []
        
        for ch_id in force_channels:
            buttons.append([
                InlineKeyboardButton(text=f"❌ {ch_id}", callback_data=f"confirm_remove_force_{ch_id}")
            ])
        
        buttons.append([
            InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_back_to_menu")
        ])
        
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await query.message.edit_text(text, reply_markup=kb)
        
    except Exception as e:
        logger.error(f"Remove force channel error: {e}")
        await query.answer("❌ Xato yuz berdi", show_alert=True)

@router.callback_query(F.data.startswith("confirm_remove_force_"))
async def confirm_remove_force_channel(query: types.CallbackQuery):
    """Majburiy obuna kanalini o'chirish tasdig'i"""
    try:
        user_id = query.from_user.id
        channel_id = query.data.replace("confirm_remove_force_", "")
        
        await db.remove_force_subscribe_channel(channel_id)
        await query.message.edit_text("✅ Kanal o'chirildi!")
        await db.add_log(user_id, "remove_force_channel", f"Kanal o'chirildi: {channel_id}")
        
    except Exception as e:
        logger.error(f"Confirm remove force channel error: {e}")
        await query.answer("❌ Xato yuz berdi", show_alert=True)

# ============================================
# BROADCAST (XABAR TARQATISH)
# ============================================

@router.callback_query(F.data == "admin_broadcast")
async def broadcast_menu_callback(query: types.CallbackQuery, state: FSMContext):
    """Broadcast menyusi"""
    try:
        user_id = query.from_user.id
        
        if not await is_admin(user_id):
            await query.answer("❌ Siz admin emassiz!", show_alert=True)
            return
        
        text = """
📢 XABAR TARQATISH

Tarqatmoqchi bo'lgan xabarni kiriting:
        """
        
        await query.message.edit_text(text)
        await state.set_state(AdminStates.broadcast_message)
        
    except Exception as e:
        logger.error(f"Broadcast menu error: {e}")
        await query.answer("❌ Xato yuz berdi", show_alert=True)

@router.callback_query(F.data == "admin_manage_users")
async def manage_users_callback(query: types.CallbackQuery, state: FSMContext):
    """Foydalanuvchilarni boshqarish"""
    try:
        user_id = query.from_user.id
        
        if not await is_admin(user_id):
            await query.answer("❌ Siz admin emassiz!", show_alert=True)
            return
        
        total_users = await db.count_users()
        
        text = f"""
👥 FOYDALANUVCHILAR BOSHQARISH

Jami foydalanuvchilar: {total_users}

Boshqarish funksiyalari:
        """
        
        buttons = [
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_back_to_menu")]
        ]
        
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await query.message.edit_text(text, reply_markup=kb)
        
    except Exception as e:
        logger.error(f"Manage users error: {e}")
        await query.answer("❌ Xato yuz berdi", show_alert=True)

@router.callback_query(F.data == "admin_back_to_menu")
async def admin_back_to_menu_callback(query: types.CallbackQuery, state: FSMContext):
    """Admin menyusiga qaytarish"""
    try:
        user_id = query.from_user.id
        
        if not await is_admin(user_id):
            await query.answer("❌ Siz admin emassiz!", show_alert=True)
            return
        
        admin_text = """
⚙️ ADMIN PANELI

Admin funksiyalarini tanlang:
        """
        
        buttons = [
            [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_statistics")],
            [InlineKeyboardButton(text="📌 Majburiy obuna", callback_data="admin_force_subscribe")],
            [InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast")],
            [InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_manage_users")]
        ]
        
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        await query.message.edit_text(admin_text, reply_markup=kb)
        await state.set_state(AdminStates.admin_menu)
        
    except Exception as e:
        logger.error(f"Admin back to menu error: {e}")
        await query.answer("❌ Xato yuz berdi", show_alert=True)
        
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
