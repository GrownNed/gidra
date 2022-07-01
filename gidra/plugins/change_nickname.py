from gidra import proto
from gidra.proxy import GenshinProxy, HandlerRouter, PacketDirection
from gidra.proxy.cmdids import CmdID

router = HandlerRouter()

@router(CmdID.GetPlayerSocialDetailRsp, PacketDirection.Server)
def change_nickname_social(proxy: GenshinProxy, msg: proto.GetPlayerSocialDetailRsp):
    msg.detail_data.nickname = f"<color=red>{msg.detail_data.nickname}</color>"
    proxy.send(msg, PacketDirection.Client)

@router(CmdID.PlayerDataNotify, PacketDirection.Server)
def change_nickname_data(proxy: GenshinProxy, msg: proto.PlayerDataNotify):
    msg.nick_name = f"<color=red>{msg.nick_name}</color>"
    proxy.send(msg, PacketDirection.Client)
