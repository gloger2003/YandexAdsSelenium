import json
from typing import List, Tuple
from selenium.webdriver.remote.webelement import WebElement
from Logger import Log
import os
import logging
import time
import chromedriver_autoinstaller
from seleniumwire.webdriver import Chrome, ChromeOptions
from pprint import pprint 

from selenium.webdriver.common.keys import Keys

import FileManager

class Object:
    def __init__(self) -> None:
        self.log = Log()
        
        pass




class Driver(Object):
    def __init__(self, incognitoMode: bool=False) -> None:
        self.incognitoMode = incognitoMode
        self.lastIndexProxy: int = -1
        self.proxy: str = None
        self.geo: str = None
        super().__init__()

        self.log.Info('Проверка наличия ChromeDriver...')
        chromedriver_autoinstaller.install()


    def CreateNewDriver(self, proxy: str=None, incognitoMode: bool=False, geo: str=None):
        self._wireOptions = {}
        self._options = ChromeOptions()
        self._options.add_argument('--ignore-certificate-errors-spki-list')

        try:
            self.Close()
        except AttributeError:
            pass

        if proxy or self.proxy:
            self._wireOptions['proxy'] = {
                'http': proxy, 
                'https': proxy,
                'socks5': proxy,
                'no_proxy': 'localhost,127.0.0.1'
            }
            self.proxy = proxy

        if incognitoMode or self.incognitoMode:
            self.incognitoMode = True
            self._options.add_argument('--incognito')
            self._wireOptions['incognito'] = True

        self.log.Info()
        self.log.Info('Запуск новой копии браузера. Параметры:')
        self.log.Info(f'- Прокси: {proxy}')
        self.log.Info(f'- Режим инкогнито: {incognitoMode}')

        self._driver = Chrome(seleniumwire_options=self._wireOptions, options=self._options)
        self.log.Info('Новая копия успешно запущена!')

        if self.geo or geo:
            self.SetGeo(self.geo)
        

    def Get(self, url: str) -> None:
        self.log.Info()
        self.log.Info(f'Загрузка новой ссылки: {url}')
        self._driver.get(url)
    
    def SearchRequest(self, text: str, page: int=0):
        self.log.Info()
        self.log.Info(f'Поиск по запросу: {text}')
        self.log.Info(f'- Запрос: {text}')
        self.log.Info(f'- Страница: {page + 1}')

        reqUrl = f"https://yandex.ru/search/?text={text}"
        if page and page != 0:
            reqUrl += f'&p={page}'
        self.Get(reqUrl)
        time.sleep(3)

    def Close(self):
        self.log.Info()
        self.log.Info('Закрытие браузера')
        self._driver.close()

    def NextProxy(self) -> Tuple[str, bool]:
        proxyList = FileManager.GetProxyList()

        self.lastIndexProxy += 1
        
        isRepeat = False
        if self.lastIndexProxy >= len(proxyList):
            isRepeat = True
            self.lastIndexProxy = 0
            
        self.SetProxy(proxyList[self.lastIndexProxy])
        return (proxyList[self.lastIndexProxy], isRepeat)

    def SetProxy(self, proxy: str) -> None:
        self.log.Info()
        self.log.Info(f'Установлен новый прокси: {proxy}')
        
        self.CreateNewDriver(proxy=proxy)
        pass

    def ClearAllCookies(self):
        self._driver.delete_all_cookies()

    def SetGeo(self, geo: str):
        self.log.Info()
        self.log.Info(f'Смена гео-локации:')
        self.log.Info(f'- Старая: {self.geo}')
        self.log.Info(f'- Новая: {geo}')

        self.Get('https://yandex.ru/tune/geo?')
        inputTag: WebElement = self._driver.find_element_by_id('city__front-input')
        inputTag.clear()
        inputTag.send_keys(geo)

        self.geo = geo

        time.sleep(1)
        inputTag.send_keys(Keys.RETURN)

        time.sleep(2)
        self._driver.find_element_by_xpath('/html/body/div[2]/form/div[4]/div/button').click()

        self.log.Info()
        self.log.Info('Гео-локация успешно изменена!')



def RUN_TEST():
    driver = Driver()
    driver.CreateNewDriver()
    
    driver.Get('https://2ip.ru/')
    time.sleep(5)
    
    driver.SearchRequest('Машинки')
    time.sleep(5)

    driver.SetGeo('Краснодар')
    time.sleep(5)

    driver.SearchRequest('Машинки')
    time.sleep(5)

    driver.NextProxy()
    driver.Get('https://2ip.ru/')
    time.sleep(5)
    
    time.sleep(20)



if __name__ == '__main__':
    RUN_TEST()
    
