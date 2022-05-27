from collections import deque
import random
import socket
import threading
import time

from lkcp import KcpObj
from loguru import logger
from gidra.proxy.handshake import Handshake

_Address = tuple[str, int]
_BUFFER_SIZE = 1 << 16


class KcpSocket:
    def __init__(self):
        self._time = time.time()
        self.recv_queue = deque()
        self.recv_queue_semaphore = threading.Semaphore(0)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _get_time(self) -> int:
        return time.time() - self._time

    def _kcp_update(self):
        while self.kcp:
            current_time = int(self._get_time() * 1000)
            self.kcp.update(current_time)

            next_time = self.kcp.check(current_time)
            diff = next_time - current_time

            if diff > 0:
                time.sleep(diff / 1000)
    
    def _kcp_recv(self):
        while self.kcp:
            data = self.sock.recv(_BUFFER_SIZE)
            self.kcp.input(data)

            while x := self.kcp.recv()[1]:
                self.recv_queue.append(x)
                self.recv_queue_semaphore.release()

    def connect(self, addr: _Address) -> bool:
        self.sock.connect(addr)
        self.addr = addr

        hs1 = Handshake(0xff, 0, 0, 1234567890, 0xffffffff)
        self.sock.send(bytes(hs1))
        logger.debug('[S] handshake sended')

        data = self.sock.recv(_BUFFER_SIZE)
        hs2 = Handshake.parse(data)
        logger.debug('[S] handshake received')

        if (hs2.magic1, hs2.enet, hs2.magic2) != (0x145, 1234567890, 0x14514545):
            self.sock.close()
            return False

        self.kcp = KcpObj(
            hs2.conv, hs2.token,
            lambda _, x: self.sock.send(x),
        )
        self.kcp.setmtu(1200)
        self.kcp.wndsize(1024, 1024)
        self.kcp.nodelay(1, 10, 2, 1)

        threading.Thread(target=self._kcp_update).start()
        threading.Thread(target=self._kcp_recv).start()

        return True

    def bind(self, addr: _Address) -> bool:
        self.sock.bind(addr)

        data, self.addr = self.sock.recvfrom(_BUFFER_SIZE)
        hs1 = Handshake.parse(data)
        logger.debug('[C] handshake received')

        if (hs1.magic1, hs1.enet, hs1.magic2) != (0xff, 1234567890, 0xffffffff):
            self.sock.close()
            return False

        conv = random.randrange(1 << 32)
        token = random.randrange(1 << 32)

        hs2 = Handshake(0x145, conv, token, 1234567890, 0x14514545)
        self.sock.sendto(bytes(hs2), self.addr)
        logger.debug('[C] handshake sended')

        self.kcp = KcpObj(
            conv, token,
            lambda _, x: self.sock.sendto(x, self.addr),
        )
        self.kcp.setmtu(1200)
        self.kcp.wndsize(1024, 1024)

        threading.Thread(target=self._kcp_update).start()
        threading.Thread(target=self._kcp_recv).start()

        return True

    def close(self):
        if not self.kcp:
            return

        hs = Handshake(0x194, self.kcp.conv, self.kcp.token, 1, 0x19419494)
        self.sock.sendto(bytes(hs), self.addr)
        self.kcp = None

        self.sock.close()

    def send(self, data: bytes):
        self.kcp.send(data)

    def recv(self) -> bytes:
        self.recv_queue_semaphore.acquire()
        return self.recv_queue.popleft()
