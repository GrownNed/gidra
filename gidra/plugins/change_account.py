from gidra import proto
from gidra.proxy import GenshinProxy, HandlerRouter, PacketDirection
from gidra.proxy.cmdids import CmdID

router = HandlerRouter()


@router(CmdID.GetPlayerTokenReq, PacketDirection.Client)
def change_account(proxy: GenshinProxy, msg: proto.GetPlayerTokenReq):
    msg.account_uid = '123'
    msg.account_token = 'abc'
    proxy.send(msg, PacketDirection.Server)

@router(CmdID.PlayerDataNotify, PacketDirection.Server)
def change_nickname_2(proxy: GenshinProxy, msg: proto.PlayerDataNotify):
    msg.nick_name = f"<color=red>{msg.nick_name}</color>"
    proxy.send(msg, PacketDirection.Client)
