from __future__ import annotations

import os
import random
import time
from random import randint
from typing import Any, NamedTuple, Union

import chromedriver_autoinstaller
import numpy as np
import scipy.interpolate as si
from fake_useragent import UserAgent
from loguru import logger
from python_rucaptcha import ImageCaptcha
from selenium.common.exceptions import *
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire.webdriver import Chrome, ChromeOptions

import io_utils
from datatypes import UrlData
from pprint import pprint


class YandexSE:
    def __init__(self, driver: Driver) -> None:
        self.driver = driver
        pass

    def set_geo_location(self, geo: Union[str, None]) -> bool:
        try:
            # Загружает страницу, где устанавливается география поиска
            self.driver.go_to_url('https://yandex.ru/tune/geo?')

            # Поле с указанием города
            input_tag = self.driver.find_element_by_id('city__front-input')
            input_tag.clear()
            for ch in geo:
                input_tag.send_keys(ch)

            # Ждём прогрузки выпадающего списка
            time.sleep(2)

            popup_div = self.driver.find_element_by_class_name(
                'popup__content')

            for li in popup_div.find_elements_by_tag_name('li'):
                title = li.find_element_by_xpath(
                    './/div[@class="b-autocomplete-item__reg"]').text
                if title.strip() == geo:
                    li.click()
                continue

            # # Выпадает список и мы выбираем первый вариант Press(<Enter>)
            # input_tag.send_keys(Keys.RETURN)
            # # Еще раз Press(<Enter>), чтобы подтвердить и перезагрузиться
            # input_tag.send_keys(Keys.RETURN)
        except Exception as e:
            logger.error('Не удалось сменить гео-локацию!')
            logger.error(e)
            self.driver.back()
            return False
        else:
            logger.info(f'Установлена новая гео-локация:')
            logger.info(f'- Гео-локация: {geo}')
            time.sleep(2)
        return True

    def search(self, text: str, page: int = 0):
        """ Создаёт и отправляет фейковый запрос в Яндекс.Поиск через URL """
        logger.info(f'Поиск по запросу: {text}')
        logger.info(f'- Запрос: {text}')
        logger.info(f'- Страница: {page + 1}')
        logger.info(f'- Гео-локация: {self.driver.geo}')
        return self.driver.go_to_url(f'https://yandex.ru/search/?'
                                     f'text={text}&p={page}')

    def _get_all_urls_data(self) -> list[UrlData]:
        """ Формирует и возвращает `list[UrlData]` из всей поисковой выдачи """
        time.sleep(5)
        # Блоки с ссылками на сайты,
        # выданные поисковиком
        blocks: list[WebElement] = self.driver.find_elements_by_xpath(
            '//li[@class="serp-item desktop-card"]')

        urls_data: list[UrlData] = []
        for block in blocks:
            # try:
            # Все ссылки, содержащиеся в блоке
            # a_tags[0] - Главная ссылка
            # a_tags[1] - Подглавная ссылка
            a_tags = block.find_elements_by_tag_name('a')

            try:
                # Этот элемент есть только у рекламы
                # там находится слово "Реклама"
                block.find_element_by_xpath(
                    './/span[@class="organic__advLabel"]')
            except NoSuchElementException:
                is_ads = False
            else:
                is_ads = True
            finally:
                title = a_tags[0].text
                url = a_tags[0].get_attribute('href')
                # Сам домен указан в отдельном блоке "b"
                # Поэтому нужно разделить текст в сабтайтл блоке
                domen = a_tags[1].text.split('›')[0]
                urls_data.append(
                    UrlData(title, url, domen, is_ads, a_tags[0]))
        return urls_data

    def get_all_urls_data(self) -> list[UrlData]:
        """ `[Обёртка для YandexSE._get_all_urls_data()]` \n
            Формирует и возвращает `list[UrlData]` из всей поисковой выдачи """
        urls_data: list[UrlData] = []
        try:
            urls_data = self._get_all_urls_data()
        except Exception as e:
            logger.error(e)
        return urls_data

    def get_target_ads_urls_data(self) -> list[UrlData]:
        """ Возвращает `list[UrlData]`, в котором только целевые домены"""

        # Домены, которые нужно оставить
        target_domens = io_utils.get_target_domens()
        urls_data = self.get_all_urls_data()

        # Форматированный список
        new_urls_data: list[UrlData] = []
        for url_data in urls_data:
            if not url_data.is_ads:
                # logger.debug(url_data.domen)
                continue
            # Указывает, является ли домен целевым
            is_targeted = False
            for target_domen in target_domens:
                if url_data.domen in target_domen:
                    is_targeted = True
                    break
            # Если домен является целевым,
            # то добавляем его в список
            if is_targeted:
                new_urls_data.append(url_data)

        return new_urls_data

    def get_non_target_ads_urls_data(self) -> list[UrlData]:
        """ Возвращает `list[UrlData]` без игнорируемых доменов """
        # Домены, которые нужно исключить
        ignored_domens = io_utils.get_ignored_domens()
        urls_data = self.get_all_urls_data()

        # Форматированный список
        new_urls_data: list[UrlData] = []
        for url_data in urls_data:
            # Указывает, нужно ли домен игнорировать
            is_ignored = False
            for ignored_domen in ignored_domens:
                if url_data.domen in ignored_domen:
                    is_ignored = True
                    break
            # Если домен не является игнорируемым,
            # то добавляем его в список
            if not is_ignored:
                new_urls_data.append(url_data)
        return new_urls_data

    def get_seo_urls_data(self) -> list[UrlData]:
        """ Возвращает `list[UrlData]` только из SEO-выдачи"""
        pprint(self.get_all_urls_data())
        return [k for k in self.get_all_urls_data() if not k.is_ads]


class Page:
    def __init__(self, driver: Driver):
        self.driver = driver

    def emulate_random_scrolling(self):
        directions = ['Скролл вверх', 'Скролл вниз']
        logger.info(f'-- Начата эмуляция скроллинга страницы')
        for _ in range(3):
            current_direction = randint(0, 1)

            logger.debug(
                f'--- {_}. Направление: {directions[current_direction]}')
            for _ in range(randint(1, 3)):
                self.driver.driver.find_element_by_tag_name('body').send_keys(
                    Keys.PAGE_DOWN if current_direction == 1 else Keys.PAGE_UP
                )
                logger.info(f'---- {directions[current_direction]}: {_}')
                time.sleep(1)

    def emulate_cursor_moving(self):
        w = self.driver.execute_script('return window.innerWidth')
        h = self.driver.execute_script('return window.innerHeight')

        x = random.randint(w // 10, w)
        y = random.randint(h // 10, h)

        # Curve base:
        points = [[0, 0], [0, 2], [2, 3],
                  [8, 8], [6, 3], [8, 2], [8, 0]]
        points = np.array(points)

        x = points[:, 0]
        y = points[:, 1]

        t = range(len(points))
        ipl_t = np.linspace(0.0, len(points) - 1, 10)

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

        action = ActionChains(self.driver.driver)

        try:
            start_element = random.choice(
                self.driver.driver.find_elements_by_tag_name('div'))
        except (NoSuchElementException,
                ElementNotInteractableException,
                ElementNotVisibleException,
                ElementNotSelectableException):
            logger.debug('Не удалось установить '
                         'стартовую позицию для курсора')
        else:
            action.move_to_element(start_element)
            action.perform()

        logger.info('Начата эмуляция движений '
                    'мыши с помощью интерполяции')

        for mouse_x, mouse_y in zip(x_i, y_i):
            try:
                action.move_by_offset(mouse_x, mouse_y)
                action.perform()
            except Exception as e:
                logger.error(f'Ошибка при установки курсора в точку:')
                logger.error(f'- X: {mouse_x}')
                logger.error(f'- Y: {mouse_y}')
                logger.error(f'- Ошибка: {e}')
                break
            else:
                logger.info(f'Установлен курсор в точку:')
                logger.info(f'- X: {mouse_x}')
                logger.info(f'- Y: {mouse_y}')

        logger.info('Конец эмуляции движений курсора')

    def emulate_all_actions(self):
        self.emulate_cursor_moving()
        self.emulate_random_scrolling()

    def solve_yandex_captcha(self, url: str, rucaptcha_key: str) -> bool:
        time.sleep(5)
        self.driver.find_element_by_class_name(
            'CheckboxCaptcha-Button').click()
        time.sleep(3)

        # Ссылка на изображения для расшифровки
        image_url = self.driver.find_element_by_class_name(
            'AdvancedCaptcha-Image').get_attribute('src')

        # Возвращается JSON содержащий информацию для решения капчи
        user_answer = ImageCaptcha.ImageCaptcha(
            rucaptcha_key=rucaptcha_key).captcha_handler(
                captcha_link=image_url)

        if not user_answer['error']:
            # решение капчи
            self.driver.find_element_by_class_name(
                'Textinput-Control').send_keys(user_answer['captchaSolve'])
            self.driver.find_element_by_class_name(
                'Textinput-Control').send_keys(Keys.RETURN)
            self.driver.go_to_url(url)
            return True

        else:
            # Тело ошибки, если есть
            print(user_answer['errorBody'])
            print(user_answer['errorBody'])
            return False

    def try_solve_yandex_captcha(self, url: str) -> bool:
        try:
            if 'Ой' in self.driver.title():
                rucaptcha_key = io_utils.get_rucaptcha_key()
                if rucaptcha_key != '':
                    return self.solve_yandex_captcha(url, rucaptcha_key)
                else:
                    raise ValueError('Ключ для решения капчи не указан!')
        except Exception as e:
            logger.error(e)
            return False
        return True

    def get_internal_link_tags(self) -> list[WebElement]:
        try:
            internal_link_tags = [
                k for k in self.driver.driver.find_elements_by_tag_name('a')]
        except (AttributeError, NoSuchElementException):
            logger.warning('Не удалось получить внутренние ссылки!')
            return []
        else:
            return internal_link_tags

    def go_to_internal_page(self, link_tag: WebElement) -> bool:
        try:
            link_tag.click()
        except Exception:
            return False
        else:
            try:
                self.driver.driver.switch_to.window(
                    window_name=self.driver.driver.window_handles[1])
                self.driver.close_driver()

                self.driver.driver.switch_to.window(
                    window_name=self.driver.driver.window_handles[0])
            except Exception:
                pass
        return True

    def click_to_random_link_tag(self,
                                 link_tags: list[WebElement],
                                 info: str) -> bool:
        """ Переходит по любой ссылке на странице """
        for _ in range(20):
            if self.go_to_internal_page(
                    random.choice(link_tags)):
                logger.info(f'{info}: '
                            f'{self.driver.current_url}')
                return True
        return False


class Driver:
    def __init__(self) -> None:
        self.DEV_MODE: bool = False
        self.incognito_mode: bool = False
        self.proxy: str = None
        self.geo: str = None
        self.user_agent: str = None

        self.max_page_count = 1
        self.max_residence_time = 100
        self.max_visit_count = 1

        chromedriver_autoinstaller.install()

    def _set_proxy(self, proxy: str) -> None:
        if proxy or self.proxy:
            self.proxy = proxy \
                if proxy else self.proxy

            if 'socks' in self.proxy:
                self.wire_options['proxy'] = {
                    'socks5': self.proxy,
                }
            elif 'http' in self.proxy:
                self.wire_options['proxy'] = {
                    'http': self.proxy,
                    'https': self.proxy,
                }
            self.wire_options['proxy']['no_proxy'] = 'localhost,127.0.0.1'

    def _set_incognito_mode(self, incognito_mode: bool) -> None:
        if incognito_mode or self.incognito_mode:
            self.incognito_mode = incognito_mode \
                if incognito_mode else self.incognito_mode
            self.chrome_options.add_argument('--incognito')

    def _set_user_agent(self, user_agent: str) -> None:
        # if user_agent or self.user_agent:
        #     self.user_agent = user_agent \
        #         if user_agent else self.user_agent
        #     self.chrome_options.add_argument(f'--user-agent={self.user_agent}')
        try:
            ua = UserAgent()
            self.chrome_options.add_argument(f'--user-agent={ua.random}')
        except Exception as e:
            logger.warning('Не удалось установить рандомный Юзер-агент')
            logger.error(e)
            pass

    def _set_geo(self, geo: str) -> None:
        if geo or self.geo:
            self.geo = geo \
                if geo else self.geo
            self.set_geo_location(self.geo)

    def _init_options(self) -> None:
        self.chrome_options.add_argument(
            '--ignore-ssl-errors')
        self.chrome_options.add_argument(
            '--ignore-certificate-errors-spki-list')
        self.chrome_options.add_argument(
            '--disable-logging')
        self.chrome_options.add_experimental_option(
            "excludeSwitches", ["disable-logging"])
        self.chrome_options.add_argument("--incognito")
        self.chrome_options.add_experimental_option(
            "excludeSwitches", ["enable-logging"])
        self.chrome_options.add_experimental_option(
            'useAutomationExtension', False)
        self.chrome_options.add_experimental_option(
            "excludeSwitches", ["enable-automation"])
        self.chrome_options.add_argument("--disable-blink-features")
        self.chrome_options.add_argument(
            "--disable-blink-features=AutomationControlled")
        # self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--no-sandbox")
        # self.chrome_options.add_experimental_option("prefs", {
        #     "download.default_directory": os.path.abspath('.'),
        #     "download.prompt_for_download": False,
        #     "download.directory_upgrade": True,
        # })
        # self.chrome_options.add_argument("--headless")

    def _create_new_driver(self):
        self._init_options()
        self.driver = Chrome(seleniumwire_options=self.wire_options,
                             chrome_options=self.chrome_options,
                             service_log_path='NUL')
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    const newProto = navigator.__proto__
                    delete newProto.webdriver
                    navigator.__proto__ = newProto
                    """
            }
        )

        size = (random.randint(1000, 1920),
                random.randint(900, 1020))
        self.driver.set_window_size(*size)

        return self.driver

    def create_new_driver(self,
                          proxy: str = None,
                          incognito_mode: bool = False,
                          geo: str = None,
                          user_agent: str = None):

        self.wire_options = {}
        self.chrome_options = ChromeOptions()

        self._set_proxy(proxy)
        self._set_incognito_mode(incognito_mode)
        self._set_user_agent(user_agent)

        self.close_driver()
        self.driver = self._create_new_driver()

        self.page = Page(self)
        self.yandex_se = YandexSE(self)

        self._set_geo(geo)

        logger.debug('Запущена новая копия браузера:')
        logger.debug(f'- Прокси: {self.proxy}')
        logger.debug(f'- Юзер-агент: {self.user_agent}')
        logger.debug(f'- Гео-локация: {self.geo}')
        logger.debug(f'- Режим инкогнито: {self.incognito_mode}')

    def close_driver(self):
        """ Закрывает окно браузера """
        try:
            self.driver.quit()
        except AttributeError:
            pass
        except Exception as e:
            logger.error(f'Непредвиденная ошибка: {e}')
        else:
            logger.debug('Браузер успешно закрыт')

    def clear_all_cookies(self):
        self.driver.delete_all_cookies()
        logger.debug('Все куки удалены')

    def set_proxy(self, proxy: Union[str, None]):
        self.clear_all_cookies()
        self.create_new_driver(proxy=proxy)

    def set_geo_location(self, geo: Union[str, None]):
        self.yandex_se.set_geo_location(geo)

    def go_to_url(self, url: str) -> bool:
        """ Загружает указанную ссылку """

        logger.info(f'Загрузка новой ссылки: {url}')

        for k in range(5):
            try:
                self.driver.get(url)
            except AttributeError:
                break
            except Exception as e:
                logger.critical(f'Не удалось загрузить страницу:')
                logger.critical(f'- Сообщение об ошибке: {e}')
                logger.critical(f'- Прокси: {self.proxy}')
                logger.critical(f'- Попытка: {k + 1}')

                time.sleep(3)
            else:
                return self.page.try_solve_yandex_captcha(url)
        return False

    def find_element_by_xpath(self, xpath: str) -> WebElement:
        return self.driver.find_element_by_xpath(xpath)

    def find_elements_by_xpath(self, xpath: str) -> list[WebElement]:
        return self.driver.find_elements_by_xpath(xpath)

    def find_element_by_tag_name(self, tag_name: str) -> WebElement:
        return self.driver.find_element_by_tag_name(tag_name)

    def find_elements_by_tag_name(self, tag_name: str) -> list[WebElement]:
        return self.driver.find_elements_by_tag_name(tag_name)

    def find_element_by_class_name(self, class_name: str) -> WebElement:
        return self.driver.find_element_by_class_name(class_name)

    def find_elements_by_class_name(self, class_name: str) -> list[WebElement]:
        return self.driver.find_elements_by_class_name(class_name)

    def find_element_by_id(self, id: str) -> WebElement:
        return self.driver.find_element_by_id(id)

    def find_elements_by_id(self, id: str) -> list[WebElement]:
        return self.driver.find_elements_by_id(id)

    def title(self):
        """ Возвращает текущий заголовок открытой вкладки """
        return self.driver.title

    def execute_script(self, script: str, *args) -> Any:
        return self.driver.execute_script(script, *args)

    def get_page_source(self) -> str:
        return self.driver.execute_script("return document.body.outerHTML;")


if __name__ == '__main__':
    from Tests import test_1
    test_1()
    time.sleep(30)
    pass
