from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReactionTypeEmoji
from aiogram.filters import Command
from aiogram.enums import ChatType
from aiogram.exceptions import TelegramBadRequest
import random, json, os

from database import (
    get_group, add_group, set_group_reaction, set_group_auto_react,
    get_channel, add_channel, set_channel_reaction, set_channel_auto_react,
    get_user_lang,
    get_user_private_active_message_id,
    set_user_private_active_message_id,
)
from keyboards.inline import reaction_kb, back_kb, group_settings_kb, channel_settings_kb

router = Router()

EMOJIS = [
    "👍","❤️","🔥","🥰","👏","😁","🤔","🤯","😱","🤬",
    "😢","🎉","🤩","🤮","💩","🙏","👌","🕊","🤡","🥱",
    "🥴","😍","🐳","❤️‍🔥","🌚","🌭","💯","🤣","⚡","🍌",
    "🏆","💔","🤨","😐","🍓","🍾","💋","🖕","😈","😴",
    "😭","🤓","👻","👨‍💻","👀","🎃","🙈","😇","😨","🤝",
    "✍️","🤗","🫡","🎅","🎄","☃️","💅","🤪","🗿","🆒",
    "💘","🙉","🦄","💊","🙊","😎","👾","🤷","😡"
]

def t(lang, key):
    path = os.path.join("locales", f"{lang}.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get(key, key)

async def is_admin(bot: Bot, chat_id: int, user_id: int) -> bool:
    member = await bot.get_chat_member(chat_id, user_id)
    return member.status in ("administrator", "creator")


async def bot_is_admin(bot: Bot, chat_id: int) -> bool:
    try:
        me = await bot.get_me()
        member = await bot.get_chat_member(chat_id, me.id)
        return member.status in ("administrator", "creator")
    except Exception:
        return False


def reaction_value_label(value: str) -> str:
    return "🎲 random" if value == "random" else (value or "🎲 random")


async def set_reaction(bot: Bot, chat_id: int, message_id: int, emoji: str):
    if emoji == "random" or not emoji:
        emoji = random.choice(EMOJIS)
    try:
        await bot.set_message_reaction(
            chat_id,
            message_id,
            reaction=[ReactionTypeEmoji(emoji=emoji)]
        )
    except Exception:
        pass


def parse_reaction_callback(data: str):
    parts = data.split("_", 3)
    if len(parts) != 4:
        return None, None, None
    _, kind, chat_id, payload = parts
    try:
        return kind, int(chat_id), payload
    except ValueError:
        return None, None, None

async def delete_msg(bot: Bot, chat_id: int, msg_id: int):
    try:
        await bot.delete_message(chat_id, msg_id)
    except Exception:
        pass


def is_fresh_private_callback(call: CallbackQuery) -> bool:
    if call.message.chat.type != "private":
        return True
    return call.message.message_id == get_user_private_active_message_id(call.from_user.id)


def stale_button_text() -> str:
    return "Bu tugma endi eskirgan, oxirgi xabarni ishlating"


async def safe_edit_text(message, *args, **kwargs):
    try:
        await message.edit_text(*args, **kwargs)
    except TelegramBadRequest as exc:
        if "message is not modified" not in str(exc):
            raise


async def safe_edit_reply_markup(message, *args, **kwargs):
    try:
        await message.edit_reply_markup(*args, **kwargs)
    except TelegramBadRequest as exc:
        if "message is not modified" not in str(exc):
            raise

# Bot guruhga qo'shilganda
@router.message(F.new_chat_members)
async def bot_added_to_group(msg: Message, bot: Bot):
    me = await bot.get_me()
    for member in msg.new_chat_members:
        if member.id == me.id:
            add_group(msg.chat.id, msg.chat.title, msg.from_user.id)


@router.my_chat_member()
async def bot_chat_member_update(update, bot: Bot):
    if update.new_chat_member.user.id != (await bot.get_me()).id:
        return

    chat = update.chat
    new_status = update.new_chat_member.status
    if new_status not in ("administrator", "member"):
        return

    if chat.type in ("group", "supergroup"):
        actor_id = update.from_user.id if update.from_user else 0
        add_group(chat.id, chat.title, actor_id)
    elif chat.type == "channel":
        actor_id = update.from_user.id if update.from_user else 0
        add_channel(chat.id, chat.title or str(chat.id), actor_id)

# /reaksiya — guruhda emoji tanlash
@router.message(Command("reaksiya"), F.chat.type.in_({"group", "supergroup"}))
async def cmd_reaksiya(msg: Message, bot: Bot):
    if not await is_admin(bot, msg.chat.id, msg.from_user.id):
        await delete_msg(bot, msg.chat.id, msg.message_id)
        return

    gr = get_group(msg.chat.id)
    selected = gr[3] if gr else "random"
    sent = await msg.answer(
        "Guruhga har safar xabar yuborilganda qaysi reaksiya bosilishini tanlang 👇\n\n✅ Tanlab bo'lganingizdan keyin tayyor tugmasini bosing",
        reply_markup=reaction_kb(selected, msg.chat.id, "group")
    )
    if msg.chat.type == "private":
        set_user_private_active_message_id(msg.from_user.id, sent.message_id)
    await delete_msg(bot, msg.chat.id, msg.message_id)

# Reaksiya tanlash callback
@router.callback_query(F.data.startswith("react_"))
async def react_selected(call: CallbackQuery):
    if call.message.chat.type == "private" and not is_fresh_private_callback(call):
        await call.answer(stale_button_text(), show_alert=True)
        return
    kind, chat_id, payload = parse_reaction_callback(call.data)
    if not kind or not chat_id:
        return

    if payload == "done":
        if kind == "group":
            gr = get_group(chat_id)
            emoji_value = gr[3] if gr else "random"
        else:
            ch = get_channel(chat_id)
            emoji_value = ch[3] if ch else "random"
        if call.message.chat.type == "private":
            lang = get_user_lang(call.from_user.id)
            if kind == "group":
                gr = get_group(chat_id)
                auto_react = bool(gr[4]) if gr else False
                await safe_edit_text(
                    call.message,
                    f"👥 <b>{gr[1] if gr else chat_id}</b>\n\nJoriy reaksiya: {reaction_value_label(emoji_value)}",
                    reply_markup=group_settings_kb(chat_id, auto_react, lang),
                    parse_mode="HTML"
                )
            else:
                ch = get_channel(chat_id)
                auto_react = bool(ch[4]) if ch else False
                await safe_edit_text(
                    call.message,
                    f"📢 <b>{ch[1] if ch else chat_id}</b>\n\nJoriy reaksiya: {reaction_value_label(emoji_value)}",
                    reply_markup=channel_settings_kb(chat_id, auto_react, lang),
                    parse_mode="HTML"
                )
        else:
            await safe_edit_text(call.message, f"✅ Reaksiya belgilandi: {reaction_value_label(emoji_value)}")
        return

    emoji = payload
    if kind == "group":
        set_group_reaction(chat_id, emoji)
        current = get_group(chat_id)
        selected = current[3] if current else emoji
    else:
        set_channel_reaction(chat_id, emoji)
        current = get_channel(chat_id)
        selected = current[3] if current else emoji

    await safe_edit_reply_markup(call.message, reply_markup=reaction_kb(selected, chat_id, kind))
    if call.message.chat.type == "private":
        set_user_private_active_message_id(call.from_user.id, call.message.message_id)
    await call.answer(f"Tanlandi: {reaction_value_label(emoji)}")

# /reaksiya_on
@router.message(Command("reaksiya_on"), F.chat.type.in_({"group", "supergroup"}))
async def cmd_reaksiya_on(msg: Message, bot: Bot):
    if not await is_admin(bot, msg.chat.id, msg.from_user.id):
        await delete_msg(bot, msg.chat.id, msg.message_id)
        return

    set_group_auto_react(msg.chat.id, True)
    await msg.answer("✅ Bu guruh uchun 🤖 Auto reaksiya yoqildi")
    await delete_msg(bot, msg.chat.id, msg.message_id)

# /reaksiya_off
@router.message(Command("reaksiya_off"), F.chat.type.in_({"group", "supergroup"}))
async def cmd_reaksiya_off(msg: Message, bot: Bot):
    if not await is_admin(bot, msg.chat.id, msg.from_user.id):
        await delete_msg(bot, msg.chat.id, msg.message_id)
        return

    set_group_auto_react(msg.chat.id, False)
    await msg.answer("❌ Bu guruh uchun 🤖 Auto reaksiya o'chirildi")
    await delete_msg(bot, msg.chat.id, msg.message_id)

# /bos
@router.message(Command("bos"), F.chat.type.in_({"group", "supergroup"}))
async def cmd_bos(msg: Message, bot: Bot):
    if not await is_admin(bot, msg.chat.id, msg.from_user.id):
        await delete_msg(bot, msg.chat.id, msg.message_id)
        return

    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        await msg.answer(
            "/bos dan keyin emoji qo'yib yuboring.\nMasalan: /bos 😎"
        )
        await delete_msg(bot, msg.chat.id, msg.message_id)
        return

    emoji = parts[1].strip()
    try:
        await bot.set_message_reaction(
            msg.chat.id,
            msg.reply_to_message.message_id if msg.reply_to_message else msg.message_id,
            reaction=[{"type": "emoji", "emoji": emoji}]
        )
    except Exception as e:
        await msg.answer(f"Xato: {e}")
    await delete_msg(bot, msg.chat.id, msg.message_id)

# /send
@router.message(Command("send"), F.chat.type.in_({"group", "supergroup"}))
async def cmd_send(msg: Message, bot: Bot):
    if not await is_admin(bot, msg.chat.id, msg.from_user.id):
        await delete_msg(bot, msg.chat.id, msg.message_id)
        return

    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        await msg.answer("Xabar matnini kiriting: /send Salom hammaga!")
        await delete_msg(bot, msg.chat.id, msg.message_id)
        return

    text = parts[1]
    await msg.answer(text)
    await delete_msg(bot, msg.chat.id, msg.message_id)

# Auto reaksiya — har yangi xabarga
@router.message(F.chat.type.in_({"group", "supergroup"}))
async def auto_react_handler(msg: Message, bot: Bot):
    gr = get_group(msg.chat.id)
    if not gr:
        return
    auto_react = bool(gr[4])
    if not auto_react or not await bot_is_admin(bot, msg.chat.id):
        return
    await set_reaction(bot, msg.chat.id, msg.message_id, gr[3])

# Auto react toggle (bot chatidan)
@router.callback_query(F.data.startswith("toggle_auto_"))
async def toggle_auto_react(call: CallbackQuery):
    if call.message.chat.type == "private" and not is_fresh_private_callback(call):
        await call.answer(stale_button_text(), show_alert=True)
        return
    chat_id = int(call.data.replace("toggle_auto_", ""))
    gr = get_group(chat_id)
    if not gr:
        await call.answer("Guruh topilmadi!", show_alert=True)
        return
    new_state = not bool(gr[4])
    set_group_auto_react(chat_id, new_state)
    lang = get_user_lang(call.from_user.id)
    await safe_edit_reply_markup(
        call.message,
        reply_markup=group_settings_kb(chat_id, new_state, lang)
    )
    if call.message.chat.type == "private":
        set_user_private_active_message_id(call.from_user.id, call.message.message_id)
    status = "yoqildi ✅" if new_state else "o'chirildi ❌"
    await call.answer(f"Auto reaksiya {status}", show_alert=True)

# Reaksiya o'zgartirish (bot chatidan)
@router.callback_query(F.data.startswith("change_react_"))
async def change_react(call: CallbackQuery):
    if call.message.chat.type == "private" and not is_fresh_private_callback(call):
        await call.answer(stale_button_text(), show_alert=True)
        return
    chat_id = int(call.data.replace("change_react_", ""))
    gr = get_group(chat_id)
    selected = gr[3] if gr else "random"
    await safe_edit_text(
        call.message,
        "Yangi reaksiyani tanlang 👇",
        reply_markup=reaction_kb(selected, chat_id, "group")
    )
    if call.message.chat.type == "private":
        set_user_private_active_message_id(call.from_user.id, call.message.message_id)


@router.callback_query(F.data.startswith("toggle_ch_auto_"))
async def toggle_ch_auto(call: CallbackQuery):
    if call.message.chat.type == "private" and not is_fresh_private_callback(call):
        await call.answer(stale_button_text(), show_alert=True)
        return
    chat_id = int(call.data.replace("toggle_ch_auto_", ""))
    ch = get_channel(chat_id)
    if not ch:
        await call.answer("Kanal topilmadi!", show_alert=True)
        return
    new_state = not bool(ch[4])
    set_channel_auto_react(chat_id, new_state)
    lang = get_user_lang(call.from_user.id)
    await safe_edit_reply_markup(
        call.message,
        reply_markup=channel_settings_kb(chat_id, new_state, lang)
    )
    if call.message.chat.type == "private":
        set_user_private_active_message_id(call.from_user.id, call.message.message_id)
    status = "yoqildi ✅" if new_state else "o'chirildi ❌"
    await call.answer(f"Auto reaksiya {status}", show_alert=True)


@router.callback_query(F.data.startswith("change_ch_react_"))
async def change_ch_react(call: CallbackQuery):
    if call.message.chat.type == "private" and not is_fresh_private_callback(call):
        await call.answer(stale_button_text(), show_alert=True)
        return
    chat_id = int(call.data.replace("change_ch_react_", ""))
    ch = get_channel(chat_id)
    selected = ch[3] if ch else "random"
    await safe_edit_text(
        call.message,
        "Yangi reaksiyani tanlang 👇",
        reply_markup=reaction_kb(selected, chat_id, "channel")
    )
    if call.message.chat.type == "private":
        set_user_private_active_message_id(call.from_user.id, call.message.message_id)


@router.channel_post()
async def auto_react_channel_post(msg: Message, bot: Bot):
    ch = get_channel(msg.chat.id)
    if not ch:
        return
    if not bool(ch[4]) or not await bot_is_admin(bot, msg.chat.id):
        return
    await set_reaction(bot, msg.chat.id, msg.message_id, ch[3])
