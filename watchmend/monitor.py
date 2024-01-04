
import asyncio
from datetime import datetime
import time

from .lib import get_all, start
from common.task import AsyncTask, PeriodicTask, ScheduledTask, TaskFlag


async def rerun_tasks(delay: int) -> None:
    tasks = await get_all()
    for _id, tp in tasks.items():
        if isinstance(tp.task.task_type, AsyncTask):
            if tp.task.status == 'auto restart':
                await start(TaskFlag(id=_id, name=None, group=None, mat=False))
        elif isinstance(tp.task.task_type, ScheduledTask):
            now = datetime.now()
            year = now.year if tp.task.task_type.year is None else tp.task.task_type.year
            month = now.month if tp.task.task_type.month is None else tp.task.task_type.month
            day = now.day if tp.task.task_type.day is None else tp.task.task_type.day
            hour = now.hour if tp.task.task_type.hour is None else tp.task.task_type.hour
            minute = now.minute if tp.task.task_type.minute is None else tp.task.task_type.minute
            second = now.second if tp.task.task_type.second is None else tp.task.task_type.second
            exec_dt = datetime(year, month, day, hour, minute, second)
            exec_timestamp_utc = exec_dt.timestamp()
            now_timestamp_utc = now.timestamp()
            diff = abs(exec_timestamp_utc - now_timestamp_utc)
            if diff < delay and exec_timestamp_utc <= now_timestamp_utc and tp.task.status == 'waiting':
                async def inner():
                    await asyncio.sleep(diff)
                    await start(TaskFlag(id=_id, name=None, group=None, mat=False))
                asyncio.create_task(inner())
        elif isinstance(tp.task.task_type, PeriodicTask):
            now = datetime.now().timestamp()
            if now >= tp.task.task_type.started_after and now - tp.task.task_type.last_run >= tp.task.task_type.interval:
                if tp.task.task_type.sync:
                    if tp.task.status == "interval" or tp.task.status == "executing":
                        await start(TaskFlag(id=_id, name=None, group=None, mat=False))
                else:
                    if tp.task.status == "interval":
                        await start(TaskFlag(id=_id, name=None, group=None, mat=False))


async def run_monitor(interval: int) -> None:
    while True:
        start_time = time.time()
        await rerun_tasks(5)
        elapsed_time = time.time() - start_time
        wait_time = max(0, interval - elapsed_time)
        await asyncio.sleep(wait_time)
