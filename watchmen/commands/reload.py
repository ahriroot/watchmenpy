from argparse import Namespace
from typing import List

from common import Config
from common.handle import Request, Response
from common.task import Task
from watchmen.commands.base import task_to_request
from watchmen.engine import send
from watchmen.utils.print_result import print_result


async def reload_task(args: Namespace, config: Config) -> None:
    tasks: List[Task] = await task_to_request(args, config)
    if len(tasks) == 0:
        print_result(Response.wrong("No task to reload"))
    else:
        requests: List[Request] = []
        for t in tasks:
            requests.append(Request(command="Reload", data=t))
        print_result(await send(config, requests))
