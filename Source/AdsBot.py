import time

import IOManager
from Driver import Driver
from M_NonTargetAdsClicker import NonTargetAdsClicker
from M_StandartProxyWarmUpper import StandartProxyWarmUpper
from M_TargetAdsClicker import TargetAdsClicker


class AdsBot(Driver):
    def __init__(self, incognitoMode: bool) -> None:
        super().__init__(incognitoMode=incognitoMode)
        self.DEV_MODE = True

        self.m_TargetAdsClicker = TargetAdsClicker(self)
        self.m_NonTargetAdsClicker = NonTargetAdsClicker(self)
        self.m_StandartProxyWarmUpper = StandartProxyWarmUpper(self)

    def ReWriteData(self):
        self.DEV_MODE = bool(input('Включить режим разработчика | [True] [False] |: '))
        self.maxPageCount = int(input('Введите максимальное кол-во страниц: '))
        self.maxResidenceTime = int(input('Введите максимальное время пребывания на сайте: '))
        self.maxVisitCount = int(input('Введите максимальное кол-во посещённых сайтов: '))
        self.geo = input('Введите гео-локацию (город): ')
        self.proxy = input('Введите прокси (login:password@address:port): ')


if __name__ == '__main__':
    adsBot = AdsBot(False)
    adsBot.m_NonTargetAdsClicker.Run()

    time.sleep(5)
