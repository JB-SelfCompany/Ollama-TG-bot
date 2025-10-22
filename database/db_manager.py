import aiosqlite
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Async SQLite database manager for bot data"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._connection: Optional[aiosqlite.Connection] = None
    
    async def init_db(self):
        """Initialize database and create tables"""
        self._connection = await aiosqlite.connect(self.db_path)
        self._connection.row_factory = aiosqlite.Row
        
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY,
                history_mode TEXT DEFAULT 'without_history',
                selected_model TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS message_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        await self._connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_message_history_user_id
            ON message_history(user_id, created_at DESC)
        """)
        
        await self._connection.commit()
        logger.info("Database initialized successfully")
    
    async def get_user_settings(self, user_id: int) -> Dict[str, Any]:
        """Get user settings"""
        async with self._connection.execute(
            "SELECT * FROM user_settings WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    'history_mode': row['history_mode'],
                    'selected_model': row['selected_model']
                }
        
        # Create default settings (history OFF by default)
        await self.create_user(user_id)
        return {
            'history_mode': 'without_history',
            'selected_model': None
        }
    
    async def create_user(self, user_id: int, username: str = None, first_name: str = None):
        """Create new user and settings"""
        try:
            await self._connection.execute(
                "INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
                (user_id, username, first_name)
            )
            await self._connection.execute(
                "INSERT OR IGNORE INTO user_settings (user_id) VALUES (?)",
                (user_id,)
            )
            await self._connection.commit()
        except Exception as e:
            logger.error(f"Error creating user: {e}")
    
    async def update_setting(self, user_id: int, setting_name: str, value: Any):
        """Update user setting"""
        await self._connection.execute(
            f"UPDATE user_settings SET {setting_name} = ? WHERE user_id = ?",
            (value, user_id)
        )
        await self._connection.commit()
    
    async def get_message_history(self, user_id: int, limit: int = 20) -> List[Dict[str, str]]:
        """Get user message history"""
        async with self._connection.execute(
            """
            SELECT user_message, bot_response
            FROM message_history
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (user_id, limit)
        ) as cursor:
            rows = await cursor.fetchall()
            # Reverse to get chronological order
            messages = [
                {'user': row['user_message'], 'bot': row['bot_response']}
                for row in reversed(rows)
            ]
            return messages
    
    async def add_message(self, user_id: int, user_message: str, bot_response: str):
        """Add message to history"""
        await self._connection.execute(
            "INSERT INTO message_history (user_id, user_message, bot_response) VALUES (?, ?, ?)",
            (user_id, user_message, bot_response)
        )
        await self._connection.commit()
        
        # Keep only last N messages
        await self._connection.execute(
            """
            DELETE FROM message_history
            WHERE user_id = ?
            AND id NOT IN (
                SELECT id FROM message_history
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            )
            """,
            (user_id, user_id, 100)
        )
        await self._connection.commit()
    
    async def clear_history(self, user_id: int):
        """Clear user message history"""
        await self._connection.execute(
            "DELETE FROM message_history WHERE user_id = ?",
            (user_id,)
        )
        await self._connection.commit()
    
    async def close(self):
        """Close database connection"""
        if self._connection:
            await self._connection.close()
            logger.info("Database connection closed")