# 🚀 ADVANCED FEATURES GUIDE

## 1. FORCE SUBSCRIBE MECHANISM

### Asosiy Logika
```
User /start
    ↓
Tekshir: Force subscribe channellar bor mi?
    ↓ YES
Ko'rsatish: Subscribe qilish kerak bo'lgan kanallar
    ↓
User "✅ Obunani tekshirish" bosadi
    ↓
Bot tekshiradi: User barcha kanallarga obunalangan mi?
    ↓ NO → Qayta message
    ↓ YES → Access berish
```

### Kod Misoli
```python
async def check_force_subscribe(user_id: int) -> bool:
    """Force subscribe tekshirish"""
    force_channels = await db.get_force_subscribe_channels()
    
    if not force_channels:
        return True  # Majburiy obuna yo'q
    
    for channel_id in force_channels:
        # Tekshir: user obunalangan mi?
        if not await db.is_user_subscribed(user_id, channel_id):
            return False
    
    return True

# Handler da
@router.callback_query(F.data == "verify_subscription")
async def verify_subscription(query: types.CallbackQuery):
    is_subscribed = await check_force_subscribe(query.from_user.id)
    
    if is_subscribed:
        await query.message.edit_text("✅ Siz barcha kanallarga obunasiz!")
    else:
        channels = await db.get_force_subscribe_channels()
        message = format_force_subscribe_message(channels)
        await query.message.edit_text(message)
```

## 2. BROADCAST SISTEMA OPTIMIZATSIYA

### Parallel Broadcasting
```python
import asyncio

async def optimized_broadcast(users: list, message: str, batch_size: int = 50):
    """Batch da xabar yuborish"""
    total = len(users)
    successful = 0
    failed = 0
    
    # Batches ga bo'lish
    for i in range(0, total, batch_size):
        batch = users[i:i + batch_size]
        
        # Parallel yuborish
        tasks = [
            send_message_safe(user['user_id'], message)
            for user in batch
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                failed += 1
            else:
                successful += 1
    
    return successful, failed

async def send_message_safe(user_id: int, text: str) -> bool:
    """Xavfsiz xabar yuborish"""
    try:
        await bot.send_message(user_id, text)
        return True
    except Exception as e:
        logger.warning(f"Failed to send to {user_id}: {e}")
        return False
```

### Rate Limiting
```python
from aiogram import types
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests: int = 30, window: int = 60):
        self.max_requests = max_requests
        self.window = window
        self.requests = {}
    
    async def check(self, user_id: int) -> bool:
        """Rate limit tekshirish"""
        now = datetime.now()
        
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Eski so'rovlarni o'chirish
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if (now - req_time).seconds < self.window
        ]
        
        if len(self.requests[user_id]) >= self.max_requests:
            return False
        
        self.requests[user_id].append(now)
        return True

# Usage
rate_limiter = RateLimiter(max_requests=30, window=60)

@router.message()
async def check_rate_limit(message: types.Message):
    if not await rate_limiter.check(message.from_user.id):
        await message.answer("⏰ Juda tez so'rov! Biroz kutib ko'ring.")
        return
```

## 3. EMOJI REACTIONS ADVANCED

### Dinamik Reaksiya Tugmalari
```python
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

async def get_reactions_keyboard(group_id: int) -> InlineKeyboardMarkup:
    """Guruhning reaksiya tugmalarini olish"""
    settings = await db.get_group_reaction_settings(group_id)
    
    if not settings or not settings['is_reactions_enabled']:
        return None
    
    reactions = settings.get('allowed_reactions', '[]')
    import json
    reactions_list = json.loads(reactions) if isinstance(reactions, str) else []
    
    if not reactions_list:
        # Default reactions
        reactions_list = await db.get_all_reactions(include_premium=False)
    
    # Tugmalarni yaratish
    buttons = []
    row = []
    
    for i, emoji in enumerate(reactions_list[:20]):  # Max 20 emoji
        button = InlineKeyboardButton(
            text=emoji,
            callback_data=f"react_{group_id}_{emoji}"
        )
        row.append(button)
        
        if (i + 1) % 5 == 0:  # 5 ta emoji bir qatorada
            buttons.append(row)
            row = []
    
    if row:
        buttons.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Xabarning ostiga reaksiya tugmalari qo'shish
@router.message()
async def add_reactions(message: types.Message):
    if message.chat.type != "group":
        return
    
    kb = await get_reactions_keyboard(message.chat.id)
    if kb:
        await message.answer(
            "Reaksiya berish uchun emoji-ni tanlang:",
            reply_markup=kb
        )
```

### Reaction Counter
```python
from collections import defaultdict

class ReactionCounter:
    def __init__(self):
        self.reactions = defaultdict(lambda: defaultdict(list))
    
    async def add_reaction(self, message_id: int, emoji: str, user_id: int):
        """Reaksiya qo'shish"""
        self.reactions[message_id][emoji].append(user_id)
    
    async def get_reactions(self, message_id: int) -> dict:
        """Xabarning reaksiyalarini olish"""
        return dict(self.reactions.get(message_id, {}))
    
    async def get_reaction_summary(self, message_id: int) -> str:
        """Reaksiya summeri"""
        reactions = await self.get_reactions(message_id)
        
        summary = "Reaksiyalar:\n"
        for emoji, users in reactions.items():
            summary += f"{emoji} x{len(users)} "
        
        return summary

reaction_counter = ReactionCounter()
```

## 4. DATABASE CACHING

### In-Memory Cache
```python
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class Cache:
    def __init__(self, ttl: int = 3600):
        self.ttl = ttl
        self.cache: Dict[str, tuple] = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """Cache dan olish"""
        if key not in self.cache:
            return None
        
        value, expires_at = self.cache[key]
        
        if datetime.now() > expires_at:
            del self.cache[key]
            return None
        
        return value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Cache ga saqlash"""
        ttl = ttl or self.ttl
        expires_at = datetime.now() + timedelta(seconds=ttl)
        self.cache[key] = (value, expires_at)
    
    async def delete(self, key: str):
        """Cache dan o'chirish"""
        if key in self.cache:
            del self.cache[key]
    
    async def clear(self):
        """Cache tozalash"""
        self.cache.clear()

# Usage
cache = Cache(ttl=3600)

async def get_user_with_cache(user_id: int):
    """Cache bilan foydalanuvchi olish"""
    cache_key = f"user_{user_id}"
    
    # Cache-dan tekshir
    cached_user = await cache.get(cache_key)
    if cached_user:
        return cached_user
    
    # Database-dan olish
    user = await db.get_user(user_id)
    
    # Cache-ga saqlash
    if user:
        await cache.set(cache_key, user)
    
    return user
```

## 5. MULTI-LANGUAGE DYNAMIC LOADING

### Tillarni Dinamik Yuklash
```python
import json
from pathlib import Path

class LocalizationManager:
    def __init__(self, locales_dir: str = "locales"):
        self.locales_dir = Path(locales_dir)
        self.languages = {}
    
    async def load_all(self):
        """Barcha tillarni yuklash"""
        for lang_file in self.locales_dir.glob("*.json"):
            lang_code = lang_file.stem
            
            with open(lang_file, 'r', encoding='utf-8') as f:
                self.languages[lang_code] = json.load(f)
    
    async def get_text(self, key: str, language: str, **kwargs) -> str:
        """Matn olish"""
        try:
            text = self.languages[language].get(key, '')
            
            if kwargs:
                text = text.format(**kwargs)
            
            return text
        except KeyError:
            return f"[Missing: {key}]"
    
    async def get_available_languages(self) -> dict:
        """Mavjud tillarni olish"""
        return {
            code: self.languages[code].get('__language_name__', code)
            for code in self.languages.keys()
        }

# JSON file structure: locales/uz.json
# {
#   "__language_name__": "O'zbekcha",
#   "welcome": "Assalomu aleykum!",
#   "goodbye": "Xayr!"
# }
```

## 6. ERROR HANDLING & RECOVERY

### Robust Error Handler
```python
class BotErrorHandler:
    def __init__(self):
        self.error_counts = defaultdict(int)
    
    async def handle_error(self, update: types.Update, error: Exception):
        """Xatoliklarni qayta ishlash"""
        logger.error(f"Error occurred: {error}")
        logger.error(f"Update: {update}")
        
        # Error statistikasi
        error_type = type(error).__name__
        self.error_counts[error_type] += 1
        
        # Critical errors
        if isinstance(error, asyncio.TimeoutError):
            logger.critical(f"Timeout error: {error}")
        
        elif isinstance(error, Exception):
            # User ga xabar yuborish
            if update.message:
                try:
                    await update.message.answer(
                        "❌ Xato yuz berdi. Admin ga xabar yuborildi."
                    )
                except:
                    pass
    
    def get_error_stats(self) -> dict:
        """Error statistikasi"""
        return dict(self.error_counts)

error_handler = BotErrorHandler()
```

## 7. PERFORMANCE MONITORING

### Bot Performance Metrics
```python
from time import time
from statistics import mean, stdev

class PerformanceMonitor:
    def __init__(self):
        self.response_times = []
        self.database_times = []
    
    async def measure_response_time(self, operation_name: str):
        """Javob vaqtini o'lchash"""
        start = time()
        
        async def decorator(func):
            result = await func()
            duration = time() - start
            
            self.response_times.append(duration)
            logger.info(f"{operation_name} took {duration:.2f}s")
            
            return result
        
        return decorator
    
    def get_stats(self) -> dict:
        """Statistika"""
        if not self.response_times:
            return {}
        
        return {
            "avg_response_time": mean(self.response_times),
            "max_response_time": max(self.response_times),
            "min_response_time": min(self.response_times),
            "total_requests": len(self.response_times)
        }

monitor = PerformanceMonitor()
```

## 8. SCHEDULED TASKS

### Cron-like Task Scheduling
```python
import asyncio
from datetime import datetime, timedelta

class TaskScheduler:
    def __init__(self):
        self.tasks = {}
    
    async def schedule_task(self, name: str, interval: int, func, args=None):
        """Vazifani jadvalga qo'shish"""
        async def task_loop():
            while True:
                try:
                    if args:
                        await func(*args)
                    else:
                        await func()
                except Exception as e:
                    logger.error(f"Scheduled task {name} error: {e}")
                
                await asyncio.sleep(interval)
        
        task = asyncio.create_task(task_loop())
        self.tasks[name] = task
    
    async def stop_task(self, name: str):
        """Vazifani to'xtattish"""
        if name in self.tasks:
            self.tasks[name].cancel()
            del self.tasks[name]

scheduler = TaskScheduler()

# Usage
async def daily_cleanup():
    """Kunlik o'chirish"""
    logger.info("Running daily cleanup...")
    # ... cleanup logic

# Bot startup-da
await scheduler.schedule_task("daily_cleanup", 86400, daily_cleanup)
```

---

**Bu advanced features-lar sizning bot-ni enterprise-level qo'lga keltiradi!** 🚀
