import os

# Flask
SECRET_KEY = os.getenv('SECRET_KEY', 'secret_key')

# Database
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:1111@localhost/users')

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'your_bot_token')
TELEGRAM_CHAT_IDS = os.getenv('TELEGRAM_CHAT_IDS', 'chat_id_1, chat_id_2').split(',')

# Notisend
PROJECT = os.getenv('PROJECT', 'project')
API_KEY = os.getenv('API_KEY', 'api_key')
