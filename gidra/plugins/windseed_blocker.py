from gidra import proto
from gidra.proxy import GenshinProxy, HandlerRouter, PacketDirection
from gidra.proxy.cmdids import CmdID

router = HandlerRouter()


@router(CmdID.WindSeedClientNotify, PacketDirection.Server)
def windseed_blocker(proxy: GenshinProxy, msg: proto.WindSeedClientNotify):
    pass
