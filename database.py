import aiosqlite
from datetime import datetime
from config import DB_PATH, DEFAULT_REGISTRATION_LIMIT


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY,
                registration_open INTEGER DEFAULT 1,
                registration_limit INTEGER DEFAULT 31
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
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
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                telegram_id INTEGER PRIMARY KEY
            )
        """)

        await db.execute(
            "INSERT OR IGNORE INTO settings (id, registration_open, registration_limit) VALUES (1, 1, ?)",
            (DEFAULT_REGISTRATION_LIMIT,)
        )

        await db.commit()


async def add_user(data: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (
                telegram_id, tg_full_name, username, full_name,
                xj_id, phone, gender, region, confirm_code, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["telegram_id"],
            data["tg_full_name"],
            data["username"],
            data["full_name"],
            data["xj_id"],
            data["phone"],
            data["gender"],
            data["region"],
            data["confirm_code"],
            datetime.now().strftime("%d.%m.%Y %H:%M")
        ))
        await db.commit()


async def is_registered(telegram_id=None, phone=None, xj_id=None):
    async with aiosqlite.connect(DB_PATH) as db:
        query = "SELECT id FROM users WHERE telegram_id = ? OR phone = ? OR xj_id = ?"
        cursor = await db.execute(query, (telegram_id, phone, xj_id))
        result = await cursor.fetchone()
        return result is not None


async def count_users():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        result = await cursor.fetchone()
        return result[0]


async def get_settings():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT registration_open, registration_limit FROM settings WHERE id = 1")
        result = await cursor.fetchone()
        return {
            "registration_open": bool(result[0]),
            "registration_limit": result[1]
        }


async def set_registration_status(status: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE settings SET registration_open = ? WHERE id = 1",
            (1 if status else 0,)
        )
        await db.commit()


async def set_registration_limit(limit: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE settings SET registration_limit = ? WHERE id = 1",
            (limit,)
        )
        await db.commit()


async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        registered = (await cursor.fetchone())[0]

        cursor = await db.execute("SELECT COUNT(*) FROM users WHERE gender = '👨 Эркак'")
        men = (await cursor.fetchone())[0]

        cursor = await db.execute("SELECT COUNT(*) FROM users WHERE gender = '👩 Аёл'")
        women = (await cursor.fetchone())[0]

        settings = await get_settings()
        limit = settings["registration_limit"]

        return {
            "limit": limit,
            "registered": registered,
            "free_places": max(limit - registered, 0),
            "men": men,
            "women": women,
            "status": "Очиқ" if settings["registration_open"] else "Ёпиқ"
        }


async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT id, full_name, xj_id, phone, gender, region, confirm_code, telegram_id
            FROM users
            ORDER BY id DESC
        """)
        return await cursor.fetchall()


async def search_user(query: str):
    async with aiosqlite.connect(DB_PATH) as db:
        like_query = f"%{query}%"
        cursor = await db.execute("""
            SELECT id, full_name, xj_id, phone, gender, region, confirm_code, telegram_id, username
            FROM users
            WHERE full_name LIKE ? OR xj_id LIKE ? OR phone LIKE ? OR confirm_code LIKE ?
        """, (like_query, like_query, like_query, like_query))
        return await cursor.fetchall()


async def delete_user_by_id(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        await db.commit()


async def get_user_by_id(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT id, full_name, xj_id, phone, gender, region, confirm_code, telegram_id, username
            FROM users
            WHERE id = ?
        """, (user_id,))
        return await cursor.fetchone()


async def get_all_telegram_ids():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT telegram_id FROM users")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]


async def add_admin(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO admins (telegram_id) VALUES (?)",
            (telegram_id,)
        )
        await db.commit()


async def remove_admin(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM admins WHERE telegram_id = ?",
            (telegram_id,)
        )
        await db.commit()


async def is_db_admin(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT telegram_id FROM admins WHERE telegram_id = ?",
            (telegram_id,)
        )
        result = await cursor.fetchone()
        return result is not None
