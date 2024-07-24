import requests
import telegram
from environs import Env
import time


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
    url = 'https://dvmn.org/api/long_polling/'
    payload = None

    bot.send_message(chat_id=tg_chat_id, text="Бот запущен")

    while True:
        try:
            response_for_checking_timestamp_to_request = get_response(url, headers, payload)
            if response_for_checking_timestamp_to_request['status'] == 'found':
                payload = None
                new_attempts = response_for_checking_timestamp_to_request['new_attempts']
                is_negative = new_attempts[0]['is_negative']
                if is_negative:
                    bot.send_message(chat_id=tg_chat_id, text=f"Преподаватель проверил работу: {new_attempts[0]['lesson_title']}\n\nК сожалению, надо исправить")
                else:
                    bot.send_message(chat_id=tg_chat_id, text=f"Преподаватель проверил работу: {new_attempts[0]['lesson_title']}\n\nУра, можно делать следующий урок!")
            else:
                timestamp = response_for_checking_timestamp_to_request['timestamp_to_request']
                payload = {'timestamp': timestamp}

        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            print('Отсутствует подключение к интернету')
            time.sleep(60)
