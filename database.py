import os
import aiosqlite
from datetime import datetime
from config import DB_PATH, DEFAULT_REGISTRATION_LIMIT

async def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY, registration_open INTEGER DEFAULT 1, registration_limit INTEGER DEFAULT 31)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            tg_full_name TEXT,
            username TEXT,
            full_name TEXT,
            xj_id TEXT UNIQUE,
            phone TEXT UNIQUE,
            gender TEXT,
            region TEXT,
            confirm_code TEXT UNIQUE,
            created_at TEXT
        )""")
        await db.execute("""CREATE TABLE IF NOT EXISTS admins (telegram_id INTEGER PRIMARY KEY)""")
        await db.execute("INSERT OR IGNORE INTO settings (id, registration_open, registration_limit) VALUES (1, 1, ?)", (DEFAULT_REGISTRATION_LIMIT,))
        await db.commit()

async def add_user(data: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.now().strftime("%d.%m.%Y %H:%M")
        await db.execute("""INSERT INTO users (telegram_id, tg_full_name, username, full_name, xj_id, phone, gender, region, confirm_code, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
            data["telegram_id"], data["tg_full_name"], data["username"], data["full_name"], data["xj_id"], data["phone"], data["gender"], data["region"], data["confirm_code"], now
        ))
        await db.commit()
        return now

async def is_registered(telegram_id=None, phone=None, xj_id=None):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT id FROM users WHERE telegram_id = ? OR phone = ? OR xj_id = ?", (telegram_id, phone, xj_id))
        return await cursor.fetchone() is not None

async def code_exists(code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT id FROM users WHERE confirm_code = ?", (code,))
        return await cursor.fetchone() is not None

async def count_users():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        row = await cursor.fetchone()
        return row[0]

async def get_settings():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT registration_open, registration_limit FROM settings WHERE id = 1")
        row = await cursor.fetchone()
        return {"registration_open": bool(row[0]), "registration_limit": row[1]}

async def set_registration_status(status: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE settings SET registration_open = ? WHERE id = 1", (1 if status else 0,))
        await db.commit()

async def set_registration_limit(limit: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE settings SET registration_limit = ? WHERE id = 1", (limit,))
        await db.commit()

async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        reg = (await (await db.execute("SELECT COUNT(*) FROM users")).fetchone())[0]
        men = (await (await db.execute("SELECT COUNT(*) FROM users WHERE gender = '👨 Эркак'")).fetchone())[0]
        women = (await (await db.execute("SELECT COUNT(*) FROM users WHERE gender = '👩 Аёл'")).fetchone())[0]
    settings = await get_settings()
    limit = settings["registration_limit"]
    return {"limit": limit, "registered": reg, "free_places": max(limit-reg, 0), "men": men, "women": women, "status": "Очиқ" if settings["registration_open"] else "Ёпиқ"}

async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT id, full_name, xj_id, phone, gender, region, confirm_code, telegram_id, username, created_at FROM users ORDER BY id DESC")
        return await cursor.fetchall()

async def search_user(query: str):
    async with aiosqlite.connect(DB_PATH) as db:
        q = f"%{query}%"
        cursor = await db.execute("""SELECT id, full_name, xj_id, phone, gender, region, confirm_code, telegram_id, username, created_at FROM users
            WHERE full_name LIKE ? OR xj_id LIKE ? OR phone LIKE ? OR confirm_code LIKE ? OR username LIKE ?""", (q, q, q, q, q))
        return await cursor.fetchall()

async def delete_user_by_id(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        await db.commit()
        return cursor.rowcount > 0

async def get_all_telegram_ids():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT telegram_id FROM users")
        rows = await cursor.fetchall()
        return [r[0] for r in rows]

async def add_admin(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO admins (telegram_id) VALUES (?)", (telegram_id,))
        await db.commit()

async def remove_admin(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM admins WHERE telegram_id = ?", (telegram_id,))
        await db.commit()

async def is_db_admin(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT telegram_id FROM admins WHERE telegram_id = ?", (telegram_id,))
        return await cursor.fetchone() is not None

