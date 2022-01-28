import requests
import logging
import sys
import os
import time
import telegram

from dotenv import load_dotenv
from logging import Formatter
from http import HTTPStatus
from exceptions import TokenError, ServerError

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)
handler.setFormatter(Formatter(
    '%(asctime)s, %(levelname)s,%(message)s, %(lineno)d, %(funcName)s'))
RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'}


def send_message(bot, message):
    """Функция отправляет сообщение в Telegram."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,)
        logging.info('Сообщение успешно отправлено')
        return True
    except telegram.error.BadRequest as error:
        logging.error(f'Cбой при отправке сообщения в Telegram:{error}')
        return False


def get_api_answer(current_timestamp):
    """Функция делает запрос к эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': 0}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != HTTPStatus.OK:
            logging.error('HTTP-запрос вернул неверный код состояния')
            raise ServerError('HTTP-запрос вернул неверный код состояния')
    except requests.RequestException as error:
        logging.error(f'Эндпоинт недоступен: {error}')
        raise ServerError(error)
    response = response.json()
    return response


def check_response(response):
    """Функция проверяет ответ API на корректность."""
    if not isinstance(response, dict):
        raise TypeError('Формат ответа API отличается от ожидаемого')
    list_hw = response.get('homeworks')
    if list_hw is None:
        logging.error('отсутствуют ожидаемые ключи')
        raise TypeError('отсутствуют ожидаемые ключи')
    if not isinstance(list_hw, list):
        raise TypeError('not list')
    homework = response.get('homeworks')[0]
    return homework


def parse_status(homework):
    """Функция извлекает статус домашней работы."""
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
        if homework_status not in HOMEWORK_STATUSES:
            raise KeyError(f'Статус работы:{homework_status} - '
                           'недокументированный статус домашней работы.')
    except TypeError:
        raise KeyError
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Функция проверяет доступность переменных окружения."""
    SECRET_LIST = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID, }
    for secret_key, secret in SECRET_LIST.items():
        if secret is None:
            logging.critical(
                f'Отсутствует переменная окружения: {secret_key}')
            return False
        logging.info('Токены проверены.')
    return True


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        raise TokenError
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            current_timestamp = response.get(
                'current_date', current_timestamp)
            if homework != []:
                send_message(bot, parse_status(homework))
                time.sleep(RETRY_TIME)
        except Exception as error:
            msg_error = ''
            message = f'Сбой в работе программы: {error}'
            logging.exception(message)
            if msg_error != message:
                if send_message(bot, message):
                    message = message
        time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
