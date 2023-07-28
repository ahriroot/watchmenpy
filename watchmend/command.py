from common import Request, Response
from watchmend.lib import run, add, re_load, start, lst


async def handle_exec(request: Request) -> Response:
    try:
        if request.command == "Run":
            return await run(request.data)
        elif request.command == "Add":
            return await add(request.data)
        elif request.command == "Reload":
            return await re_load(request.data)
        elif request.command == "Start":
            return await start(request.data)
        elif request.command == "List":
            return await lst(request.data)
    except ValueError as e:
        return Response.failed(str(e))
