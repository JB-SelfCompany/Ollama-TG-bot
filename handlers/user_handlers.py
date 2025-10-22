from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
import logging
import re

from database.db_manager import DatabaseManager
from keyboards.main_keyboard import get_main_keyboard, get_model_keyboard
from services.ollama_service import OllamaService
from services.search_service import SearchService
from utils.message_splitter import MessageSplitter
from config import Config

logger = logging.getLogger(__name__)

router = Router(name='user_handlers')
config = Config()
ollama_service = OllamaService(config)
search_service = SearchService(config) if config.SEARCH_ENABLED else None

# Log initialization
logger.info(f"Search service initialized: {search_service is not None}")
logger.info(f"Config SEARCH_ENABLED: {config.SEARCH_ENABLED}")


@router.message(Command("start"))
async def cmd_start(message: Message, db: DatabaseManager):
    """Handle /start command"""
    user_id = message.from_user.id
    
    await db.create_user(
        user_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    
    search_status = "включен (Google)" if config.SEARCH_ENABLED else "выключен"
    
    await message.answer(
        f"Приветствую! Я помощник, работающий с моделями Ollama.\n\n"
        f"🔍 Веб-поиск: {search_status}\n"
        f"💬 Отправьте текстовое сообщение или изображение для анализа.\n"
        f"❓ Добавьте '?' в конце сообщения для автоматического поиска в Google.\n"
        f"📚 История диалога по умолчанию выключена.\n\n"
        f"Используйте кнопки меню для управления ботом:",
        reply_markup=get_main_keyboard()
    )


# Button handlers
@router.message(F.text == "История On/Off")
async def toggle_history(message: Message, db: DatabaseManager):
    """Toggle history mode via button"""
    user_id = message.from_user.id
    settings = await db.get_user_settings(user_id)
    current_mode = settings['history_mode']
    new_mode = "without_history" if current_mode == "with_history" else "with_history"
    
    await db.update_setting(user_id, 'history_mode', new_mode)
    status = "включена" if new_mode == "with_history" else "выключена"
    await message.answer(f"✅ История диалога {status}.", reply_markup=get_main_keyboard())


@router.message(F.text == "Очистить историю")
async def clear_history(message: Message, db: DatabaseManager):
    """Clear message history via button"""
    user_id = message.from_user.id
    await db.clear_history(user_id)
    await message.answer("✅ История диалога очищена.", reply_markup=get_main_keyboard())


@router.message(F.text == "Выбор модели")
async def show_models(message: Message):
    """Show available models via button"""
    models = ollama_service.get_available_models()
    if not models:
        await message.answer(
            "⚠️ Не удалось получить список моделей. Убедитесь, что Ollama запущена.",
            reply_markup=get_main_keyboard()
        )
        return
    
    await message.answer(
        "🤖 Выберите модель:",
        reply_markup=get_model_keyboard(models)
    )


@router.message(F.text == "◀️ Назад")
async def back_to_main(message: Message):
    """Return to main menu via button"""
    await message.answer("📋 Главное меню:", reply_markup=get_main_keyboard())


@router.message(F.text)
async def handle_text(message: Message, db: DatabaseManager):
    """Handle text messages - questions and model selection"""
    user_id = message.from_user.id
    user_input = message.text
    
    # Check if it's a model selection
    available_models = ollama_service.get_available_models()
    if user_input in available_models:
        await db.update_setting(user_id, 'selected_model', user_input)
        await message.answer(
            f"✅ Модель изменена на {user_input}.",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Show typing indicator
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    # Get user settings
    settings = await db.get_user_settings(user_id)
    model = settings['selected_model'] or config.DEFAULT_MODEL
    
    # Auto-detect search based on '?' at the end
    ends_with_question = user_input.strip().endswith('?')
    
    logger.info("=" * 80)
    logger.info(f"📩 NEW MESSAGE from user {user_id}")
    logger.info(f"   Message: '{user_input}'")
    logger.info(f"   🔍 Search service available: {search_service is not None}")
    logger.info(f"   ❓ Ends with '?': {ends_with_question}")
    logger.info(f"   🤖 Model: {model}")
    logger.info("=" * 80)
    
    # Get history if enabled
    messages = []
    if settings['history_mode'] == 'with_history':
        messages = await db.get_message_history(user_id, config.MAX_HISTORY_LENGTH)
        logger.info(f"📚 Loaded {len(messages)} messages from history")
    
    try:
        response = None
        
        # AUTOMATIC search detection: only by '?' at the end
        should_search = (
            search_service is not None and
            config.SEARCH_ENABLED and
            ends_with_question
        )
        
        logger.info(f"🔍 SEARCH DECISION: {should_search}")
        
        if should_search:
            logger.info(f"🚀 STARTING GOOGLE SEARCH WORKFLOW for query: {user_input}")
            
            # Send search status
            search_msg = await message.answer("🔍 Выполняю поиск в Google...")
            
            try:
                # Perform Google search
                logger.info("📡 Calling search_service.search()...")
                search_results = await search_service.search(user_input)
                logger.info(f"📊 Google Search returned {len(search_results)} results")
                
                if search_results:
                    logger.info("✅ Search successful, formatting context for LLM...")
                    
                    # Format search context for LLM
                    search_context = search_service.format_search_context_for_llm(
                        user_input,
                        search_results
                    )
                    logger.info(f"📝 Search context length: {len(search_context)} chars")
                    
                    # Update status
                    await search_msg.edit_text("🤖 Анализирую результаты поиска...")
                    
                    # Get response with search context (NO history to reduce context size)
                    logger.info("🤖 Sending to LLM with search context...")
                    response = await ollama_service.get_response_with_search(
                        user_input,
                        search_context,
                        [],  # Empty history for search requests
                        model
                    )
                    logger.info(f"✅ LLM response received: {len(response)} chars")
                    
                    # Delete search status message
                    await search_msg.delete()
                else:
                    logger.warning("⚠️ Search returned no results, falling back")
                    await search_msg.delete()
                    await message.answer("⚠️ Не удалось найти результаты. Отвечаю без поиска...")
                    response = await ollama_service.get_response(user_input, messages, model)
                    
            except Exception as search_error:
                logger.error(f"❌ Search workflow error: {search_error}", exc_info=True)
                await search_msg.delete()
                await message.answer("⚠️ Ошибка при поиске. Отвечаю без поиска...")
                response = await ollama_service.get_response(user_input, messages, model)
        else:
            # Regular response without search
            logger.info("💬 Processing without search (regular response)")
            response = await ollama_service.get_response(user_input, messages, model)
        
        # Remove HTML tags from response
        cleaned_response = re.sub(r'<[^>]+>', '', response)
        logger.info(f"📤 Sending response: {len(cleaned_response)} chars")
        
        # Save to history if enabled
        if settings['history_mode'] == 'with_history':
            await db.add_message(user_id, user_input, cleaned_response)
            logger.info("💾 Message saved to history")
        
        # Split and send response
        message_chunks = MessageSplitter.split_message(cleaned_response)
        logger.info(f"📨 Sending {len(message_chunks)} message chunk(s)")
        
        for idx, chunk in enumerate(message_chunks):
            # Add keyboard only to last message
            keyboard = get_main_keyboard() if idx == len(message_chunks) - 1 else None
            await message.answer(chunk, reply_markup=keyboard)
        
        logger.info("✅ Message handling complete")
        
    except Exception as e:
        logger.error(f"❌ Error processing message: {e}", exc_info=True)
        await message.answer(
            f"❌ Произошла ошибка при обработке сообщения: {str(e)}",
            reply_markup=get_main_keyboard()
        )