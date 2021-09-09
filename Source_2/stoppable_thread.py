import threading
from typing import Callable, Iterable


class StoppableThread(threading.Thread):
    def __init__(self, target: Callable, args: Iterable = []):
        super().__init__(target=target, args=args, daemon=True)
        self._stop_event = threading.Event()

    def stop(self):
        """ Останавливает все события в потоке, \n
            тем самым полностью останавливая поток \n
            `Нежелательное решение, но в данном случае` \n
            `у этого подхода нет негативных последствий`"""
        self._stop_event.set()

    def stopped(self):
        """ Возвращает состоние потока """
        return self._stop_event.is_set()
