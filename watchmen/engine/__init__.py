from typing import List

from common.config import Config
from common.handle import Request, Response
from watchmen.engine.sock import send as send_sock
from watchmen.engine.socket import send as send_socket


async def send(config: Config, requests: List[Request]) -> List[Response]:
    if config.watchmen.engine == "sock":
        return await send_sock(config.sock.path, requests)
    elif config.watchmen.engine == "socket":
        return await send_socket(config.socket.host, config.socket.port, requests)
    else:
        raise Exception("No engine found")
