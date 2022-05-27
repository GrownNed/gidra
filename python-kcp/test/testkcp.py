# -*- coding: utf-8 -*-
import lkcp
from lkcp import KcpObj
from utils import *
from latencysm import LatencySimulator
import sys

g_oLsm = None

_input = input if sys.version_info.major == 3 else raw_input

def test(mode):
    global g_oLsm
    initrndseed()
    g_oLsm = LatencySimulator(25, 80, 150)
    conv = 123
    token = 321
    p1 = 1
    p2 = 2
    okcp1 = KcpObj(conv, token, lambda _, x: g_oLsm.send(1, x))
    okcp2 = KcpObj(conv, token, lambda _, x: g_oLsm.send(2, x))
    start_ts = getms()
    slap = start_ts + 20
    index = 0
    inext = 0
    count = 0
    sumrtt = 0
    maxrtt = 0
    okcp1.wndsize(128,128)
    okcp2.wndsize(128,128)

    if mode == 0:
        okcp1.nodelay(0, 10, 0, 0)
        okcp2.nodelay(0, 10, 0, 0)
    elif mode == 1:
        okcp1.nodelay(0, 10, 0, 1)
        okcp2.nodelay(0, 10, 0, 1)
    else:
        okcp1.nodelay(1, 10, 2, 1)
        okcp2.nodelay(1, 10, 2, 1)

    while True:
        current = getms()
        nextt1 = okcp1.check(current)
        nextt2 = okcp2.check(current)
        nextt = min(nextt1, nextt2)
        diff = nextt - current
        if diff > 0:
            msleep(diff)
            current = getms()

        okcp1.update(current)
        okcp2.update(current)

        ##每隔 20ms，okcp1发送数据
        while current >= slap:
            s1 = uint322netbytes(index)
            s2 = uint322netbytes(current)
            okcp1.send(s1+s2)
            slap += 20
            index += 1

        #处理虚拟网络：检测是否有udp包从p1->p2
        while True:
            ilen,pkg = g_oLsm.recv(p2)
            if ilen < 0:
                break
            #如果 p2收到udp，则作为下层协议输入到okcp2
            okcp2.input(pkg)

        #处理虚拟网络：检测是否有udp包从p2->p1
        while True:
            ilen,pkg = g_oLsm.recv(p1)
            if ilen < 0:
                break
            #如果 p1收到udp，则作为下层协议输入到okcp1
            okcp1.input(pkg)

        #okcp2接收到任何包都返回回去
        while True:
            ilen,pkg = okcp2.recv()
            if ilen <= 0:
                break
            okcp2.send(pkg)

        #okcp1收到okcp2的回射数据
        while True:
            ilen,pkg = okcp1.recv() 
            if ilen <= 0:
                break
            sn = netbytes2uint32(pkg[:4])
            ts = netbytes2uint32(pkg[4:8])
            rtt = current - ts
            if sn != inext:
                print("ERROR sn count %d %d!=%d\n"%(count, sn, inext))
                return
            inext += 1
            sumrtt += rtt
            count += 1
            if rtt > maxrtt:
                maxrtt = rtt
            print("[RECV] mode=%d sn=%d rtt=%d\n"%(mode, sn, rtt))

        if inext > 20:
            break

    cost = getms() - start_ts
    print("mode %d total %dms avgrtt=%d maxrtt=%d\n"%(mode, cost, sumrtt/count, maxrtt))
    del okcp1
    del okcp2

test(0) #默认模式，类似 TCP：正常模式，无快速重传，常规流控
_input("press enter to next")
test(1) #普通模式，关闭流控等
_input("press enter to next")
test(2) #快速模式，所有开关都打开，且关闭流控