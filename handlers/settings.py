from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

from config import SUBSCRIBE_CHANNEL
from database import (
    get_user,
    add_user,
    get_user_lang,
    set_user_lang,
    get_user_private_auto_react,
    set_user_private_auto_react,
    get_user_private_active_message_id,
    set_user_private_active_message_id,
    get_setting,
)
from keyboards.inline import lang_kb, settings_menu_kb, subscribe_kb
from handlers.utils import get_subscription_duration_seconds
import json, os
import random
from datetime import datetime, timedelta

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


async def safe_edit_text(message, *args, **kwargs):
    try:
        await message.edit_text(*args, **kwargs)
    except TelegramBadRequest as exc:
        if "message is not modified" not in str(exc):
            raise


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


def get_required_subscribe_channel() -> str:
    channel = get_setting("subscribe_channel") or SUBSCRIBE_CHANNEL
    return channel if channel else ""


def is_subscription_window_active() -> bool:
    channel = get_required_subscribe_channel()
    if not channel:
        return True

    duration_value = get_setting("subscribe_duration_value")
    duration_unit = get_setting("subscribe_duration_unit") or "forever"
    started_at = get_setting("subscribe_started_at")
    if duration_unit == "forever":
        return True
    if not started_at or not duration_value:
        return True

    try:
        started = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    except Exception:
        return True

    seconds = get_subscription_duration_seconds(int(duration_value), duration_unit)
    if not seconds:
        return True
    return datetime.utcnow() < started + timedelta(seconds=seconds)


async def is_user_subscribed(bot, user_id: int) -> bool:
    channel = get_required_subscribe_channel()
    if not channel:
        return True
    if not is_subscription_window_active():
        return True
    try:
        member = await bot.get_chat_member(channel, user_id)
        return member.status not in ("left", "kicked")
    except Exception:
        return False


def t(lang, key):
    path = os.path.join("locales", f"{lang}.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get(key, key)

# /settings buyrug'i
@router.message(Command("settings"))
async def cmd_settings(msg: Message):
    if not get_user(msg.from_user.id):
        add_user(msg.from_user.id, msg.from_user.username, msg.from_user.full_name)
    lang = get_user_lang(msg.from_user.id)
    if msg.chat.type == "private":
        private_auto_react = get_user_private_auto_react(msg.from_user.id)
        sent = await msg.answer(
            t(lang, "settings_menu").format(
                status=t(lang, "private_react_on") if private_auto_react else t(lang, "private_react_off")
            ),
            reply_markup=settings_menu_kb(private_auto_react, lang)
        )
        set_user_private_active_message_id(msg.from_user.id, sent.message_id)
        await react_random(msg.bot, sent.chat.id, sent.message_id)
        return

    sent = await msg.answer(
        t(lang, "choose_lang"),
        reply_markup=lang_kb()
    )
    set_user_private_active_message_id(msg.from_user.id, sent.message_id)


@router.callback_query(F.data == "toggle_private_react")
async def toggle_private_react(call: CallbackQuery):
    if not is_fresh_private_callback(call):
        await call.answer(stale_button_text(), show_alert=True)
        return
    current = get_user_private_auto_react(call.from_user.id)
    new_value = not current
    set_user_private_auto_react(call.from_user.id, new_value)
    lang = get_user_lang(call.from_user.id)
    await safe_edit_text(
        call.message,
        t(lang, "settings_menu").format(
            status=t(lang, "private_react_on") if new_value else t(lang, "private_react_off")
        ),
        reply_markup=settings_menu_kb(new_value, lang)
    )
    await call.answer(t(lang, "private_react_on") if new_value else t(lang, "private_react_off"), show_alert=True)

# Til tanlash callback
@router.callback_query(F.data.startswith("setlang_"))
async def set_lang(call: CallbackQuery):
    lang = call.data.split("_")[1]  # uz / ru / en
    set_user_lang(call.from_user.id, lang)
    new_lang = get_user_lang(call.from_user.id)
    await call.answer(t(new_lang, "lang_set"), show_alert=True)
    if call.message.chat.type == "private":
        private_auto_react = get_user_private_auto_react(call.from_user.id)
        if not await is_user_subscribed(call.bot, call.from_user.id):
            required_channel = get_required_subscribe_channel()
            await safe_edit_text(
                call.message,
                t(new_lang, "sub_required").format(channel=required_channel),
                reply_markup=subscribe_kb(required_channel, new_lang),
                parse_mode="HTML"
            )
            set_user_private_active_message_id(call.from_user.id, call.message.message_id)
            return

        await safe_edit_text(
            call.message,
            t(new_lang, "settings_menu").format(
                status=t(new_lang, "private_react_on") if private_auto_react else t(new_lang, "private_react_off")
            ),
            reply_markup=settings_menu_kb(private_auto_react, new_lang),
        )
        set_user_private_active_message_id(call.from_user.id, call.message.message_id)
        return

    await safe_edit_text(
        call.message,
        t(new_lang, "choose_lang"),
        reply_markup=lang_kb(),
    )
    set_user_private_active_message_id(call.from_user.id, call.message.message_id)
