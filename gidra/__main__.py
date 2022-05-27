import time

from gidra.plugins import (change_account, change_nickname,
                            commands, windseed_blocker)
from gidra.proxy import GenshinProxy


def main():
    proxy = GenshinProxy(('localhost', 8888), ('8.209.111.105', 22101))

    proxy.add(change_account.router)
    proxy.add(change_nickname.router)
    proxy.add(windseed_blocker.router)
    proxy.add(commands.router)

    proxy.start()

    while True:
        time.sleep(3)

if __name__ == '__main__':
    main()
