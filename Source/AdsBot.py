import os
import sys
import time
from threading import Thread

import requests

from Driver import Driver
from IOManager import GetAuthData, GetUserInput
from M_NonTargetAdsClicker import NonTargetAdsClicker
from M_StandartProxyWarmUpper import StandartProxyWarmUpper
from M_TargetAdsClicker import TargetAdsClicker
from TimingManager import TimingManager


class AdsBot(Driver):
    def __init__(self, incognitoMode: bool) -> None:
        super().__init__(incognitoMode=incognitoMode)
        
        self.DEV_MODE = True
        self.currentModule: int = 0

        self.isSubscribe = False


        self.m_TargetAdsClicker = TargetAdsClicker(self)
        self.m_NonTargetAdsClicker = NonTargetAdsClicker(self)
        self.m_StandartProxyWarmUpper = StandartProxyWarmUpper(self)

        self.modules = [
            (self.m_StandartProxyWarmUpper, 'Модуль стандартного прогрева прокси', 'Без описания'),
            (self.m_NonTargetAdsClicker, 'Модуль нецелевого обхода', 'Без описания'),
            (self.m_TargetAdsClicker, 'Модуль целевого обхода', 'Без описания')
        ]

        self.timingManager = TimingManager(self)


    def ReWriteData(self) -> None:
        self.log.Info('Перезапись свойств вебдрайвера')
        self.DEV_MODE = GetUserInput('Включить режим разработчика | [True] [False] |', bool, False)
        self.maxPageCount = GetUserInput('Введите максимальное кол-во страниц', int, self.maxPageCount)
        self.maxResidenceTime = GetUserInput('Введите максимальное время пребывания на сайте', int, self.maxResidenceTime)
        self.maxVisitCount = GetUserInput('Введите максимальное кол-во посещённых сайтов', int, self.maxVisitCount)
        self.geo = GetUserInput('Введите гео-локацию (город): ', str, None)
        self.proxy = GetUserInput('Введите прокси (login:password@address:port) (Работает только в режиме разработчика!)', str, None)
        self.log.Info('Конец перезаписи свойств вебдрайвера')

        self.CreateNewDriver()

    def ChangeModule(self) -> None:
        print()
        [print(f'- {k[1]}: {k[2]}') for k in self.modules]
        print()
        self.currentModule = GetUserInput('Выберите номер модуля (1 = 0)', int, self.currentModule)
        print()

    def StartModuleWithoutTimingManager(self):
        print()
        [print(f'- {k[1]}: {k[2]}') for k in self.modules]
        print()
        self.currentModule = GetUserInput('Выберите номер модуля (1 = 0), который хотите запустить', int, self.currentModule)
        print()
        self.log.Info(f'[{self.modules[self.currentModule][1]}] назначен запускаемым')
        self.log.Info('Запуск модуля...')
        self.CreateNewDriver()
        self.modules[self.currentModule][0].Run()


    def Run(self):
        while True:
            print()
            mode = GetUserInput(
                'Выберите раздел:' \
                '\n1. Перезаписать свойства вебдрайвера' \
                '\n2. Запустить TimingManager'\
                '\n3. Сменить запускаемый модуль для TimingManager' \
                '\n4. Запустить модуль без TimingManager', int, None)

            if mode == 1:
                self.ReWriteData()
                pass
            elif mode == 2:
                return self.timingManager.Run()
            elif mode == 3:
                self.ChangeModule()
            elif mode == 4:
                return self.StartModuleWithoutTimingManager()
            else:
                self.Run()

    def Exit(self):
        del self
        quit()


def CloseAdsBot(adsBot: AdsBot):
    try:
        adsBot.isSubscribe = False
        adsBot.Close()
    except:
        pass
    os._exit(0)
    # adsBot.Exit()

def CheckSubscribeForever(adsBot: AdsBot):
    while True:
        try:
            authData = GetAuthData()
            
            login = authData[0]
            password = authData[1]

            jsonRes = requests.get(f'http://control-panel123.herokuapp.com/get_user?login={login}&password={password}').json()
            
            
            if jsonRes['status'] == 'OK':
                if jsonRes['check']:
                    if not adsBot.isSubscribe:
                        adsBot.isSubscribe = True
                        adsBot.log.Info()
                        adsBot.log.Info('Подписка успешно подтверждена! Данные подписки:')
                        adsBot.log.Info(f"- Дата начала: {jsonRes['start_date']}")
                        adsBot.log.Info(f"- Дата конца: {jsonRes['finish_date']}")
                        adsBot.log.Info()
                else:
                    adsBot.log.Critical()
                    adsBot.log.Critical('Подписка закончила время действия! Данные подписки:')
                    adsBot.log.Critical(f"- Дата начала: {jsonRes['start_date']}")
                    adsBot.log.Critical(f"- Дата конца: {jsonRes['finish_date']}")
                    adsBot.log.Critical('Выход!')
                    adsBot.log.Critical()
                    CloseAdsBot(adsBot=adsBot)

            elif jsonRes['status'] == 'NOT_FOUND_USER':
                adsBot.log.Critical()
                adsBot.log.Critical('Неверный логин или пароль, измените данные в AUTH_DATA.txt!')
                adsBot.log.Critical('Выход!')
                adsBot.log.Critical()
                CloseAdsBot(adsBot=adsBot)
            else:
                adsBot.log.Critical()
                adsBot.log.Critical('К сожалению, мы не нашли ваш профиль в базе данных :(')
                adsBot.log.Critical('Обратитесь к продавцу для решения данной проблемы')
                adsBot.log.Critical('Пользоваться юотом без подписки нельзя, поэтому мы его закрываем!')
                adsBot.log.Critical()
                CloseAdsBot(adsBot=adsBot)
        
        except Exception as e:
            adsBot.log.Critical()
            adsBot.log.Critical('Не удалось подтвердить подписку!')
            adsBot.log.Critical('Выход!')
            adsBot.log.Critical()
            CloseAdsBot(adsBot=adsBot)
        time.sleep(10)


if __name__ == '__main__':
    try:
        adsBot = AdsBot(False)
        
        adsBot.maxResidenceTime = 20 # Это макс время пребывания на сайте (домене...) поэтому так быстро и проходит по ним
        adsBot.maxPageCount = 2 # Макс кол-во страниц в поиске, по которым он проходится 
        adsBot.maxVisitCount = 3
        adsBot.geo = 'Москва'

        adsBot.DEV_MODE = True

        Thread(target=CheckSubscribeForever, args=[adsBot]).start()

        time.sleep(5)
        adsBot.Run()
        
        # adsBot.CreateNewDriver()
        # adsBot.m_TargetAdsClicker.Run()
        # adsBot.m_NonTargetAdsClicker.Run()
        # adsBot.m_StandartProxyWarmUpper.Run()

        time.sleep(5)
    
    except SystemExit:
        CloseAdsBot(adsBot)

    except Exception as e:
        print(e)
        if not adsBot.DEV_MODE: 
            adsBot.log.Critical(e)
            raise e
            
