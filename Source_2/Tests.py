from Driver import Driver
from pprint import pprint
from loguru import logger


def test_1():
    driver = Driver()
    driver.create_new_driver()
    driver.yandex_se.search('еда')

    logger.debug(len(driver.yandex_se.get_seo_urls_data()))


if __name__ == '__main__':
    test_1()
