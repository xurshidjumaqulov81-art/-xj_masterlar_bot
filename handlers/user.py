from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from config import ADMIN_IDS
from states import RegisterStates
from keyboards import (
    start_keyboard,
    phone_keyboard,
    gender_keyboard,
    region_keyboard,
    confirm_keyboard,
)
from texts import *
from database import (
    add_user,
    is_registered,
    count_users,
    get_settings,
    is_db_admin,
)
from utils.validators import is_valid_xj_id, normalize_phone, clean_text
from utils.code_generator import generate_confirm_code

router = Router()


async def send_to_admins(bot: Bot, text: str):
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, text)
        except Exception:
            pass


async def get_admin_ids():
    return ADMIN_IDS


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(WELCOME_TEXT, reply_markup=start_keyboard)


@router.message(F.text == "📝 Рўйхатдан ўтиш")
async def register_start(message: Message, state: FSMContext):
    settings = await get_settings()
    registered_count = await count_users()

    if not settings["registration_open"]:
        await message.answer(REGISTRATION_CLOSED, reply_markup=ReplyKeyboardRemove())
        return

    if registered_count >= settings["registration_limit"]:
        await message.answer(LIMIT_FULL, reply_markup=ReplyKeyboardRemove())
        return

    if await is_registered(telegram_id=message.from_user.id):
        await message.answer(ALREADY_REGISTERED, reply_markup=ReplyKeyboardRemove())
        return

    await message.answer(START_INFO_TEXT)
    await message.answer(ASK_FULL_NAME, reply_markup=ReplyKeyboardRemove())
    await state.set_state(RegisterStates.full_name)


@router.message(RegisterStates.full_name)
async def get_full_name(message: Message, state: FSMContext):
    full_name = clean_text(message.text)

    if len(full_name) < 5:
        await message.answer("❌ Исм ва фамилияни тўлиқ киритинг.")
        return

    await state.update_data(full_name=full_name)
    await message.answer(ASK_XJ_ID)
    await state.set_state(RegisterStates.xj_id)


@router.message(RegisterStates.xj_id)
async def get_xj_id(message: Message, state: FSMContext):
    xj_id = clean_text(message.text)

    if not is_valid_xj_id(xj_id):
        await message.answer(INVALID_XJ_ID)
        return

    if await is_registered(xj_id=xj_id):
        await message.answer("❌ Ушбу XJ ID билан аввал рўйхатдан ўтилган.")
        return

    await state.update_data(xj_id=xj_id)
    await message.answer(ASK_PHONE, reply_markup=phone_keyboard)
    await state.set_state(RegisterStates.phone)


@router.message(RegisterStates.phone)
async def get_phone(message: Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
        if not phone.startswith("+"):
            phone = "+" + phone
    else:
        await message.answer("❌ Илтимос, телефон рақамни пастдаги тугма орқали юборинг.")
        return

    phone = normalize_phone(phone)

    if await is_registered(phone=phone):
        await message.answer("❌ Ушбу телефон рақам билан аввал рўйхатдан ўтилган.")
        return

    await state.update_data(phone=phone)
    await message.answer(ASK_GENDER, reply_markup=gender_keyboard)
    await state.set_state(RegisterStates.gender)


@router.message(RegisterStates.gender)
async def get_gender(message: Message, state: FSMContext):
    gender = message.text

    if gender not in ["👨 Эркак", "👩 Аёл"]:
        await message.answer("❌ Илтимос, жинсингизни тугма орқали танланг.")
        return

    await state.update_data(gender=gender)
    await message.answer(ASK_REGION, reply_markup=region_keyboard)
    await state.set_state(RegisterStates.region)


@router.message(RegisterStates.region)
async def get_region(message: Message, state: FSMContext):
    region = message.text

    regions = [
        "Тошкент шаҳри",
        "Тошкент вилояти",
        "Андижон",
        "Наманган",
        "Фарғона",
        "Самарқанд",
        "Бухоро",
        "Навоий",
        "Жиззах",
        "Сирдарё",
        "Қашқадарё",
        "Сурхондарё",
        "Хоразм",
        "Қорақалпоғистон Республикаси",
    ]

    if region not in regions:
        await message.answer("❌ Илтимос, вилоятни тугма орқали танланг.")
        return

    await state.update_data(region=region)
    data = await state.get_data()

    await message.answer(
        CONFIRM_TEXT.format(
            full_name=data["full_name"],
            xj_id=data["xj_id"],
            phone=data["phone"],
            gender=data["gender"],
            region=data["region"],
        ),
        reply_markup=confirm_keyboard
    )

    await state.set_state(RegisterStates.confirm)


@router.callback_query(RegisterStates.confirm, F.data == "confirm_no")
async def confirm_no(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("✏️ Маълумотларни қайта киритамиз.")
    await callback.message.answer(ASK_FULL_NAME, reply_markup=ReplyKeyboardRemove())
    await state.set_state(RegisterStates.full_name)
    await callback.answer()


@router.callback_query(RegisterStates.confirm, F.data == "confirm_yes")
async def confirm_yes(callback: CallbackQuery, state: FSMContext, bot: Bot):
    settings = await get_settings()
    registered_count = await count_users()

    if not settings["registration_open"]:
        await callback.message.answer(REGISTRATION_CLOSED)
        await state.clear()
        await callback.answer()
        return

    if registered_count >= settings["registration_limit"]:
        await callback.message.answer(LIMIT_FULL)
        await state.clear()
        await callback.answer()
        return

    data = await state.get_data()

    if await is_registered(
        telegram_id=callback.from_user.id,
        phone=data["phone"],
        xj_id=data["xj_id"]
    ):
        await callback.message.answer(ALREADY_REGISTERED)
        await state.clear()
        await callback.answer()
        return

    confirm_code = generate_confirm_code()

    user_data = {
        "telegram_id": callback.from_user.id,
        "tg_full_name": callback.from_user.full_name,
        "username": callback.from_user.username or "Йўқ",
        "full_name": data["full_name"],
        "xj_id": data["xj_id"],
        "phone": data["phone"],
        "gender": data["gender"],
        "region": data["region"],
        "confirm_code": confirm_code,
    }

    await add_user(user_data)

    await callback.message.answer(
        SUCCESS_TEXT.format(confirm_code=confirm_code),
        reply_markup=ReplyKeyboardRemove()
    )

    admin_text = ADMIN_NEW_USER.format(
        full_name=user_data["full_name"],
        xj_id=user_data["xj_id"],
        phone=user_data["phone"],
        gender=user_data["gender"],
        region=user_data["region"],
        confirm_code=user_data["confirm_code"],
        tg_full_name=user_data["tg_full_name"],
        username=f"@{user_data['username']}" if user_data["username"] != "Йўқ" else "Йўқ",
        telegram_id=user_data["telegram_id"],
        created_at="Ҳозир"
    )

    await send_to_admins(bot, admin_text)

    await state.clear()
    await callback.answer("✅ Рўйхатдан ўтдингиз!")
