from Driver import Driver
from M_StandartProxyWarmUpper import MStandartProxyWarmUpper
import FileManager
import time

class AdsBot(Driver):
    def __init__(self, incognitoMode: bool) -> None:
        super().__init__(incognitoMode=incognitoMode)

        self.mStandartProxyWarmUpper = MStandartProxyWarmUpper(self)


if __name__ == '__main__':
    adsBot = AdsBot(False)
    adsBot.mStandartProxyWarmUpper.Run()

    time.sleep(5)
    # adsBot.Close()
    
