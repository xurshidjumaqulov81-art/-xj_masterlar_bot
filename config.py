import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8935060500:AAEffFbkI_at4kKfWy3TgcHIhR8w_c9Tybs")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "199169309").split(",") if x.strip().isdigit()]
DB_PATH = os.getenv("DB_PATH", "data/xj_travel.db")
DEFAULT_REGISTRATION_LIMIT = int(os.getenv("DEFAULT_REGISTRATION_LIMIT", "31"))
BOT_USERNAME = os.getenv("BOT_USERNAME", "xj_masterlar_bot")

