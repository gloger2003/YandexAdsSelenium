from selenium.webdriver.remote.webelement import WebElement
from FileManager import GetProxyListWarmUp
from Driver import Driver
from random import randint
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from Logger import Log

from typing import List, Tuple
from pprint import pprint

import time



class MStandartProxyWarmUpper:
    def __init__(self, driver: Driver, visitCount: int=2) -> None:
        self.log = Log()

        self.driver = driver
        self.visitCount = visitCount

        self.proxyList = GetProxyListWarmUp()
        pass


    def Run(self):
        links = self.GetSiteLinks('продукты')
        pprint(links)


    def GetSiteLinks(self, text: str, page: int=None):
        reqUrl = f"https://yandex.ru/search/?text={text}"
        if page:
            reqUrl += f'&p={page}'
        self.driver.Get(reqUrl)
        time.sleep(3)

        allSerpItems = self.driver._driver.find_elements_by_class_name('serp-item')
        
        self.log.Info('')
        self.log.Info(f'Кол-во ссылок до форматирования: {len(allSerpItems)}')
        self.log.Info(f"Из них, возможно, контекстная реклама: {len(self.driver._driver.find_elements(By.CLASS_NAME, 'Label'))}")

        siteLinks: List[Tuple[str, str]] = []
        newSerpItems: List[WebElement] = []

        self.log.Info('')
        self.log.Info('Проверка ссылок')

        self.log.Info('')
        for serpItem in allSerpItems:
            if 'реклама' in serpItem.text:
                self.log.Info('Ссылка с контекстной рекламой игнорирована')
            else:
                newSerpItems.append(serpItem)

        self.log.Info()
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

