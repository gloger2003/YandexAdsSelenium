from __future__ import annotations
from distutils.log import error
import io_utils
from dev_cfg import DEV_MODE
import time

from types import FunctionType, MethodType
from typing import Callable

from loguru import logger

# import datatypes
from datatypes import UrlData
from driver import Driver, YandexSE, UrlData
from stoppable_thread import StoppableThread


class BaseTacticalThread:
    def __init__(self, driver: Driver, get_urls_data: MethodType) -> None:
        self.__is_worked = False
        self.__thread: StoppableThread = None

        self.driver: Driver = driver
        self.get_urls_data: YandexSE.get_all_urls_data = get_urls_data

    @staticmethod
    def log_msg_domen_complete(url_data:  UrlData):
        logger.info('Домен успешно обработан:')
        logger.info(f' | Название ссылки: {url_data.title}')
        logger.info(f' | Домен: {url_data.domen}')

    @staticmethod
    def log_msg_none_search(text: str, page: int, geo: str):
        logger.info('Не удалось обработать поисковой запрос:')
        logger.info(f' | Ключ-запрос: {text}')
        logger.info(f' | Страница: {page}')
        logger.info(f' | Геолокация поиска: {geo}')

    @staticmethod
    def log_msg_none_link_tags(text: str, page: int, geo: str):
        logger.info('Полезные ссылки отсутствуют:')
        logger.info(f' | Ключ-запрос: {text}')
        logger.info(f' | Страница: {page}')
        logger.info(f' | Геолокация поиска: {geo}')

    @logger.catch
    def _process(self, text: str, page: int):
        """ Запуск обобщённой логики для работы с сайтами """
        if self.driver.yandex_se.search(text, page):
            urls_data: list[UrlData] = self.get_urls_data()
            # Если получили список целевых ссылок
            if urls_data:
                for url_data in urls_data:
                    try:
                        # Якобы кликаем на ссылку и переходим на страницу
                        # url_data.tag.click()
                        self.driver.go_to_url(url_data.url)
                        # time.sleep(3)
                        self.driver.page.emulate_all_actions()
                    except Exception as e:
                        logger.error(e)
                    else:
                        self.log_msg_domen_complete(url_data)
            else:
                self.log_msg_none_link_tags(text, page, self.driver.geo)
        else:
            self.log_msg_none_search(text, page, self.driver.geo)

        # Если нужно, то переходим на след. страницу
        # и выполняем ту же логику с помощью рекурсии
        if page < self.driver.max_page_count:
            self._process(text, page + 1)

    def run(self):
        """ (Основной метод) \n
            Подготавливает драйвер и зацикливает `self._process` """
        try:
            self.__is_worked = True
            proxies = io_utils.get_proxies()
            proxies = proxies if proxies else [None]

            keywords = io_utils.get_keywords()
            for keyword in keywords:
                for proxy in proxies:
                    self.driver.create_new_driver(proxy=proxy)
                    for page in range(self.driver.max_page_count):
                        self._process(keyword, page)
        except Exception as e:
            logger.error(e)
        finally:
            self.__is_worked = False
            logger.success('Модуль завершил свою работу!')

    def start_thread(self) -> StoppableThread:
        """ Запускает `self.offline_process` в отдельном потоке """
        self.__thread = StoppableThread(target=self.offline_process)
        self.__thread.start()
        self.__is_worked = True

    def stop_thread(self):
        """ Останавливает отдельный поток с `self.offline_process`,
            тем самым останавливая работу всей логики """
        self.__thread.stop()
        self.__is_worked = False

    def is_stopped(self):
        """ `Thread.stopped` \n
            Возвращает текущее состояние потока """
        return self.__thread.stopped()

    def is_worked(self) -> bool:
        """ Показывает, завершена ли работа логики в `self.offline_process`, \n
            если `self.offline_process` не был запущен в потоке, \n
            то возвращает `False`"""
        return self.__is_worked
