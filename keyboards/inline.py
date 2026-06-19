from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import json
import os

def load_lang(lang):
    path = os.path.join("locales", f"{lang}.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)

# /start — asosiy menyu
def main_menu_kb(lang="uz"):
    t = load_lang(lang)
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text=t["btn_channel"], callback_data="type_channel"))
    kb.row(InlineKeyboardButton(text=t["btn_group"], callback_data="type_group"))
    kb.row(InlineKeyboardButton(text=t["btn_video"], url="https://t.me/Reaksiya_News"))
    return kb.as_markup()

# Til tanlash klaviaturasi
def lang_kb():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="setlang_uz"))
    kb.row(InlineKeyboardButton(text="🇬🇧 English", callback_data="setlang_en"))
    kb.row(InlineKeyboardButton(text="🇷🇺 Русский", callback_data="setlang_ru"))
    return kb.as_markup()

def settings_menu_kb(private_auto_react: bool, lang="uz"):
    t = load_lang(lang)
    status = t.get("private_react_on", "✅ Yoqilgan") if private_auto_react else t.get("private_react_off", "❌ O'chirilgan")
    button_label = t.get("private_react_button", "Shaxsiy reaksiya")
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text=f"{button_label}: {status}", callback_data="toggle_private_react"))
    kb.row(InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="setlang_uz"))
    kb.row(InlineKeyboardButton(text="🇬🇧 English", callback_data="setlang_en"))
    kb.row(InlineKeyboardButton(text="🇷🇺 Русский", callback_data="setlang_ru"))
    kb.row(InlineKeyboardButton(text=t["btn_back"], callback_data="back_main"))
    return kb.as_markup()

# Obuna tugmasi
def subscribe_kb(channel, lang="uz"):
    t = load_lang(lang)
    kb = InlineKeyboardBuilder()
    url = f"https://t.me/{channel.lstrip('@')}"
    kb.row(InlineKeyboardButton(text=t["subscribe_button"], url=url))
    return kb.as_markup()

# Kanal ro'yxati klaviaturasi
def channels_kb(channels: list, lang="uz"):
    t = load_lang(lang)
    kb = InlineKeyboardBuilder()
    for chat_id, title in channels:
        kb.row(InlineKeyboardButton(text=f"📢 {title}", callback_data=f"ch_{chat_id}"))
    kb.row(InlineKeyboardButton(text=t["btn_add_channel"], callback_data="add_channel"))
    kb.row(InlineKeyboardButton(text=t["btn_back"], callback_data="back_main"))
    return kb.as_markup()

# Guruh ro'yxati klaviaturasi
def groups_kb(groups: list, lang="uz"):
    t = load_lang(lang)
    kb = InlineKeyboardBuilder()
    for chat_id, title in groups:
        kb.row(InlineKeyboardButton(text=f"👥 {title}", callback_data=f"gr_{chat_id}"))
    kb.row(InlineKeyboardButton(text=t["btn_add_group"], callback_data="add_group"))
    kb.row(InlineKeyboardButton(text=t["btn_back"], callback_data="back_main"))
    return kb.as_markup()

# Reaksiya emoji tanlash klaviaturasi
EMOJIS = [
    "👍","❤️","🔥","🥰","👏","😁","🤔","🤯","😱","🤬",
    "😢","🎉","🤩","🤮","💩","🙏","👌","🕊","🤡","🥱",
    "🥴","😍","🐳","❤️‍🔥","🌚","🌭","💯","🤣","⚡","🍌",
    "🏆","💔","🤨","😐","🍓","🍾","💋","🖕","😈","😴",
    "😭","🤓","👻","👨‍💻","👀","🎃","🙈","😇","😨","🤝",
    "✍️","🤗","🫡","🎅","🎄","☃️","💅","🤪","🗿","🆒",
    "💘","🙉","🦄","💊","🙊","😎","👾","🤷","😡"
]

def reaction_kb(selected: str = None, chat_id: int = None, kind: str = "group"):
    kb = InlineKeyboardBuilder()
    row = []
    for i, emoji in enumerate(EMOJIS):
        mark = "✅" if emoji == selected else ""
        row.append(InlineKeyboardButton(
            text=f"{emoji}{mark}",
            callback_data=f"react_{kind}_{chat_id}_{emoji}" if chat_id is not None else f"react_{emoji}"
        ))
        if len(row) == 5:
            kb.row(*row)
            row = []
    if row:
        kb.row(*row)
    random_mark = "✅" if selected == "random" else ""
    kb.row(
        InlineKeyboardButton(text=f"🎲 Random reaksiya{random_mark}", callback_data=f"react_{kind}_{chat_id}_random" if chat_id is not None else "react_random"),
        InlineKeyboardButton(text="Tanlab bo'ldim ✅", callback_data=f"react_{kind}_{chat_id}_done" if chat_id is not None else "react_done")
    )
    return kb.as_markup()

# Guruh sozlamalari
def group_settings_kb(chat_id, auto_react, lang="uz"):
    t = load_lang(lang)
    status = "✅ Yoqilgan" if auto_react else "❌ O'chirilgan"
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text=f"Auto reaksiya: {status}", callback_data=f"toggle_auto_{chat_id}"))
    kb.row(InlineKeyboardButton(text="🎭 Reaksiyani o'zgartirish", callback_data=f"change_react_{chat_id}"))
    kb.row(InlineKeyboardButton(text=t["btn_back"], callback_data="type_group"))
    return kb.as_markup()

# Kanal sozlamalari
def channel_settings_kb(chat_id, auto_react, lang="uz"):
    t = load_lang(lang)
    status = "✅ Yoqilgan" if auto_react else "❌ O'chirilgan"
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text=f"Auto reaksiya: {status}", callback_data=f"toggle_ch_auto_{chat_id}"))
    kb.row(InlineKeyboardButton(text="🎭 Reaksiyani o'zgartirish", callback_data=f"change_ch_react_{chat_id}"))
    kb.row(InlineKeyboardButton(text=t["btn_back"], callback_data="type_channel"))
    return kb.as_markup()

# Admin panel
def admin_kb(is_root: bool = False):
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users"),
        InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")
    )
    kb.row(
        InlineKeyboardButton(text="📨 Xabar yuborish", callback_data="admin_broadcast"),
        InlineKeyboardButton(text="🚫 Bloklash", callback_data="admin_block")
    )
    kb.row(
        InlineKeyboardButton(text="✅ Blokdan chiqarish", callback_data="admin_unblock"),
        InlineKeyboardButton(text="📋 Bloklangan", callback_data="admin_view_blocked")
    )
    kb.row(InlineKeyboardButton(text="🤖 Botlar", callback_data="admin_bots"))
    if is_root:
        kb.row(
            InlineKeyboardButton(text="➕ Yangi bot", callback_data="admin_new_bot"),
            InlineKeyboardButton(text="➕ Admin qo'shish", callback_data="admin_add")
        )
        kb.row(InlineKeyboardButton(text="👑 Adminlar", callback_data="admin_admins"))
    kb.row(InlineKeyboardButton(text="➕ Majburiy obuna", callback_data="admin_sub"))
    return kb.as_markup()

# Orqaga tugmasi
def back_kb(callback="back_main"):
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="↩️ Orqaga", callback_data=callback))
    return kb.as_markup()


def invite_link_kb(url: str, back_callback: str = "back_main", label: str = "➕ Qo‘shish"):
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text=label, url=url))
    kb.row(InlineKeyboardButton(text="↩️ Orqaga", callback_data=back_callback))
    return kb.as_markup()
