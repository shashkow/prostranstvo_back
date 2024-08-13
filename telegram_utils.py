import requests
import logging
import config

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    for chat_id in config.TELEGRAM_CHAT_IDS:
        data = {'chat_id': chat_id, 'text': message}
        response = requests.post(url, json=data)
        if response.status_code != 200:
            logging.error(f"Failed to send message: {response.text}")
            raise Exception(f"Failed to send message: {response.text}")
