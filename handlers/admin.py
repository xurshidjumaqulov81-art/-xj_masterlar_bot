from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from filters import AdminFilter
from states import AdminStates
from keyboards import admin_keyboard
from texts import *
from database import (
    get_stats,
    set_registration_status,
    set_registration_limit,
    get_all_users,
    search_user,
    delete_user_by_id,
    get_all_telegram_ids,
    add_admin,
    remove_admin,
)

router = Router()


@router.message(AdminFilter(), F.text == "/admin")
async def admin_panel(message: Message):
    await message.answer(ADMIN_PANEL_TEXT, reply_markup=admin_keyboard)


@router.message(AdminFilter(), F.text == "📊 Статистика")
async def admin_stats(message: Message):
    stats = await get_stats()
    await message.answer(ADMIN_STATS_TEXT.format(**stats))


@router.message(AdminFilter(), F.text == "🔒 Ёпиш")
async def close_registration(message: Message):
    await set_registration_status(False)
    await message.answer("🔒 Рўйхатдан ўтиш ёпилди.")


@router.message(AdminFilter(), F.text == "🔓 Очиш")
async def open_registration(message: Message):
    await set_registration_status(True)
    await message.answer("🔓 Рўйхатдан ўтиш очилди.")


@router.message(AdminFilter(), F.text == "➕ Лимит")
async def ask_limit(message: Message, state: FSMContext):
    await message.answer(SET_LIMIT_ASK_TEXT)
    await state.set_state(AdminStates.set_limit)


@router.message(AdminFilter(), AdminStates.set_limit)
async def set_limit(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Фақат рақам киритинг.")
        return

    limit = int(message.text)
    await set_registration_limit(limit)

    await message.answer(SET_LIMIT_DONE_TEXT.format(limit=limit), reply_markup=admin_keyboard)
    await state.clear()


@router.message(AdminFilter(), F.text == "👥 Рўйхатдагилар")
async def list_users(message: Message):
    users = await get_all_users()

    if not users:
        await message.answer("Ҳали рўйхатдан ўтганлар йўқ.")
        return

    text = "👥 Рўйхатдан ўтганлар:\n\n"

    for user in users[:30]:
        user_id, full_name, xj_id, phone, gender, region, confirm_code, telegram_id = user
        text += (
            f"№{user_id}\n"
            f"👤 {full_name}\n"
            f"🆔 {xj_id}\n"
            f"📞 {phone}\n"
            f"🚻 {gender}\n"
            f"📍 {region}\n"
            f"🔑 {confirm_code}\n"
            f"🆔 Telegram ID: {telegram_id}\n\n"
        )

    if len(users) > 30:
        text += f"Яна {len(users) - 30} та иштирокчи бор."

    await message.answer(text)


@router.message(AdminFilter(), F.text == "📢 Барчага хабар")
async def ask_broadcast(message: Message, state: FSMContext):
    await message.answer(BROADCAST_ASK_TEXT)
    await state.set_state(AdminStates.broadcast)


@router.message(AdminFilter(), AdminStates.broadcast)
async def send_broadcast(message: Message, state: FSMContext, bot: Bot):
    telegram_ids = await get_all_telegram_ids()

    sent = 0
    failed = 0

    for telegram_id in telegram_ids:
        try:
            await bot.send_message(telegram_id, message.text)
            sent += 1
        except Exception:
            failed += 1

    await message.answer(
        BROADCAST_DONE_TEXT.format(sent=sent, failed=failed),
        reply_markup=admin_keyboard
    )
    await state.clear()


@router.message(AdminFilter(), F.text == "🔍 Қидириш")
async def ask_search(message: Message, state: FSMContext):
    await message.answer(SEARCH_ASK_TEXT)
    await state.set_state(AdminStates.search)


@router.message(AdminFilter(), AdminStates.search)
async def search_user_handler(message: Message, state: FSMContext):
    results = await search_user(message.text)

    if not results:
        await message.answer(NOT_FOUND_TEXT, reply_markup=admin_keyboard)
        await state.clear()
        return

    text = "🔍 Қидирув натижалари:\n\n"

    for user in results:
        user_id, full_name, xj_id, phone, gender, region, confirm_code, telegram_id, username = user
        text += (
            f"№{user_id}\n"
            f"👤 {full_name}\n"
            f"🆔 {xj_id}\n"
            f"📞 {phone}\n"
            f"🚻 {gender}\n"
            f"📍 {region}\n"
            f"🔑 {confirm_code}\n"
            f"🆔 Telegram ID: {telegram_id}\n"
            f"🔗 Username: @{username if username else 'Йўқ'}\n\n"
        )

    await message.answer(text, reply_markup=admin_keyboard)
    await state.clear()


@router.message(AdminFilter(), F.text == "🗑 Ўчириш")
async def ask_delete(message: Message, state: FSMContext):
    await message.answer("🗑 Ўчириш учун иштирокчи № рақамини киритинг.")
    await state.set_state(AdminStates.search)


@router.message(AdminFilter(), F.text.regexp(r"^\d+$"))
async def delete_by_number(message: Message):
    user_id = int(message.text)
    await delete_user_by_id(user_id)
    await message.answer(USER_DELETED_TEXT, reply_markup=admin_keyboard)


@router.message(AdminFilter(), F.text == "👮 Админ қўшиш")
async def ask_add_admin(message: Message, state: FSMContext):
    await message.answer("👮 Янги админнинг Telegram ID рақамини киритинг.")
    await state.set_state(AdminStates.add_admin)


@router.message(AdminFilter(), AdminStates.add_admin)
async def add_admin_handler(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Telegram ID фақат рақам бўлиши керак.")
        return

    await add_admin(int(message.text))
    await message.answer("✅ Янги админ қўшилди.", reply_markup=admin_keyboard)
    await state.clear()


@router.message(AdminFilter(), F.text == "❌ Админни ўчириш")
async def ask_remove_admin(message: Message, state: FSMContext):
    await message.answer("❌ Ўчириладиган админнинг Telegram ID рақамини киритинг.")
    await state.set_state(AdminStates.remove_admin)


@router.message(AdminFilter(), AdminStates.remove_admin)
async def remove_admin_handler(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Telegram ID фақат рақам бўлиши керак.")
        return

    await remove_admin(int(message.text))
    await message.answer("✅ Админ ўчирилди.", reply_markup=admin_keyboard)
    await state.clear()


@router.message(AdminFilter(), F.text == "💬 Бир кишига хабар")
async def private_message_start(message: Message, state: FSMContext):
    await message.answer("💬 Аввал иштирокчининг Telegram ID рақамини, кейин хабарни шу кўринишда юборинг:\n\n123456789 | Салом, сафар ҳақида эслатма.")
    await state.set_state(AdminStates.private_message)


@router.message(AdminFilter(), AdminStates.private_message)
async def send_private_message(message: Message, state: FSMContext, bot: Bot):
    if "|" not in message.text:
        await message.answer("❌ Формат нотўғри.\n\nМисол:\n123456789 | Хабар матни")
        return

    telegram_id, text = message.text.split("|", 1)

    if not telegram_id.strip().isdigit():
        await message.answer("❌ Telegram ID рақам бўлиши керак.")
        return

    try:
        await bot.send_message(int(telegram_id.strip()), text.strip())
        await message.answer("✅ Хабар юборилди.", reply_markup=admin_keyboard)
    except Exception:
        await message.answer("❌ Хабар юбориб бўлмади.", reply_markup=admin_keyboard)

    await state.clear()
