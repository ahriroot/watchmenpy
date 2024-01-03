from typing import List

from common.config import Config
from common.handle import Request, Response
from watchmen.engine.sock import send as send_sock


async def send(config: Config, requests: List[Request]) -> List[Response]:
    if config.watchmen.engine == "sock":
        return await send_sock(config.sock.path, requests)
    else:
        raise Exception("No engine found")
