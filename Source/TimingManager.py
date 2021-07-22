from FileManager import GetSleepTimingsList, GetWorkTimingsList
import datetime
import os
import time
from threading import Thread
from typing import List, Tuple

from Driver import Driver
from Logger import Log

class TimingManager:
    def __init__(self) -> None:
        self.driver: Driver = None
        self.log = Log()
        self.adsBot = None
        pass

    def ParseTimingList(self, timingList: List[str]) -> List[Tuple[datetime.time, datetime.time]]:
        timings = []
        for line in timingList:
            try:
                strTimings = line.strip(' ').split('-')

                start = datetime.time.fromisoformat(strTimings[0])
                stop = datetime.time.fromisoformat(strTimings[1])
                
                timings.append((start, stop))
            except:
                self.log.Error(f'Неверный формат или данные:')
                self.log.Error(f'- Строка: {line}')
        return timings

    def TryToSleep(self, timings: List[Tuple[datetime.time, datetime.time]]) -> bool:
        now = datetime.datetime.now().time()

        for timing in timings:
            start = timing[0]
            stop = timing[1]

            if start < now < stop:
                self.driver.Quit()
                self.driver = None

                self.log.Info('Включён спящий режим. Выбранный тайминг:')
                self.log.Info(f'- Начало: {start.isoformat()}')
                self.log.Info(f'- Окончание: {stop.isoformat()}')

                return True
        return False

    def _Run(self):
        while True:
            time.sleep(5)
            
            if not self.TryToSleep(GetSleepTimingsList()):
                self.TryToWork(GetWorkTimingsList())
                
                


    def Run(self, driver: Driver):
        self.driver = driver
        
        self.thread = Thread(target=self._Run)
        # self.thread.

        

