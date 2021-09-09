from __future__ import annotations
from typing import NoReturn
from stoppable_thread import StoppableThread
from threading import Thread
from ads_bot import AdsBot
from driver import Driver

from loguru import logger

from datatypes import TacticalModule, Timing
import datetime
import io_utils

import time


class TimingManager:
    def __init__(self, ads_bot: AdsBot) -> None:
        self.ads_bot = ads_bot
        self.__thread: StoppableThread = None
        pass

    @staticmethod
    def parse_timings(str_timings: list[str]) -> list[Timing]:
        # Список с таймингами
        timings: list[Timing] = []
        for str_timing in str_timings:
            try:
                # Каждый str_timing - это:
                # time - time
                # После конвертации в str_timing_data:
                # -> [time, time]
                str_timing_data = str_timing.strip(' ').split('-')

                # Конвертируем строки в time
                start = datetime.time.fromisoformat(
                    str_timing_data[0].strip())
                end = datetime.time.fromisoformat(
                    str_timing_data[1].strip())

            except Exception as e:
                logger.error(f'Неверный формат или данные:')
                logger.error(f'- Строка: {str_timing}')
                logger.error(f'- Ошибка: {e}')
            else:
                timing = Timing(start, end)
                timings.append(timing)
        return timings

    def _start_tm_thread(self,
                         tmodule: TacticalModule,
                         timing: Timing) -> NoReturn:
        # Создаём окно браузера, чтобы избежать ошибок и запускаем call-модуль
        self.ads_bot.create_new_driver()
        tmodule.object.start_thread()

        logger.info(f'Запущен call-модуль:')
        logger.info(f'- Модуль: {tmodule.title}')
        logger.info(f'- Начало: {timing.start.isoformat()}')
        logger.info(f'- Окончание: {timing.end.isoformat()}')

    def _stop_tm_thread(self,
                        tmodule: TacticalModule,
                        timing: Timing) -> NoReturn:
        # Создаём окно браузера, чтобы избежать ошибок запускаем call-модуль
        self.ads_bot.close_driver()
        tmodule.object.stop_thread()

        logger.info(f'Остановлен call-модуль:')
        logger.info(f'- Модуль: {tmodule.title}')
        logger.info(f'- Начало: {timing.start.isoformat()}')
        logger.info(f'- Окончание: {timing.end.isoformat()}')
        pass

    def try_work(self, timings: list[Timing]) -> bool:
        """ Запускает call-модуль, если один из таймингов
            является позитивным """
        # Call-модуль, который нужно будет запустить
        tmodule = self.ads_bot.get_current_tmodule()

        # Проверяем, запущен ли call-модуль
        if tmodule.object.is_worked:
            return False

        # Получаем локальное время на машине
        current_time = datetime.datetime.now().time()

        for timing in timings:
            if timing.start < current_time < timing.stop:
                if not tmodule.object.is_worked:
                    return self._start_tm_thread(self.ads_bot, tmodule, timing)

        # Если не один из таймингов не запустил call-модуль,
        # то нужно обязательно вернуть False
        # для корректной работы TimingManager
        return False

    def try_sleep(self, timings: list[Timing]) -> bool:
        # Call-модуль, который нужно будет запустить
        tmodule = self.ads_bot.get_current_tmodule()

        # Проверяем, остановлен ли поток
        if not tmodule.object.is_worked():
            return False

        # Получаем локальное время на машине
        current_time = datetime.datetime.now().time()

        for timing in timings:
            if timing.start < current_time < timing.stop:
                if not tmodule.object.is_worked:
                    # Создаём окно браузера, чтобы избежать ошибок
                    # и запускаем call-модуль
                    return self._stop_tm_thread(tmodule, timing)

        # Если не один из таймингов не остановил call-модуль,
        # то нужно обязательно вернуть False
        # для корректной работы TimingManager
        return False

    def _process(self):
        if not self.try_sleep(
                self.parse_timings(io_utils.get_sleep_timings())):
            self.try_work(
                self.parse_timings(io_utils.get_work_timings()))
        time.sleep(5)

    def offline_process(self):
        while True:
            try:
                self._process()
            except Exception as e:
                logger.error(e)

    def start_thread(self):
        self.__thread = StoppableThread(target=self._process)
        self.__thread.start()

    def stop_thread(self):
        self.__thread.stop()
