from __future__ import annotations

import os
import shutil
import time

import requests
from loguru import logger

import io_utils
from datatypes import TacticalModule, Command
from driver import Driver
from tactical_module import NonTargetAdsClicker, SeoClicker, TargetAdsClicker

import command_executor
from command_executor import CmdExc_SetTModule, CommandExecutor
from command_executor import (CmdExc_Clear,
                              CmdExc_GetValue,
                              CmdExc_GetVersion,
                              CmdExc_Exit,
                              CmdExc_SetTModule,
                              _all_commands)


def check_user_subscribe(ads_bot: AdsBot):
    """ Проверяет наличие подписки у пользователя """
    try:
        auth_data = io_utils.get_auth_data()
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
    ads_bot.close_driver()
    os._exit(0)


def init_logger():
    """ Инициализирует логгер и задаёт ему настройки
        в зависимости от DEV_MODE """
    dir_name = './ScriptLogs'
    log_date = time.strftime('%H.%M.%S %d-%m-%Y')
    log_file_name = f'{dir_name}/{log_date}.log'

    if DEV_MODE:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
        logger.add(log_file_name, encoding='utf-8')
    else:
        logger.add(log_file_name, encoding='utf-8',
                   format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
                          '<level>{level: <8}</level> | '
                          '<level>{message}</level>')

    if not os.path.exists(dir_name):
        os.mkdir(dir_name)


class Commander:
    def __init__(self, ads_bot: AdsBot) -> None:
        self.ads_bot = ads_bot
        self.__command_map: dict[str, CommandExecutor] = {}

        # Записывает все команды в список коммандера,
        # чтобы тот мог работать с ними
        for cls in command_executor.ALL_COMMANDS:
            obj = cls(ads_bot)
            self.__command_map[obj.get_name()] = obj

    def __get_user_input(self) -> Command:
        """ Получает пользовательский ввод и
            преобразует его в Command """
        _user_input = input('</-Введите команду-/> ').rstrip().lstrip()
        _name, *_args = _user_input.split(' ')
        _command = Command(_name, _args)
        return _command

    def find_command(command: Command) -> str:
        pass

    def listen(self):
        while True:
            _command = self.__get_user_input()
            try:
                self.__command_map.get(_command.name).execute(_command)
            except AttributeError as e:
                logger.error('Неизвестная команда:')
                logger.error(f' | Сообщение: {e}')
            pass


class AdsBot(Driver):
    __version__ = '3.0 Dev'

    def __init__(self) -> None:
        super().__init__()

        self.create_new_driver()

        self.is_subscribed = False

        # Все call-модули
        self.__tmodules = [
            TacticalModule('Модуль целевого обхода доменов',
                           'Обходит все целевые домены из КР',
                           TargetAdsClicker(self),
                           '0.1'),
            TacticalModule('Модуль нецелевого обхода доменов',
                           'Обходит все нецелевые домены из КР',
                           NonTargetAdsClicker(self),
                           '0.1'),
            TacticalModule('Модуль обхода СЕО-выдачи',
                           'Обходит все домены из СЕО-выдачи',
                           SeoClicker(self),
                           '0.1')
        ]
        # Индекс call-модуля
        self.__tmodule_id = 0

    def get_current_tmodule(self) -> TacticalModule:
        """ Возвращает выбранный call-модуль """
        return self.__tmodules[self.__tmodule_id]

    def set_current_tmodule(self, tmodule_id: int):
        """ Устанавливает текущий модуль,
            а именно устанавливает значение __tmodule_id """
        tmodules_count = len(self.__tmodules) - 1
        tmodule_id = (tmodule_id
                      if tmodule_id <= tmodules_count
                      else tmodules_count)
        self.__tmodule_id = tmodule_id

    @classmethod
    def get_version(cls):
        """ Возвращает версию AdsBot """
        return cls.__version__


if __name__ == '__main__':
    global DEV_MODE
    DEV_MODE = True

    init_logger()

    ads_bot = AdsBot()
    commander = Commander(ads_bot)
    commander.listen()
    # check_user_subscribe(ads_bot)
