from seleniumwire.webdriver import Chrome
import chromedriver_autoinstaller
import time

chromedriver_autoinstaller.install()

driver = Chrome()
driver.get('https://vk.com/im')
time.sleep(1000)