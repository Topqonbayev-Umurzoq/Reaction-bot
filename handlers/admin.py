from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from config import ADMIN_ID
from database import (
    get_all_users, block_user, unblock_user,
    add_admin, get_admins, is_admin_user, remove_admin, remove_all_admins
)
from keyboards.inline import admin_kb, back_kb

router = Router()

class AdminState(StatesGroup):
    waiting_broadcast = State()
    waiting_block_id = State()
    waiting_unblock_id = State()
    waiting_add_admin = State()
    waiting_remove_admin = State()



def is_root_admin(user_id):
    return user_id == ADMIN_ID


def is_admin(user_id):
    return user_id == ADMIN_ID or is_admin_user(user_id)


# /admin buyrug'i
@router.message(Command("admin"))
async def cmd_admin(msg: Message):
    if not is_admin(msg.from_user.id):
        return
    is_root = is_root_admin(msg.from_user.id)
    extra = f"\n\n<b>Hozirgi ID:</b> <code>{msg.from_user.id}</code>"
    if is_root:
        extra += "\n<b>Siz bosh admin hisoblanasiz.</b>"
    else:
        extra += "\nSiz admin sifatida ishlayapsiz."

    await msg.answer(
        "👨‍💼 <b>Admin Panel</b>" + extra,
        reply_markup=admin_kb(is_root=is_root),
        parse_mode="HTML"
    )


# Foydalanuvchilar ro'yxati
@router.callback_query(F.data == "admin_users")
async def admin_users(call: CallbackQuery):
    if not is_admin(call.from_user.id):
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
    conn.close()

    text = (
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{total}</b>\n"
        f"🚫 Bloklangan: <b>{blocked}</b>\n"
        f"👥 Guruhlar: <b>{groups}</b>\n"
        f"📢 Kanallar: <b>{channels}</b>"
    )
    await call.message.edit_text(text, reply_markup=back_kb("admin_back"), parse_mode="HTML")


# Xabar yuborish (broadcast)
@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
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
    await state.set_state(AdminState.waiting_block_id)
    await call.message.edit_text(
        "🚫 Bloklash uchun foydalanuvchi ID sini kiriting:",
        reply_markup=back_kb("admin_back")
    )


@router.message(AdminState.waiting_block_id)
async def admin_block_do(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id):
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
    await state.set_state(AdminState.waiting_unblock_id)
    await call.message.edit_text(
        "✅ Blokdan chiqarish uchun foydalanuvchi ID sini kiriting:",
        reply_markup=back_kb("admin_back")
    )


@router.message(AdminState.waiting_unblock_id)
async def admin_unblock_do(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id):
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
    await state.set_state(AdminState.waiting_add_admin)
    await call.message.edit_text(
        "➕ Admin qo'shish uchun foydalanuvchi ID sini kiriting:\n\n(Bekor qilish uchun /cancel)",
        reply_markup=back_kb("admin_back")
    )


@router.message(AdminState.waiting_add_admin)
async def admin_add_do(msg: Message, state: FSMContext):
    if not is_root_admin(msg.from_user.id):
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

    await call.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


# Admin olib tashlashni tanlash
@router.callback_query(F.data == "admin_remove_select")
async def admin_remove_select(call: CallbackQuery, state: FSMContext):
    if not is_root_admin(call.from_user.id):
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
    
    await call.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data == "admin_remove_all_confirm")
async def admin_remove_all_confirm(call: CallbackQuery):
    if not is_root_admin(call.from_user.id):
        return
    remove_all_admins()
    await call.message.edit_text(
        "✅ Barcha adminlar adminlikdan olib tashlandi.", 
        reply_markup=back_kb("admin_back"), 
        parse_mode="HTML"
    )


# Majburiy obuna
@router.callback_query(F.data == "admin_sub")
async def admin_sub(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    await call.message.edit_text(
        "➕ <b>Majburiy obuna</b>\n\nBu funksiya tez orada qo'shiladi.",
        reply_markup=back_kb("admin_back"),
        parse_mode="HTML"
    )


# Admin orqaga
@router.callback_query(F.data == "admin_back")
async def admin_back(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    await call.message.edit_text(
        "👨‍💼 <b>Admin Panel</b>",
        reply_markup=admin_kb(is_root=is_root_admin(call.from_user.id)),
        parse_mode="HTML"
    )


# /cancel
@router.message(Command("cancel"))
async def cmd_cancel(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("❌ Bekor qilindi.")
