from threading import Thread
import time
import sys
import os



class B():
    def __init__(self) -> None:
        self.c = 0
        pass

start = True

def main():
    while start:
        print('Работает')
        time.sleep(2)



try:
    if __name__ == '__main__':
        a = Thread(target=main)
        a.start()
        a.join()
        time.sleep(3)
        exit()

except SystemExit:
    print('Вышел')
    start = 0
except:
    sys.exit()
finally:
    input()