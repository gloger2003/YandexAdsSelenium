from __future__ import annotations
from driver import Driver

import os
from typing import Callable, Type, Union

from loguru import logger

from datatypes import Command
import io_utils


class CommandExecutor:
    def __init__(self, ads_bot: Driver, name: str = ...) -> None:
        self.__name = name
        self._ads_bot = ads_bot
        self._current_command = None
        pass

    def __get_cmd_exc_method(self, command_name: str) -> Callable:
        """ Преобразует имя в имя атрибута и
            возвращает ссылку на атрибут класса """
        _cmd_exc_method = self.__getattribute__(
            f'_cmd_{self.__name}_{command_name}')
        return _cmd_exc_method

    def execute(self, command: Union[Command, str]):
        """ Преобразует команду в атрибут и
            вызывает его с переданными параметрами

            Синтаксис команды:
            ------------------
            `[команда]` \n
            `[команда] [аргументы]` \n
            `[команда] [подкоманда]` \n
            `[команда] [подкоманда] [аргументы]`
        """
        self._current_command = command
        try:
            _exc_cmd = self.__get_cmd_exc_method(command.args[0])
            _exc_cmd(*command.args[1:]) if command.args[1:] else _exc_cmd()
        except IndexError:
            self.__getattribute__(f'_cmd_{self.__name}')()
        except AttributeError:
            self.__getattribute__(f'_cmd_{self.__name}')(*command.args)

    def print_msg(self, msg: str):
        print()
        print(f'____[ CmdExc: {self.__name} ]_____')
        print()
        [print(f'>>> {line}') for line in msg.split('\n')]
        print()

    def get_name(self):
        return self.__name


class CmdExc_GetValue(CommandExecutor):
    def __init__(self, ads_bot: Driver) -> None:
        super().__init__(ads_bot, 'get_value')

    def _cmd_get_value_all(self):
        self.print_msg(
            'Максимальное кол-во страниц:\n'
            f' | max_page_count: {self._ads_bot.max_page_count}\n'
            'Максимальное время нахождения на сайте:\n'
            f' | max_residence_time: {self._ads_bot.max_residence_time}\n'
            'Максимальное кол-во визитов\n'
            f' | max_visit_count: {self._ads_bot.max_visit_count}\n'
            'Режим разработчика:\n'
            f' | DEV_MODE: {self._ads_bot.DEV_MODE}\n'
            'Режим инкогнито:\n'
            f' | incognito_mode: {self._ads_bot.incognito_mode}\n'
            'Текущий прокси-сервер:\n'
            f' | proxy: {self._ads_bot.proxy}\n'
            'Текущий юзер-агент:\n'
            f' | user_agent: {self._ads_bot.user_agent}\n'
            'Текущая геолокация поиска:\n'
            f' | geo: {self._ads_bot.geo}'
        )


class CmdExc_SetValue(CommandExecutor):
    def __init__(self, ads_bot: Driver) -> None:
        super().__init__(ads_bot, 'set_value')

    def _cmd_set_value_max_page_count(self, value: str):
        self._ads_bot.max_page_count = int(value)

    def _cmd_set_value_max_residence_time(self, value: str):
        self._ads_bot.max_residence_time = int(value)

    def _cmd_set_value_max_visit_count(self, value: str):
        self._ads_bot.max_visit_count = int(value)

    def _cmd_set_value_incognito_mode(self, value: str):
        self._ads_bot.incognito_mode = bool(value)

    def _cmd_set_value_proxy(self, value: str):
        self._ads_bot.proxy = value if value != '0' else None

    def _cmd_set_value_user_agent(self, value: str):
        self._ads_bot.user_agent = value if value != '0' else None

    def _cmd_set_value_geo(self, value: str):
        self._ads_bot.geo = value if value != '0' else None


class CmdExc_GetVersion(CommandExecutor):
    def __init__(self, ads_bot: Driver) -> None:
        super().__init__(ads_bot, 'get_version')

    def _cmd_get_version_tmodule(self):
        """ Сообщает версию текущего tmodule """
        _tmodule = self._ads_bot.get_current_tmodule()
        self.print_msg(f'{_tmodule.title}: v{_tmodule.version}')

    def _cmd_get_version_ads_bot(self):
        """ Сообщает текущую версию ads_bot"""
        self.print_msg(f'ads_bot: v{self._ads_bot.get_version()}')


class CmdExc_Exit(CommandExecutor):
    def __init__(self, ads_bot: Driver) -> None:
        super().__init__(ads_bot, 'exit')

    def _cmd_exit(self):
        self.print_msg('Работа завершена!')
        exit(0)


class CmdExc_Clear(CommandExecutor):
    def __init__(self, ads_bot: Driver) -> None:
        super().__init__(ads_bot, 'clear')

    def _cmd_clear(self):
        os.system('cls')


class CmdExc_SetTModule(CommandExecutor):
    def __init__(self, ads_bot: Driver) -> None:
        super().__init__(ads_bot, 'set_tmodule')

    def _cmd_set_tmodule(self, command_id: str):
        self._ads_bot.set_current_tmodule(int(command_id))


class CmdExc_GetTModule(CommandExecutor):
    def __init__(self, ads_bot: Driver) -> None:
        super().__init__(ads_bot, 'get_tmodule')

    def _cmd_get_tmodule(self):
        self.print_msg(f'{self._ads_bot.get_current_tmodule()}')


class CmdExc_Start(CommandExecutor):
    def __init__(self, ads_bot: Driver) -> None:
        super().__init__(ads_bot, 'start')

    def _cmd_start_tmodule_test(self, text: str, page: str):
        _tmodule = self._ads_bot.get_current_tmodule().obj
        _tmodule._process(text, int(page))

    def _cmd_start_tmodule(self):
        self._ads_bot.get_current_tmodule().obj.run()


class CmdExc_WriteToFile(CommandExecutor):
    def __init__(self, ads_bot: Driver) -> None:
        super().__init__(ads_bot, 'w2f')

    def _cmd_w2f(self, basename: str, value: str):
        var_name = f'{basename.upper()}_FILE_NAME'
        file_name = io_utils.__dict__.get(var_name)
        with open(file_name, 'a', encoding='utf-8') as f:
            f.write(f'{value}\n')


ALL_COMMANDS: list[Type[CommandExecutor]] = [
    CmdExc_Clear,
    CmdExc_Exit,
    CmdExc_GetTModule,
    CmdExc_SetTModule,
    CmdExc_GetValue,
    CmdExc_SetValue,
    CmdExc_Start,
    CmdExc_WriteToFile,
]
