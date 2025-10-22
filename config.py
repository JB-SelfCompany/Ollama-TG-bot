import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    """Bot configuration settings"""
    
    # Bot settings
    BOT_TOKEN: str = os.getenv('BOT_TOKEN', '')
    
    # Database settings
    DATABASE_PATH: str = os.getenv('DATABASE_PATH', 'bot_data.db')
    
    # Model settings
    OLLAMA_URL: str = os.getenv('OLLAMA_URL', 'http://localhost:11434')
    DEFAULT_MODEL: str = os.getenv('DEFAULT_MODEL', 'qwen3:14b-q8_0')
    
    # Google Search settings
    SEARCH_ENABLED: bool = os.getenv('SEARCH_ENABLED', 'true').lower() == 'true'
    SEARCH_REGION: str = os.getenv('SEARCH_REGION', 'ru-ru')
    SEARCH_MAX_RESULTS: int = int(os.getenv('SEARCH_MAX_RESULTS', '10'))
    SEARCH_SLEEP_INTERVAL: int = int(os.getenv('SEARCH_SLEEP_INTERVAL', '2'))
    SEARCH_PAGES_TO_SCRAPE: int = int(os.getenv('SEARCH_PAGES_TO_SCRAPE', '5'))  # NEW
    
    # Limits - INCREASED timeout for large models
    MAX_HISTORY_LENGTH: int = int(os.getenv('MAX_HISTORY_LENGTH', '20'))
    MAX_MESSAGE_LENGTH: int = int(os.getenv('MAX_MESSAGE_LENGTH', '4000'))
    REQUEST_TIMEOUT: int = int(os.getenv('REQUEST_TIMEOUT', '300'))