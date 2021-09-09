from __future__ import annotations

import datetime
from typing import NamedTuple

from selenium.webdriver.remote.webelement import WebElement


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
    version: str


class Timing(NamedTuple):
    start: datetime.time
    end: datetime.time


class Command(NamedTuple):
    name: str
    args: list[str]
