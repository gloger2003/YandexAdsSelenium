from typing import List
from selenium.webdriver.remote.webelement import WebElement
from Logger import Log
import os
import logging
import time
import chromedriver_autoinstaller
from seleniumwire.webdriver import Chrome
from pprint import pprint 


class Main:
    HTTP_PROXY_FILE_NAME = './HTTP_PROXIES.txt'
    SOCKS5_PROXY_FILE_NAME = './SOCKS5_PROXIES.txt'

    def __init__(self) -> None:
        self.log = Log()

        self.lastIndexProxy: int = -1
        pass

    def ReadFile(self, fileName: str) -> str:
        text: str = ''
        try:
            with open(fileName, 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            self.log.Error(f'Файл "{fileName}" не найден, создан новый!')
            open(fileName, 'w', encoding='utf-8').close()
        except Exception as e:
            self.log.Error(f'Ошибка при открытии файла "{fileName}"')
        return text

    def FormatProxies(self, proxyList: List[str], proxyType: str) -> List[str]:
        badProxyList = self.ReadFile(self.HTTP_PROXY_FILE_NAME).split('\n')
        proxyList = []
        for badProxy in badProxyList:
            splittedBadProxy = badProxy.split('@')
            splittedBadProxy.reverse()
            proxyList.append(f'{proxyType}://' + '@'.join(splittedBadProxy))
        return proxyList

    def GetHttpProxyList(self) -> List[str]:
        return self.FormatProxies(self.ReadFile(self.HTTP_PROXY_FILE_NAME).split('\n'), 'http')

    def GetSocksProxyList(self) -> List[str]:
        return self.FormatProxies(self.ReadFile(self.SOCKS5_PROXY_FILE_NAME).split('\n'), 'socks5')

    def GetProxyList(self) -> List[str]:
        return self.GetHttpProxyList() + self.GetSocksProxyList()

        
            



class Driver(Main):
    def __init__(self) -> None:
        super().__init__()

        self.log.Info('Проверка наличия ChromeDriver...')
        if chromedriver_autoinstaller.install():
            self.log.Warning('ChromeDriver не обнаружен! Он был автоматически загружен на диск!')
        else:
            self.log.Info('ChromeDriver обнаружен!')
        pass

        self.CreateNewDriver()


    def CreateNewDriver(self, proxy: str=None):
        self._options = {}
        if proxy:
            self._options['proxy'] = {
                'http': proxy, 
                'https': proxy,
                'socks5': proxy,
                'no_proxy': 'localhost,127.0.0.1'
            }
        self._driver = Chrome(seleniumwire_options=self._options)
    
    def FindElementById(self, id_: str) -> WebElement:
        return self._driver.find_element_by_id(id_)

    def FindElementsById(self, id_: str) -> List[WebElement]:
        return self._driver.find_elements_by_id(id_)

    def FindElementByClassName(self, className: str) -> WebElement:
        return self._driver.find_element_by_class_name(className)

    def FindElementsByClassName(self, className: str) -> List[WebElement]:
        return self._driver.find_elements_by_class_name(className)

    def FindElementByName(self, name: str) -> WebElement:
        return self._driver.find_element_by_name(name)

    def FindElementsByName(self, name: str) -> List[WebElement]:
        return self._driver.find_elements_by_name(name)
    

    def Get(self, url: str) -> None:
        self._driver.get(url)

    def Close(self):
        self._driver.close()

    def NextProxy(self) -> str:
        proxyList = self.GetProxyList()

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

    
