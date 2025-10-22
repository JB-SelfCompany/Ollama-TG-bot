import os
import logging
from aiogram import Router, F
from aiogram.types import Message
import ollama

from database.db_manager import DatabaseManager
from config import Config
from keyboards.main_keyboard import get_main_keyboard

logger = logging.getLogger(__name__)
router = Router(name='photo_handlers')

config = Config()


@router.message(F.photo)
async def handle_photo(message: Message, db: DatabaseManager):
    """Handle photo messages"""
    user_id = message.from_user.id
    
    # Download photo
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    photo_path = f"temp_photo_{user_id}_{photo.file_id}.jpg"
    
    try:
        await message.bot.download_file(file.file_path, photo_path)
        
        # Get user settings
        settings = await db.get_user_settings(user_id)
        model = settings['selected_model'] or config.DEFAULT_MODEL
        
        # Analyze image with Ollama
        response = ollama.chat(
            model=model,
            messages=[{
                'role': 'user',
                'content': message.caption or "Что изображено на этой фотографии?",
                'images': [photo_path]
            }]
        )
        
        await message.answer(response['message']['content'], reply_markup=get_main_keyboard())
        
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        await message.answer("Произошла ошибка при анализе изображения.")
    finally:
        if os.path.exists(photo_path):
            os.remove(photo_path)
