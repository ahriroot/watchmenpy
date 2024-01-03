import json
import socket
from pathlib import Path
from typing import List

from common.handle import Request, Response
from watchmen.utils.serialize import CustomEncoder


async def send(path: str, requests: List[Request]) -> List[Response]:
    sock_path = Path(path)
    if not sock_path.exists():
        raise Exception(f'Socket file {path} not exists')

    client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client_socket.connect(path)

    client_message = json.dumps(requests, cls=CustomEncoder)
    client_socket.send(client_message.encode('utf-8'))

    server_response = client_socket.recv(10240).decode('utf-8')

    response: List[Response] = []
    for i in json.loads(server_response):
        response.append(Response(i['code'], i['msg'], i['data']))

    client_socket.close()

    return response
