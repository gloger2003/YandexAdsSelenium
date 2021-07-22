from seleniumwire.webdriver import Chrome
import chromedriver_autoinstaller
import time

chromedriver_autoinstaller.install()

proxy = 'http://8eKePS:8AtuC3CUy2ub@z.mobileproxy.space:64029'

wireOptions = {}
wireOptions['proxy'] = {
    'http': proxy,
    'https': proxy,
    'socks5': proxy,
    'no_proxy': 'localhost,127.0.0.1'
}


driver = Chrome()
driver.get('https://2ip.ru/')
time.sleep(1000)
