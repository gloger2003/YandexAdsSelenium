from __future__ import annotations
# from ads_bot import AdsBot

from base_tactical_thread import BaseTacticalThread
from driver import Driver


class TargetAdsClicker(BaseTacticalThread):
    def __init__(self, ads_bot: Driver) -> None:
        super().__init__(
            ads_bot,
            ads_bot.yandex_se.get_target_ads_urls_data)


class NonTargetAdsClicker(BaseTacticalThread):
    def __init__(self, ads_bot: Driver) -> None:
        super().__init__(
            ads_bot,
            ads_bot.yandex_se.get_non_target_ads_urls_data)


class SeoClicker(BaseTacticalThread):
    def __init__(self, ads_bot: Driver) -> None:
        super().__init__(
            ads_bot,
            ads_bot.yandex_se.get_seo_urls_data)


if __name__ == '__main__':
    driver = Driver()
    driver.max_page_count = 0
    driver.incognito_mode = False
    driver.create_new_driver()
    tac = SeoClicker(driver)
    tac._process('аптека', 0)
    driver.close_driver()
    # time.sleep(20)
