import asyncio
import json

from common.config import Config
from common.handle import Request
from watchmend.command import handle_exec


async def start(config: Config) -> asyncio.Task[None]:
    return asyncio.create_task(run_socket(host=config.socket.host, port=config.socket.port))


async def run_socket(host: str, port: int) -> None:
    server: asyncio.Server = await asyncio.start_server(handle_connection, host=host, port=port)
    async with server:
        await server.serve_forever()


async def handle_connection(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    buf = await reader.read(102400)

    text = buf.decode()
    responses = []
    for i in json.loads(text):
        response = await handle_exec(Request.from_dict(i))
        responses.append(response)

    b = json.dumps([i.into_dict() for i in responses]).encode("utf-8")

    writer.write(b)
    await writer.drain()

    writer.close()
    await writer.wait_closed()
