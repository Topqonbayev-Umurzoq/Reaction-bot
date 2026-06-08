from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
import json, os

from database import get_user, add_user, get_user_lang, is_blocked, get_all_channels_by_user, get_all_groups_by_user
from keyboards.inline import main_menu_kb, channels_kb, groups_kb, lang_kb

router = Router()

def t(lang, key):
    path = os.path.join("locales", f"{lang}.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get(key, key)

# /start buyrug'i — faqat bot bilan shaxsiy chatda
@router.message(CommandStart())
async def cmd_start(msg: Message):
    user = msg.from_user
    existing_user = get_user(user.id)

    if not existing_user:
        add_user(user.id, user.username, user.full_name)
        await msg.answer(
            t("uz", "choose_lang"),
            reply_markup=lang_kb(),
            parse_mode="HTML"
        )
        return

    if is_blocked(user.id):
        await msg.answer("❌ Siz bloklandingiz.")
        return

    lang = get_user_lang(user.id)
    await msg.answer(
        f"{t(lang, 'welcome')}\n\n{t(lang, 'your_id').format(id=user.id)}",
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML"
    )

# KANAL UCHUN tugmasi
@router.callback_query(F.data == "type_channel")
async def channel_section(call: CallbackQuery):
    lang = get_user_lang(call.from_user.id)
    channels = get_all_channels_by_user(call.from_user.id)

    if not channels:
        text = t(lang, "no_channels")
    else:
        text = t(lang, "channel_list")

    await call.message.edit_text(text, reply_markup=channels_kb(channels, lang))

# GURUH UCHUN tugmasi
@router.callback_query(F.data == "type_group")
async def group_section(call: CallbackQuery):
    lang = get_user_lang(call.from_user.id)
    groups = get_all_groups_by_user(call.from_user.id)

    if not groups:
        text = t(lang, "no_groups")
    else:
        text = t(lang, "group_list")

    await call.message.edit_text(text, reply_markup=groups_kb(groups, lang))

# Orqaga — bosh menyu
@router.callback_query(F.data == "back_main")
async def back_main(call: CallbackQuery):
    lang = get_user_lang(call.from_user.id)
    await call.message.edit_text(
        t(lang, "welcome"),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML"
    )

# Kanal qo'shish yo'riqnomasi
@router.callback_query(F.data == "add_channel")
async def add_channel_guide(call: CallbackQuery):
    lang = get_user_lang(call.from_user.id)
    from keyboards.inline import back_kb
    await call.message.edit_text(
        t(lang, "add_bot_to_channel"),
        reply_markup=back_kb("type_channel")
    )

# Guruh qo'shish yo'riqnomasi
@router.callback_query(F.data == "add_group")
async def add_group_guide(call: CallbackQuery):
    lang = get_user_lang(call.from_user.id)
    from keyboards.inline import back_kb
    await call.message.edit_text(
        t(lang, "add_bot_to_group"),
        reply_markup=back_kb("type_group")
    )

# Kanal tanlanganda sozlamalar
@router.callback_query(F.data.startswith("ch_"))
async def channel_settings(call: CallbackQuery):
    chat_id = int(call.data.split("_")[1])
    lang = get_user_lang(call.from_user.id)
    from database import get_channel
    from keyboards.inline import channel_settings_kb
    ch = get_channel(chat_id)
    if not ch:
        await call.answer("Kanal topilmadi!", show_alert=True)
        return
    auto_react = bool(ch[4])
    emoji = ch[3]
    await call.message.edit_text(
        f"📢 <b>{ch[1]}</b>\n\nJoriy reaksiya: {emoji}",
        reply_markup=channel_settings_kb(chat_id, auto_react, lang),
        parse_mode="HTML"
    )

# Guruh tanlanganda sozlamalar
@router.callback_query(F.data.startswith("gr_"))
async def group_settings(call: CallbackQuery):
    chat_id = int(call.data.split("_")[1])
    lang = get_user_lang(call.from_user.id)
    from database import get_group
    from keyboards.inline import group_settings_kb
    gr = get_group(chat_id)
    if not gr:
        await call.answer("Guruh topilmadi!", show_alert=True)
        return
    auto_react = bool(gr[4])
    emoji = gr[3]
    await call.message.edit_text(
        f"👥 <b>{gr[1]}</b>\n\nJoriy reaksiya: {emoji}",
        reply_markup=group_settings_kb(chat_id, auto_react, lang),
        parse_mode="HTML"
    )
