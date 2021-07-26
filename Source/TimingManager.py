import datetime
import os
import time
from threading import Thread
from typing import List, Tuple, Union

from Driver import Driver
from IOManager import GetSleepTimingsList, GetWorkTimingsList
from Logger import Log
from M_NonTargetAdsClicker import NonTargetAdsClicker
from M_StandartProxyWarmUpper import StandartProxyWarmUpper
from M_TargetAdsClicker import TargetAdsClicker


class TimingManager:
    def __init__(self, adsBot) -> None:
        # self.adsBot.driver: Driver = None
        self.log = Log()
        self.adsBot = adsBot
        pass

    def ParseTimingList(self, timingList: List[str]) -> List[Tuple[datetime.time, datetime.time]]:
        timings = []
        for line in timingList:
            try:
                strTimings = line.strip(' ').split('-')

                start = datetime.time.fromisoformat(strTimings[0].strip())
                stop = datetime.time.fromisoformat(strTimings[1].strip())
                
                timings.append((start, stop))
            except Exception as e:
                self.log.Error(f'Неверный формат или данные:')
                self.log.Error(f'- Строка: {line}')
                self.log.Error(f'- Ошибка: {e}')
        return timings

    def TryToSleep(self, timings: List[Tuple[datetime.time, datetime.time]]) -> bool:
        now = datetime.datetime.now().time()

        if not self.moduleData[0].isWorked:
            self.log.Debug('Начата проверка на переход в сон:')
            self.log.Debug(f'- Имя модуля: {self.moduleData[1]}')
            self.log.Debug(f'- Индекс модуля: {self.adsBot.currentModule}')
            self.log.Debug(f'- Описание модуля: {self.moduleData[2]}')

        for timing in timings:
            if timing:
                start = timing[0]
                stop = timing[1]

                if start < now < stop:
                    try:
                        self.adsBot.Close()
                        self.adsBot._driver = None
                    except:
                        self.adsBot._driver = None
                        pass

                    self.moduleData[0].isWorked = False

                    self.log.Info('Включён спящий режим. Выбранный тайминг:')
                    self.log.Info(f'- Начало: {start.isoformat()}')
                    self.log.Info(f'- Окончание: {stop.isoformat()}')

                    return True
            else:
                self.log.Info('Пустой тайминг в SLEEP_TIMINGS')
        
        self.log.Debug('Переходить в сон не нужно!')
        return False

    def TryToWork(self, timings: List[Tuple[datetime.time, datetime.time]]) -> bool:
        now = datetime.datetime.now().time()

        self.log.Debug(f'Начата проверка на запуск модуля:')
        self.log.Debug(f'- Имя модуля: {self.moduleData[1]}')
        self.log.Debug(f'- Индекс модуля: {self.adsBot.currentModule}')
        self.log.Debug(f'- Описание модуля: {self.moduleData[2]}')

        for timing in timings:
            if timing:
                start = timing[0]
                stop = timing[1]

                if start < now < stop:
                    if not self.moduleData[0].isWorked:
                        self.adsBot.CreateNewDriver()

                        Thread(target=self.moduleData[0].Run).start()
                        
                        self.log.Info(f'Запущен модуль: {self.moduleData[1]}')

                        self.log.Info(f'Выбранный тайминг:')
                        self.log.Info(f'- Начало: {start.isoformat()}')
                        self.log.Info(f'- Окончание: {stop.isoformat()}')
                        return True
            else:
                self.log.Info('Пустой тайминг в WORK_TIMINGS')
        return False


    def _Run(self):
        while True:
            if not self.TryToSleep(self.ParseTimingList(GetSleepTimingsList())):
                self.TryToWork(self.ParseTimingList(GetWorkTimingsList()))
            time.sleep(5)
                

    def Run(self):
        # self.adsBot.driver = driver

        self.moduleData = self.adsBot.modules[self.adsBot.currentModule]
        
        self.thread = Thread(target=self._Run)
        self.thread.start()

        self.log.Info('TimingManager запущен!')
        self.log.Info(f'- Тайминги для работы: {GetWorkTimingsList()}')
        self.log.Info(f'- Тайминги для сна: {GetSleepTimingsList()}')

        

