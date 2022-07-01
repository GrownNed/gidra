from gidra import proto
from gidra.proxy import GenshinProxy, HandlerRouter, PacketDirection
from gidra.proxy.cmdids import CmdID

router = HandlerRouter()


@router(CmdID.GetPlayerTokenReq, PacketDirection.Client)
def change_account(proxy: GenshinProxy, msg: proto.GetPlayerTokenReq):
    msg.account_uid = '123'
    msg.account_token = 'abc'
    proxy.send(msg, PacketDirection.Server)
