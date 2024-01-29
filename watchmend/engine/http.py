import asyncio
import json
import mimetypes
from pathlib import Path

from common.config import Config
from common.handle import Request
from watchmend.command import handle_exec


async def start(config: Config) -> asyncio.Task[None]:
    return asyncio.create_task(run_http(host=config.http.host, port=config.http.port))


async def run_http(host: str, port: int) -> None:
    server: asyncio.Server = await asyncio.start_server(handle_connection, host=host, port=port)
    async with server:
        await server.serve_forever()


async def handle_connection(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    buf = await reader.read(102400)

    request = buf.decode()
    headers, body = request.split('\r\n\r\n')
    method, path, _ = headers.split('\r\n')[0].split(' ')

    if method == 'GET':
        if path == '/':
            path = '/index.html'

        path = path[1:]

        filepath = Path(__file__).parent.parent.joinpath(
            "http-panel", "dist", path
        )

        mime, _ = mimetypes.guess_type(str(filepath))

        with open(filepath, 'rb') as f:
            content = f.read()
        response = 'HTTP/1.1 200 OK\r\n'
        response += f'Content-Type: {mime}\r\n'
        response += '\r\n'
        response = response.encode() + content
        writer.write(response)
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    else:
        reses = []
        for i in json.loads(body):
            res = await handle_exec(Request.from_dict(i))
            reses.append(res)

        b = json.dumps([i.into_dict() for i in reses]).encode("utf-8")

        response = 'HTTP/1.1 200 OK\r\n'
        response += 'Content-Type: application/json\r\n'
        response += '\r\n'
        response = response.encode() + b

        writer.write(response)
        await writer.drain()

        writer.close()
        await writer.wait_closed()
