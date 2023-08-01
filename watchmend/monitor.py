
import asyncio
import time

from .lib import get_all, start
from common.task import AsyncTask, TaskFlag


async def rerun_tasks() -> None:
    tasks = await get_all()
    for _id, tp in tasks.items():
        if isinstance(tp.task.task_type, AsyncTask):
            if tp.task.status == 'auto restart':
                await start(TaskFlag(id=_id, name=tp.task.name, mat=False))


async def run_monitor() -> None:
    interval = 5
    while True:
        start_time = time.time()
        await rerun_tasks()
        elapsed_time = time.time() - start_time
        wait_time = max(0, interval - elapsed_time)
        await asyncio.sleep(wait_time)
