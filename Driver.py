from typing import List
from selenium.webdriver.remote.webelement import WebElement
from Logger import Log
import os
import logging
import time
import chromedriver_autoinstaller
from seleniumwire.webdriver import Chrome, ChromeOptions
from pprint import pprint 

import FileManager

class Object:
    def __init__(self) -> None:
        self.log = Log()
        self.lastIndexProxy: int = -1
        pass




class Driver(Object):
    def __init__(self, incognitoMode: bool=False) -> None:
        self.incognitoMode = incognitoMode
        super().__init__()

        self.log.Info('Проверка наличия ChromeDriver...')
        if chromedriver_autoinstaller.install():
            self.log.Warning('ChromeDriver не обнаружен! Он был автоматически загружен на диск!')
        else:
            self.log.Info('ChromeDriver обнаружен!')
        pass

        self.CreateNewDriver()


    def CreateNewDriver(self, proxy: str=None):
        self._wireOptions = {}
        self._options = ChromeOptions()
        self._options.add_argument('--ignore-certificate-errors-spki-list')

        if proxy:
            self._wireOptions['proxy'] = {
                'http': proxy, 
                'https': proxy,
                'socks5': proxy,
                'no_proxy': 'localhost,127.0.0.1'
            }

        if self.incognitoMode:
            self._options.add_argument('--incognito')
            self._wireOptions['incognito'] = True

        self._driver = Chrome(seleniumwire_options=self._wireOptions, options=self._options, )
        

    def Get(self, url: str) -> None:
        self._driver.get(url)

    def Close(self):
        self._driver.close()

    def NextProxy(self) -> str:
        proxyList = FileManager.GetProxyList()

        self.lastIndexProxy += 1
        if self.lastIndexProxy >= len(proxyList):
            self.lastIndexProxy = 0
            
        self.SetProxy(proxyList[self.lastIndexProxy])
        return proxyList[self.lastIndexProxy]

    def SetProxy(self, proxy: str) -> None:
        self.log.Info(f'Установлен новый прокси: {proxy}')
        self._driver.close()
        self.CreateNewDriver(proxy)
        pass

    def ClearAllCookies(self):
        self._driver.delete_all_cookies()



if __name__ == '__main__':
    driver = Driver()
    driver.Get('https://www.google.com')
    time.sleep(3)
    driver.Close()
    exit()

    
