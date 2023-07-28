import asyncio
import json
from pathlib import Path

from common.config import Config
from common.handle import Request, Response, Status
from common.task import AsyncTask
from watchmend.command import handle_exec


async def start(config: Config) -> asyncio.Task[None]:
    return asyncio.create_task(run_sock(path=config.sock.path))


async def run_sock(path: str) -> None:
    sock_path = Path(path)

    if sock_path.exists() and sock_path.is_socket():
        sock_path.unlink()

    server: asyncio.Server = await asyncio.start_unix_server(handle_connection, path=path)
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
