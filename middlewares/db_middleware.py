from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from database.db_manager import DatabaseManager


class DatabaseMiddleware(BaseMiddleware):
    """Middleware to pass database manager to handlers"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        data['db'] = self.db
        return await handler(event, data)
