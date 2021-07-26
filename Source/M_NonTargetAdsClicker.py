import time
from typing import List, Tuple

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

from Driver import Driver
from IOManager import GetProxyList, GetReqTextList, GetIgnoredDomensList
from Logger import Log


class NonTargetAdsClicker:
    def __init__(self, driver: Driver) -> None:
        self.log = Log()
        self.driver = driver

        # self.driver.maxPageCount: int = 2
        # self.driver.maxResidenceTime: int = 20
        self.isWorked = False
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
                newSerpItems.append(serpItem)
            else:
                self.log.Info('- Ссылка из СЕО выдачи удалена')

        self.log.Info('')
        self.log.Info(f'Кол-во ссылок после форматирования: {len(newSerpItems)}')
        
        self.log.Info('')
        self.log.Info('Запись нецелевых ссылок и доменов')
        for serpItem in newSerpItems:
            siteLinkTags: List[WebElement] = serpItem.find_elements_by_tag_name('a')
            try:
                domen: str = siteLinkTags[1].find_elements_by_tag_name('b')[0].text
                link: str = siteLinkTags[0].get_attribute('href')

                if not domen in GetIgnoredDomensList():
                    if domen.strip() != '':
                        siteLinks.append((domen, link))
                        self.log.Info(f'Записал:') 
                        self.log.Info(f'- {domen}')
                        self.log.Info(f'- {link}')
                        self.log.Info('')
                    else:
                        raise(IndexError())
                else:
                    self.log.Info(f'Домен игнорирован: {domen}')

            except IndexError:
                self.log.Debug('Найден битый serp-item')
                self.log.Debug('')
                pass

        return siteLinks

    def _Run(self, proxy: str='localhost'):
        for reqText in GetReqTextList():
                
            page: int = -1

            while page < self.driver.maxPageCount:
                page += 1
                links = self.GetSiteLinks(reqText=reqText, page=page)

                self.log.Info()
                self.log.Info('Начата эмуляция действий пользователя')

                for link in links:   
                    startTime = time.time()
                    totalTime = 0

                    self.log.Info(f'- Ссылка: {link[1]}')
                    self.log.Info(f'- Домен: {link[0]}')
                    
                    while True:
                        self.driver.Get(link[1])

                        internalLinkTags = self.driver.GetInternalLinkTags(link[0])

                        if internalLinkTags:   
                            if self.driver.ClickToRandomLinkTag(internalLinkTags, '-- Переход на внутреннюю ссылку: '):
                                self.driver.EmulateRandomScroll()

                        else:
                            self.log.Info('Пропускаю сайт:')
                            self.log.Info(f'- Ссылка: {link[1]}')
                            self.log.Info(f'- Домен: {link[0]}')
                            break


                        totalTime = time.time() - startTime
                        if totalTime >= self.driver.maxResidenceTime:
                            break
                        self.log.Info(f'Время пребывания на данный момент: {totalTime}s')


                    self.log.Info()
                    self.log.Info(f'Эмуляция действий на сайте окончена:')
                    self.log.Info(f'- Домен: {link[0]}:')
                    self.log.Info(f'- Ссылка: {link[1]}')
                    self.log.Info(f'- Время нахождения: {totalTime}')
                    self.log.Info(f'- Прокси: {proxy}')

            self.log.Info()
            self.log.Info(f'Обход нецелевого домена завершён:')
            self.log.Info(f'- Использованный прокси: {proxy}')
            self.log.Info(f'- Использованная гео-локация: {self.driver.geo}')
            self.log.Info(f'- Ссылок пройдено: {len(links)}')


    def Run(self):
        self.isWorked = True

        self.log.Info()
        self.log.Info('Запущен модуль работы с целевыми доменами')

        if self.driver.DEV_MODE:
            self._Run()
        else:
            for proxy in GetProxyList():
                self.driver.SetProxy(proxy=proxy)
                self._Run(proxy=proxy)

        self.log.Info()
        self.log.Info('Обход нецелевых доменов полностью завершён со всех доступных прокси:')
        self.log.Info(f'- Использованные прокси: {GetProxyList()}')
        self.log.Info(f'- Использованная гео-локация: {self.driver.geo}')

        self.isWorked = False
        pass

