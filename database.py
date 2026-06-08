import sqlite3
from config import DB_NAME

def get_conn():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    # Foydalanuvchilar jadvali
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id     INTEGER PRIMARY KEY,
        username    TEXT,
        full_name   TEXT,
        lang        TEXT DEFAULT 'uz',
        is_blocked  INTEGER DEFAULT 0,
        joined_at   TEXT DEFAULT (datetime('now'))
    )''')

    # Guruhlar jadvali
    c.execute('''CREATE TABLE IF NOT EXISTS groups (
        chat_id         INTEGER PRIMARY KEY,
        title           TEXT,
        reaction_emoji  TEXT DEFAULT '👍',
        auto_react      INTEGER DEFAULT 0,
        added_by        INTEGER,
        added_at        TEXT DEFAULT (datetime('now'))
    )''')

    # Kanallar jadvali
    c.execute('''CREATE TABLE IF NOT EXISTS channels (
        chat_id         INTEGER PRIMARY KEY,
        title           TEXT,
        reaction_emoji  TEXT DEFAULT '👍',
        auto_react      INTEGER DEFAULT 0,
        added_by        INTEGER,
        added_at        TEXT DEFAULT (datetime('now'))
    )''')

    # Adminlar jadvali
    c.execute('''CREATE TABLE IF NOT EXISTS admins (
        user_id     INTEGER PRIMARY KEY,
        added_by    INTEGER,
        added_at    TEXT DEFAULT (datetime('now'))
    )''')

    conn.commit()
    conn.close()

# --- Foydalanuvchi funksiyalari ---

def add_user(user_id, username, full_name):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''INSERT OR IGNORE INTO users (user_id, username, full_name)
                 VALUES (?, ?, ?)''', (user_id, username, full_name))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_user_lang(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT lang FROM users WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 'uz'

def set_user_lang(user_id, lang):
    conn = get_conn()
    c = conn.cursor()
    c.execute('UPDATE users SET lang = ? WHERE user_id = ?', (lang, user_id))
    conn.commit()
    conn.close()

def get_all_users():
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT user_id, username, full_name, lang, is_blocked, joined_at FROM users')
    rows = c.fetchall()
    conn.close()
    return rows

def block_user(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('UPDATE users SET is_blocked = 1 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def unblock_user(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('UPDATE users SET is_blocked = 0 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def is_blocked(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT is_blocked FROM users WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    return bool(row and row[0])

# --- Guruh funksiyalari ---

def add_group(chat_id, title, added_by):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''INSERT OR IGNORE INTO groups (chat_id, title, added_by)
                 VALUES (?, ?, ?)''', (chat_id, title, added_by))
    conn.commit()
    conn.close()

def get_group(chat_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM groups WHERE chat_id = ?', (chat_id,))
    row = c.fetchone()
    conn.close()
    return row

def set_group_reaction(chat_id, emoji):
    conn = get_conn()
    c = conn.cursor()
    c.execute('UPDATE groups SET reaction_emoji = ? WHERE chat_id = ?', (emoji, chat_id))
    conn.commit()
    conn.close()

def set_group_auto_react(chat_id, value: bool):
    conn = get_conn()
    c = conn.cursor()
    c.execute('UPDATE groups SET auto_react = ? WHERE chat_id = ?', (int(value), chat_id))
    conn.commit()
    conn.close()

# --- Kanal funksiyalari ---

def add_channel(chat_id, title, added_by):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''INSERT OR IGNORE INTO channels (chat_id, title, added_by)
                 VALUES (?, ?, ?)''', (chat_id, title, added_by))
    conn.commit()
    conn.close()

def get_channel(chat_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM channels WHERE chat_id = ?', (chat_id,))
    row = c.fetchone()
    conn.close()
    return row

def set_channel_reaction(chat_id, emoji):
    conn = get_conn()
    c = conn.cursor()
    c.execute('UPDATE channels SET reaction_emoji = ? WHERE chat_id = ?', (emoji, chat_id))
    conn.commit()
    conn.close()

def set_channel_auto_react(chat_id, value: bool):
    conn = get_conn()
    c = conn.cursor()
    c.execute('UPDATE channels SET auto_react = ? WHERE chat_id = ?', (int(value), chat_id))
    conn.commit()
    conn.close()

# --- Admin funksiyalari ---

def add_admin(user_id, added_by):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''INSERT OR IGNORE INTO admins (user_id, added_by)
                 VALUES (?, ?)''', (user_id, added_by))
    conn.commit()
    conn.close()


def get_admins():
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT user_id, added_by, added_at FROM admins')
    rows = c.fetchall()
    conn.close()
    return rows


def is_admin_user(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT 1 FROM admins WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    return bool(row)


def get_all_channels_by_user(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT chat_id, title FROM channels WHERE added_by = ?', (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_all_groups_by_user(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT chat_id, title FROM groups WHERE added_by = ?', (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows
