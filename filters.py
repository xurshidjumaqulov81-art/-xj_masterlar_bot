from aiogram.filters import BaseFilter
from aiogram.types import Message

from config import ADMIN_IDS
from database import is_db_admin


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        telegram_id = message.from_user.id

        if telegram_id in ADMIN_IDS:
            return True

        if await is_db_admin(telegram_id):
            return True

        return False
