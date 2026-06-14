from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from config import ADMIN_ID, SUBSCRIBE_CHANNEL
from database import (
    get_all_users, block_user, unblock_user, is_blocked,
    add_admin, get_admins, is_admin_user, remove_admin, remove_all_admins,
    get_all_blocked_users, unblock_all_users,
    get_setting, set_setting, delete_setting,
    add_bot, get_bot_count, get_all_bots, update_bot_status, remove_bot
)
from keyboards.inline import admin_kb, back_kb

router = Router()

class AdminState(StatesGroup):
    waiting_broadcast = State()
    waiting_block_id = State()
    waiting_unblock_id = State()
    waiting_add_admin = State()
    waiting_remove_admin = State()
    waiting_unblock_blocked = State()
    waiting_sub_channel = State()
    waiting_new_bot_token = State()



def is_root_admin(user_id):
    return user_id == ADMIN_ID


def is_admin(user_id):
    return user_id == ADMIN_ID or is_admin_user(user_id)


# /admin buyrug'i
@router.message(Command("admin"))
async def cmd_admin(msg: Message):
    if not is_admin(msg.from_user.id):
        return
    if is_blocked(msg.from_user.id):
        await msg.answer("❌ Siz bloklandingiz.")
        return
    is_root = is_root_admin(msg.from_user.id)
    extra = f"\n\n<b>Hozirgi ID:</b> <code>{msg.from_user.id}</code>"
    if is_root:
        extra += "\n<b>Siz bosh admin hisoblanasiz.</b>"
    else:
        extra += "\nSiz admin sifatida ishlayapsiz."

    from database import get_conn, get_setting
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM groups")
    groups = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM channels")
    channels = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM bots")
    bots = c.fetchone()[0]
    conn.close()

    required_channel = get_setting("subscribe_channel") or SUBSCRIBE_CHANNEL
    if not required_channel:
        required_channel = "yo'q"

    await msg.answer(
        "👨‍💼 <b>Admin Panel</b>" + extra +
        f"\n\n👥 Guruhlar: <b>{groups}</b>\n📢 Kanallar: <b>{channels}</b>\n🤖 Botlar: <b>{bots}</b>\n\nMajburiy obuna: <b>{required_channel}</b>\n\nBu botlar asosiy bot orqali boshqariladi.",
        reply_markup=admin_kb(is_root=is_root),
        parse_mode="HTML"
    )


# Foydalanuvchilar ro'yxati
@router.callback_query(F.data == "admin_users")
async def admin_users(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    if is_blocked(call.from_user.id):
        await call.answer("❌ Siz bloklandingiz.")
        return
    users = get_all_users()
    if not users:
        await call.message.edit_text("Hali foydalanuvchi yo'q.", reply_markup=back_kb("admin_back"))
        return

    text = f"👥 <b>Foydalanuvchilar ({len(users)} ta):</b>\n\n"
    for u in users[:30]:  # max 30 ta
        uid, uname, name, lang, blocked, joined = u
        status = "🚫" if blocked else "✅"
        uname_str = f"@{uname}" if uname else "—"
        text += f"{status} <b>{name}</b> ({uname_str})\nID: <code>{uid}</code> | Til: {lang}\n\n"

    await call.message.edit_text(text, reply_markup=back_kb("admin_back"), parse_mode="HTML")


# Statistika
@router.callback_query(F.data == "admin_stats")
async def admin_stats(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    if is_blocked(call.from_user.id):
        await call.answer("❌ Siz bloklandingiz.")
        return
    from database import get_conn
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE is_blocked = 1")
    blocked = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM groups")
    groups = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM channels")
    channels = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM bots")
    bots = c.fetchone()[0]
    conn.close()

    text = (
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{total}</b>\n"
        f"🚫 Bloklangan: <b>{blocked}</b>\n"
        f"👥 Guruhlar: <b>{groups}</b>\n"
        f"📢 Kanallar: <b>{channels}</b>\n"
        f"🤖 Botlar: <b>{bots}</b>"
    )
    await call.message.edit_text(text, reply_markup=back_kb("admin_back"), parse_mode="HTML")


# Xabar yuborish (broadcast)
@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    if is_blocked(call.from_user.id):
        await call.answer("❌ Siz bloklandingiz.")
        return
    await state.set_state(AdminState.waiting_broadcast)
    await call.message.edit_text(
        "📨 Barcha foydalanuvchilarga yuboriladigan xabarni kiriting:\n\n(Bekor qilish uchun /cancel)",
        reply_markup=back_kb("admin_back")
    )


@router.message(AdminState.waiting_broadcast)
async def admin_broadcast_send(msg: Message, state: FSMContext, bot: Bot):
    if not is_admin(msg.from_user.id):
        return
    if is_blocked(msg.from_user.id):
        await msg.answer("❌ Siz bloklandingiz.")
        await state.clear()
        return
    await state.clear()
    users = get_all_users()
    success, fail = 0, 0
    for u in users:
        uid = u[0]
        if u[4]:  # bloklangan
            continue
        try:
            await bot.copy_message(uid, msg.chat.id, msg.message_id)
            success += 1
        except Exception:
            fail += 1
    await msg.answer(f"✅ Yuborildi: {success} ta\n❌ Xato: {fail} ta")


# Bloklash
@router.callback_query(F.data == "admin_block")
async def admin_block_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    if is_blocked(call.from_user.id):
        await call.answer("❌ Siz bloklandingiz.")
        return
    await state.set_state(AdminState.waiting_block_id)
    await call.message.edit_text(
        "🚫 Bloklash uchun foydalanuvchi ID sini kiriting:",
        reply_markup=back_kb("admin_back")
    )


@router.message(AdminState.waiting_block_id)
async def admin_block_do(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id):
        return
    if is_blocked(msg.from_user.id):
        await msg.answer("❌ Siz bloklandingiz.")
        await state.clear()
        return
    await state.clear()
    try:
        uid = int(msg.text.strip())
        block_user(uid)
        await msg.answer(f"✅ {uid} bloklandi.")
    except ValueError:
        await msg.answer("❌ Noto'g'ri ID!")


# Blokdan chiqarish
@router.callback_query(F.data == "admin_unblock")
async def admin_unblock_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    if is_blocked(call.from_user.id):
        await call.answer("❌ Siz bloklandingiz.")
        return
    await state.set_state(AdminState.waiting_unblock_id)
    await call.message.edit_text(
        "✅ Blokdan chiqarish uchun foydalanuvchi ID sini kiriting:",
        reply_markup=back_kb("admin_back")
    )


@router.message(AdminState.waiting_unblock_id)
async def admin_unblock_do(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id):
        return
    if is_blocked(msg.from_user.id):
        await msg.answer("❌ Siz bloklandingiz.")
        await state.clear()
        return
    await state.clear()
    try:
        uid = int(msg.text.strip())
        unblock_user(uid)
        await msg.answer(f"✅ {uid} blokdan chiqarildi.")
    except ValueError:
        await msg.answer("❌ Noto'g'ri ID!")


# Admin qo'shish
@router.callback_query(F.data == "admin_add")
async def admin_add_start(call: CallbackQuery, state: FSMContext):
    if not is_root_admin(call.from_user.id):
        return
    if is_blocked(call.from_user.id):
        await call.answer("❌ Siz bloklandingiz.")
        return
    await state.set_state(AdminState.waiting_add_admin)
    await call.message.edit_text(
        "➕ Admin qo'shish uchun foydalanuvchi ID sini kiriting:\n\n(Bekor qilish uchun /cancel)",
        reply_markup=back_kb("admin_back")
    )


@router.message(AdminState.waiting_add_admin)
async def admin_add_do(msg: Message, state: FSMContext):
    if not is_root_admin(msg.from_user.id):
        return
    if is_blocked(msg.from_user.id):
        await msg.answer("❌ Siz bloklandingiz.")
        await state.clear()
        return
    await state.clear()
    try:
        uid = int(msg.text.strip())
        if uid == ADMIN_ID:
            await msg.answer("✅ Bu ID bosh adminga tegishli.")
            return
        if is_admin_user(uid):
            await msg.answer("❌ Bu foydalanuvchi allaqachon admin.")
            return
        add_admin(uid, msg.from_user.id)
        await msg.answer(f"✅ {uid} yangi admin sifatida qo'shildi.")
    except ValueError:
        await msg.answer("❌ Noto'g'ri ID!")


# Adminlar ro'yxati
@router.callback_query(F.data == "admin_admins")
async def admin_admins(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    if is_blocked(call.from_user.id):
        await call.answer("❌ Siz bloklandingiz.")
        return
    admins = get_admins()
    text = "👑 <b>Adminlar ro'yxati</b>\n\n"
    text += f"🧑‍💼 Asosiy admin: <code>{ADMIN_ID}</code>\n\n"
    
    kb = back_kb("admin_back")
    
    if not admins:
        text += "Hozircha boshqa adminlar yo'q."
    else:
        text += "Boshqa adminlar:\n\n"
        for user_id, added_by, added_at in admins:
            text += f"ID: <code>{user_id}</code> | qo'shgan: <code>{added_by}</code> | {added_at}\n"
        
        # Agar bosh admin bo'lsa, adminlarni olib tashlash tugmasini ko'rsatamiz
        if is_root_admin(call.from_user.id) and len(admins) > 0:
            kb = InlineKeyboardBuilder()
            kb.row(InlineKeyboardButton(text="🗑️ Admin olib tashlash", callback_data="admin_remove_select"))
            kb.row(InlineKeyboardButton(text="🗑️🗑️ Barcha adminlarni olib tashlash", callback_data="admin_remove_all"))
            kb.row(InlineKeyboardButton(text="↩️ Orqaga", callback_data="admin_back"))
            kb = kb.as_markup()

    await call.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


# Admin olib tashlashni tanlash
@router.callback_query(F.data == "admin_remove_select")
async def admin_remove_select(call: CallbackQuery, state: FSMContext):
    if not is_root_admin(call.from_user.id):
        return
    if is_blocked(call.from_user.id):
        await call.answer("❌ Siz bloklandingiz.")
        return
    await state.set_state(AdminState.waiting_remove_admin)
    await call.message.edit_text(
        "🗑️ <b>Adminlikdan olib tashlash</b>\n\nAdmin ID sini kiriting:\n\n(Bekor qilish uchun /cancel)",
        reply_markup=back_kb("admin_admins"),
        parse_mode="HTML"
    )


@router.message(AdminState.waiting_remove_admin)
async def admin_remove_do(msg: Message, state: FSMContext):
    if not is_root_admin(msg.from_user.id):
        return
    if is_blocked(msg.from_user.id):
        await msg.answer("❌ Siz bloklandingiz.")
        await state.clear()
        return
    await state.clear()
    try:
        uid = int(msg.text.strip())
        if is_admin_user(uid):
            remove_admin(uid)
            await msg.answer(f"✅ {uid} adminlikdan olib tashlandi.")
        else:
            await msg.answer("❌ Bu foydalanuvchi admin emas.")
    except ValueError:
        await msg.answer("❌ Noto'g'ri ID!")


# Barcha adminlarni olib tashlashni tasdiqlash
@router.callback_query(F.data == "admin_remove_all")
async def admin_remove_all(call: CallbackQuery):
    if not is_root_admin(call.from_user.id):
        return
    if is_blocked(call.from_user.id):
        await call.answer("❌ Siz bloklandingiz.")
        return
    admins = get_admins()
    if not admins:
        await call.answer("❌ Olib tashlanadigan admin yo'q.")
        return
    
    text = f"⚠️ <b>Tasdiqla</b>\n\n{len(admins)} ta adminni barcha adminlikdan olib tashlash?"
    
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="✅ Tasdiqla", callback_data="admin_remove_all_confirm"),
        InlineKeyboardButton(text="❌ Bekor", callback_data="admin_admins")
    )
    
    await call.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")


@router.callback_query(F.data == "admin_remove_all_confirm")
async def admin_remove_all_confirm(call: CallbackQuery):
    if not is_root_admin(call.from_user.id):
        return
    if is_blocked(call.from_user.id):
        await call.answer("❌ Siz bloklandingiz.")
        return
    remove_all_admins()
    await call.message.edit_text(
        "✅ Barcha adminlar adminlikdan olib tashlandi.", 
        reply_markup=back_kb("admin_back"), 
        parse_mode="HTML"
    )


# Bloklangan foydalanuvchilar ro'yxati
@router.callback_query(F.data == "admin_view_blocked")
async def admin_view_blocked(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    if is_blocked(call.from_user.id):
        await call.answer("❌ Siz bloklandingiz.")
        return
    
    blocked_users = get_all_blocked_users()
    text = "📋 <b>Bloklangan foydalanuvchilar</b>\n\n"
    
    kb = back_kb("admin_back")
    
    if not blocked_users:
        text += "Hozircha bloklangan foydalanuvchi yo'q."
    else:
        text += f"Jami: {len(blocked_users)} ta\n\n"
        for user_id, username, full_name in blocked_users:
            uname_str = f"@{username}" if username else "—"
            text += f"• <code>{user_id}</code> | {full_name} ({uname_str})\n"
        
        kb = InlineKeyboardBuilder()
        kb.row(InlineKeyboardButton(text="🗑️ Foydalanuvchi olib tashlash", callback_data="admin_unblock_select"))
        kb.row(InlineKeyboardButton(text="🗑️🗑️ Barcha bloklanganlarni olib tashlash", callback_data="admin_unblock_all"))
        kb.row(InlineKeyboardButton(text="↩️ Orqaga", callback_data="admin_back"))
        kb = kb.as_markup()

    await call.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


# Bloklangan foydalanuvchi olib tashlashni tanlash
@router.callback_query(F.data == "admin_unblock_select")
async def admin_unblock_select(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    if is_blocked(call.from_user.id):
        await call.answer("❌ Siz bloklandingiz.")
        return
    await state.set_state(AdminState.waiting_unblock_blocked)
    await call.message.edit_text(
        "🗑️ <b>Blokdan chiqarish</b>\n\nFoydalanuvchi ID sini kiriting:\n\n(Bekor qilish uchun /cancel)",
        reply_markup=back_kb("admin_view_blocked"),
        parse_mode="HTML"
    )


@router.message(AdminState.waiting_unblock_blocked)
async def admin_unblock_blocked_do(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id):
        return
    if is_blocked(msg.from_user.id):
        await msg.answer("❌ Siz bloklandingiz.")
        await state.clear()
        return
    await state.clear()
    try:
        uid = int(msg.text.strip())
        if is_blocked(uid):
            unblock_user(uid)
            await msg.answer(f"✅ {uid} blokdan chiqarildi.")
        else:
            await msg.answer("❌ Bu foydalanuvchi bloklangan emas.")
    except ValueError:
        await msg.answer("❌ Noto'g'ri ID!")


# Barcha bloklanganlarni olib tashlashni tasdiqlash
@router.callback_query(F.data == "admin_unblock_all")
async def admin_unblock_all(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    if is_blocked(call.from_user.id):
        await call.answer("❌ Siz bloklandingiz.")
        return
    
    blocked_users = get_all_blocked_users()
    if not blocked_users:
        await call.answer("❌ Olib tashlanadigan foydalanuvchi yo'q.")
        return
    
    text = f"⚠️ <b>Tasdiqla</b>\n\n{len(blocked_users)} ta foydalanuvchini barcha blokdan chiqarish?"
    
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="✅ Tasdiqla", callback_data="admin_unblock_all_confirm"),
        InlineKeyboardButton(text="❌ Bekor", callback_data="admin_view_blocked")
    )
    
    await call.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")


@router.callback_query(F.data == "admin_unblock_all_confirm")
async def admin_unblock_all_confirm(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    if is_blocked(call.from_user.id):
        await call.answer("❌ Siz bloklandingiz.")
        return
    unblock_all_users()
    await call.message.edit_text(
        "✅ Barcha bloklangan foydalanuvchilar blokdan chiqarildi.", 
        reply_markup=back_kb("admin_back"), 
        parse_mode="HTML"
    )


# Majburiy obuna
@router.callback_query(F.data == "admin_sub")
async def admin_sub(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    if is_blocked(call.from_user.id):
        await call.answer("❌ Siz bloklandingiz.")
        return

    current_channel = get_setting("subscribe_channel") or SUBSCRIBE_CHANNEL
    if not current_channel:
        current_channel = "yo'q"

    await state.set_state(AdminState.waiting_sub_channel)
    await call.message.edit_text(
        "➕ <b>Majburiy obuna</b>\n\n"
        f"Hozirgi kanal: <b>{current_channel}</b>\n\n"
        "Obuna talab qilinadigan kanal username (@username) ni yuboring.\n"
        "Agar talabni olib tashlamoqchi bo'lsangiz, clear deb yozing.",
        reply_markup=back_kb("admin_back"),
        parse_mode="HTML"
    )


@router.message(AdminState.waiting_sub_channel)
async def admin_set_sub_channel(msg: Message, state: FSMContext):
    if not is_root_admin(msg.from_user.id):
        await state.clear()
        return
    if is_blocked(msg.from_user.id):
        await msg.answer("❌ Siz bloklandingiz.")
        await state.clear()
        return

    text = msg.text.strip()
    if text.lower() == "clear":
        delete_setting("subscribe_channel")
        await msg.answer("✅ Majburiy obuna bekor qilindi.", reply_markup=back_kb("admin_back"))
        await state.clear()
        return

    channel = text
    if channel.startswith("https://t.me/"):
        channel = channel.split("https://t.me/")[-1].strip()
    if not channel.startswith("@"):
        channel = "@" + channel

    try:
        await msg.bot.get_chat(channel)
        set_setting("subscribe_channel", channel)
        await msg.answer(f"✅ Majburiy obuna kanali {channel} qilib belgilandi.", reply_markup=back_kb("admin_back"))
    except Exception:
        await msg.answer("❌ Kanal topilmadi yoki username noto'g'ri. Iltimos qayta urinib ko'ring.")
    finally:
        await state.clear()


@router.callback_query(F.data == "admin_new_bot")
async def admin_new_bot(call: CallbackQuery, state: FSMContext):
    if not is_root_admin(call.from_user.id):
        return
    if is_blocked(call.from_user.id):
        await call.answer("❌ Siz bloklandingiz.")
        return

    await state.set_state(AdminState.waiting_new_bot_token)
    await call.message.edit_text(
        "➕ <b>Yangi bot qo'shish</b>\n\n"
        "Bot tokenini yuboring. Token to'g'ri bo'lsa, u bazaga saqlanadi.",
        reply_markup=back_kb("admin_back"),
        parse_mode="HTML"
    )


async def check_bot_token(token: str) -> tuple[str, str, str]:
    test_bot = Bot(token=token)
    try:
        me = await test_bot.get_me()
        username = f"@{me.username}" if me.username else str(me.id)
        title = me.full_name or me.username or username
        await test_bot.session.close()
        return "active", username, title
    except Exception:
        try:
            await test_bot.session.close()
        except Exception:
            pass
        return "invalid", "unknown", "unknown"


@router.message(AdminState.waiting_new_bot_token)
async def admin_new_bot_do(msg: Message, state: FSMContext):
    if not is_root_admin(msg.from_user.id):
        await state.clear()
        return
    if is_blocked(msg.from_user.id):
        await msg.answer("❌ Siz bloklandingiz.")
        await state.clear()
        return

    token = msg.text.strip()
    parts = token.split()
    if parts and parts[0].lower() == "bot" and len(parts) > 1:
        token = parts[1].strip()

    status, username, title = await check_bot_token(token)
    if status == "active":
        add_bot(token, username, title, msg.from_user.id)
        update_bot_status(token, "active")
        await msg.answer(f"✅ Yangi bot saqlandi: {title} ({username})", reply_markup=back_kb("admin_back"))
    else:
        await msg.answer("❌ Token noto'g'ri yoki botga ulanish mumkin emas. Iltimos qayta urinib ko'ring.")
    await state.clear()


@router.callback_query(F.data == "admin_bots")
async def admin_bots(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    if is_blocked(call.from_user.id):
        await call.answer("❌ Siz bloklandingiz.")
        return

    bots = get_all_bots()
    if not bots:
        await call.message.edit_text(
            "🤖 <b>Botlar ro'yxati</b>\n\nHozircha botlar saqlanmagan.",
            reply_markup=InlineKeyboardBuilder()
                .row(InlineKeyboardButton(text="➕ Yangi bot", callback_data="admin_new_bot"))
                .row(InlineKeyboardButton(text="↩️ Orqaga", callback_data="admin_back"))
                .as_markup(),
            parse_mode="HTML"
        )
        return

    text = "🤖 <b>Botlar ro'yxati</b>\n\n"
    active_count = 0
    invalid_count = 0
    for bot_token, bot_username, bot_title, added_by, added_at, status, last_checked in bots:
        status_icon = "✅" if status == "active" else "❌"
        if status == "active":
            active_count += 1
        else:
            invalid_count += 1
        text += (
            f"{status_icon} <b>{bot_title}</b> ({bot_username})\n"
            f"ID: <code>{added_by}</code> | Qo'shildi: {added_at}\n"
            f"Holat: <b>{status}</b> | Tekshirilgan: {last_checked}\n\n"
        )

    text = f"🤖 <b>Botlar ro'yxati</b> — Faol: {active_count}, Nofaol: {invalid_count}\n\n" + text

    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="🔄 Statusni yangilash", callback_data="admin_refresh_bots"))
    kb.row(InlineKeyboardButton(text="🗑️ Yaroqsiz botlarni o'chirish", callback_data="admin_cleanup_invalid_bots"))
    kb.row(InlineKeyboardButton(text="➕ Yangi bot", callback_data="admin_new_bot"))
    kb.row(InlineKeyboardButton(text="↩️ Orqaga", callback_data="admin_back"))

    await call.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")


@router.callback_query(F.data == "admin_refresh_bots")
async def admin_refresh_bots(call: CallbackQuery):
    if not is_root_admin(call.from_user.id):
        return
    if is_blocked(call.from_user.id):
        await call.answer("❌ Siz bloklandingiz.")
        return

    bots = get_all_bots()
    if not bots:
        await call.answer("🤖 Ro'yxatda bot yo'q.")
        return

    msg = await call.message.edit_text("⏳ Botlar holati tekshirilmoqda...", parse_mode="HTML")
    active = 0
    invalid = 0

    for bot_token, _, _, _, _, _, _ in bots:
        status, username, title = await check_bot_token(bot_token)
        update_bot_status(bot_token, status)
        if status == "active":
            active += 1
        else:
            invalid += 1

    await msg.edit_text(f"✅ Tekshirildi. Faol: {active}, Nofaol: {invalid}.\n\nRo'yxatni qayta oching.")


@router.callback_query(F.data == "admin_cleanup_invalid_bots")
async def admin_cleanup_invalid_bots(call: CallbackQuery):
    if not is_root_admin(call.from_user.id):
        return
    if is_blocked(call.from_user.id):
        await call.answer("❌ Siz bloklandingiz.")
        return

    bots = get_all_bots()
    invalid_bots = [bot_token for bot_token, _, _, _, _, status, _ in bots if status != "active"]
    if not invalid_bots:
        await call.answer("✅ Nofaol bot yo'q.")
        return

    for bot_token in invalid_bots:
        remove_bot(bot_token)

    await call.message.edit_text(
        f"🗑️ {len(invalid_bots)} ta yaroqsiz bot o'chirildi.",
        reply_markup=InlineKeyboardBuilder()
            .row(InlineKeyboardButton(text="🤖 Botlar ro'yxati", callback_data="admin_bots"))
            .row(InlineKeyboardButton(text="↩️ Orqaga", callback_data="admin_back"))
            .as_markup(),
        parse_mode="HTML"
    )


# Admin orqaga
@router.callback_query(F.data == "admin_back")
async def admin_back(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    if is_blocked(call.from_user.id):
        await call.answer("❌ Siz bloklandingiz.")
        return

    await state.clear()
    from database import get_conn
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM groups")
    groups = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM channels")
    channels = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM bots")
    bots = c.fetchone()[0]
    conn.close()

    required_channel = get_setting("subscribe_channel") or SUBSCRIBE_CHANNEL
    if not required_channel:
        required_channel = "yo'q"

    await call.message.edit_text(
        f"👨‍💼 <b>Admin Panel</b>\n\n👥 Guruhlar: <b>{groups}</b>\n📢 Kanallar: <b>{channels}</b>\n🤖 Botlar: <b>{bots}</b>\n\nMajburiy obuna: <b>{required_channel}</b>\n\nBu botlar asosiy bot orqali boshqariladi.",
        reply_markup=admin_kb(is_root=is_root_admin(call.from_user.id)),
        parse_mode="HTML"
    )


# /cancel
@router.message(Command("cancel"))
async def cmd_cancel(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("❌ Bekor qilindi.")
