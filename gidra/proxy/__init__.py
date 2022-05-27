from __future__ import annotations

import base64
from enum import Enum
from threading import Thread
from typing import Callable

from betterproto import Message
from loguru import logger

from gidra import mhycrypt
from gidra.proxy.cmdids import CmdID
from gidra.proxy.kcp_socket import KcpSocket, _Address
from gidra.proxy.packet import Packet

Handler = Callable[['GenshinProxy', Message], None]


class PacketDirection(Enum):
    Client = 0
    Server = 1


class HandlerRouter:
    _handlers: dict[tuple[CmdID, PacketDirection], Handler]

    def __init__(self):
        self._handlers = {}

    def add(self, router: HandlerRouter):
        self._handlers |= router._handlers

    def get(self, cmdid: CmdID, source: PacketDirection) -> Handler | None:
        return self._handlers.get((cmdid, source))

    def __call__(self, cmdid: CmdID, source: PacketDirection):
        def wrapper(handler: Handler):
            self._handlers[(cmdid, source)] = handler
            return handler
        return wrapper


class ServerProxy(Thread):
    client_proxy: ClientProxy

    def __init__(self, proxy: GenshinProxy, addr: _Address):
        self.proxy = proxy
        self.proxy_server_addr = addr
        self.sock = KcpSocket()
        super().__init__(daemon=True)

    def run(self):
        if not self.sock.bind(self.proxy_server_addr):
            logger.error('[C] can\'t bind')
            return

        logger.info('[C] binded')
        while True:
            data = self.sock.recv()
            # logger.debug(f'[C] {data.hex()}')
            self.proxy.handle(data, PacketDirection.Server)


class ClientProxy(Thread):
    server_proxy: ServerProxy

    def __init__(self, proxy: GenshinProxy, addr: _Address):
        self.proxy = proxy
        self.server_addr = addr
        self.sock = KcpSocket()
        super().__init__(daemon=True)

    def run(self):
        if not self.sock.connect(self.server_addr):
            logger.error('[S] can\'t connect')
            return

        logger.info('[S] connected')
        while True:
            data = self.sock.recv()
            # logger.debug(f'[S] {data.hex()}')
            self.proxy.handle(data, PacketDirection.Client)


class GenshinProxy:
    def __init__(self, src_addr: _Address, dst_addr: _Address):
        self.router = HandlerRouter()
        self.src_addr = src_addr
        self.dst_addr = dst_addr
        self.key = base64.b64decode('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')

    def add(self, router: HandlerRouter):
        self.router.add(router)

    def handle(self, data: bytes, direction: PacketDirection):
        data = mhycrypt.xor(data, self.key)

        try:
            packet = Packet().parse(data)
        except Exception:
            self.send_raw(data, direction)
            return
        
        # logger.debug(f'{direction.name} {packet.cmdid} {packet.body}')

        if handler := self.router.get(packet.cmdid, PacketDirection(direction.value ^ 1)):
            handler(self, packet.body)
        else:
            self.send_raw(data, direction)

        if packet.cmdid == CmdID.GetPlayerTokenRsp:
            self.key = mhycrypt.new_key(packet.body.secret_key_seed)

    def send(self, msg: Message, direction: PacketDirection):
        packet = Packet(body=msg)
        self.send_raw(bytes(packet), direction)

    def send_raw(self, data: bytes, direction: PacketDirection):
        data = mhycrypt.xor(data, self.key)

        match direction:
            case PacketDirection.Server: self.client_proxy.sock.send(data)
            case PacketDirection.Client: self.server_proxy.sock.send(data)

    def start(self):
        self.server_proxy = ServerProxy(self, self.src_addr)
        self.client_proxy = ClientProxy(self, self.dst_addr)

        self.server_proxy.client_proxy = self.client_proxy
        self.client_proxy.server_proxy = self.server_proxy

        self.server_proxy.start()
        self.client_proxy.start()
