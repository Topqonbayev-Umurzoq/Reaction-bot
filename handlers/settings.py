from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from database import get_user_lang, set_user_lang
from keyboards.inline import lang_kb, main_menu_kb
import json, os

router = Router()

def t(lang, key):
    path = os.path.join("locales", f"{lang}.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get(key, key)

# /settings buyrug'i
@router.message(Command("settings"))
async def cmd_settings(msg: Message):
    lang = get_user_lang(msg.from_user.id)
    await msg.answer(
        t(lang, "settings_menu"),
        reply_markup=lang_kb()
    )

# Til tanlash callback
@router.callback_query(F.data.startswith("setlang_"))
async def set_lang(call: CallbackQuery):
    lang = call.data.split("_")[1]  # uz / ru / en
    set_user_lang(call.from_user.id, lang)
    new_lang = get_user_lang(call.from_user.id)
    await call.answer(t(new_lang, "lang_set"), show_alert=True)
    await call.message.edit_text(
        f"{t(new_lang, 'welcome')}\n\n{t(new_lang, 'your_id').format(id=call.from_user.id)}",
        reply_markup=main_menu_kb(new_lang),
        parse_mode="HTML"
    )
