# 🤖 REAKSIYALAR BOT - Aiogram 3.x

**Professional Telegram Bot** - Emoji Reactions, Multi-language, Force Subscribe

---

## 📌 Features

✅ **Multi-language Localization** (UZ, EN, RU)
✅ **User Panel** - Kanal va Guruh Boshqarish
✅ **Admin Panel** - Statistika, Broadcast, Force Subscribe
✅ **Emoji Reactions** - 70+ Emoji + Premium
✅ **Force Subscribe** - Majburiy obuna tekshirish
✅ **Broadcast System** - Til filtr bilan xabar tarqatish
✅ **FSM (Finite State Machine)** - Turli holatlarni boshqarish
✅ **SQLite/PostgreSQL** - Fully async database
✅ **Clean Code** - Modular va tushunarli struktura
✅ **Logging & Monitoring** - Barcha harakatlar log qilinadi

---

## 🏗️ Architecture

### Database Sxemasi

```
┌─────────────────────────────────┐
│         USERS JADVALI           │
├─────────────────────────────────┤
│ user_id (PK)                   │
│ username, first_name           │
│ language_code (uz/en/ru)       │
│ is_admin, is_blocked           │
│ created_at, updated_at         │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│       CHANNELS JADVALI          │
├─────────────────────────────────┤
│ channel_id (PK)                │
│ channel_title, username        │
│ is_force_subscribe             │
│ added_by_user (FK)             │
└─────────────────────────────────┘

┌──────────────────────────────────┐
│    GROUP_REACTIONS JADVALI       │
├──────────────────────────────────┤
│ group_id (PK)                   │
│ is_reactions_enabled            │
│ allowed_reactions (JSON)        │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│   BROADCAST_HISTORY JADVALI      │
├──────────────────────────────────┤
│ id (PK)                         │
│ admin_id (FK)                   │
│ message_text                    │
│ language_filter                 │
│ successful, failed              │
└──────────────────────────────────┘
```

### Handlers Flow

```
/start
  ├─→ Til tanlash (Language Selection)
  │   └─→ UserStates.selecting_language
  │
  └─→ Asosiy menyu (Main Menu)
      ├─→ ⚙️ Kanallar (Channels)
      ├─→ 👥 Guruhlar (Groups)
      ├─→ ℹ️ Qo'llanma (Guide)
      └─→ 📊 Statistika (Statistics)

/admin (Faqat adminlar)
  ├─→ Admin paneli
  ├─→ 📊 Statistika
  ├─→ 📌 Majburiy obuna
  ├─→ 📢 Broadcast
  └─→ 👥 Foydalanuvchilar boshqarish
```

---

## 🚀 Installation

### System Requirements
- Python 3.10+
- pip (Python package manager)
- SQLite3 (yoki PostgreSQL)

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/reactions-bot.git
cd reactions-bot
```

### Step 2: Virtual Environment
```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration
```bash
cp .env.example .env
# .env ni o'zingizning tokenlari bilan to'ldiring
nano .env
```

### Step 5: Run Bot
```bash
python main.py
```

---

## 📁 Project Structure

```
reactions-bot/
│
├── main.py                      # Asosiy entry point
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker configuration
├── docker-compose.yml           # Docker Compose
├── .env.example                 # Environment template
│
├── database/
│   ├── __init__.py
│   ├── db_manager.py           # AsyncIO Database Manager
│   └── schema.sql              # SQL Sxema
│
├── config/
│   ├── __init__.py
│   ├── config.py               # Config + FSM States
│   └── localization.py         # 3 ta tilda lokalizatsiya
│
├── handlers/
│   ├── __init__.py
│   ├── user_handlers.py        # Foydalanuvchi handlers
│   └── admin_handlers.py       # Admin handlers
│
├── utils/
│   ├── __init__.py
│   └── helpers.py              # Yordamchi funksiyalar
│
├── logs/
│   └── bot.log                 # Bot loglari
│
└── data/
    └── reactions_bot.db        # SQLite Database
```

---

## 🔧 Configuration

### Bot Token
```bash
# @BotFather ga boqing
/newbot → Token oling → .env ga joylashtiring
```

### Admin IDs
```env
ADMIN_IDS=123456789,987654321
```

### Database
```env
# SQLite (default)
DATABASE_PATH=reactions_bot.db

# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/reactions_bot
```

### Logging
```python
# config.py
LOG_LEVEL=INFO
```

---

## 🎯 Bot Commands

### User Commands
```
/start      - Botni ishga tushirish va til tanlash
/help       - Yordam va qo'llanma
/settings   - Sozlamalar
```

### Admin Commands
```
/admin      - Admin paneli (faqat adminlar)
```

---

## 🌐 Localization (3 til)

### Qo'llab-quvatilgan Tillar:
- 🇺🇿 **O'zbekcha** (uz)
- 🇬🇧 **English** (en)  
- 🇷🇺 **Русский** (ru)

### Tilni qanday qo'shish:

```python
# localization.py
LOCALIZATION = {
    'my_text_key': {
        'uz': 'O\'zbek matni',
        'en': 'English text',
        'ru': 'Русский текст'
    }
}

# Handler da
text = get_text('my_text_key', language)
```

---

## 💾 Database Operations

### Foydalanuvchi qo'shish
```python
await db.add_or_update_user(
    user_id=message.from_user.id,
    username=message.from_user.username,
    first_name=message.from_user.first_name,
    language="uz"
)
```

### Foydalanuvchi olish
```python
user = await db.get_user(user_id)
language = user['language_code']
```

### Statistika yangilash
```python
await db.update_statistics()
stats = await db.get_statistics()
```

### Broadcast yuborish
```python
users = await db.get_all_users(language='uz')  # Filtr bilan
for user in users:
    await message.bot.send_message(user['user_id'], text)
```

---

## 🤖 FSM (Finite State Machine)

### User States
```python
class UserStates(StatesGroup):
    selecting_language = State()
    selecting_channel = State()
    add_channel = State()
    manage_reactions = State()
```

### Admin States
```python
class AdminStates(StatesGroup):
    admin_menu = State()
    broadcast_message = State()
    manage_force_subscribe = State()
```

### State bilan handler
```python
@router.message(StateFilter(UserStates.selecting_language))
async def handle_language(message: types.Message, state: FSMContext):
    await state.clear()  # State tozalash
```

---

## 📊 Features Detail

### 1. Multi-language System
```
User /start → Language selection menu
→ Choose language (uz/en/ru)
→ Save to database
→ All messages in selected language
```

### 2. User Panel
```
⚙️ Channels      → Kanal qo'shish/o'chirish
👥 Groups        → Reaksiyalarni sozlash
ℹ️ Guide         → Qo'llanma videolari
📊 Statistics    → Bot statistikasi
```

### 3. Admin Panel
```
📊 Statistics           → Real-time statistika
📌 Force Subscribe      → Majburiy obuna kanallar
📢 Broadcast            → Xabar tarqatish (til filtr bilan)
👥 User Management     → Foydalanuvchilar boshqarish
```

### 4. Emoji Reactions
```
73 ta default emoji ✅
Premium emoji qo'shimcha ✨
Guruh bilan customize qilish 🎯
```

### 5. Force Subscribe
```
Admin /admin → Majburiy obuna → Kanal qo'shish
User botdan foydalanish → Subscribe tekshirish → Access
```

### 6. Broadcast System
```
Message content → Language filter (uz/en/ru/all) → Send
Progress tracking (X/total) → Success/Failed reporting
```

---

## 🔐 Security Features

✅ **Admin verification** - Faqat admin IDs
✅ **User blocking** - Spam users va rule breakers
✅ **Rate limiting** - Broadcast da delay
✅ **SQL injection prevention** - Parametrized queries
✅ **Async operations** - Blocking operatsiyasiz
✅ **Logging all actions** - Audit trail
✅ **Database encryption** - Token va sensitive data

---

## 📈 Monitoring & Logging

### Log levels
```
DEBUG   - Development ma'lumotlari
INFO    - Muhim voqealar
WARNING - Ogohlantirishlar
ERROR   - Xatolar
```

### Log example
```
2024-01-15 10:30:45,123 - handlers.user_handlers - INFO - User 123456789 selected language: uz
2024-01-15 10:31:12,456 - handlers.admin_handlers - INFO - Admin 987654321 accessed admin panel
```

---

## 🚀 Deployment

### Local Development
```bash
python main.py
# Polling mode
```

### Production (Webhook)
```python
# main.py da webhook_setup() qilish
WEBHOOK_URL = "https://your-domain.com/webhook"
```

### Docker
```bash
# Build
docker build -t reactions-bot .

# Run
docker run -e BOT_TOKEN=xxx reactions-bot

# Docker Compose
docker-compose up -d
```

### Systemd Service (Linux)
```ini
[Unit]
Description=Reactions Bot
After=network.target

[Service]
Type=simple
User=bot
WorkingDirectory=/home/bot/reactions-bot
ExecStart=/home/bot/reactions-bot/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 🐛 Troubleshooting

### "BOT_TOKEN not found"
```bash
# .env fayli bilan tekshiring
cat .env
# BOT_TOKEN=xxx qatorini qo'shing
```

### Database locked
```bash
# SQLite concurrent access masalasi
# Yechim: SQLite WAL mode yoqish (config.py)
```

### Memory leak
```bash
# Monitor RAM
docker stats reactions_bot

# Yechim: Event loop proper cleanup
```

### Timeout error
```bash
# Network connectivity tekshiring
# REQUEST_TIMEOUT qiymatini ko'paytiring
```

---

## 📚 Code Examples

### Simple Handler
```python
@router.message(Command("hello"))
async def hello(message: types.Message):
    await message.answer("Assalomu aleykum!")
```

### Handler with State
```python
@router.message(StateFilter(UserStates.add_channel))
async def process_channel(message: types.Message, state: FSMContext):
    channel_id = message.text
    await db.add_channel(channel_id, "Channel", "@username", message.from_user.id)
    await message.answer("✅ Kanal qo'shildi!")
    await state.clear()
```

### Database Operations
```python
# Add user
await db.add_or_update_user(user_id, username, first_name, last_name, language, is_bot)

# Get user
user = await db.get_user(user_id)

# Update language
await db.set_user_language(user_id, "en")

# Get statistics
stats = await db.get_statistics()
```

### Error Handling
```python
try:
    await message.answer(text)
except Exception as e:
    logger.error(f"Error: {e}")
    await message.answer("❌ Xato yuz berdi")
```

---

## 🤝 Contributing

1. **Fork** repository
2. **Create** feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** changes (`git commit -m 'Add AmazingFeature'`)
4. **Push** to branch (`git push origin feature/AmazingFeature`)
5. **Open** Pull Request

---

## 📄 License

MIT License - see LICENSE file

---

## 👨‍💻 Author

**Created by**: Professional Telegram Bot Developer

---

## 📞 Support

- 🐛 **Issues**: GitHub Issues
- 📧 **Email**: support@example.com
- 💬 **Telegram**: @support_username

---

## 🎓 Learning Resources

- [Aiogram Docs](https://docs.aiogram.dev/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Python AsyncIO](https://docs.python.org/3/library/asyncio.html)
- [SQLite](https://www.sqlite.org/docs.html)

---

**Last Updated**: January 2024
**Bot Status**: ✅ Production Ready

---

**Rahmat foydalanganingiz uchun!** 🙏
