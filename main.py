import requests
import telegram
from environs import Env
import time
from bs4 import BeautifulSoup


def get_response(url, headers, payload=None):
    response = requests.get(url,  headers=headers, params=payload)
    response.raise_for_status()
    return response.json()


def get_improvements(profile_url, lesson_title):
    response = requests.get(profile_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    lessons = soup.find(class_="mb-5").find_all(class_="card")
    for lesson in lessons:
        lesson_text = lesson.text
        if lesson_title in lesson_text:
            improvement = lesson.find(class_="card-body").find(class_="d-flex").find(class_="badge")
            return improvement.text


if __name__ == '__main__':

    env = Env()
    env.read_env()
    telegram_bot_token = env.str('TELEGRAM_BOT_TOKEN')
    tg_chat_id = env.str('TG_CHAT_ID')
    dvmn_api_tiken = env.str('DVMN_API_TOKEN')
    profile_url = env.str('PROFILE_URL')
    bot = telegram.Bot(token=telegram_bot_token)
    headers = {"Authorization": 'Token '+dvmn_api_tiken}
    api_url = 'https://dvmn.org/api/long_polling/'
    payload = None

    bot.send_message(chat_id=tg_chat_id, text="Бот запущен")

    while True:
        try:
            response = get_response(api_url, headers, payload)
            if response['status'] == 'found':
                payload = None
                new_attempts = response['new_attempts']
                is_negative = new_attempts[0]['is_negative']
                lesson_title = new_attempts[0]['lesson_title']
                if is_negative:
                    improvements = get_improvements(profile_url, lesson_title)
                    bot.send_message(chat_id=tg_chat_id, text=f"Преподаватель проверил работу: {new_attempts[0]['lesson_title']}\n\nК сожалению, надо исправить {improvements}")
                else:
                    bot.send_message(chat_id=tg_chat_id, text=f"Преподаватель проверил работу: {new_attempts[0]['lesson_title']}\n\nУра, можно делать следующий урок!")
            else:
                timestamp = response['timestamp_to_request']
                payload = {'timestamp': timestamp}

        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            print('Отсутствует подключение к интернету')
            time.sleep(60)
