from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.enums import ChatType
import random, json, os

from database import (
    get_group, add_group, set_group_reaction, set_group_auto_react,
    get_user_lang
)
from keyboards.inline import reaction_kb, back_kb, group_settings_kb

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

async def delete_msg(bot: Bot, chat_id: int, msg_id: int):
    try:
        await bot.delete_message(chat_id, msg_id)
    except Exception:
        pass

# Bot guruhga qo'shilganda
@router.message(F.new_chat_members)
async def bot_added_to_group(msg: Message, bot: Bot):
    me = await bot.get_me()
    for member in msg.new_chat_members:
        if member.id == me.id:
            add_group(msg.chat.id, msg.chat.title, msg.from_user.id)

# /reaksiya — guruhda emoji tanlash
@router.message(Command("reaksiya"), F.chat.type.in_({"group", "supergroup"}))
async def cmd_reaksiya(msg: Message, bot: Bot):
    if not await is_admin(bot, msg.chat.id, msg.from_user.id):
        await delete_msg(bot, msg.chat.id, msg.message_id)
        return

    gr = get_group(msg.chat.id)
    selected = gr[3] if gr else "👍"
    sent = await msg.answer(
        "Guruhga har safar xabar yuborilganda qaysi reaksiya bosilishini tanlang 👇\n\n✅ Tanlab bo'lganingizdan keyin tayyor tugmasini bosing",
        reply_markup=reaction_kb(selected)
    )
    await delete_msg(bot, msg.chat.id, msg.message_id)

# Reaksiya tanlash callback
@router.callback_query(F.data.startswith("react_"))
async def react_selected(call: CallbackQuery):
    data = call.data
    chat_id = call.message.chat.id

    if data == "react_done":
        gr = get_group(chat_id)
        emoji = gr[3] if gr else "👍"
        await call.message.edit_text(f"✅ Reaksiya belgilandi: {emoji}")
        return

    if data == "react_random":
        emoji = random.choice(EMOJIS)
    else:
        emoji = data.replace("react_", "")

    set_group_reaction(chat_id, emoji)
    await call.message.edit_reply_markup(reply_markup=reaction_kb(emoji))
    await call.answer(f"Tanlandi: {emoji}")

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
    if not auto_react:
        return
    emoji = gr[3] or "👍"
    try:
        await bot.set_message_reaction(
            msg.chat.id,
            msg.message_id,
            reaction=[{"type": "emoji", "emoji": emoji}]
        )
    except Exception:
        pass

# Auto react toggle (bot chatidan)
@router.callback_query(F.data.startswith("toggle_auto_"))
async def toggle_auto_react(call: CallbackQuery):
    chat_id = int(call.data.replace("toggle_auto_", ""))
    gr = get_group(chat_id)
    if not gr:
        await call.answer("Guruh topilmadi!", show_alert=True)
        return
    new_state = not bool(gr[4])
    set_group_auto_react(chat_id, new_state)
    lang = get_user_lang(call.from_user.id)
    await call.message.edit_reply_markup(
        reply_markup=group_settings_kb(chat_id, new_state, lang)
    )
    status = "yoqildi ✅" if new_state else "o'chirildi ❌"
    await call.answer(f"Auto reaksiya {status}", show_alert=True)

# Reaksiya o'zgartirish (bot chatidan)
@router.callback_query(F.data.startswith("change_react_"))
async def change_react(call: CallbackQuery):
    chat_id = int(call.data.replace("change_react_", ""))
    gr = get_group(chat_id)
    selected = gr[3] if gr else "👍"
    await call.message.edit_text(
        "Yangi reaksiyani tanlang 👇",
        reply_markup=reaction_kb(selected)
    )
