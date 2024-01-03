from argparse import Namespace
from typing import List

from common import Config
from common.handle import Request, Response
from common.task import Task
from watchmen.commands.base import taskflag_to_request
from watchmen.engine import send
from watchmen.utils.print_result import print_result


async def stop(args: Namespace, config: Config) -> None:
    tasks: List[Task] = await taskflag_to_request(args, config)
    if len(tasks) == 0:
        print_result(Response.wrong("No task to stop"))
    else:
        requests: List[Request] = []
        for t in tasks:
            requests.append(Request(command="Stop", data=t))
        print_result(await send(config, requests))
