import os
import random
import time
from pprint import pformat, pprint
from random import choice, randint
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

import IOUtils
from loguru import logger


# RUCAPTCHA_KEY = '8d7c6cb7d5e9223165451134353fcdd2'


class Driver:
    def __init__(self, incognito_mode: bool = False) -> None:
        self.DEV_MODE = False
        self.incognito_mode = incognito_mode
        self.lastIndexProxy: int = -1
        self.proxy: str = None
        self.geo: str = None
        self.user_agent: str = None

        self.maxPageCount: int = 1
        self.maxResidenceTime: int = 100
        self.maxVisitCount: int = 1
        super().__init__()

        logger.info('Проверка наличия ChromeDriver...')
        chromedriver_autoinstaller.install()

    def create_new_driver(self,
                          proxy: str = None,
                          incognito_mode: bool = False,
                          geo: str = None,
                          user_agent: str = None):

        try:
            self.close()
        except AttributeError:
            pass

        self._wire_options = {}
        self._options = ChromeOptions()

        self._options.add_argument(
            '--ignore-certificate-errors-spki-list')
        self._options.add_argument(
            '--disable-logging')
        self._options.add_experimental_option(
            "excludeSwitches", ["enable-logging"])

        if proxy or self.proxy:
            if not proxy:
                proxy = self.proxy

            if 'socks' in proxy:
                self._wire_options['proxy'] = {
                    'socks5': proxy,
                    # 'no_proxy': 'localhost,127.0.0.1'
                }
            elif 'http' in proxy:
                self._wire_options['proxy'] = {
                    'http': proxy,
                    'https': proxy,
                    # 'no_proxy': 'localhost,127.0.0.1'
                }

            self.proxy = proxy

        if incognito_mode or self.incognito_mode:
            self.incognito_mode = True
            self._options.add_argument('--incognito')

        if user_agent or self.user_agent:
            self.user_agent = user_agent
            self._options.add_argument(f'--user-agent={user_agent}')

        logger.debug('Запуск новой копии браузера. Параметры:')
        logger.debug(f'- Прокси: {proxy}')
        logger.debug(f'- Юзер-агент: {user_agent}')
        logger.debug(f'- Гео-локация: {self.geo}')
        logger.debug(f'- Режим инкогнито: {incognito_mode}')

        self.driver = Chrome(seleniumwire_options=self._wire_options,
                             options=self._options, service_log_path='NUL')

        if self.geo or geo:
            self.set_geo_location(self.geo)

    def get(self, url: str) -> None:
        logger.info(f'Загрузка новой ссылки: {url}')

        loadAttemsCount = 0
        while loadAttemsCount < 5:
            try:
                self.driver.get(url)
                break
            except AttributeError:
                break
            except Exception as e:
                loadAttemsCount += 1

                logger.critical(f'Не удалось загрузить страницу:')
                logger.critical(f'- Сообщение об ошибке: {e}')
                logger.critical(f'- Прокси: {self.proxy}')
                logger.critical(f'- Попытка: {loadAttemsCount}')

                time.sleep(3)

        self.try_solve_yandex_captcha(url)

    def get_internal_link_tags(self, currentDomen: str) -> List[WebElement]:
        try:
            internalLinkTags = [
                k for k in self.driver.find_elements_by_tag_name('a')]

            new_internal_link_tags = []

            for linkTag in internalLinkTags:
                try:
                    if currentDomen in (linkTag.get_attribute('href') and
                                        linkTag.get_attribute("target") == ''):
                        new_internal_link_tags.append(linkTag)
                except StaleElementReferenceException:
                    pass
                except TypeError:
                    raise AttributeError
            return internalLinkTags

        except AttributeError:
            logger.warning('Не удалось получить внутренние ссылки!')
            return []

    def click_to_random_link_tag(self,
                                 link_tags: List[WebElement],
                                 info: str) -> bool:
        tryCount = 0
        while True:
            if tryCount >= 20:
                return False
            try:
                random.choice(link_tags).click()
                logger.info(f'{info}: {self.driver.current_url}')
                break
            except ():
                pass

            tryCount += 1

        try:
            self.driver.switch_to.window(
                window_name=self.driver.window_handles[1])
            self.driver.close()

            self.driver.switch_to.window(
                window_name=self.driver.window_handles[0])
        except ():
            pass
        return True

    def search_request(self, text: str, page: int = 0) -> None:
        logger.info(f'Поиск по запросу: {text}')
        logger.info(f'- Запрос: {text}')
        logger.info(f'- Страница: {page + 1}')
        logger.info(f'- Гео-локация: {self.geo}')

        reqUrl = f"https://yandex.ru/search/?text={text}"
        if page and page != 0:
            reqUrl += f'&p={page}'
        self.get(reqUrl)
        time.sleep(1)

    def close(self):
        logger.info('Закрытие браузера')
        self.driver.close()

    def emulate_random_scrolling(self):
        directions = ['Скролл вниз', 'Скролл вверх']
        logger.info(f'-- Начата эмуляция скроллинга страницы')
        for _ in range(3):
            currentDirection = randint(0, 1)

            logger.info(
                f'--- {_}. Направление: {directions[currentDirection]}')
            for _ in range(randint(1, 3)):
                self.driver.find_element_by_tag_name('body').send_keys(
                    Keys.PAGE_DOWN if currentDirection == 1 else Keys.PAGE_UP
                )
                logger.info(f'---- {directions[currentDirection]}: {_}')
                time.sleep(1)

    def set_proxy(self, proxy: str = 'localhost') -> None:
        logger.debug(f'Установлен новый прокси: {proxy}')
        self.clear_all_cookies()
        self.create_new_driver(proxy=proxy)
        pass

    def clear_all_cookies(self):
        self.driver.delete_all_cookies()
        logger.debug('Куки удалены')

    def set_geo_location(self, geo: str):
        logger.info(f'Смена гео-локации:')
        logger.info(f'- Старая: {self.geo}')
        logger.info(f'- Новая: {geo}')

        self.get('https://yandex.ru/tune/geo?')
        inputTag: WebElement = self.driver.find_element_by_id(
            'city__front-input')
        inputTag.clear()
        inputTag.send_keys(geo)

        self.geo = geo

        time.sleep(1)
        inputTag.send_keys(Keys.RETURN)
        inputTag.send_keys(Keys.RETURN)

        time.sleep(2)
        # self._driver.find_element_by_xpath('/html/body/div[2]/form/div[4]/div/button').click()

        logger.info('Гео-локация успешно изменена!')

    def quit(self) -> None:
        try:
            self.driver.quit()
        except ():
            pass

    def emulate_cursor_moving(self):
        w = self.driver.execute_script('return window.innerWidth')
        h = self.driver.execute_script('return window.innerHeight')

        x = random.randint(w // 10, w)
        y = random.randint(h // 10, h)

        # Curve base:
        points = [[0, 0], [0, 2], [2, 3], [8, 8], [6, 3], [8, 2], [8, 0]]
        points = np.array(points)

        x = points[:, 0]
        y = points[:, 1]

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

        x_i = si.splev(ipl_t, x_list)  # x interpolate values
        y_i = si.splev(ipl_t, y_list)  # y interpolate values

        action = ActionChains(self.driver)

        # pprint(self._driver.find_elements_by_tag_name('div'))
        startElement = random.choice(
            self.driver.find_elements_by_tag_name('div'))

        # # First, go to your start point or Element:
        # action.move_to_element(startElement)
        # action.perform()

        logger.info('Начата эмуляцию движений мыши с помощью интерполяции')

        for mouse_x, mouse_y in zip(x_i, y_i):
            try:
                action.move_by_offset(mouse_x, mouse_y)
                action.perform()
            except Exception as e:
                logger.Error()
                logger.Error(f'Ошибка при установки курсора в точку:')
                logger.Error(f'- X: {mouse_x}')
                logger.Error(f'- Y: {mouse_y}')
                logger.Error(f'- Ошибка: {e}')
            else:
                logger.info(f'Установлен курсор в точку:')
                logger.info(f'- X: {mouse_x}')
                logger.info(f'- Y: {mouse_y}')

        logger.info('Конец эмуляции движений курсора')


def run_all_tests():
    driver = Driver()
    driver.create_new_driver()

    driver.set_proxy(IOUtils.get_proxy_list()[3])

    driver.get('https://2ip.ru/')

    time.sleep(20)


if __name__ == '__main__':
    run_all_tests()
