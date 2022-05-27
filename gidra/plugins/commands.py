from loguru import logger

from gidra import proto
from gidra.proxy import GenshinProxy, HandlerRouter, PacketDirection
from gidra.proxy.cmdids import CmdID

router = HandlerRouter()

uid = None
enter_scene_token = None


@router(CmdID.GetPlayerTokenRsp, PacketDirection.Server)
def get_player_token_rsp(proxy: GenshinProxy, msg: proto.GetPlayerTokenRsp):
    global uid
    uid = msg.uid

    proxy.send(msg, PacketDirection.Client)


@router(CmdID.SceneInitFinishRsp, PacketDirection.Server)
def scene_init_finish_rsp(proxy: GenshinProxy, msg: proto.SceneInitFinishRsp):
    global enter_scene_token
    enter_scene_token = msg.enter_scene_token
    
    msg.retcode = None
    proxy.send(msg, PacketDirection.Client)


@router(CmdID.EnterSceneReadyRsp, PacketDirection.Server)
def enter_scene_ready_rsp(proxy: GenshinProxy, msg: proto.EnterSceneReadyRsp):
    msg.retcode = None
    proxy.send(msg, PacketDirection.Client)


@router(CmdID.EnterSceneDoneRsp, PacketDirection.Server)
def enter_scene_done_rsp(proxy: GenshinProxy, msg: proto.EnterSceneDoneRsp):
    msg.retcode = None
    proxy.send(msg, PacketDirection.Client)


@router(CmdID.EnterSceneReadyRsp, PacketDirection.Server)
def enter_scene_ready_rsp(proxy: GenshinProxy, msg: proto.EnterSceneReadyRsp):
    msg.retcode = None
    proxy.send(msg, PacketDirection.Client)


@router(CmdID.PostEnterSceneRsp, PacketDirection.Server)
def post_enter_scene_rsp(proxy: GenshinProxy, msg: proto.PostEnterSceneRsp):
    msg.retcode = None
    proxy.send(msg, PacketDirection.Client)


@router(CmdID.MarkMapReq, PacketDirection.Client)
def tp_with_mark(proxy: GenshinProxy, msg: proto.MarkMapReq):
    mark = msg.mark

    if msg.op != proto.MarkMapReqOperation.ADD or not mark.name.startswith('!'):
        proxy.send(msg, PacketDirection.Server)
        return

    global uid
    global enter_scene_token

    command, *args = mark.name[1:].split()
    match command:
        case 'tp':
            pos = proto.Vector(x=mark.pos.x, y=int(args[0]), z=mark.pos.z)
            player_enter_scene_notify = proto.PlayerEnterSceneNotify(
                scene_id=msg.mark.scene_id,
                pos=pos,
                type=proto.EnterType.ENTER_GOTO_BY_PORTAL,
                target_uid=uid,
                world_level=3,
                enter_scene_token=enter_scene_token,
                is_first_login_enter_scene=False,
                scene_tag_id_list=[107, 113, 117, 125],
                enter_reason=1,
                world_type=1,
            )
            proxy.send(player_enter_scene_notify, PacketDirection.Client)
        case 'join':
            player_apply_enter_mp_req = proto.PlayerApplyEnterMpReq(target_uid=int(args[0]))
            proxy.send(player_apply_enter_mp_req, PacketDirection.Server)
        case 'open_state':
            set_open_state_req = proto.SetOpenStateReq(key=int(args[0]))
            proxy.send(set_open_state_req, PacketDirection.Server)


@router(CmdID.PrivateChatReq, PacketDirection.Client)
def chat_request(proxy: GenshinProxy, msg: proto.PrivateChatReq):
    if not msg.text.startswith('!'):
        proxy.send(msg, PacketDirection.Server)
        return
    
    command, *args = msg.text[1:].split()
    match command:
        case 'join':
            player_apply_enter_mp_req = proto.PlayerApplyEnterMpReq(target_uid=int(args[0]))
            proxy.send(player_apply_enter_mp_req, PacketDirection.Server)
