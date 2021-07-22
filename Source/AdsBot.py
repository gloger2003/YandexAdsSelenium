import time

import FileManager
from Driver import Driver
from M_NonTargetAdsClicker import NonTargetAdsClicker
from M_StandartProxyWarmUpper import StandartProxyWarmUpper
from M_TargetAdsClicker import TargetAdsClicker


class AdsBot(Driver):
    def __init__(self, incognitoMode: bool) -> None:
        super().__init__(incognitoMode=incognitoMode)
        self.DEV_MODE = True

        self.targetAdsClicker = TargetAdsClicker(self)
        self.nonTargetAdsClicker = NonTargetAdsClicker(self)
        self.mStandartProxyWarmUpper = StandartProxyWarmUpper(self)


if __name__ == '__main__':
    adsBot = AdsBot(False)
    adsBot.nonTargetAdsClicker.Run()

    time.sleep(5)
