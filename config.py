import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("8935060500:AAEffFbkI_at4kKfWy3TgcHIhR8w_c9Tybs")

ADMIN_IDS = [
    199169309,  # Бу ерга ўз Telegram ID рақамингизни ёзинг
]

DB_PATH = "data/xj_travel.db"

DEFAULT_REGISTRATION_LIMIT = 31

BOT_USERNAME = "xj_masterlar_bot"
