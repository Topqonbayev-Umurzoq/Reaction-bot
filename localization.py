# config/localization.py
# ============================================
# REAKSIYALAR BOT - LOKALIZATSIYA
# ============================================

LANGUAGES = {
    'uz': '🇺🇿 O\'zbekcha',
    'en': '🇬🇧 English',
    'ru': '🇷🇺 Русский'
}

# ============================================
# LOCALIZATION DICTIONARY
# ============================================

LOCALIZATION = {
    # ============ START VA LANG SELECTION ============
    'start_welcome': {
        'uz': '👋 Assalomu aleykum! Reaksiyalar Bot-ga xush kelibsiz!\n\nTil tanlang:',
        'en': '👋 Welcome to Reactions Bot!\n\nPlease select your language:',
        'ru': '👋 Добро пожаловать в бот реакций!\n\nВыберите язык:'
    },
    'language_selected': {
        'uz': '✅ Til tanlandı: O\'zbekcha',
        'en': '✅ Language selected: English',
        'ru': '✅ Язык выбран: Русский'
    },

    # ============ MAIN MENU ============
    'main_menu': {
        'uz': '📱 Asosiy menyu\n\nQuyidagilardan birini tanlang:',
        'en': '📱 Main Menu\n\nSelect one of the options:',
        'ru': '📱 Главное меню\n\nВыберите один из вариантов:'
    },
    'btn_channels': {
        'uz': '⚙️ Kanallar',
        'en': '⚙️ Channels',
        'ru': '⚙️ Каналы'
    },
    'btn_groups': {
        'uz': '👥 Guruhlar',
        'en': '👥 Groups',
        'ru': '👥 Группы'
    },
    'btn_guide': {
        'uz': 'ℹ️ Qo\'llanma (Video)',
        'en': 'ℹ️ Guide (Video)',
        'ru': 'ℹ️ Руководство (Видео)'
    },
    'btn_stats': {
        'uz': '📊 Statistika',
        'en': '📊 Statistics',
        'ru': '📊 Статистика'
    },
    'btn_settings': {
        'uz': '⚙️ Sozlamalar',
        'en': '⚙️ Settings',
        'ru': '⚙️ Настройки'
    },
    'btn_back': {
        'uz': '⬅️ Orqaga',
        'en': '⬅️ Back',
        'ru': '⬅️ Назад'
    },

    # ============ CHANNELS ============
    'channels_menu': {
        'uz': '⚙️ KANAL BOSHQARISH\n\nQaysi kanalni boshqarmoqchisiz?',
        'en': '⚙️ CHANNEL MANAGEMENT\n\nWhich channel do you want to manage?',
        'ru': '⚙️ УПРАВЛЕНИЕ КАНАЛАМИ\n\nКакой канал вы хотите управлять?'
    },
    'btn_add_channel': {
        'uz': '➕ Kanal qo\'shish',
        'en': '➕ Add Channel',
        'ru': '➕ Добавить канал'
    },
    'btn_remove_channel': {
        'uz': '➖ Kanal o\'chirish',
        'en': '➖ Remove Channel',
        'ru': '➖ Удалить канал'
    },
    'no_channels': {
        'uz': '❌ Hali kanallar qo\'shilmagan.',
        'en': '❌ No channels added yet.',
        'ru': '❌ Каналы еще не добавлены.'
    },
    'enter_channel_id': {
        'uz': 'Kanal ID-sini yoki @username ni kiriting:',
        'en': 'Enter channel ID or @username:',
        'ru': 'Введите ID канала или @username:'
    },
    'channel_added': {
        'uz': '✅ Kanal muvaffaqiyatli qo\'shildi!',
        'en': '✅ Channel added successfully!',
        'ru': '✅ Канал успешно добавлен!'
    },
    'channel_removed': {
        'uz': '✅ Kanal o\'chirildi!',
        'en': '✅ Channel removed!',
        'ru': '✅ Канал удален!'
    },
    'invalid_channel': {
        'uz': '❌ Kanal noto\'g\'ri! Qayta urinib ko\'ring.',
        'en': '❌ Invalid channel! Please try again.',
        'ru': '❌ Неверный канал! Пожалуйста, попробуйте снова.'
    },

    # ============ GROUPS ============
    'groups_menu': {
        'uz': '👥 GURUH REAKSIYALARI\n\nReaksiyalarni sozlash:',
        'en': '👥 GROUP REACTIONS\n\nConfigure reactions:',
        'ru': '👥 РЕАКЦИИ ГРУППЫ\n\nНастроить реакции:'
    },
    'btn_reactions_on': {
        'uz': '✅ Reaksiyalarni yoqish',
        'en': '✅ Enable Reactions',
        'ru': '✅ Включить реакции'
    },
    'btn_reactions_off': {
        'uz': '❌ Reaksiyalarni o\'chirish',
        'en': '❌ Disable Reactions',
        'ru': '❌ Отключить реакции'
    },
    'btn_select_reactions': {
        'uz': '🎯 Reaksiya tanlash',
        'en': '🎯 Select Reactions',
        'ru': '🎯 Выбрать реакции'
    },
    'reactions_enabled': {
        'uz': '✅ Reaksiyalar yoqildi!',
        'en': '✅ Reactions enabled!',
        'ru': '✅ Реакции включены!'
    },
    'reactions_disabled': {
        'uz': '❌ Reaksiyalar o\'chirildi!',
        'en': '❌ Reactions disabled!',
        'ru': '❌ Реакции отключены!'
    },
    'select_reaction_emoji': {
        'uz': '🎯 Kerakli emoji-ni tanlang:',
        'en': '🎯 Select the required emoji:',
        'ru': '🎯 Выберите требуемый эмодзи:'
    },

    # ============ ADMIN PANEL ============
    'admin_panel': {
        'uz': '🔐 ADMIN PANELI\n\nAdmin funktsiyalari:',
        'en': '🔐 ADMIN PANEL\n\nAdmin functions:',
        'ru': '🔐 ПАНЕЛЬ АДМИНИСТРАТОРА\n\nФункции администратора:'
    },
    'btn_statistics': {
        'uz': '📊 Statistika',
        'en': '📊 Statistics',
        'ru': '📊 Статистика'
    },
    'btn_force_subscribe': {
        'uz': '📌 Majburiy obuna',
        'en': '📌 Force Subscribe',
        'ru': '📌 Принудительная подписка'
    },
    'btn_broadcast': {
        'uz': '📢 Xabar tarqatish',
        'en': '📢 Broadcast Message',
        'ru': '📢 Трансляция сообщения'
    },
    'btn_manage_users': {
        'uz': '👥 Foydalanuvchilar',
        'en': '👥 Users Management',
        'ru': '👥 Управление пользователями'
    },
    'not_admin': {
        'uz': '❌ Siz admin emassiz! Bu buyruq faqat adminlar uchun.',
        'en': '❌ You are not an admin! This command is only for admins.',
        'ru': '❌ Вы не администратор! Эта команда только для администраторов.'
    },

    # ============ STATISTICS ============
    'statistics': {
        'uz': '📊 STATISTIKA\n\n👥 Jami foydalanuvchilar: {total_users}\n👥 Jami guruhlar: {total_groups}\n📢 Jami kanallar: {total_channels}\n📈 Bugun yangi: {daily_new_users}',
        'en': '📊 STATISTICS\n\n👥 Total Users: {total_users}\n👥 Total Groups: {total_groups}\n📢 Total Channels: {total_channels}\n📈 New Today: {daily_new_users}',
        'ru': '📊 СТАТИСТИКА\n\n👥 Всего пользователей: {total_users}\n👥 Всего групп: {total_groups}\n📢 Всего каналов: {total_channels}\n📈 Новых сегодня: {daily_new_users}'
    },

    # ============ FORCE SUBSCRIBE ============
    'force_subscribe_menu': {
        'uz': '📌 MAJBURIY OBUNA SOZLAMALARI',
        'en': '📌 FORCE SUBSCRIBE SETTINGS',
        'ru': '📌 НАСТРОЙКИ ПРИНУДИТЕЛЬНОЙ ПОДПИСКИ'
    },
    'btn_add_force_channel': {
        'uz': '➕ Majburiy kanal qo\'shish',
        'en': '➕ Add Force Channel',
        'ru': '➕ Добавить обязательный канал'
    },
    'must_subscribe': {
        'uz': '⚠️ Ushbu botdan foydalanish uchun quyidagi kanallarga obuna bo\'lishingiz kerak:\n\n{channels}\n\nObunani tasdiqlash uchun "✅ Obunani tekshirish" tugmasini bosing.',
        'en': '⚠️ To use this bot, you must subscribe to the following channels:\n\n{channels}\n\nPress "✅ Verify Subscription" to confirm.',
        'ru': '⚠️ Чтобы использовать этого бота, вы должны подписаться на следующие каналы:\n\n{channels}\n\nНажмите \"✅ Проверить подписку\", чтобы подтвердить.'
    },
    'btn_verify_subscription': {
        'uz': '✅ Obunani tekshirish',
        'en': '✅ Verify Subscription',
        'ru': '✅ Проверить подписку'
    },
    'not_subscribed': {
        'uz': '❌ Siz hali obuna bo\'lmagansiz! Iltimos, barcha kanallarga obuna bo\'ling.',
        'en': '❌ You are not subscribed yet! Please subscribe to all channels.',
        'ru': '❌ Вы еще не подписались! Пожалуйста, подпишитесь на все каналы.'
    },
    'subscribed': {
        'uz': '✅ Obunalangan! Bot-dan foydalanishni davom ettira olasiz.',
        'en': '✅ Subscribed! You can continue using the bot.',
        'ru': '✅ Подписано! Вы можете продолжить использование бота.'
    },

    # ============ BROADCAST ============
    'broadcast_menu': {
        'uz': '📢 XABAR TARQATISH\n\nHabarni kiriting (til filtri ixtiyoriy):',
        'en': '📢 BROADCAST MESSAGE\n\nEnter message (language filter optional):',
        'ru': '📢 ТРАНСЛЯЦИЯ СООБЩЕНИЯ\n\nВведите сообщение (фильтр языка необязателен):'
    },
    'enter_broadcast_message': {
        'uz': 'Xabarni kiriting:',
        'en': 'Enter message:',
        'ru': 'Введите сообщение:'
    },
    'select_language_filter': {
        'uz': 'Til filtrini tanlang (Barcha = hamma foydalanuvchilarga):',
        'en': 'Select language filter (All = all users):',
        'ru': 'Выберите фильтр языка (Все = все пользователи):'
    },
    'btn_all_users': {
        'uz': '🌍 Barcha foydalanuvchilar',
        'en': '🌍 All Users',
        'ru': '🌍 Все пользователи'
    },
    'broadcasting': {
        'uz': '📤 Xabar tarqatilmoqda... (0/{total})',
        'en': '📤 Broadcasting... (0/{total})',
        'ru': '📤 Трансляция... (0/{total})'
    },
    'broadcast_done': {
        'uz': '✅ Xabar muvaffaqiyatli tarqatildi!\n\n📤 Yuborilgan: {sent}/{total}\n❌ Xato: {failed}',
        'en': '✅ Message broadcast successfully!\n\n📤 Sent: {sent}/{total}\n❌ Failed: {failed}',
        'ru': '✅ Сообщение успешно отправлено!\n\n📤 Отправлено: {sent}/{total}\n❌ Ошибок: {failed}'
    },

    # ============ ERRORS & MESSAGES ============
    'error': {
        'uz': '❌ Xato yuz berdi. Qayta urinib ko\'ring.',
        'en': '❌ An error occurred. Please try again.',
        'ru': '❌ Произошла ошибка. Пожалуйста, попробуйте еще раз.'
    },
    'cancelled': {
        'uz': '❌ Bekor qilindi.',
        'en': '❌ Cancelled.',
        'ru': '❌ Отменено.'
    },
    'timeout': {
        'uz': '⏰ Vaqt tugadi. Iltimos, qayta boshlang.',
        'en': '⏰ Time is up. Please start again.',
        'ru': '⏰ Время истекло. Пожалуйста, начните заново.'
    }
}

def get_text(key: str, language: str, **kwargs) -> str:
    """
    Lokalizatsiya matnini olish
    
    Args:
        key: Matn kaliti (masalan: 'start_welcome')
        language: Til kodi ('uz', 'en', 'ru')
        **kwargs: Format parametrlari
    
    Returns:
        Formatlashtirgan matn
    """
    try:
        text = LOCALIZATION.get(key, {}).get(language, '')
        if not text:
            # Fallback to 'uz' agar matn topilmasa
            text = LOCALIZATION.get(key, {}).get('uz', f'[Missing: {key}]')
        
        # Format parametrlari bilan to'ldirish
        if kwargs:
            text = text.format(**kwargs)
        
        return text
    except Exception as e:
        return f'[Error: {e}]'

def get_language_name(lang_code: str) -> str:
    """Til nomini olish"""
    return LANGUAGES.get(lang_code, 'Unknown')
