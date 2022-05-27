from gidra import proto
from gidra.proxy import GenshinProxy, HandlerRouter, PacketDirection
from gidra.proxy.cmdids import CmdID

router = HandlerRouter()

# Не работает на себе, потому что никнейм передаётся ещё где то, но работает на всех остальных
@router(CmdID.GetPlayerSocialDetailRsp, PacketDirection.Server)
def change_nickname(proxy: GenshinProxy, msg: proto.GetPlayerSocialDetailRsp):
    msg.detail_data.nickname = f"<color=red>{msg.detail_data.nickname}</color>"
    proxy.send(msg, PacketDirection.Client)
