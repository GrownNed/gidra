from utils import *

class DelayPacket:
    def __init__(self, ptr):
        self.ptr = ptr

    def getdata(self):
        return self.ptr

    def setts(self,ts):
        self.ts = ts

    def getts(self):
        return self.ts

class LatencySimulator:
    def __init__(self, lostrate=10, rttmin=60, rttmax=125):
        self.lostrate = lostrate/2
        self.rttmin = rttmin/2
        self.rttmax = rttmax/2
        self.tunnel12 = []
        self.tunnel21 = []

    def clear(self):
        self.tunnel12 = []
        self.tunnel21 = []

    def send(self, send_peer, data):
        if rndvalue(1,100) <= self.lostrate:
            return
        pkg = DelayPacket(data)
        delay = rndvalue(self.rttmin, self.rttmax)
        current = getms()
        pkg.setts(current+delay)
        if send_peer == 1:
            self.tunnel12.append(pkg)
        else:
            self.tunnel21.append(pkg)

    def recv(self, recv_peer):
        current = getms()
        tunnel = None
        if recv_peer == 1:
            tunnel = self.tunnel21
        else:
            tunnel = self.tunnel12
        if len(tunnel) <= 0:
            return -1,None
        pkg = tunnel[0]
        if pkg.getts() > current:
            return -1,None
        tunnel.pop(0)
        data = pkg.getdata()
        return len(data),data
