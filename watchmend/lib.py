import asyncio
from asyncio.subprocess import Process
import atexit
import json
import os
from pathlib import Path
import re
import signal
from typing import Dict, Optional

from common.handle import Response, Status
from common.task import AsyncTask, PeriodicTask, ScheduledTask, Task, TaskFlag
from common.utils import get_with_home_path


class TaskProcess:
    def __init__(self, task: Task, joinhandle: Optional[asyncio.Task] = None, child: Optional[Process] = None) -> None:
        self.task = task
        self.joinhandle = joinhandle
        self.child = child


class Tasks:
    _instance = None

    def __init__(self) -> None:
        self._tasks: Dict[int, TaskProcess] = {}
        self._cache_path: Optional[Path] = None

        atexit.register(self._atexit)

    def _atexit(self):
        for v in self._tasks.values():
            if v.child is not None:
                try:
                    v.child.kill()
                except:
                    pass

    def set_cache_path(self, path: Path) -> None:
        self._cache_path = path

    def get_cache_path(self) -> Optional[Path]:
        return self._cache_path

    def add(self, task_id: int, tp: TaskProcess) -> None:
        self._tasks[task_id] = tp

    def check(self, task_id: int) -> bool:
        return task_id in self._tasks

    def get(self, task_id: int) -> Optional[TaskProcess]:
        return self._tasks.get(task_id)

    def get_by_name(self, name: str) -> Optional[TaskProcess]:
        for tp in self._tasks.values():
            if tp.task.name == name:
                return tp
        return None

    def get_all(self) -> Dict[int, TaskProcess]:
        return self._tasks

    def remove(self, task_id: int) -> None:
        if task_id in self._tasks:
            del self._tasks[task_id]

    def __new__(cls) -> "Tasks":
        if cls._instance is None:
            cls._instance = super(Tasks, cls).__new__(cls)
        return cls._instance


tasks = Tasks()


async def get_all() -> Dict[int, Task]:
    """
    Get all tasks.
    :return: Response
    """
    return tasks.get_all()


async def load(path: str) -> None:
    """
    Load tasks from file.
    :param path: File path
    :return: Response
    """
    path_home = get_with_home_path(path)

    tasks.set_cache_path(path_home)

    if not path_home.exists() or not path_home.is_file():
        raise Exception(f"Cache file [{path_home}] is not valid")

    with open(path_home, "r") as f:
        tasks_cache = json.load(f)

    for task in tasks_cache:
        tp = TaskProcess(task=Task.from_dict(task))
        if isinstance(tp.task.task_type, AsyncTask):
            if tp.task.status == "running":
                child = await tp.task.start()

                task_id = tp.task.id
                max_restart = tp.task.task_type.max_restart
                has_restart = tp.task.task_type.has_restart

                async def watch():
                    await child.wait()
                    print(task_id)
                    print(child.returncode)
                    print(max_restart)
                    print(has_restart)
                    returncode = child.returncode
                    if max_restart is None:
                        await update(task_id, None, "stopped", returncode, False)
                    else:
                        if max_restart == 0:
                            await update(task_id, None, "auto restart", returncode, True)
                        else:
                            if has_restart < max_restart:
                                await update(task_id, None, "auto restart", returncode, True)
                            else:
                                await update(task_id, None, "stopped", returncode, False)

                tp.joinhandle = asyncio.create_task(watch())
                tp.child = child
                tp.task.pid = child.pid
                tp.task.status = "running"
                tp.task.code = None
        tasks.add(tp.task.id, tp)


async def cache() -> None:
    path = tasks.get_cache_path()
    if path is not None:
        parent = path.parent
        if not parent.exists():
            parent.mkdir(parents=True)
        tasks_cache = []
        for tp in tasks.get_all().values():
            tasks_cache.append(tp.task.into_dict())
        with open(path, "w") as f:
            json.dump(tasks_cache, f)


async def update(task_id: int, pid: int, status: str, code: int, restart: Optional[bool] = False) -> Response:
    """
    Update task status.
    :param task_id: Task id
    :param pid: Process id
    :param status: Task status
    :param code: Exit code
    :param restart: Restart
    :return: Response
    """
    tp = tasks.get(task_id)
    if tp is None:
        return Response.failed(f"Task [{task_id}] not exists")

    tp.task.pid = pid
    tp.task.status = status
    tp.task.code = code

    if isinstance(tp.task.task_type, AsyncTask):
        has = tp.task.task_type.has_restart
        if restart is not None:
            if tp.task.task_type.max_restart is None:
                has = 0
            else:
                if has < tp.task.task_type.max_restart:
                    has += 1
        tp.task.task_type.has_restart = has

    return Response.success(f"Task [{task_id}] updated")


async def run(task: Task) -> Response:
    """
    Run task.
    :param task: Task
    :return: Response
    """
    await add(task)
    return await start(TaskFlag(id=task.id, name="", mat=False))


async def add(task: Task) -> Response:
    if tasks.check(task.id):
        return Response.failed(f"Task [{task.id}] already exists")

    tp = TaskProcess(task)
    tasks.add(task.id, tp)
    asyncio.create_task(cache())
    return Response.success(f"Task [{task.id}] added")


async def re_load(task: Task) -> Response:
    """
    Run task.
    :param task: Task
    :return: Response
    """
    await remove(TaskFlag(id=task.id, name="", mat=False), to_cache=False)
    return await add(task)


async def start(tf: TaskFlag) -> None:
    """
    Start task.
    :param tf: TaskFlag
    :return: None
    """
    tp = tasks.get(tf.id)
    if tp is None:
        raise ValueError(f"Task [{tf.id}] not exists")

    if isinstance(tp.task.task_type, AsyncTask):
        if tp.task.status == "running":
            raise ValueError(f"Task [{tf.id}] is running")

        child = await tp.task.start()

        async def watch():
            await child.wait()
            returncode = child.returncode
            if tp.task.task_type.max_restart is None:
                await update(tp.task.id, None, "stopped", returncode, restart)
            else:
                if tp.task.task_type.max_restart == 0:
                    await update(tp.task.id, None, "auto restart", returncode)
                else:
                    if tp.task.task_type.has_restart < tp.task.task_type.max_restart:
                        await update(tp.task.id, None, "auto restart", returncode)
                    else:
                        await update(tp.task.id, None, "stopped", returncode)

        tp.joinhandle = asyncio.create_task(watch())
        tp.child = child
        tp.task.pid = child.pid
        tp.task.status = "running"
        tp.task.code = None

        asyncio.create_task(cache())

        return Response.success(f"Task [{tf.id}] started")
    elif isinstance(tp.task.task_type, PeriodicTask):
        print("This task type is currently not supported")
    elif isinstance(tp.task.task_type, ScheduledTask):
        print("This task type is currently not supported")
    raise ValueError("Task type not supported")


async def stop(tf: TaskFlag, to_cache: bool = True) -> Response:
    tp = tasks.get(tf.id)
    if tp is None:
        raise ValueError(f"Task [{tf.id}] not exists")

    if tp.task.status != "running" and tp.task.status != "auto restart":
        raise ValueError(f"Task [{tf.id}] is not running")

    pid = tp.task.pid
    if pid is None:
        raise ValueError(f"Task [{tf.id}] is not running")

    try:
        os.kill(pid, signal.SIGTERM)
        tp.task.status = "stopped"
        if to_cache:
            asyncio.create_task(cache())
        return Response.success(f"Task [{tf.id}] stopped")
    except ProcessLookupError:
        raise ValueError(f"Task [{tf.id}] is not running")


async def restart(tf: TaskFlag) -> Response:
    await stop(tf, False)
    return await start(tf)


async def remove(tf: TaskFlag, to_cache: bool = True) -> Response:
    if tf.id > 0:
        tp = tasks.get(tf.id)
    else:
        tp = tasks.get_by_name(tf.name)

    if tp is None:
        raise ValueError(f"Task [{tf.id}] not exists")

    if tp.task.status == "running":
        raise ValueError("Task is running, please stop it first")

    tasks.remove(tp.task.id)

    if to_cache:
        asyncio.create_task(cache())

    return Response.success(f"Task [{tf.id}] removed")


async def lst(condition: Optional[TaskFlag]) -> Response:
    """
    List task.
    :param condition: Optional[TaskFlag]
    :return: Response
    """
    if condition is None:
        # list all task status
        statuses = []
        for k, v in tasks.get_all().items():
            status = Status(
                id=k,
                name=v.task.name,
                command=v.task.command,
                args=v.task.args,
                dir=v.task.dir,
                env=v.task.env,
                stdin=v.task.stdin,
                stdout=v.task.stdout,
                stderr=v.task.stderr,
                created_at=v.task.created_at,
                task_type=v.task.task_type,
                pid=v.task.pid,
                status=v.task.status,
                exit_code=v.task.code,
            )
            statuses.append(status)
        return Response.success(statuses)
    else:
        # list task status by condition
        if condition.id > 0:
            # condition by id
            tp = tasks.get(condition.id)
            if tp is None:
                return Response.success([])
            status = Status(
                id=tp.task.id,
                name=tp.task.name,
                command=tp.task.command,
                args=tp.task.args,
                dir=tp.task.dir,
                env=tp.task.env,
                stdin=tp.task.stdin,
                stdout=tp.task.stdout,
                stderr=tp.task.stderr,
                created_at=tp.task.created_at,
                task_type=tp.task.task_type,
                pid=tp.task.pid,
                status=tp.task.status,
                exit_code=tp.task.code,
            )
            return Response.success([status])
        elif condition.mat:
            # condition by name with regex
            statuses = []
            for k, v in tasks.get_all().items():
                if re.match(condition.name, v.task.name):
                    status = Status(
                        id=k,
                        name=v.task.name,
                        command=v.task.command,
                        args=v.task.args,
                        dir=v.task.dir,
                        env=v.task.env,
                        stdin=v.task.stdin,
                        stdout=v.task.stdout,
                        stderr=v.task.stderr,
                        created_at=v.task.created_at,
                        task_type=v.task.task_type,
                        pid=v.task.pid,
                        status=v.task.status,
                        exit_code=v.task.code,
                    )
                    statuses.append(status)
            return Response.success(statuses)
        else:
            # condition by name
            tp = tasks.get_by_name(condition.name)
            if tp is None:
                return Response.success([])
            status = Status(
                id=tp.task.id,
                name=tp.task.name,
                command=tp.task.command,
                args=tp.task.args,
                dir=tp.task.dir,
                env=tp.task.env,
                stdin=tp.task.stdin,
                stdout=tp.task.stdout,
                stderr=tp.task.stderr,
                created_at=tp.task.created_at,
                task_type=tp.task.task_type,
                pid=tp.task.pid,
                status=tp.task.status,
                exit_code=tp.task.code,
            )
            return Response.success([status])
