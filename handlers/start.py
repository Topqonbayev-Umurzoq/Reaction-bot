from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
import json, os
import random

from database import get_user, add_user, get_user_lang, get_user_private_auto_react, get_user_private_active_message_id, set_user_private_active_message_id, is_blocked, get_all_channels_by_user, get_all_groups_by_user
from keyboards.inline import main_menu_kb, channels_kb, groups_kb, lang_kb

router = Router()

def t(lang, key):
    path = os.path.join("locales", f"{lang}.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get(key, key)


EMOJIS = [
    "👍","❤️","🔥","🥰","👏","😁","🤔","🤯","😱","🤬",
    "😢","🎉","🤩","🤮","💩","🙏","👌","🕊","🤡","🥱",
    "🥴","😍","🐳","❤️‍🔥","🌚","🌭","💯","🤣","⚡","🍌",
    "🏆","💔","🤨","😐","🍓","🍾","💋","🖕","😈","😴",
    "😭","🤓","👻","👨‍💻","👀","🎃","🙈","😇","😨","🤝",
    "✍️","🤗","🫡","🎅","🎄","☃️","💅","🤪","🗿","🆒",
    "💘","🙉","🦄","💊","🙊","😎","👾","🤷","😡"
]


async def react_random(bot, chat_id, message_id):
    try:
        await bot.set_message_reaction(
            chat_id,
            message_id,
            reaction=[{"type": "emoji", "emoji": random.choice(EMOJIS)}]
        )
    except Exception:
        pass


def is_fresh_private_callback(call: CallbackQuery) -> bool:
    if call.message.chat.type != "private":
        return True
    return call.message.message_id == get_user_private_active_message_id(call.from_user.id)


def stale_button_text() -> str:
    return "Bu tugma endi eskirgan, oxirgi xabarni ishlating"

# /start buyrug'i — faqat bot bilan shaxsiy chatda
@router.message(CommandStart())
async def cmd_start(msg: Message):
    user = msg.from_user
    existing_user = get_user(user.id)

    if not existing_user:
        add_user(user.id, user.username, user.full_name)
        sent = await msg.answer(
            t("uz", "choose_lang"),
            reply_markup=lang_kb(),
            parse_mode="HTML"
        )
        set_user_private_active_message_id(user.id, sent.message_id)
        await react_random(msg.bot, sent.chat.id, sent.message_id)
        return

    if is_blocked(user.id):
        await msg.answer("❌ Siz bloklandingiz.")
        return

    lang = get_user_lang(user.id)
    sent = await msg.answer(
        f"{t(lang, 'welcome')}\n\n{t(lang, 'your_id').format(id=user.id)}",
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML"
    )
    set_user_private_active_message_id(user.id, sent.message_id)
    await react_random(msg.bot, sent.chat.id, sent.message_id)

# KANAL UCHUN tugmasi
@router.callback_query(F.data == "type_channel")
async def channel_section(call: CallbackQuery):
    if not is_fresh_private_callback(call):
        await call.answer(stale_button_text(), show_alert=True)
        return
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
    if not is_fresh_private_callback(call):
        await call.answer(stale_button_text(), show_alert=True)
        return
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
    if not is_fresh_private_callback(call):
        await call.answer(stale_button_text(), show_alert=True)
        return
    lang = get_user_lang(call.from_user.id)
    await call.message.edit_text(
        t(lang, "welcome"),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML"
    )
    set_user_private_active_message_id(call.from_user.id, call.message.message_id)

# Kanal qo'shish yo'riqnomasi
@router.callback_query(F.data == "add_channel")
async def add_channel_guide(call: CallbackQuery):
    if not is_fresh_private_callback(call):
        await call.answer(stale_button_text(), show_alert=True)
        return
    lang = get_user_lang(call.from_user.id)
    from keyboards.inline import back_kb
    await call.message.edit_text(
        t(lang, "add_bot_to_channel"),
        reply_markup=back_kb("type_channel")
    )

# Guruh qo'shish yo'riqnomasi
@router.callback_query(F.data == "add_group")
async def add_group_guide(call: CallbackQuery):
    if not is_fresh_private_callback(call):
        await call.answer(stale_button_text(), show_alert=True)
        return
    lang = get_user_lang(call.from_user.id)
    from keyboards.inline import back_kb
    await call.message.edit_text(
        t(lang, "add_bot_to_group"),
        reply_markup=back_kb("type_group")
    )

# Kanal tanlanganda sozlamalar
@router.callback_query(F.data.startswith("ch_"))
async def channel_settings(call: CallbackQuery):
    if not is_fresh_private_callback(call):
        await call.answer(stale_button_text(), show_alert=True)
        return
    chat_id = int(call.data.split("_")[1])
    lang = get_user_lang(call.from_user.id)
    from database import get_channel
    from keyboards.inline import channel_settings_kb
    ch = get_channel(chat_id)
    if not ch:
        await call.answer("Kanal topilmadi!", show_alert=True)
        return
    auto_react = bool(ch[4])
    emoji = ch[3] if ch[3] != "random" else "🎲 random"
    await call.message.edit_text(
        f"📢 <b>{ch[1]}</b>\n\nJoriy reaksiya: {emoji}",
        reply_markup=channel_settings_kb(chat_id, auto_react, lang),
        parse_mode="HTML"
    )

# Guruh tanlanganda sozlamalar
@router.callback_query(F.data.startswith("gr_"))
async def group_settings(call: CallbackQuery):
    if not is_fresh_private_callback(call):
        await call.answer(stale_button_text(), show_alert=True)
        return
    chat_id = int(call.data.split("_")[1])
    lang = get_user_lang(call.from_user.id)
    from database import get_group
    from keyboards.inline import group_settings_kb
    gr = get_group(chat_id)
    if not gr:
        await call.answer("Guruh topilmadi!", show_alert=True)
        return
    auto_react = bool(gr[4])
    emoji = gr[3] if gr[3] != "random" else "🎲 random"
    await call.message.edit_text(
        f"👥 <b>{gr[1]}</b>\n\nJoriy reaksiya: {emoji}",
        reply_markup=group_settings_kb(chat_id, auto_react, lang),
        parse_mode="HTML"
    )


async def private_auto_react_handler(msg: Message, bot):
    user = msg.from_user
    if not user:
        return
    if is_blocked(user.id):
        return
    if not get_user_private_auto_react(user.id):
        return
    await react_random(bot, msg.chat.id, msg.message_id)


@router.message(F.chat.type == "private", F.text, ~F.text.startswith("/"))
async def private_text_auto_react_handler(msg: Message, bot):
    await private_auto_react_handler(msg, bot)


@router.message(F.chat.type == "private", ~F.text)
async def private_nontext_auto_react_handler(msg: Message, bot):
    await private_auto_react_handler(msg, bot)
