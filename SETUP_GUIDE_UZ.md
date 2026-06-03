# REAKSIYALAR BOT - TO'LIQ SETUP GUIDE

## 📋 LOYIHANING STRUKTURA

```
reactions-bot/
├── main.py                 # Asosiy bot fayli
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore
├── README.md
├── database/
│   ├── __init__.py
│   ├── db_manager.py      # Database manager sinfi
│   └── schema.sql         # SQL schema
├── config/
│   ├── __init__.py
│   ├── config.py          # Bot konfiguratsiyasi va FSM states
│   └── localization.py    # Til lokalizatsiyasi (UZ, EN, RU)
├── handlers/
│   ├── __init__.py
│   ├── user_handlers.py   # Foydalanuvchi uchun handlers
│   └── admin_handlers.py  # Admin uchun handlers
├── utils/
│   ├── __init__.py
│   ├── keyboards.py       # Klaviaturas va dugmalar
│   └── helpers.py         # Yordamchi funksiyalar
└── logs/
    └── bot.log           # Bot loglari
```

## 🚀 INSTALLATION

### 1️⃣ PYTHON VA GIT
```bash
# Python 3.10+ kerak
python --version

# Git klonlash
git clone https://github.com/yourusername/reactions-bot.git
cd reactions-bot
```

### 2️⃣ VIRTUAL ENVIRONMENT
```bash
# Virtual environment yaratish
python -m venv venv

# Aktivlash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3️⃣ DEPENDENCIES
```bash
# Requirements o'rnatish
pip install -r requirements.txt
```

### 4️⃣ DATABASE SETUP

#### SQLite uchun (Oddiy):
```bash
# Database avtomatik yaratiladi main.py ishga tushganda
python main.py
```

#### PostgreSQL uchun (Production):
```sql
-- PostgreSQL create database
createdb reactions_bot

-- SQL schema import qilish
psql -U postgres -d reactions_bot -f database/schema.sql
```

### 5️⃣ ENVIRONMENT VARIABLES
```bash
# .env.example dan .env yaratish
cp .env.example .env

# .env ni o'zingizning tokenlari bilan to'ldirish
nano .env

# Yoki UNIX:
export BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
export ADMIN_IDS="123456789"
```

## 🤖 BOT TOKENNI QANDAY OLISH?

1. **Telegram ga boqing**: @BotFather
2. **/newbot** yuboring
3. Bot nomini va usernameni kiriting
4. Token olasiz - uni `.env` ga joylashtiring

## 🔧 KONFIGURATSIYA

### config.py
```python
# Admin IDlari o'rnatish
ADMIN_IDS = [123456789, 987654321]

# Database path
DATABASE_PATH = "reactions_bot.db"

# Bot timeout
REQUEST_TIMEOUT = 60
```

### localization.py
Tilda matnlarni o'zingizning kerakli qilib o'zgartirishingiz mumkin:
```python
'start_welcome': {
    'uz': 'Sizning o\'z xabari',
    'en': 'Your message',
    'ru': 'Ваше сообщение'
}
```

## 🏃 BOT ISHGA TUSHIRISH

### Development uchun (Polling):
```bash
python main.py
```

### Production uchun (Webhook):
```python
# main.py da
WEBHOOK_URL = "https://your-domain.com/webhook"
```

## 📊 DATABASE STRUCTURE

### Users Jadvali
```
user_id (PRIMARY KEY)
username
first_name
last_name
language_code (uz/en/ru)
is_admin (BOOLEAN)
created_at
```

### Groups Jadvali
```
group_id (PRIMARY KEY)
group_title
group_type
is_active
```

### Channels Jadvali
```
channel_id (PRIMARY KEY)
channel_title
channel_username
is_force_subscribe
added_by_user (FK)
```

## 🎯 ASOSIY FEATURES

### 1. Til Tanlash
```
/start → Til menyusi → Til tanlandi → Asosiy menyu
```

### 2. Kanallar Boshqarish
```
Kanallar → Kanal qo'shish → ID kiriting → Majburiy obuna
```

### 3. Reaksiyalar
```
Guruh → Reaksiyalarni yoqish → Emoji tanlash → Saqlash
```

### 4. Majburiy Obuna (Force Subscribe)
```
Admin /admin → Majburiy obuna → Kanal qo'shish → Tekshirish
```

### 5. Broadcast
```
/admin → Xabar tarqatish → Matn kiriting → Til filter → Yuborish
```

## 🔒 SECURITY TIPS

1. **Token ni xavfsiz saqlash**: `.env` ni `.gitignore` da qo'y
2. **Admin IDs ni tekshiring**: Faqat ishonchli IDlarni qo'shing
3. **Rate limiting**: Broadcast da delay qo'yilgan
4. **Database backup**: Muntazam backup oling
5. **Logging**: Barcha harakatlar log qilinadi

## 🐛 DEBUGGING

### Logging config
```python
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Log fayllarni ko'rish
```bash
tail -f logs/bot.log
```

## 🚀 DEPLOYMENT

### Docker (Opsional)
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### Docker Compose
```yaml
version: '3'
services:
  bot:
    build: .
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - ADMIN_IDS=${ADMIN_IDS}
    volumes:
      - ./data:/app/data
```

## 📝 CODE STRUCTURE

### Handler yaratish:
```python
@router.message(Command("mycommand"))
async def my_handler(message: types.Message):
    await message.answer("Response")
```

### Database operatsiya:
```python
# Foydalanuvchi qo'shish
await db.add_or_update_user(
    user_id=123,
    username="john",
    language="uz"
)

# Foydalanuvchi olish
user = await db.get_user(123)
```

## 🎓 LEARNING RESOURCES

- **Aiogram docs**: https://docs.aiogram.dev/
- **Telegram Bot API**: https://core.telegram.org/bots/api
- **Python asyncio**: https://docs.python.org/3/library/asyncio.html

## 🤝 CONTRIBUTION

1. Fork qilamiz
2. Feature branch yaratamiz
3. Commit qilamiz
4. Push qilamiz
5. Pull request ochishimiz kerak

## 📄 LICENSE

MIT License - Batafsil: LICENSE fayl

## 📧 SUPPORT

- **Issues**: GitHub Issues
- **Email**: your-email@example.com
- **Telegram**: @your_username

---

**Qat'iy ko'riklar!** 🚀
Bot ishga tushganda, /admin buyrug'i orqali admin panelni tekshiring.
Barcha tizim yo'l-yo'riqlar log qilinadi.
