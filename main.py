import requests
import telegram
from environs import Env
import time
import logging


class BotLogsHandler(logging.Handler):
    def __init__(self, tg_chat_id, bot, level=logging.NOTSET):
        super().__init__(level=level)
        self.tg_chat_id = tg_chat_id
        self.bot = bot

    def emit(self, record):
        log_entry = self.format(record)
        self.bot.send_message(self.tg_chat_id,   text=log_entry)


def get_response(url, headers, payload=None):
    response = requests.get(url,  headers=headers, params=payload)
    response.raise_for_status()
    return response.json()


if __name__ == '__main__':
    env = Env()
    env.read_env()
    telegram_bot_token = env.str('TELEGRAM_BOT_TOKEN')
    tg_chat_id = env.str('TG_CHAT_ID')
    dvmn_api_tiken = env.str('DVMN_API_TOKEN')
    bot = telegram.Bot(token=telegram_bot_token)
    headers = {"Authorization": 'Token '+dvmn_api_tiken}
    api_url = 'https://dvmn.org/api/long_polling/'
    payload = None

    bot_logger = logging.getLogger("Bot logger")
    bot_logger.setLevel(logging.INFO)
    bot_logger.addHandler(BotLogsHandler(tg_chat_id, bot))
    bot_logger.info("Бот запущен")

    while True:
        try:
            api_message = get_response(api_url, headers, payload)
            if api_message['status'] == 'found':
                payload = None
                new_attempts = api_message['new_attempts']
                is_negative = new_attempts[0]['is_negative']
                if is_negative:
                    bot.send_message(chat_id=tg_chat_id, text=f"Преподаватель проверил работу: {new_attempts[0]['lesson_title']}\n\nК сожалению, надо исправить")
                else:
                    bot.send_message(chat_id=tg_chat_id, text=f"Преподаватель проверил работу: {new_attempts[0]['lesson_title']}\n\nУра, можно делать следующий урок!")
                bot_logger.info('Пользователь получил сообщение')
            else:
                timestamp = api_message['timestamp_to_request']
                payload = {'timestamp': timestamp}

        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            bot_logger.error('Бот упал с ошибкой: ')
            bot_logger.error('Отсутствует подключение к интернету')
            time.sleep(60)
        except Exception as err:
            bot_logger.error('Бот упал с ошибкой: ')
            bot_logger.exception(err)
