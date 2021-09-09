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
                'Выберите раздел:'
                '\n1. Перезаписать свойства вебдрайвера'
                '\n2. Запустить TimingManager'
                '\n3. Сменить запускаемый модуль для TimingManager'
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


def close_driverAdsBot(adsBot: AdsBot):
    try:
        adsBot.isSubscribe = False
        adsBot.close_driver()
    except:
        pass
    os._exit(0)
    # adsBot.Exit()


def CheckSubscribe(adsBot: AdsBot):
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
                close_driverAdsBot(adsBot=adsBot)

        elif jsonRes['status'] == 'NOT_FOUND_USER':
            adsBot.log.Critical()
            adsBot.log.Critical('Неверный логин или пароль, измените данные в AUTH_DATA.txt!')
            adsBot.log.Critical('Выход!')
            adsBot.log.Critical()
            close_driverAdsBot(adsBot=adsBot)
        else:
            adsBot.log.Critical()
            adsBot.log.Critical('К сожалению, мы не нашли ваш профиль в базе данных :(')
            adsBot.log.Critical('Обратитесь к продавцу для решения данной проблемы')
            adsBot.log.Critical('Пользоваться юотом без подписки нельзя, поэтому мы его закрываем!')
            adsBot.log.Critical()
            close_driverAdsBot(adsBot=adsBot)
    
    except Exception as e:
        adsBot.log.Critical()
        adsBot.log.Critical('Не удалось подтвердить подписку!')
        adsBot.log.Critical('Выход!')
        adsBot.log.Critical()
        close_driverAdsBot(adsBot=adsBot)
        

def CheckSubscribeForever(adsBot: AdsBot):
    while True:
        CheckSubscribe(adsBot)
        time.sleep(10)
        


if __name__ == '__main__':
    try:
        adsBot = AdsBot(False)
        
        adsBot.maxResidenceTime = 20 # Это макс время пребывания на сайте (домене...) поэтому так быстро и проходит по ним
        adsBot.maxPageCount = 1 # Макс кол-во страниц в поиске, по которым он проходится 
        adsBot.maxVisitCount = 3
        adsBot.geo = None

        adsBot.DEV_MODE = False
        # Thread(target=CheckSubscribeForever, args=[adsBot]).start()
        # CheckSubscribe(adsBot)
        # adsBot.Run()
        # Thread(target=CheckSubscribeForever, args=[adsBot]).start()
        # time.sleep(5)

        adsBot.CreateNewDriver()
        # adsBot.Get('http://yabs.yandex.ru/count/WoWejI_zO203zHW012eEZW6sQmQjO0K080GGW0WnrGG9OG00000u109mze_peAKAW06euyEAnx7supY80UlKhezxa07-qxBBqO20W0AO0VxJiijHk06aXxJ58i01NDW1aegbd07W0Qx6_nde0U81e0BQz_4OqgxH0fW3gESXZg0A-0Ist3M81RRSDP05oESze0NoiH2e1P_K3R05dzGDk0Mrsm_01SNEBSW5iCmBxi-Y2xW6rgi1oGQW_67JjJeeQEK9U53xZ-neFR07W82O3BW7W0Nn1wZnK76CsSSuW0W4q0Y4We21nEtxk0pmFyaA4e5yXb2kzJ_u2e2r6AeB4FJCwbK9U000WvO5tgF81G3P2-WBjjmry0iAY0o-lTw-0QaCM36gn4zir3_e3AS2u0s3W810YGwgEFizlcJfeFc7cztMZfHee0x0X3tO3W6X3zNerAdsg-m_sG-048c3knxG4D-U5dXoTO1fos0_iH8jVNsD8QJaF-aITivB3JQN_MAdZEVVsuYnc-7W4xNR3w0KjTiFg1J8vptQelM71kWKX0BG5TgYzOS6s1N1YlRieu-y_6Fme1RGbfo81iaMq1Q-lTw-0O4Nc1Umh_WTg1S9m1Uq4jWNm8GzcHYW61Mm6FBaeuW6q1WX-1ZVvU3sWPVViCC1W1cG6G6W6Qe3i1cu6V___m7I6H9vOM9pNtDbSdPbSYzoDJKnBJBe6O320_0PWC83WHh__wUBWGxiJf0QW42O6jJ3Kx0Q-RMIWfoXYB8Ck1e3zHe10000WXjHCJOoDpauCJ0nCpGvCZSmEIqnE3GnCp0nD3GoEJ8sD38sDJOtEIrpONCpBJ0sDp0jDpLcBNDXSoriDorYOMnXRcDbSYquC3WmBK91J2qrD3Wmi1jKk1i3WXpf780T_tya8644Xb42AM0CAcDJTH7FE4a4sjz1T833-t96ArkHmr2mTt8fYLmxH6AyvJJlkV8FHzABcYmgdEJ8bm_P4Aja9G6taLkoCXc9wRRamtCi15un6u-oELeq0jZNCPIR2oQ4dOQC2kkUP40F60BwgYMd_rNZr2m5gs6iHYHu~1?from=yandex.ru%3Bsearch%26%23x2F%3B%3Bweb%3B%3B0%3B&q=%D0%BA%D0%B0%D0%BA+%D1%81%D0%BE%D0%B1%D1%80%D0%B0%D1%82%D1%8C+%D0%BC%D0%B8%D0%BD%D1%83%D1%81+%D1%81%D0%BB%D0%BE%D0%B2%D0%B0&etext=2202.zKd6sCUOt0oItspWms2JNlhDe_fcb4nxF1DGZfDQ_LiWlaVsTGnjZtQ12elk0XTwtrmBauB2NdFbD5-KQAuaDWl1cHhnb2dta2J3aWVuanQ.fad4fd6cbd49922b47cf16482ce8f29162e8328a&baobab_event_id=krvtv3wwgp')
        # adsBot.EmulateCursorMove()
        adsBot.m_TargetAdsClicker.Run()
        close_driverAdsBot(adsBot)

    except SystemExit:
        close_driverAdsBot(adsBot)

    except Exception as e:
        print(e)
        if not adsBot.DEV_MODE: 
            adsBot.log.Critical(e)
            raise e
            
