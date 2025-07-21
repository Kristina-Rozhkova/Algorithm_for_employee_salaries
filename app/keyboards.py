from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

main = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Информация о зарплате")]],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню...",
)

group_type = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Месяц", callback_data="month")],
        [InlineKeyboardButton(text="День", callback_data="day")],
        [InlineKeyboardButton(text="Час", callback_data="hour")],
    ]
)
