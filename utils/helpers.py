import logging
import re
from typing import List

logger = logging.getLogger(__name__)


async def send_long_message(bot, chat_id: int, text: str, max_length: int = 4000):
    """Split and send long messages"""
    while text:
        part = text[:max_length]
        text = text[max_length:]
        await bot.send_message(chat_id, part)


def format_messages_for_context(messages: List[dict]) -> str:
    """Format message history for context"""
    return "\n".join(
        f"Пользователь: {msg['user']}\nБот: {msg['bot']}"
        for msg in messages
    )


def escape_html(text: str) -> str:
    """
    Escape HTML special characters for Telegram
    
    Replaces:
    - < with &lt;
    - > with &gt;
    - & with &amp;
    """
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;'))


def clean_unsupported_html_tags(text: str) -> str:
    """
    Remove unsupported HTML tags from text
    
    Telegram only supports: <b>, <strong>, <i>, <em>, <u>, <ins>, 
    <s>, <strike>, <del>, <span>, <tg-spoiler>, <a>, <code>, <pre>
    
    This function removes all other tags while keeping the content.
    """
    # List of supported tags by Telegram
    supported_tags = [
        'b', 'strong', 'i', 'em', 'u', 'ins', 
        's', 'strike', 'del', 'span', 'tg-spoiler', 
        'a', 'code', 'pre', 'blockquote'
    ]
    
    # Remove unsupported tags but keep their content
    # Pattern: <tag> or </tag> or <tag attr="value">
    pattern = r'</?(?!(?:' + '|'.join(supported_tags) + r')\b)[^>]+>'
    cleaned = re.sub(pattern, '', text)
    
    return cleaned


def strip_all_html_tags(text: str) -> str:
    """
    Remove all HTML tags from text
    
    Use this when you want plain text without any formatting
    """
    return re.sub(r'<[^>]+>', '', text)