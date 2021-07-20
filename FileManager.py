from Logger import Log
import os
from typing import List


DIR_NAME = './PREFS'
HTTP_PROXY_FILE_NAME = f'./{DIR_NAME}/HTTP_PROXIES.txt'
SOCKS5_PROXY_FILE_NAME = f'./{DIR_NAME}/SOCKS5_PROXIES.txt'
HTTP_PROXY_WARM_UP_FILE_NAME = f'./{DIR_NAME}/HTTP_WARM_UP_PROXIES.txt'
SOCKS5_PROXY_WARM_UP_FILE_NAME = f'./{DIR_NAME}/SOCKS5_WARM_UP_PROXIES.txt'

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



if __name__ == '__main__':
    GetProxyListWarmUp()