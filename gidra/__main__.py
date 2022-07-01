from gidra.plugins import (change_account, change_nickname,
                            commands, windseed_blocker)

import requests
from gidra.proxy import GenshinProxy
from bottle import route, run, request
from gidra.proto import QueryCurrRegionHttpRsp
import ec2b, base64

@route('/query_cur_region')
def handle_query_cur():
    # Trick to bypass system proxy, this way we don't need to hardcode ec2b key
    session = requests.Session()
    session.trust_env = False

    r = session.get(f'https://oseurodispatch.yuanshen.com/query_cur_region?{request.query_string}')

    proto = QueryCurrRegionHttpRsp()
    proto.parse(base64.b64decode(r.text))

    if proto.retcode == 0:
        proto.region_info.gateserver_ip = '127.0.0.1'
        proto.region_info.gateserver_port = 8888
        proxy.key = ec2b.derive(proto.client_secret_key)

    return base64.b64encode(bytes(proto)).decode()

proxy = GenshinProxy(('127.0.0.1', 8888), ('47.245.143.151', 22102))

def main():
    proxy.add(change_account.router)
    proxy.add(change_nickname.router)
    proxy.add(windseed_blocker.router)
    proxy.add(commands.router)

    proxy.start()

    run(host='127.0.0.1', port=8081, debug=False)

if __name__ == '__main__':
    main()
