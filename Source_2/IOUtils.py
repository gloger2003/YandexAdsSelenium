from pprint import pprint
import os
from typing import Callable, List, Union

# import logger

from loguru import logger

DIR_NAME = './PREFS'

HTTP_PROXY_FILE_NAME = f'./{DIR_NAME}/HTTP_PROXIES.txt'
SOCKS5_PROXY_FILE_NAME = f'./{DIR_NAME}/SOCKS5_PROXIES.txt'

HTTP_PROXY_WARM_UP_FILE_NAME = f'./{DIR_NAME}/HTTP_WARM_UP_PROXIES.txt'
SOCKS5_PROXY_WARM_UP_FILE_NAME = f'./{DIR_NAME}/SOCKS5_WARM_UP_PROXIES.txt'

REQ_TEXTS_WARM_UP_FILE_NAME = f'./{DIR_NAME}/REQ_TEXTS_WARM_UP.txt'
REQ_TEXTS_FILE_NAME = f'./{DIR_NAME}/REQ_TEXTS.txt'

TARGET_DOMENS_FILE_NAME = f'./{DIR_NAME}/TARGET_DOMENS.txt'
IGNORED_DOMENS_FILE_NAME = f'./{DIR_NAME}/IGNORED_DOMENS.txt'

WORK_TIMINGS_FILE_NAME = f'./{DIR_NAME}/WORK_TIMINGS.txt'
SLEEP_TIMINGS_FILE_NAME = f'./{DIR_NAME}/SLEEP_TIMINGS.txt'

AUTH_DATA_FILE_NAME = f'./{DIR_NAME}/AUTH_DATA.txt'
RUCAPTCHA_KEY_FILE_NAME = f'./{DIR_NAME}/RUCAPTCHA_KEY.txt'


if not os.path.exists(DIR_NAME):
    os.mkdir(DIR_NAME)


def read_file(file_name: str) -> str:
    text: str = ''
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        logger.error(f'Файл "{file_name}" не найден, создан новый!')
        open(file_name, 'w', encoding='utf-8').close()
    except Exception as e:
        logger.error(f'Ошибка при открытии файла "{file_name}"')
    return text


def format_proxies(bad_proxies: List[str], proxy_type: str) -> List[str]:
    return [f'{proxy_type}://{proxy}'
            for proxy in bad_proxies
            if proxy.strip() != '']


def get_http_proxies() -> List[str]:
    return format_proxies(read_file(HTTP_PROXY_FILE_NAME).split('\n'), 'http')


def get_socks_proxies() -> List[str]:
    return format_proxies(
        read_file(SOCKS5_PROXY_FILE_NAME).split('\n'), 'socks5')


def get_proxy_list() -> List[str]:
    return (get_http_proxies() +
            get_socks_proxies())


def get_http_warm_up_proxies() -> List[str]:
    return format_proxies(
        read_file(HTTP_PROXY_WARM_UP_FILE_NAME).split('\n'), 'http')


def get_socks_warm_up_proxies() -> List[str]:
    return format_proxies(
        read_file(SOCKS5_PROXY_WARM_UP_FILE_NAME).split('\n'), 'socks5')


def get_warm_up_proxies() -> List[str]:
    return (get_http_warm_up_proxies() +
            get_socks_warm_up_proxies())


def get_req_warm_up_texts() -> List[str]:
    return read_file(REQ_TEXTS_WARM_UP_FILE_NAME).split('\n')


def get_req_texts() -> List[str]:
    return read_file(REQ_TEXTS_FILE_NAME).split('\n')


def get_target_domens() -> List[str]:
    return [k.strip() for k in
            read_file(TARGET_DOMENS_FILE_NAME).split('\n')]


def get_ignored_domens() -> List[str]:
    return [k.strip() for k in
            read_file(IGNORED_DOMENS_FILE_NAME).split('\n')]


def get_work_timings() -> List[str]:
    return read_file(WORK_TIMINGS_FILE_NAME).split('\n')


def get_sleep_timings() -> List[str]:
    return read_file(SLEEP_TIMINGS_FILE_NAME).split('\n')


def get_auth_data() -> List[str]:
    return [k.strip() for k in
            read_file(AUTH_DATA_FILE_NAME).split('\n')]


def get_rucaptcha_key() -> str:
    return read_file(RUCAPTCHA_KEY_FILE_NAME).split('\n')[0].strip()


def get_user_input(message: str,
                   convert_to: Callable,
                   default_value: Union[int, float, str, bool],
                   error_message: str = 'Неверные данные!',
                   loop: bool = False) -> Union[int, float, str, bool]:
    while True:
        try:
            user_value = input(
                f'{message}\nТип: {convert_to}'
                f'\nЗначение по-умолчанию: {default_value}\nВаш ввод: ')
            convertedValue = convert_to(user_value)
        except ():
            logger.error(error_message)
            logger.error(f'Значение [{user_value}] невозможно '
                         f'конвертировать в тип [{convert_to}]')

            if loop:
                logger.error('Попробуйте ввести другое значение')
            else:
                logger.warning('Установлено значение по-умолчанию: '
                               f'{default_value}')
                return default_value
        else:
            break
    return convertedValue


if __name__ == '__main__':
    pprint(get_proxy_list())
