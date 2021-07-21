import json
import logging
import os
import time
from pprint import pprint
from random import randint
from typing import List, Tuple

import chromedriver_autoinstaller
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from seleniumwire.webdriver import Chrome, ChromeOptions

from python_rucaptcha import ImageCaptcha

import FileManager
from Logger import Log


class Object:
    def __init__(self) -> None:
        self.log = Log()
        
        pass

RUCAPTCHA_KEY = '8d7c6cb7d5e9223165451134353fcdd2'


class Driver(Object):
    def __init__(self, incognitoMode: bool=False) -> None:
        self.incognitoMode = incognitoMode
        self.lastIndexProxy: int = -1
        self.proxy: str = None
        self.geo: str = None
        super().__init__()

        self.log.Info('Проверка наличия ChromeDriver...')
        chromedriver_autoinstaller.install()

        self.CreateNewDriver()


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
        
        if 'Ой' in self._driver.title:
            self._driver.find_element_by_class_name('CheckboxCaptcha-Button').click()
            time.sleep(3)

            # Ссылка на изображения для расшифровки
            image_link = self._driver.find_element_by_class_name('AdvancedCaptcha-Image').get_attribute('src')

            # time.sleep(1000)

            # Возвращается JSON содержащий информацию для решения капчи
            user_answer = ImageCaptcha.ImageCaptcha(rucaptcha_key=RUCAPTCHA_KEY).captcha_handler(captcha_link=image_link)

            if not user_answer['error']:
                # решение капчи
                self._driver.find_element_by_name('rep').send_keys(user_answer['captchaSolve'])
                self._driver.find_element_by_name('rep').send_keys(Keys.RETURN)
                print(user_answer['captchaSolve'])
                print(user_answer['taskId'])

                self._driver.get(url)

            elif user_answer['error']:
                # Тело ошибки, если есть
                print(user_answer ['errorBody'])
                print(user_answer ['errorBody'])
                raise(BaseException('Капча не была решена!'))

    def GetInternalLinkTags(self, currentDomen: str) -> List[str]:
        try:
            internalLinkTags = [k for k in self._driver.find_elements_by_tag_name('a')]
            internalLinkTags = [internalLinkTags.remove(k) if currentDomen in k.get_attribute('href') else k for k in internalLinkTags]
            return internalLinkTags
        except AttributeError:
            self.log.Warning('Не удалось получить внутренние ссылки!')
            return []

    def ClickToRandomLinkTag(self, linkTags: List[WebElement], info: str) -> bool:
        tryCount = 0
        while True:
            if tryCount >= 20:
                return False
            try:
                linkTags[randint(0, len(linkTags) - 1)].click()
                self.log.Info(f'{info}: {self._driver.current_url}')
                break
            except:
                pass
            tryCount += 1
        return True        
    
    def SearchRequest(self, text: str, page: int=0) -> None:
        self.log.Info()
        self.log.Info(f'Поиск по запросу: {text}')
        self.log.Info(f'- Запрос: {text}')
        self.log.Info(f'- Страница: {page + 1}')
        self.log.Info(f'- Гео-локация: {self.geo}')

        reqUrl = f"https://yandex.ru/search/?text={text}"
        if page and page != 0:
            reqUrl += f'&p={page}'
        self.Get(reqUrl)
        time.sleep(1)

    def Close(self):
        self.log.Info()
        self.log.Info('Закрытие браузера')
        self._driver.close()

    def EmulateRandomScroll(self):
        self.log.Info(f'-- Начата эмуляция скроллинга страницы')
        for _ in range(3):
            direction = randint(0, 1)
            self.log.Info(f'--- {_}. Направление: {direction}')
            for _ in range(randint(1, 3)):
                self._driver.find_element_by_tag_name('body').send_keys(
                    Keys.PAGE_DOWN if direction == 1 else Keys.PAGE_UP
                )
                self.log.Info(f'---- {_}')
                time.sleep(1)

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
    
