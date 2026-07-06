from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

start_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="📝 Рўйхатдан ўтиш")]], resize_keyboard=True)
phone_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="📞 Телефон рақамни юбориш", request_contact=True)]], resize_keyboard=True, one_time_keyboard=True)
gender_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="👨 Эркак"), KeyboardButton(text="👩 Аёл")]], resize_keyboard=True, one_time_keyboard=True)
region_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Тошкент шаҳри"), KeyboardButton(text="Тошкент вилояти")],
    [KeyboardButton(text="Андижон"), KeyboardButton(text="Наманган")],
    [KeyboardButton(text="Фарғона"), KeyboardButton(text="Самарқанд")],
    [KeyboardButton(text="Бухоро"), KeyboardButton(text="Навоий")],
    [KeyboardButton(text="Жиззах"), KeyboardButton(text="Сирдарё")],
    [KeyboardButton(text="Қашқадарё"), KeyboardButton(text="Сурхондарё")],
    [KeyboardButton(text="Хоразм"), KeyboardButton(text="Қорақалпоғистон Республикаси")],
], resize_keyboard=True, one_time_keyboard=True)
confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Ҳа, тасдиқлайман", callback_data="confirm_yes")],
    [InlineKeyboardButton(text="✏️ Қайта тўлдираман", callback_data="confirm_no")],
])
admin_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="👥 Рўйхатдагилар")],
    [KeyboardButton(text="🔍 Қидириш"), KeyboardButton(text="📢 Барчага хабар")],
    [KeyboardButton(text="➕ Лимит"), KeyboardButton(text="🔒 Ёпиш"), KeyboardButton(text="🔓 Очиш")],
    [KeyboardButton(text="🗑 Ўчириш"), KeyboardButton(text="💬 Бир кишига хабар")],
    [KeyboardButton(text="👮 Админ қўшиш"), KeyboardButton(text="❌ Админни ўчириш")],
], resize_keyboard=True)

