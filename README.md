# Telegram Reaction Bot 🤖

Telegram guruh va kanallarga avtomatik reaksiya qo'shaydigan bot.

## Xususiyatlari ✨

- ✅ Avtomatik reaksiya qo'shish
- 📊 Reaksiya statistikasi
- 🎯 Kanallar va guruhlarga to'liq qo'llab-quvvatlash
- ⚙️ Oson sozlash va boshqarish

## O'rnatish 📦

### 1. Python o'rnatish
Python 3.8+ o'rnatilganligini tekshiring:
```bash
python --version
```

### 2. Paketlarni o'rnatish
```bash
pip install -r requirements.txt
```

### 3. Bot tokenini olish
1. Telegramda [@BotFather](https://t.me/botfather) bilan chat ochish
2. `/newbot` buyrug'ini yuboring
3. Bot nomini va foydalanuvchi nomini kiriting
4. Olgan tokeni .env faylga qo'ying

### 4. .env faylini sozlash
`.env` faylini ochib, bot tokenini qo'ying:
```
BOT_TOKEN=your_bot_token_here
```

## Ishga tushirish 🚀

```bash
python main.py
```

## Buyruqlar 📝

- `/start` - Botni boshlash
- `/help` - Yordam olish
- `/reactions` - Mavjud reaksiyalar
- `/stats` - Bot statistikasi

## Konfiguratsiya ⚙️

`config.py` faylida quyidagilarni o'zgartirishingiz mumkin:

```python
# Standart reaksiyalar
DEFAULT_REACTIONS = ['👍', '❤️', '🔥', '😂', '😢', '🎉', '👏', '✅']

# Avtomatik reaksiyalarni yoqish/o'chirish
ENABLE_AUTO_REACTIONS = True

# Faqat admin buyruqlarini yoqish
ADMIN_ONLY = False
```

## Foydalanish 💡

1. Bot qo'shilgan guruhlarda avtomatik reaksiya qo'shishni boshlaydi
2. Quyidagi reaksiyalardan iborat:
   - 👍 Thumbs up
   - ❤️ Heart
   - 🔥 Fire
   - 😂 Laughing
   - 😢 Sad
   - 🎉 Celebration
   - 👏 Clapping
   - ✅ Check mark

## Muammolarni hal qilish 🔧

**Bot reaksiya qo'sha olmayapti:**
- Bot guruhga qo'shilganligini tekshiring
- Botga reaksiya qo'shish ruxsati berilganligini tekshiring
- Telegram Bot API versiyasini tekshiring (5.4+ zarur)

**Token xatosi:**
- `.env` faylida tokenni tekshiring
- Token to'g'ri kiritilganligini tekshiring

## Kerakli ruxsatlar 🔐

Botga quyidagi ruxsatlarni bering:

- ✅ Xabarlarni o'qish
- ✅ Reaksiya qo'shish
- ✅ Guruh statistikasini olish

## Teknikal ma'lumotlar 🛠️

- **Til**: Python 3.8+
- **Kutubxona**: python-telegram-bot
- **API**: Telegram Bot API 5.4+

## Litsenziya 📄

MIT License

## Qo'llab-quvvatlash 💬

Muammolar uchun issue ochish yoki PR yuborish mumkin.
