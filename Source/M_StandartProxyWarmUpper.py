from selenium.webdriver.remote.webelement import WebElement
from FileManager import GetProxyListWarmUp, GetReqTextWarmUpList
from Driver import Driver
from random import randint
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from Logger import DEV_MODE, Log

from typing import List, Tuple
from pprint import pprint

import time



class StandartProxyWarmUpper:
    def __init__(self, driver: Driver) -> None:
        self.log = Log()

        self.driver = driver

        self.maxVisitCount: int=2
        self.geo: str = ''
        self.maxResidenceTime: int = 600

        self.proxyList = GetProxyListWarmUp()
        pass

    def GetSiteLinks(self, reqText: str, page: int=0):

        self.driver.SearchRequest(reqText, page)

        allSerpItems = self.driver._driver.find_elements_by_class_name('serp-item')

        if not allSerpItems:
            self.log.Info()
            self.log.Info(f'Найден прокси с плохой репутацией')
            self.log.Info(f'- Прокси: {self.driver.proxy}')
        
        self.log.Info('')
        self.log.Info(f'Кол-во ссылок до форматирования: {len(allSerpItems)}')
        self.log.Info(f"Из них, возможно, контекстная реклама: {len(self.driver._driver.find_elements(By.CLASS_NAME, 'Label'))}")

        siteLinks: List[Tuple[str, str]] = []
        newSerpItems: List[WebElement] = []

        self.log.Info('')
        self.log.Info('Проверка ссылок:')
        for serpItem in allSerpItems:
            if 'реклама' in serpItem.text:
                self.log.Info('- Ссылка с контекстной рекламой удалена')
            else:
                newSerpItems.append(serpItem)

        self.log.Info('')
        self.log.Info(f'Кол-во ссылок после форматирования: {len(newSerpItems)}')
        
        self.log.Info('')
        self.log.Info('Запись ссылок и доменов')
        self.log.Info('')
        for serpItem in newSerpItems:
            siteLinkTags: List[WebElement] = serpItem.find_elements_by_tag_name('a')
            try:
                domen: str = siteLinkTags[1].find_elements_by_tag_name('b')[0].text
                link: str = siteLinkTags[0].get_attribute('href')

                if domen.strip() != '':
                    siteLinks.append((domen, link))
                    self.log.Info(f'Записал:') 
                    self.log.Info(f'- {domen}')
                    self.log.Info(f'- {link}')
                    self.log.Info('')
                else:
                    raise(IndexError())
            except IndexError:
                self.log.Debug('Найден битый serp-item')
                self.log.Debug('')
                pass

        return siteLinks

    def GetUserInput(self):
        self.geo = input('Введите местоположение или оставьте пустым: ')
        self.maxVisitCount = input('Введите сколько ссылок нужно пройти для прогрева: ')

    def _Run(self, proxy: str='localhost'):
        for reqText in GetReqTextWarmUpList():
            
            visittedCount: int = 0
            page: int = -1

            while not visittedCount >= self.maxVisitCount:
                page += 1
                links = self.GetSiteLinks(reqText=reqText, page=page)

                self.log.Info()
                self.log.Info('Начата эмуляция действий пользователя')

                for link in links:
                    if visittedCount >= self.maxVisitCount:
                        break
                    
                    startTime = time.time()

                    self.log.Info(f'- Ссылка: {link[1]}')
                    self.log.Info(f'- Домен: {link[0]}')
                    
                    while True:
                        self.driver.Get(link[1])

                        internalLinkTags = self.driver.GetInternalLinkTags(link[0])

                        if internalLinkTags:   
                            if self.driver.ClickToRandomLinkTag(internalLinkTags, '-- Переход на внутреннюю ссылку: '):
                                self.driver.EmulateRandomScroll()

                                totalTime = time.time() - startTime
                                if totalTime >= self.maxResidenceTime:
                                    break

                            self.log.Info(f'Время пребывания на данный момент: {totalTime}s')
                        else:
                            self.log.Info('Пропускаю сайт:')
                            self.log.Info(f'- Ссылка: {link[1]}')
                            self.log.Info(f'- Домен: {link[0]}')

                    visittedCount += 1
                
                self.log.Info()
                self.log.Info(f'Часть прогрева завершена:')
                self.log.Info(f'- Поисковой запрос: {reqText}')
                self.log.Info(f'- Частично прогретый прокси: {proxy}')
            
            self.log.Info()
            self.log.Info(f'Прогрев завершён')
            self.log.Info(f'- Прогретый прокси: {proxy}')


    def Run(self):
        self.log.Info()
        self.log.Info('Начат прогрев прокси')

        if DEV_MODE:
            self._Run()
        else:
            for proxy in GetProxyListWarmUp():
                self.driver.SetProxy(proxy=proxy)
            



