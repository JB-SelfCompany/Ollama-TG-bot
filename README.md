# <div align="center"> 🤖 Ollama AI Telegram Bot

<div align="center">

[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.13%2B-blue?logo=python)](https://www.python.org/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)](https://telegram.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-blue)](https://docs.aiogram.dev/)

Интеллектуальный Telegram-бот с локальной AI-моделью Ollama, поддержкой веб-поиска и анализа изображений. Бот работает полностью на вашем сервере без зависимости от сторонних API для генерации ответов.

</div>

## 🌟 Особенности

### 🧠 Локальная AI-модель
- Работа с любыми моделями Ollama (Llama, Qwen, DeepSeek и др.)
- Полный контроль над AI без зависимости от внешних API
- Возможность переключения между моделями в реальном времени
- Поддержка vision-моделей для анализа изображений

### 🔍 Умный веб-поиск
- Интеграция с DuckDuckGo для актуальной информации
- Автоматический поиск при вопросах, заканчивающихся на '?'
- Парсинг контента веб-страниц для глубокого анализа
- Контекстуализация результатов поиска для AI-модели

### 🖼️ Анализ изображений
- Распознавание объектов и сцен на фотографиях
- Описание содержимого изображений
- Поддержка multimodal vision-моделей (Qwen2.5-VL и др.)
- Возможность задавать вопросы об изображении через caption

### 💬 Управление диалогами
- Переключаемая история сообщений (вкл/выкл)
- Контекстуальные ответы с учетом предыдущих сообщений
- Очистка истории одной командой
- Ограничение глубины контекста для оптимизации

### ⚙️ Гибкая настройка
- Выбор AI-модели через интерактивное меню
- Настройка параметров поиска и тайм-аутов
- Автоматическое разделение длинных ответов
- Персональные настройки для каждого пользователя

## 🛠 Технологический стек

### Core Framework
- **Python 3.13+** - Современные возможности языка
- **aiogram 3.x** - Асинхронный фреймворк для Telegram Bot API
- **Ollama** - Локальные LLM модели (Llama, Qwen, DeepSeek и др.)
- **aiosqlite** - Асинхронная работа с базой данных

### AI & Search
- **Ollama API** - Локальные языковые модели
- **DuckDuckGo** - Веб-поиск без ограничений API
- **BeautifulSoup4** - Парсинг HTML-контента
- **Requests** - HTTP-запросы для web scraping

### Utilities
- **python-dotenv** - Управление конфигурацией
- **asyncio** - Асинхронное программирование

## 📋 Предварительные требования

### Системные требования
- Python 3.13 или выше
- Ollama (установленный локально)
- 8GB+ VRAM (зависит от размера модели)
- GPU рекомендуется (но не обязательна)

### Необходимые компоненты

**1. Установка Python с помощью pyenv (рекомендуется)**

pyenv позволяет легко управлять несколькими версиями Python на одной системе[web:54][web:55].

**Linux/Ubuntu:**

Установка зависимостей
```bash
sudo apt-get update
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm
libncurses5-dev libncursesw5-dev xz-utils tk-dev
libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev git
```

Установка pyenv
```bash
curl https://pyenv.run | bash
```

Добавление в ~/.bashrc или ~/.zshrc
```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
```

Перезагрузка оболочки
```bash
exec "$SHELL"
```

**macOS:**

Установка XCode Command Line Tools
```bash
xcode-select --install
```

Установка зависимостей через Homebrew
```bash
brew install openssl readline sqlite3 xz zlib
```

Установка pyenv через Homebrew
```bash
brew update
brew install pyenv
```

Добавление в ~/.zshrc (для zsh) или ~/.bash_profile (для bash)
```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init --path)"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
```

Перезагрузка оболочки
```bash
exec "$SHELL"
```

**Windows:**

Установка pyenv-win через PowerShell (от имени администратора)
```bash
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
```

Или через Git
```bash
git clone https://github.com/pyenv-win/pyenv-win.git "$HOME/.pyenv"
```

Добавьте переменные окружения:
```bash
[System.Environment]::SetEnvironmentVariable('PYENV',$env:USERPROFILE + ".pyenv\pyenv-win","User")
[System.Environment]::SetEnvironmentVariable('PYENV_HOME',$env:USERPROFILE + ".pyenv\pyenv-win","User")
[System.Environment]::SetEnvironmentVariable('path', $env:USERPROFILE + ".pyenv\pyenv-win\bin;" + $env:USERPROFILE + ".pyenv\pyenv-win\shims;" + [System.Environment]::GetEnvironmentVariable('path', "User"),"User")
```

Перезапустите PowerShell

**Использование pyenv:**

Просмотр доступных версий Python
```bash
pyenv install --list
```

Установка Python 3.12 (или новее)
```bash
pyenv install 3.12.11
```

Установка Python 3.13 (рекомендуется)
```bash
pyenv install 3.13.5
```

Установка локальной версии для проекта
```bash
cd /path/to/ollama-telegram-bot
pyenv local 3.13.5
```

Проверка текущей версии
```bash
python --version
pyenv version
```

**2. Установка Ollama**

Linux
```bash
curl https://ollama.ai/install.sh | sh
```

macOS
```bash
brew install ollama
```

Windows
```bash
Скачайте установщик с https://ollama.ai
```

**3. Загрузка AI-модели**

Быстрая модель для начала (рекомендуется)
```bash
ollama pull llama2:latest
```

Или более продвинутая модель
```bash
ollama pull qwen2.5:14b
```

Для анализа изображений
```bash
ollama pull qwen2.5vl:7b
```

**4. Telegram Bot Token**

Получите токен у [@BotFather](https://t.me/botfather):
1. Отправьте `/newbot`
2. Следуйте инструкциям
3. Сохраните полученный токен

## 📦 Установка

### 1. Клонируйте репозиторий

```bash
git clone hhttps://github.com/JB-SelfCompany/Ollama-TG-bot
cd ollama-tg-bot
```

### 2. Создайте виртуальное окружение

**С использованием pyenv (рекомендуется):**

Создайте виртуальное окружение
```bash
pyenv virtualenv 3.13.5 venv
```

Установите нужную версию Python для проекта
```bash
pyenv local venv
```

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

### 4. Настройте конфигурацию

```bash
Создайте файл `.env` в корне проекта (пример .env.example):
```

```bash
# Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here
DATABASE_PATH=bot_data.db

# Ollama Settings
OLLAMA_URL=http://localhost:11434
DEFAULT_MODEL=qwen3:14b-q8_0

# Search Settings
SEARCH_ENABLED=true
SEARCH_REGION=ru-ru
SEARCH_MAX_RESULTS=8
SEARCH_PAGES_TO_SCRAPE=4

# Performance Limits
MAX_HISTORY_LENGTH=20
MAX_MESSAGE_LENGTH=4000
REQUEST_TIMEOUT=300
```

### 5. Запустите Ollama

Запустите Ollama-сервер
```bash
ollama serve
```

В отдельном терминале проверьте доступность
```bash
curl http://localhost:11434
```

## 🚀 Запуск

### Запуск бота

```bash
python bot_main.py
```

При успешном запуске вы увидите:

```bash
INFO - Bot started successfully
INFO - Search service initialized: True
```

### Запуск в фоновом режиме (Linux)

С использованием screen
```bash
screen -S ollama-bot
python bot_main.py
```

Нажмите Ctrl+A, затем D для отсоединения

С использованием systemd
```bash
sudo nano /etc/systemd/system/ollama-bot.service
```

Пример systemd service файла:

```bash
[Unit]
Description=Ollama TG Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=user
Group=user
WorkingDirectory=/home/user/ollama-tg-bot

# Execute bot
ExecStart=/bin/bash -c 'source /home/user/.pyenv/versions/3.13.5/envs/venv/bin/activate && cd /home/user/ollama-tg-bot && /home/user/.pyenv/versions/3.13.5/envs/venv/bin/python3.13 bot_main.py'

# Restart configuration
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=ollama-tg-bot

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable ollama-bot
sudo systemctl start ollama-bot
```

## 💬 Использование

### Основные команды

- `/start` - Запустить бота и увидеть меню

### Интерактивное меню

Бот использует кнопочное меню для удобного управления:

1. **История On/Off** - Включить/выключить сохранение контекста диалога
2. **Выбор модели** - Переключиться на другую установленную модель
3. **Очистить историю** - Удалить весь контекст диалога

### Примеры использования

**Обычный вопрос (без поиска):**  
Пользователь: Объясни, что такое машинное обучение  
Бот: [Ответ на основе знаний модели]

**Вопрос с веб-поиском:**  
Пользователь: Какая погода в Москве сегодня?  
Бот: 🔍 Выполняю поиск в Google...  
🤖 Анализирую результаты поиска...  
[Актуальная информация из интернета]  

**Анализ изображения:**  
Пользователь: [Отправляет фото]  
или [Фото с подписью "Что это за порода собаки?"]  
Бот: [Описание изображения или ответ на вопрос]  

**Работа с историей:**  
Пользователь: Расскажи о Python  
Бот: [Ответ о Python]  

Пользователь: А какие у него преимущества  
Бот: [Ответ с учетом контекста предыдущего сообщения]  

## 📁 Структура проекта

```
ollama-tg-bot/
├── bot_main.py # Точка входа приложения
├── config.py # Конфигурация и настройки
├── requirements.txt # Зависимости Python
├── .env # Переменные окружения (не в git)
├── .env.example # Шаблон конфигурации
│
├── handlers/ # Обработчики сообщений
│ ├── init.py
│ ├── user_handlers.py # Текстовые сообщения и команды
│ └── photo_handlers.py # Обработка изображений
│
├── database/ # Слой работы с данными
│ ├── init.py
│ └── db_manager.py # SQLite менеджер
│
├── services/ # Бизнес-логика
│ ├── init.py
│ ├── ollama_service.py # Интеграция с Ollama API
│ └── search_service.py # DuckDuckGo веб-поиск
│
├── keyboards/ # UI элементы
│ ├── init.py
│ └── main_keyboard.py # Reply-клавиатуры
│
├── middlewares/ # Middleware компоненты
│ ├── init.py
│ └── db_middleware.py # Database middleware
│
└── utils/ # Утилиты
├── init.py
├── message_splitter.py # Разделение длинных сообщений
└── helpers.py # Вспомогательные функции
```

## 🏗 Архитектура

### Асинхронная обработка

Весь код построен на async/await паттернах:

- Неблокирующие запросы к Ollama API
- Параллельный парсинг веб-страниц при поиске
- Эффективная работа с множеством пользователей

### База данных

SQLite с тремя основными таблицами:

- `users` - Пользовательские данные
- `user_settings` - Персональные настройки (модель, режим истории)
- `message_history` - История диалогов

### Веб-поиск

DuckDuckGo HTML-интерфейс с оптимизациями:

- Параллельный scraping до N страниц
- Умная экстракция контента (удаление навигации, footer)
- Ограничение размера контекста для AI

### AI Integration

Гибкая интеграция с Ollama:

- Два режима: обычный и с контекстом поиска
- Настраиваемые тайм-ауты для больших моделей
- Автоматическое управление контекстным окном

## ⚙️ Настройка

### Параметры конфигурации

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `BOT_TOKEN` | Токен Telegram-бота | - |
| `OLLAMA_URL` | URL Ollama API | `http://localhost:11434` |
| `DEFAULT_MODEL` | Модель по умолчанию | `qwen3:14b-q8_0t` |
| `SEARCH_ENABLED` | Включить веб-поиск | `true` |
| `SEARCH_MAX_RESULTS` | Макс. результатов поиска | `8` |
| `SEARCH_PAGES_TO_SCRAPE` | Кол-во страниц для парсинга | `4` |
| `MAX_HISTORY_LENGTH` | Глубина истории | `20` |
| `REQUEST_TIMEOUT` | Тайм-аут запросов (сек) | `300` |

### Рекомендации по моделям

**Быстрые модели (4-8GB RAM):**
- `llama2:7b` - Универсальная модель
- `mistral:7b` - Отличное качество/скорость
- `phi3:mini` - Очень быстрая

**Качественные модели (16GB+ RAM):**
- `qwen2.5:14b` - Лучший выбор для русского языка
- `llama3:13b` - Высокое качество ответов
- `mixtral:8x7b` - Топовая модель (требует GPU)

**Vision модели (для изображений):**
- `qwen2.5vl:7b` - Multimodal модель
- `llava:13b` - Анализ изображений

### Оптимизация производительности

**Для медленных систем:**
```bash
DEFAULT_MODEL=phi3:mini
REQUEST_TIMEOUT=180
SEARCH_PAGES_TO_SCRAPE=2
MAX_HISTORY_LENGTH=10
```

**Для мощных систем:**
```bash
DEFAULT_MODEL=qwen2.5:14b
REQUEST_TIMEOUT=600
SEARCH_PAGES_TO_SCRAPE=8
MAX_HISTORY_LENGTH=30
```

## 🔧 Разработка

### Добавление новых обработчиков

1. Создайте файл в `handlers/`:

```bash
from aiogram import Router, F
from aiogram.types import Message

router = Router(name='my_handler')

@router.message(F.text == "новая команда")
async def handle_new_command(message: Message):
await message.answer("Ответ на команду")
```

2. Зарегистрируйте в `bot_main.py`:

```bash
from handlers import my_handler

dp.include_router(my_handler.router)
```

### Добавление новых сервисов

Создайте класс в `services/`:

```bash
class MyService:
def init(self, config: Config):
self.config = config

async def process(self, data: str) -> str:
    # Ваша логика
    return result
```

### Логирование

Бот использует встроенный Python logging:

```bash
import logging
logger = logging.getLogger(name)

logger.info("Информация")
logger.warning("Предупреждение")
logger.error("Ошибка", exc_info=True)
```

## 🐛 Решение проблем

### Ollama не отвечает

Проверьте, запущен ли сервер
```bash
curl http://localhost:11434
```

Перезапустите Ollama
```bash
pkill ollama
ollama serve
```

### Модель работает медленно

- Используйте меньшую модель (`phi3:mini`)
- Увеличьте `REQUEST_TIMEOUT` в `.env`
- Отключите историю диалога
- Используйте GPU, если доступен

### Ошибка при поиске

Отключите поиск в .env
```bash
SEARCH_ENABLED=false
```

### База данных заблокирована

Удалите и пересоздайте БД
```bash
rm bot_data.db
python bot_main.py
```

### Проблемы с версией Python

Проверьте версию Python
```bash
python --version
```

С pyenv переключитесь на нужную версию
```bash
pyenv local 3.12.11
pyenv versions
```

## 📝 Требования к зависимостям

Минимальные версии библиотек указаны в `requirements.txt`:

```
aiogram>=3.4.0
aiosqlite>=0.19.0
requests>=2.31.0
beautifulsoup4>=4.12.0
python-dotenv>=1.0.0
ollama>=0.1.0
```

## 🤝 Контрибьюция

Вклад в проект приветствуется! Пожалуйста:

1. Fork репозиторий
2. Создайте feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit изменения (`git commit -m 'Add AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

### Стандарты кода

- Следуйте PEP 8
- Добавляйте type hints
- Пишите docstrings для функций
- Используйте async/await для IO операций

## 📄 Лицензия

Этот проект распространяется под лицензией GPLv3. Смотрите файл [LICENSE](LICENSE) для подробностей.

## 🙏 Благодарности

- [Ollama](https://ollama.ai/) - За потрясающий фреймворк локальных LLM
- [aiogram](https://github.com/aiogram/aiogram) - За отличную библиотеку для Telegram Bot API
- [DuckDuckGo](https://duckduckgo.com/) - За свободный веб-поиск
- [pyenv](https://github.com/pyenv/pyenv) - За удобное управление версиями Python

## 📧 Контакты

Если у вас есть вопросы или предложения:

- Создайте [Issue](https://github.com/JB-SelfCompany/Ollama-TG-bot/issues)
- Pull Request всегда приветствуются

## 🗺️ Roadmap

- [ ] Интеграция с дополнительными поисковыми системами
- [ ] Поддержка голосовых сообщений
- [ ] RAG (Retrieval-Augmented Generation) с документами
- [ ] Мультиязычная поддержка интерфейса

---

<div align="center">
  
**Сделано с ❤️ для open-source сообщества**

⭐ Если проект вам помог, поставьте звезду на GitHub!

[Наверх](#-особенности)

</div>
