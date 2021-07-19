import os
import time
import logging
import sys
import shutil

DEV_MODE = True


class Log:
    class Level:
        INFO =      ' [INFO]     |'
        ERROR =     ' [ERROR]    |'
        DEBUG =     ' [DEBUG]    |'
        CRITICAL =  ' [CRITICAL] |'
        WARNING =   ' [WARNING]  |' 

    dirName = './LOGS'
    logDate = time.strftime('%H.%M.%S %d-%m-%Y')
    fileName = f'{dirName}/{logDate}.log'

    Now = lambda _: time.strftime('%H:%M:%S %d-%m-%Y')
    FormatToLog = lambda _, date, level, message: f'[{date}]{level} {message}'

    def __init__(self) -> None:
        
        if DEV_MODE:
            shutil.rmtree(self.dirName)

        if not os.path.exists(self.dirName):
            os.mkdir(self.dirName)

        open(self.fileName, 'w', encoding='utf-8').close()
        pass
    
    def Logging(self, level: str, message: str) -> None:
        log = self.FormatToLog(self.Now(), level, message)
        try:
            print(log)
            with open(self.fileName, 'a', encoding='utf-8') as f:
                f.write(f'{log}\n')
        except FileNotFoundError:
            open(self.fileName, 'w', encoding='utf-8').close()
            print(f"\n{self.FormatToLog(self.Now(), self.Level.CRITICAL, 'Лог был удалён, был создан новый!')}\n")
        except Exception as e:
            print(f"\n{self.FormatToLog(self.Now(), self.Level.CRITICAL, 'Не удалось записать лог! {e}')}\n")

    def Info(self, message: str) -> None:
        self.Logging(self.Level.INFO, message)

    def Warning(self, message: str) -> None:
        self.Logging(self.Level.WARNING, message)
    
    def Critical(self, message: str) -> None:
        self.Logging(self.Level.CRITICAL, message)

    def Debug(self, message: str) -> None:
        self.Logging(self.Level.DEBUG, message)

    def Error(self, message: str) -> None:
        self.Logging(self.Level.ERROR, message)

if __name__ == '__main__':
    log = Log()
    log.Debug('ddffdfd')
    log.Warning('fgfgfd')