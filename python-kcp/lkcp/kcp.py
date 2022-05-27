from . import core
import sys

__all__ = ["KcpObj"]

i = 0

class KcpObj:
    def __init__(self, conv, token, callback):
        self.conv = conv
        self.token = token

        global i
        self.cobj = core.lkcp_create(conv, token, i, callback)
        i += 1

    def wndsize(self, sndwnd, rcvwnd):
        core.lkcp_wndsize(self.cobj, sndwnd, rcvwnd)

    def nodelay(self, nodelay, interval, resend, nc):
        return core.lkcp_nodelay(self.cobj, nodelay, interval, resend, nc)

    def check(self, current):
        return core.lkcp_check(self.cobj, current)

    def update(self, current):
        core.lkcp_update(self.cobj, current)

    def send(self, data):
        if sys.version_info.major == 3 and isinstance(data, str):
            data = data.encode("UTF-8")
        return core.lkcp_send(self.cobj, data)

    def input(self, data):
        return core.lkcp_input(self.cobj, data)

    def recv(self):
        return core.lkcp_recv(self.cobj)

    def flush(self):
        core.lkcp_flush(self.cobj)
    
    def setmtu(self, mtu):
        core.lkcp_setmtu(self.cobj, mtu)
