from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Get main bot keyboard (without search toggle)"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="История On/Off"), KeyboardButton(text="Выбор модели")],
            [KeyboardButton(text="Очистить историю")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_model_keyboard(models: list[str]) -> ReplyKeyboardMarkup:
    """Get model selection keyboard"""
    buttons = [[KeyboardButton(text=model)] for model in models]
    buttons.append([KeyboardButton(text="◀️ Назад")])
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
    return keyboard