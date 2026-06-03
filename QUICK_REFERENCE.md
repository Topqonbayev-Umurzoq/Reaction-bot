# ⚡ REAKSIYALAR BOT - QUICK REFERENCE GUIDE

## 🚀 30 SECONDS START

```bash
# 1. Dependencies
pip install -r requirements.txt

# 2. Configure
export BOT_TOKEN="your_token_here"

# 3. Run
python main.py
```

---

## 📖 COMMAND REFERENCE

### User Commands
```
/start       → Bot start, language selection
/help        → Help & guide
/settings    → User settings
```

### Admin Commands
```
/admin       → Admin panel (admin only)
```

### Keyboard Options
```
⚙️ Channels          → Manage channels
👥 Groups            → Configure reactions
ℹ️ Guide             → Video guide
📊 Statistics        → Bot stats
⬅️ Back              → Return to menu
```

---

## 🎯 HANDLER EXAMPLES

### Simple Handler (Greeting)
```python
@router.message(Command("hello"))
async def hello(message: types.Message):
    await message.answer("Assalomu aleykum! 👋")
```

### Handler with Language
```python
@router.message(F.text == "Hi")
async def hello_en(message: types.Message):
    user = await db.get_user(message.from_user.id)
    lang = user['language_code']
    text = get_text('welcome', lang)
    await message.answer(text)
```

### Handler with State
```python
@router.message(StateFilter(UserStates.add_channel))
async def add_channel_handler(message: types.Message, state: FSMContext):
    channel_id = message.text
    await db.add_channel(channel_id, "Ch", "@user_id", message.from_user.id)
    await message.answer("✅ Added!")
    await state.clear()
```

### Admin Handler
```python
@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if not await is_admin(message.from_user.id):
        await message.answer("❌ Admin only!")
        return
    
    await message.answer("Welcome to Admin Panel")
```

---

## 💾 DATABASE OPERATIONS

### User Operations
```python
# Add/Update user
await db.add_or_update_user(user_id, username, first_name, last_name, "uz")

# Get user
user = await db.get_user(user_id)

# Set language
await db.set_user_language(user_id, "en")

# Get all users
users = await db.get_all_users()

# Get users by language
uz_users = await db.get_all_users(language='uz')

# Count users
count = await db.count_users()

# Admin operations
await db.set_admin(user_id, is_admin=True)
admin_ids = await db.get_admin_ids()
```

### Channel Operations
```python
# Add channel
await db.add_channel(channel_id, "Ch Title", "@username", admin_id)

# Get channel
channel = await db.get_channel(channel_id)

# Remove channel
await db.remove_channel(channel_id)

# Get all channels
channels = await db.get_all_channels()

# Count channels
count = await db.count_channels()
```

### Group Reactions
```python
# Get reactions
settings = await db.get_group_reaction_settings(group_id)

# Update reactions
await db.update_group_reactions(group_id, True, '["❤️", "👍"]')

# Get all reactions
reactions = await db.get_all_reactions()

# With premium
reactions_premium = await db.get_all_reactions(include_premium=True)
```

### Force Subscribe
```python
# Add force channel
await db.add_force_subscribe_channel(channel_id)

# Remove from force
await db.remove_force_subscribe_channel(channel_id)

# Get force channels
channels = await db.get_force_subscribe_channels()

# Check subscription
is_subscribed = await db.is_user_subscribed(user_id, channel_id)

# Add subscription
await db.add_subscription(user_id, channel_id)
```

### Statistics
```python
# Get statistics
stats = await db.get_statistics()
# Output: {total_users, total_groups, total_channels, ...}

# Update statistics
await db.update_statistics()
```

### Logging
```python
# Add log
await db.add_log(user_id, "action_name", "Details...")

# Example logs
await db.add_log(user_id, "language_selection", "Selected: uz")
await db.add_log(user_id, "broadcast", "Sent message to 100 users")
```

---

## 🎨 KEYBOARD EXAMPLES

### Simple Keyboard
```python
buttons = [
    [KeyboardButton(text="Button 1")],
    [KeyboardButton(text="Button 2")],
    [KeyboardButton(text="Button 3")]
]
kb = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
await message.answer("Choose:", reply_markup=kb)
```

### Inline Keyboard
```python
buttons = [
    [InlineKeyboardButton(text="Click", callback_data="action_1")],
    [InlineKeyboardButton(text="Link", url="https://google.com")]
]
kb = InlineKeyboardMarkup(inline_keyboard=buttons)
await message.answer("Choose:", reply_markup=kb)
```

### Dynamic Keyboard
```python
buttons = []
for lang in LANGUAGES:
    buttons.append([
        InlineKeyboardButton(
            text=LANGUAGES[lang],
            callback_data=f"lang_{lang}"
        )
    ])
kb = InlineKeyboardMarkup(inline_keyboard=buttons)
```

---

## 🌍 LOCALIZATION

### Adding Text
```python
LOCALIZATION['my_key'] = {
    'uz': 'O\'zbek matn',
    'en': 'English text',
    'ru': 'Русский текст'
}
```

### Using Text
```python
# Simple
text = get_text('my_key', 'uz')

# With formatting
text = get_text('greeting', lang, name="John")
# In localization.py: 'greeting': {'uz': 'Salom {name}!'}
```

### Add New Language
```python
# 1. Add to LANGUAGES
LANGUAGES['fr'] = '🇫🇷 Français'

# 2. Add to LOCALIZATION
LOCALIZATION['start_welcome']['fr'] = 'Bienvenue...'

# 3. Done!
```

---

## 🔧 FSM STATE MANAGEMENT

### Set State
```python
await state.set_state(UserStates.add_channel)
```

### Get Data
```python
data = await state.get_data()
value = data.get('key')
```

### Update Data
```python
await state.update_data(key='value')
```

### Clear State
```python
await state.clear()
```

### Check State
```python
@router.message(StateFilter(UserStates.add_channel))
async def handle_state(message: types.Message):
    # This runs only in add_channel state
    pass
```

---

## 🚨 ERROR HANDLING

### Try-Catch
```python
try:
    await message.answer("Message")
except Exception as e:
    logger.error(f"Error: {e}")
    await message.answer("❌ Error occurred")
```

### Specific Errors
```python
try:
    await db.add_user(...)
except asyncio.TimeoutError:
    logger.error("Database timeout")
except Exception as e:
    logger.error(f"Unknown error: {e}")
```

### Safe Message Send
```python
try:
    await bot.send_message(user_id, "Hello")
except Exception as e:
    logger.warning(f"Failed to send: {e}")
    # Continue...
```

---

## 📊 STATISTICS

### Get Statistics
```python
stats = await db.get_statistics()

total_users = stats['total_users']
total_groups = stats['total_groups']
total_channels = stats['total_channels']
```

### Display Statistics
```python
stats_text = f"""
📊 STATISTICS
👥 Users: {stats['total_users']}
👥 Groups: {stats['total_groups']}
📢 Channels: {stats['total_channels']}
"""
await message.answer(stats_text)
```

---

## 🎯 BROADCAST

### Simple Broadcast
```python
users = await db.get_all_users()

for user in users:
    try:
        await bot.send_message(user['user_id'], "Message")
    except Exception as e:
        logger.warning(f"Failed: {e}")
```

### Broadcast with Language Filter
```python
users = await db.get_all_users(language='uz')

for user in users:
    await bot.send_message(user['user_id'], "O'zbekchada xabar")
```

### Broadcast with Progress
```python
total = len(users)
status_msg = await message.answer(f"Sending... (0/{total})")

for i, user in enumerate(users):
    await bot.send_message(user['user_id'], text)
    
    if (i + 1) % 10 == 0:
        await status_msg.edit_text(f"Sending... ({i+1}/{total})")
```

---

## 🔐 SECURITY

### Check Admin
```python
async def is_admin(user_id: int) -> bool:
    user = await db.get_user(user_id)
    return user['is_admin'] if user else False

if not await is_admin(user_id):
    await message.answer("❌ Admin only!")
    return
```

### Rate Limiting
```python
from datetime import datetime, timedelta

user_requests = {}

def can_request(user_id: int) -> bool:
    if user_id not in user_requests:
        user_requests[user_id] = []
    
    now = datetime.now()
    user_requests[user_id] = [
        t for t in user_requests[user_id]
        if (now - t).seconds < 60
    ]
    
    if len(user_requests[user_id]) > 30:
        return False
    
    user_requests[user_id].append(now)
    return True
```

### Input Validation
```python
@router.message()
async def validate_input(message: types.Message):
    if len(message.text) > 1000:
        await message.answer("❌ Message too long")
        return
    
    if not message.text.strip():
        await message.answer("❌ Empty message")
        return
```

---

## 🔍 DEBUGGING

### Logging
```python
import logging
logger = logging.getLogger(__name__)

logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.debug("Debug message")
```

### Check Database
```python
# Test connection
try:
    user = await db.get_user(123)
    print(f"✅ Database OK: {user}")
except Exception as e:
    print(f"❌ Database Error: {e}")
```

### Bot Info
```python
me = await bot.get_me()
print(f"Bot: {me.first_name} (@{me.username})")
print(f"ID: {me.id}")
```

---

## 📋 DEPLOYMENT CHECKLIST

- [ ] `.env` file configured
- [ ] BOT_TOKEN added
- [ ] ADMIN_IDS set
- [ ] DATABASE_PATH correct
- [ ] requirements.txt installed
- [ ] main.py runs without errors
- [ ] Database initialized
- [ ] All handlers registered
- [ ] Logging configured
- [ ] Error handling in place
- [ ] Ready for production

---

## 🆘 COMMON ISSUES

### Bot token invalid
```
❌ Error: Unauthorized
✅ Solution: Check .env, use correct token from @BotFather
```

### Database locked
```
❌ Error: database is locked
✅ Solution: SQLite uses locks, use WAL mode or PostgreSQL
```

### Handler not triggered
```
❌ Handler not running
✅ Solution: Check @router is registered in main.py
```

### State not working
```
❌ State not changing
✅ Solution: Use StateFilter, check state names
```

### Message not sending
```
❌ Message failed
✅ Solution: Check user_id, bot permissions, try-catch errors
```

---

## 📚 FILE STRUCTURE QUICK REF

```
reactions-bot/
├── main.py                 ← START HERE
├── config/
│   ├── config.py          ← Bot & FSM config
│   └── localization.py    ← Languages (3 ta til)
├── database/
│   ├── db_manager.py      ← Database operations
│   └── schema.sql         ← Database structure
├── handlers/
│   ├── user_handlers.py   ← User features
│   └── admin_handlers.py  ← Admin features
├── requirements.txt       ← Dependencies
├── .env                   ← Tokens & config (create from .env.example)
└── Dockerfile             ← Docker setup
```

---

## ✅ WORKFLOW SUMMARY

### Development
```
1. Edit code
2. python main.py
3. Test in Telegram
4. Fix bugs
5. Repeat
```

### Production
```
1. docker-compose up -d
2. docker-compose logs -f bot
3. Monitor & maintain
4. Update when needed
```

---

**Happy coding! 🚀**
