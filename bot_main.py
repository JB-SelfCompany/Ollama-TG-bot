import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import Config
from database.db_manager import DatabaseManager
from handlers import user_handlers, photo_handlers
from middlewares.db_middleware import DatabaseMiddleware

logger = logging.getLogger(__name__)


async def set_bot_commands(bot: Bot):
    """Set bot commands in menu"""
    commands = [
        BotCommand(command="start", description="🚀 Запустить бота")
    ]
    await bot.set_my_commands(commands)


async def main():
    """Main bot entry point"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize config
    config = Config()
    
    # Initialize database
    db = DatabaseManager(config.DATABASE_PATH)
    await db.init_db()
    
    # Initialize bot without parse_mode (sends plain text)
    bot = Bot(token=config.BOT_TOKEN)
    
    dp = Dispatcher()
    
    # Register middleware
    dp.message.middleware(DatabaseMiddleware(db))
    dp.callback_query.middleware(DatabaseMiddleware(db))
    
    # Include routers
    dp.include_router(user_handlers.router)
    dp.include_router(photo_handlers.router)
    
    # Set bot commands
    await set_bot_commands(bot)
    
    # Delete webhook and start polling
    await bot.delete_webhook(drop_pending_updates=True)
    
    logger.info("Bot started successfully")
    
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await db.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())