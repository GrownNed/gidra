from __future__ import annotations

import struct
from dataclasses import dataclass

HANDSHAKE_FORMAT = ">IIIII"


@dataclass
class Handshake:
    magic1: int
    conv: int
    token: int
    enet: int
    magic2: int

    def __bytes__(self) -> bytes:
        return struct.pack(
            HANDSHAKE_FORMAT,
            self.magic1, self.conv, self.token, self.enet, self.magic2,
        )

    @staticmethod
    def parse(data: bytes) -> Handshake:
        return Handshake(*struct.unpack(HANDSHAKE_FORMAT, data))
