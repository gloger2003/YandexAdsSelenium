import time
from pprint import pprint
from random import randint
from typing import List, Tuple

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from seleniumwire.webdriver import Chrome

from Driver import Driver
from loguru import logger

import IOUtils


class TargetAdsClicker:
    def __init__(self, ads_bot: AdsBot, driver: Chrome) -> None:
        self.driver = driver
        self.is_worked = False
        pass

    def GetSiteLinks(self, reqText: str, page: int = 0):
        self.driver.yandex_se.search(reqText, page)

        allSerpItems = self.driver.find_elements_by_class_name('serp-item')

        if not allSerpItems:
            logger.info()
            logger.info(f'Найден прокси с плохой репутацией')
            logger.info(f'- Прокси: {self.driver.proxy}')
        
        logger.info('')
        logger.info(f'Кол-во ссылок до форматирования: {len(allSerpItems)}')
        logger.info(f"Из них, возможно, контекстная реклама: {len(self.driver._driver.find_elements(By.CLASS_NAME, 'Label'))}")

        siteLinks: List[Tuple[str, str]] = []
        newSerpItems: List[WebElement] = []

        logger.info('')
        logger.info('Проверка ссылок:')
        for serpItem in allSerpItems:
            if 'реклама' in serpItem.text:
                newSerpItems.append(serpItem)
            else:
                logger.info('- Ссылка из СЕО выдачи удалена')

        logger.info('')
        logger.info(f'Кол-во ссылок после форматирования: {len(newSerpItems)}')
        
        logger.info('')
        logger.info('Запись целевых ссылок и доменов')
        for serpItem in newSerpItems:
            siteLinkTags: List[WebElement] = serpItem.find_elements_by_tag_name('a')
            try:
                domen: str = siteLinkTags[1].find_elements_by_tag_name('b')[0].text
                link: str = siteLinkTags[0].get_attribute('href')

                if domen in GetTargetDomensList():
                    if domen.strip() != '':
                        siteLinks.append((domen, link))
                        logger.info(f'Записал:') 
                        logger.info(f'- {domen}')
                        logger.info(f'- {link}')
                        logger.info('')
                    else:
                        raise(IndexError())

            except IndexError:
                logger.Debug('Найден битый serp-item')
                logger.Debug('')
                pass

        return siteLinks

    def _Run(self, proxy: str='localhost'):
        for reqText in GetReqTextList():
                
            page: int = -1

            while page < self.driver.maxPageCount:
                page += 1
                self.driver.ClearAllCookies()
                
                links = self.GetSiteLinks(reqText=reqText, page=page)

                logger.info()
                logger.info('Начата эмуляция действий пользователя')
                for link in links:
                    
                    startTime = time.time()

                    logger.info(f'- Ссылка: {link[1]}')
                    logger.info(f'- Домен: {link[0]}')
                    
                    self.driver.Get(link[1])

                    while True:
                        self.driver.EmulateRandomScroll()
                        self.driver.EmulateCursorMove()
                        
                        internalLinkTags = self.driver.GetInternalLinkTags(link[0])

                        if internalLinkTags:   
                            if self.driver.ClickToRandomLinkTag(internalLinkTags, '-- Переход на внутреннюю ссылку: '):
                                self.driver.EmulateRandomScroll()

                        else:
                            logger.info()
                            logger.info('Внутренних ссылок нет. Жду 5 сек.')

                            time.sleep(5)
                            pass


                        totalTime = time.time() - startTime
                        if totalTime >= self.driver.maxResidenceTime:
                            break
                        logger.info(f'Время пребывания на данный момент: {totalTime}s')
                        
                    totalTime = time.time() - startTime
                    logger.info()
                    logger.info(f'Эмуляция действий на сайте окончена:')
                    logger.info(f'- Домен: {link[0]}:')
                    logger.info(f'- Ссылка: {link[1]}')
                    logger.info(f'- Время нахождения: {totalTime}')
                    logger.info(f'- Прокси: {proxy}')

        logger.info()
        logger.info(f'Обход целевых доменов завершён с одного прокси')
        logger.info(f'- Использованный прокси: {proxy}')
        logger.info(f'- Использованная гео-локация: {self.driver.geo}')
        logger.info(f'- Ссылок пройдено: {len(links)}')

    def Run(self):
        self.is_worked = True

        logger.info()
        logger.info('Запущен модуль работы с целевыми доменами')

        if self.driver.DEV_MODE:
            self._Run()
        else:
            for proxy in IOUtils.get_proxy_list():
                self.driver.SetProxy(proxy=proxy)
                self._Run(proxy=proxy)

        logger.info()
        logger.info('Обход целевых доменов полностью завершён со всех доступных прокси')
        logger.info(f'- Использованные прокси: {IOUtils()}')
        logger.info(f'- Использованная гео-локация: {self.driver.geo}')

        self.is_worked = False
        pass
