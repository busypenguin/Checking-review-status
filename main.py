import requests
import telegram
from environs import Env


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

    while True:
        try:
            headers = {"Authorization": 'Token '+dvmn_api_tiken}
            url = 'https://dvmn.org/api/long_polling/'
            response_for_checking_timestamp = get_response(url, headers)
            if response_for_checking_timestamp:
                timestamp = response_for_checking_timestamp['timestamp_to_request']
                payload = {'timestamp': timestamp}
                response_for_getting_review = get_response(url, headers, payload)
                new_attempts = response_for_getting_review['new_attempts']
                is_negative = new_attempts[0]['is_negative']
                if is_negative:
                    bot.send_message(chat_id=tg_chat_id, text=f"Преподаватель проверил работу: {new_attempts[0]['lesson_title']}\n\nК сожалению, надо исправить")
                else:
                    bot.send_message(chat_id=tg_chat_id, text=f"Преподаватель проверил работу: {new_attempts[0]['lesson_title']}\n\nУра, можно делать следующий урок!")

        except requests.exceptions.ReadTimeout:
            print('Слишком долгая загрузка')
        except requests.exceptions.ConnectionError:
            print('Отсутствует подключение к интернету')
        except KeyError:   # из-за 30 строки
            continue
