import os
import random
import time
from pprint import pprint
from random import randint
from typing import List, Tuple

import chromedriver_autoinstaller
import numpy as np
import scipy.interpolate as si
import selenium
from python_rucaptcha import ImageCaptcha
from selenium.common.exceptions import *
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from seleniumwire.webdriver import Chrome, ChromeOptions

import IOManager
from Logger import Log


class Object:
    def __init__(self) -> None:
        self.log = Log()
        
        pass

# RUCAPTCHA_KEY = '8d7c6cb7d5e9223165451134353fcdd2'
RUCAPTCHA_KEY = IOManager.GetRucaptchaKey()

class Driver(Object):
    def __init__(self, incognitoMode: bool=False) -> None:
        self.DEV_MODE = False
        self.incognitoMode = incognitoMode
        self.lastIndexProxy: int = -1
        self.proxy: str = None
        self.geo: str = None
        self.userAgent: str = None

        self.maxPageCount: int = 1
        self.maxResidenceTime: int = 100
        self.maxVisitCount: int = 1
        super().__init__()

        self.log.Info('Проверка наличия ChromeDriver...')
        chromedriver_autoinstaller.install()

        # self.CreateNewDriver()


    def CreateNewDriver(self, proxy: str=None, incognitoMode: bool=False, geo: str=None, userAgent: str=None):
        self._wireOptions = {}
        self._options = ChromeOptions()
        self._options.add_argument('--ignore-certificate-errors-spki-list')
        self._options.add_argument('--disable-logging')
        self._options.add_experimental_option("excludeSwitches", ["enable-logging"])

        try:
            self.Close()
        except AttributeError:
            pass
        

        if proxy or self.proxy:
            if not proxy:
                proxy = self.proxy

            if 'socks' in proxy:
                self._wireOptions['proxy'] = {
                    'socks5': proxy,
                    'no_proxy': 'localhost,127.0.0.1'
                }
            elif 'http' in proxy:
                self._wireOptions['proxy'] = {
                    'http': proxy, 
                    'https': proxy,
                    'no_proxy': 'localhost,127.0.0.1'
                }

            self.proxy = proxy

        if incognitoMode or self.incognitoMode:
            self.incognitoMode = True
            self._options.add_argument('--incognito')

        if userAgent or self.userAgent:
            self.userAgent = userAgent
            self._options.add_argument(f'--user-agent={userAgent}')

        self.log.Info()
        self.log.Info('Запуск новой копии браузера. Параметры:')
        self.log.Info(f'- Прокси: {proxy}')
        self.log.Info(f'- Юзер-агент: {userAgent}')
        self.log.Info(f'- Гео-локация: {self.geo}')
        self.log.Info(f'- Режим инкогнито: {incognitoMode}')

        self._driver = Chrome(seleniumwire_options=self._wireOptions, options=self._options, service_log_path='NUL')
        self.log.Info('Новая копия успешно запущена!')

        if self.geo or geo:
            self.SetGeo(self.geo)
        
    def Get(self, url: str) -> None:
        self.log.Info()
        self.log.Info(f'Загрузка новой ссылки: {url}')

        loadAttemsCount = 0
        while loadAttemsCount < 5:
            try:
                self._driver.get(url)
                break
            except AttributeError:
                break
            except Exception as e:
                loadAttemsCount += 1

                self.log.Critical()
                self.log.Critical(f'Не удалось загрузить страницу:')
                self.log.Critical(f'- Сообщение об ошибке: {e}')
                self.log.Critical(f'- Прокси: {self.proxy}')
                self.log.Critical(f'- Попытка: {loadAttemsCount}')

                time.sleep(3)
        
        self.TryFindCaptcha(url)
        
    def TryFindCaptcha(self, url: str):
        if 'Ой' in self._driver.title:
            self._driver.find_element_by_class_name('CheckboxCaptcha-Button').click()
            time.sleep(3)

            # Ссылка на изображения для расшифровки
            imageLink = self._driver.find_element_by_class_name('AdvancedCaptcha-Image').get_attribute('src')

            # Возвращается JSON содержащий информацию для решения капчи
            userAnswer = ImageCaptcha.ImageCaptcha(rucaptcha_key=RUCAPTCHA_KEY).captcha_handler(captcha_link=imageLink)

            if not userAnswer['error']:
                # решение капчи
                self._driver.find_element_by_name('rep').send_keys(userAnswer['captchaSolve'])
                self._driver.find_element_by_name('rep').send_keys(Keys.RETURN)
                print(userAnswer['captchaSolve'])
                print(userAnswer['taskId'])

                self._driver.get(url)

            elif userAnswer['error']:
                # Тело ошибки, если есть
                print(userAnswer ['errorBody'])
                print(userAnswer ['errorBody'])
                raise(BaseException('Капча не была решена!'))

    def GetInternalLinkTags(self, currentDomen: str) -> List[WebElement]:
        try:
            internalLinkTags = [k for k in self._driver.find_elements_by_tag_name('a')]

            newInternalLinkTags = []
            
            for linkTag in internalLinkTags:
                try:
                    if currentDomen in linkTag.get_attribute('href') and linkTag.get_attribute("target") == '':
                        newInternalLinkTags.append(linkTag)
                except StaleElementReferenceException:
                    pass
                except TypeError:
                    raise(AttributeError())
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
        
        try:
            self._driver.switch_to.window(window_name=self._driver.window_handles[1])
            self._driver.close()

            self._driver.switch_to.window(window_name=self._driver.window_handles[0])
        except:
            pass

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
        directions = ['Скролл вниз', 'Скролл вверх']
        self.log.Info(f'-- Начата эмуляция скроллинга страницы')
        for _ in range(3):
            currentDirection = randint(0, 1)

            self.log.Info(f'--- {_}. Направление: {directions[currentDirection]}')
            for _ in range(randint(1, 3)):
                self._driver.find_element_by_tag_name('body').send_keys(
                    Keys.PAGE_DOWN if currentDirection == 1 else Keys.PAGE_UP
                )
                self.log.Info(f'---- {directions[currentDirection]}: {_}')
                time.sleep(1)

    def SetProxy(self, proxy: str='localhost') -> None:
        self.log.Info()
        self.log.Info(f'Установлен новый прокси: {proxy}')
        
        self.ClearAllCookies()
        self.CreateNewDriver(proxy=proxy)
        pass

    def ClearAllCookies(self):
        self.log.Info('Куки удалены:')
        self.log.Info(f'- JSON: {self._driver.get_cookies()}')
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
        inputTag.send_keys(Keys.RETURN)

        time.sleep(2)
        # self._driver.find_element_by_xpath('/html/body/div[2]/form/div[4]/div/button').click()

        self.log.Info()
        self.log.Info('Гео-локация успешно изменена!')

    def Quit(self) -> None:
        try:
            self._driver.quit()
        except:
            pass

    def EmulateCursorMove(self):
        
        w = self._driver.execute_script('return window.innerWidth')
        h = self._driver.execute_script('return window.innerHeight')

        x = random.randint(w // 10, w)
        y = random.randint(h // 10, h)
        
        # Curve base:
        points = [[0, 0], [0, 2], [2, 3], [8, 8], [6, 3], [8, 2], [8, 0]];
        points = np.array(points)

        x = points[:,0]
        y = points[:,1]


        t = range(len(points))
        ipl_t = np.linspace(0.0, len(points) - 1, 100)

        x_tup = si.splrep(t, x, k=3)
        y_tup = si.splrep(t, y, k=3)

        x_list = list(x_tup)
        xl = x.tolist()
        x_list[1] = xl + [0.0, 0.0, 0.0, 0.0]

        y_list = list(y_tup)
        yl = y.tolist()
        y_list[1] = yl + [0.0, 0.0, 0.0, 0.0]

        x_i = si.splev(ipl_t, x_list) # x interpolate values
        y_i = si.splev(ipl_t, y_list) # y interpolate values

        action =  ActionChains(self._driver)

        # pprint(self._driver.find_elements_by_tag_name('div'))
        startElement = random.choice(self._driver.find_elements_by_tag_name('div'))

        # # First, go to your start point or Element:
        # action.move_to_element(startElement)
        # action.perform()

        self.log.Info('Начата эмуляцию движений мыши с помощью интерполяции')

        for mouse_x, mouse_y in zip(x_i, y_i):
            try:
                action.move_by_offset(mouse_x, mouse_y)
                action.perform()     
            except Exception as e:
                self.log.Error()
                self.log.Error(f'Ошибка при установки курсора в точку:') 
                self.log.Error(f'- X: {mouse_x}')
                self.log.Error(f'- Y: {mouse_y}')
                self.log.Error(f'- Ошибка: {e}')
            else:
                self.log.Info()
                self.log.Info(f'Установлен курсор в точку:') 
                self.log.Info(f'- X: {mouse_x}')
                self.log.Info(f'- Y: {mouse_y}')
        
        self.log.Info('Конец эмуляции движений курсора')




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

    driver.Get('https://2ip.ru/')
    time.sleep(5)
    
    time.sleep(20)



if __name__ == '__main__':
    RUN_TEST()
    
