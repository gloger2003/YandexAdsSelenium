from __future__ import annotations

import os
import shutil
import time

import requests
from loguru import logger

import IOUtils
from Driver import Driver


def check_user_subscribe(ads_bot: AdsBot):
    """ Проверяет наличие подписки у пользователя """
    try:
        auth_data = IOUtils.get_auth_data()
        login = auth_data[0]
        password = auth_data[1]

        json_res = requests.get(f'http://control-panel123.herokuapp.com/'
                                f'get_user?login={login}&'
                                f'password={password}', timeout=10).json()

        if json_res['status'] == 'OK':
            if json_res['check']:
                if not ads_bot.is_subscribed:
                    ads_bot.is_subscribed = True
                    logger.info('Подписка успешно подтверждена! '
                                'Данные подписки:')
                    logger.info(f"- Дата начала: "
                                f"{json_res['start_date']}")
                    logger.info(f"- Дата конца: "
                                f"{json_res['finish_date']}")
            else:
                logger.critical('Подписка закончила время действия! '
                                'Данные подписки:')
                logger.critical(f"- Дата начала: "
                                f"{json_res['start_date']}")
                logger.critical(f"- Дата конца: "
                                f"{json_res['finish_date']}")
                logger.critical('Выход!')
                exit_from_program(ads_bot)

        elif json_res['status'] == 'NOT_FOUND_USER':
            logger.critical('Неверный логин или пароль, '
                            'измените данные в AUTH_DATA.txt!')
            logger.critical('Обратитесь к продавцу, '
                            'возможно это ошибка сервера')
            logger.critical('Выход!')
            exit_from_program(ads_bot)
        else:
            logger.critical('К сожалению, мы не нашли '
                            'ваш профиль в базе данных :(')
            logger.critical('Обратитесь к продавцу для '
                            'решения данной проблемы')
            logger.critical('Пользоваться юотом без подписки нельзя, '
                            'поэтому мы его закрываем!')
            exit_from_program(ads_bot)

    except Exception as e:
        logger.critical('Не удалось подтвердить подписку!')
        logger.critical('Выход!')
        exit_from_program(ads_bot)
    pass


def loop_check_user_subscribe(ads_bot: AdsBot):
    while True:
        check_user_subscribe(ads_bot)
        time.sleep(10)


def exit_from_program(ads_bot: AdsBot):
    ads_bot.is_subscribed = False
    ads_bot.close()
    os._exit(0)


class AdsBot(Driver):
    def __init__(self) -> None:
        self.is_subscribed = False
        super().__init__()


if __name__ == '__main__':
    DEV_MODE = True

    dir_name = './LOGS'
    log_date = time.strftime('%H.%M.%S %d-%m-%Y')
    log_file_name = f'{dir_name}/{log_date}.log'

    if DEV_MODE:
        shutil.rmtree(dir_name)

    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

    logger.add(log_file_name, encoding='utf-8')
    logger.debug('Запустил...')
