from __future__ import annotations

import os
from pprint import pprint
from typing import Callable, Union

from loguru import logger


DIR_NAME = './ScriptOptions'

HTTP_PROXY_FILE_NAME = f'./{DIR_NAME}/http_proxies.cfg'
SOCKS_PROXY_FILE_NAME = f'./{DIR_NAME}/socks_proxies.cfg'

KEYWORDS_FILE_NAME = f'./{DIR_NAME}/keywords.cfg'

TARGET_DOMENS_FILE_NAME = f'./{DIR_NAME}/target_domens.cfg'
IGNORED_DOMENS_FILE_NAME = f'./{DIR_NAME}/ignored_domens.cfg'

WORK_TIMINGS_FILE_NAME = f'./{DIR_NAME}/work_timings.cfg'
SLEEP_TIMINGS_FILE_NAME = f'./{DIR_NAME}/sleep_timings.cfg'

AUTH_DATA_FILE_NAME = f'./{DIR_NAME}/auth_data.cfg'
RUCAPTCHA_KEY_FILE_NAME = f'./{DIR_NAME}/rucaptcha_key.cfg'


if not os.path.exists(DIR_NAME):
    os.mkdir(DIR_NAME)

# Проходимся по всем локальным переменным
for name, file_name in locals().copy().items():
    # Находим все константы путей
    if name.endswith('_FILE_NAME'):
        try:
            # Преобразовываем в формат:
            # "{Папка}/{ИМЯ_КОНСТАНТЫ_БЕЗ_FILE_NAME}.txt"
            # file_name = (f'{DIR_NAME}/'
            #              f'{name.replace("_FILE_NAME", ".txt")}')
            if not os.path.exists(file_name):
                open(file_name, 'w', encoding='utf-8').close()
        except Exception as e:
            logger.error(e)


def read_file(file_name: str) -> str:
    text = ''
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        logger.error(f'Файл "{file_name}" не найден, создан новый!')
        open(file_name, 'w', encoding='utf-8').close()
    except Exception as e:
        logger.error(f'Ошибка при открытии файла "{file_name}"')
    finally:
        f.close()
    return text


def format_proxies(bad_proxies: list[str], proxy_type: str) -> list[str]:
    return [f'{proxy_type}://{proxy}'
            for proxy in bad_proxies
            if proxy.strip() != '']


def get_http_proxies() -> list[str]:
    return format_proxies(read_file(HTTP_PROXY_FILE_NAME).split('\n'), 'http')


def get_socks_proxies() -> list[str]:
    return format_proxies(
        read_file(SOCKS_PROXY_FILE_NAME).split('\n'), 'socks5')


def get_proxies() -> list[str]:
    return (get_http_proxies() +
            get_socks_proxies())


def get_keywords() -> list[str]:
    return read_file(KEYWORDS_FILE_NAME).split('\n')


def get_target_domens() -> list[str]:
    return [k.strip() for k in
            read_file(TARGET_DOMENS_FILE_NAME).split('\n')]


def get_ignored_domens() -> list[str]:
    return [k.strip() for k in
            read_file(IGNORED_DOMENS_FILE_NAME).split('\n')]


def get_work_timings() -> list[str]:
    return read_file(WORK_TIMINGS_FILE_NAME).split('\n')


def get_sleep_timings() -> list[str]:
    return read_file(SLEEP_TIMINGS_FILE_NAME).split('\n')


def get_auth_data() -> list[str]:
    return [k.strip() for k in
            read_file(AUTH_DATA_FILE_NAME).split('\n')]


def get_rucaptcha_key() -> str:
    return read_file(RUCAPTCHA_KEY_FILE_NAME).split('\n')[0].strip()


def print_msg(message: str) -> int:
    message_lines = message.split('\n')

    delimiter = '='
    max_line_len = max([len(k) for k in message_lines]) + 6

    print(delimiter * max_line_len)
    for line in message_lines:
        ws = ' ' * (max_line_len - len(line) - 5)
        print(f'|| {line}{ws}||')
    print(delimiter * max_line_len)
    return max_line_len


def get_user_input(message: str,
                   convert_to: Callable,
                   default_value: Union[int, float, str, bool],
                   error_message: str = 'Неверные данные!',
                   loop: bool = False) -> Union[int, float, str, bool]:
    while True:
        try:
            print('\n')
            msg = (f'{message}\n  Тип: {convert_to}'
                   f'\n  Значение по-умолчанию: {default_value}')
            border_line = '-' * (print_msg(msg) - 2)
            print(f'+{border_line}+')
            user_value = input('| ВВОД | ')
            print(f'+{border_line}+')
            converted_value = convert_to(user_value)
        except Exception:
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
    return converted_value


if __name__ == '__main__':
    get_user_input('Сколько страниц нужно проверить?',
                   int, 1, 'Неверное значение', loop=True)
