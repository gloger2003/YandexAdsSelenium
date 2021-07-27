from pprint import pprint
from Logger import Log
import os
from typing import List, Union


DIR_NAME = './PREFS'

HTTP_PROXY_FILE_NAME = f'./{DIR_NAME}/HTTP_PROXIES.txt'
SOCKS5_PROXY_FILE_NAME = f'./{DIR_NAME}/SOCKS5_PROXIES.txt'

HTTP_PROXY_WARM_UP_FILE_NAME = f'./{DIR_NAME}/HTTP_WARM_UP_PROXIES.txt'
SOCKS5_PROXY_WARM_UP_FILE_NAME = f'./{DIR_NAME}/SOCKS5_WARM_UP_PROXIES.txt'

REQ_TEXTS_WARM_UP_FILE_NAME = f'./{DIR_NAME}/REQ_TEXTS_WARM_UP.txt'
REQ_TEXTS_FILE_NAME = f'./{DIR_NAME}/REQ_TEXTS.txt'

TARGET_DOMENS_FILE_NAME = f'./{DIR_NAME}/TARGET_DOMENS.txt'
IGNORED_DOMENS_FILE_NAME = f'./{DIR_NAME}/IGNORED_DOMENS.txt'

WORK_TIMINGS_FILE_NAME = f'./{DIR_NAME}/WORK_TIMINGS.txt'
SLEEP_TIMINGS_FILE_NAME = f'./{DIR_NAME}/SLEEP_TIMINGS.txt'

AUTH_DATA_FILE_NAME = f'./{DIR_NAME}/AUTH_DATA.txt'


if not os.path.exists(DIR_NAME):
    os.mkdir(DIR_NAME)

log: Log = Log()


def ReadFile(fileName: str) -> str:
    text: str = ''
    try:
        with open(fileName, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        log.Error(f'Файл "{fileName}" не найден, создан новый!')
        open(fileName, 'w', encoding='utf-8').close()
    except Exception as e:
        log.Error(f'Ошибка при открытии файла "{fileName}"')
    return text


def FormatProxies(badProxyList: List[str], proxyType: str) -> List[str]:
    proxyList = []
    for badProxy in badProxyList:
        badProxy = badProxy.strip()
        if badProxy != '':
            splittedBadProxy = badProxy.split('@')
            splittedBadProxy.reverse()
            proxyList.append(f'{proxyType}://' + '@'.join(splittedBadProxy))
    return proxyList


def GetHttpProxyList() -> List[str]:
    return FormatProxies(ReadFile(HTTP_PROXY_FILE_NAME).split('\n'), 'http')


def GetSocksProxyList() -> List[str]:
    return FormatProxies(ReadFile(SOCKS5_PROXY_FILE_NAME).split('\n'), 'socks5')


def GetProxyList() -> List[str]:
    return GetHttpProxyList() + GetSocksProxyList()


def GetHttpProxyListWarmUp() -> List[str]:
    return FormatProxies(ReadFile(HTTP_PROXY_WARM_UP_FILE_NAME).split('\n'), 'http')


def GetSocksProxyListWarmUp() -> List[str]:
    return FormatProxies(ReadFile(SOCKS5_PROXY_WARM_UP_FILE_NAME).split('\n'), 'socks5')


def GetProxyListWarmUp() -> List[str]:
    return GetHttpProxyListWarmUp() + GetSocksProxyListWarmUp()


def GetReqTextWarmUpList() -> List[str]:
    return ReadFile(REQ_TEXTS_WARM_UP_FILE_NAME).split('\n')


def GetReqTextList() -> List[str]:
    return ReadFile(REQ_TEXTS_FILE_NAME).split('\n')


def GetTargetDomensList() -> List[str]:
    return [k.strip() for k in ReadFile(TARGET_DOMENS_FILE_NAME).split('\n')]


def GetIgnoredDomensList() -> List[str]:
    return [k.strip() for k in ReadFile(IGNORED_DOMENS_FILE_NAME).split('\n')]


def GetWorkTimingsList() -> List[str]:
    return ReadFile(WORK_TIMINGS_FILE_NAME).split('\n')


def GetSleepTimingsList() -> List[str]:
    return ReadFile(SLEEP_TIMINGS_FILE_NAME).split('\n')

def GetAuthData() -> List[str]:
    return ReadFile(AUTH_DATA_FILE_NAME).split('\n')


def GetUserInput(message: str, ConvertTo: Union[int, float, str, bool], defaultValue: Union[int, float, str, bool], errorMessage: str='Неверные данные!', loop: bool=False) -> Union[int, float, str, bool]:
    while True:
        try:
            userValue = input(f'{message}\nТип: {ConvertTo}\nЗначение по-умолчанию: {defaultValue}\nВаш ввод: ')
            convertedValue = ConvertTo(userValue)
            return convertedValue
        except:
            log.Error(errorMessage)
            log.Error(f'Значение [{userValue}] невозможно конвертировать в тип [{ConvertTo}]')

            if loop:
                log.Error('Попробуйте ввести другое значение')
            else:
                log.Warning(f'Установлено значение по-умолчанию: {defaultValue}')
                return defaultValue
    


if __name__ == '__main__':
    pprint(GetTargetDomensList())
