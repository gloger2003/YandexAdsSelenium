# from base_tactical_thread import BaseTacticalThread
import datetime
from typing import NamedTuple

from selenium.webdriver.remote.webelement import WebElement

# if __name__ == '__main__':
#     from base_tactical_thread import BaseTacticalThread


class UrlData(NamedTuple):
    title: str
    url: str
    domen: str
    is_ads: bool
    tag: WebElement


class TacticalModule(NamedTuple):
    title: str
    desc: str
    obj: object


class Timing(NamedTuple):
    start: datetime.time
    end: datetime.time
