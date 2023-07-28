import asyncio
from asyncio.subprocess import Process
from typing import Dict, Optional

from common.handle import Response, Status
from common.task import AsyncTask, PeriodicTask, ScheduledTask, Task, TaskFlag


class TaskProcess:
    def __init__(self, task: Task, joinhandle: Optional[asyncio.Task] = None, child: Optional[Process] = None) -> None:
        self.task = task
        self.joinhandle = joinhandle
        self.child = child


class Tasks:
    _instance = None

    def __init__(self) -> None:
        self._tasks: Dict[int, TaskProcess] = {}

    def add(self, task_id: int, tp: TaskProcess) -> None:
        self._tasks[task_id] = tp

    def check(self, task_id: int) -> bool:
        return task_id in self._tasks

    def get(self, task_id: int) -> Optional[TaskProcess]:
        return self._tasks.get(task_id)

    def __new__(cls) -> "Tasks":
        if cls._instance is None:
            cls._instance = super(Tasks, cls).__new__(cls)
        return cls._instance


tasks = Tasks()


async def update(task_id: int, pid: int, status: str, code: int) -> Response:
    """
    Update task status.
    :param task_id: Task id
    :param pid: Process id
    :param status: Task status
    :param code: Exit code
    :return: Response
    """
    tp = tasks.get(task_id)
    if tp is None:
        return Response.failed(f"Task [{task_id}] not exists")

    tp.task.pid = pid
    tp.task.status = status
    tp.task.code = code

    return Response.success(f"Task [{task_id}] updated")


async def run(task: Task) -> Response:
    """
    Run task.
    :param task: Task
    :return: Response
    """
    status = Status(
        id=1,
        name="watchmen",
        command="watchmen",
        args=["--config"],
        dir=None,
        env={},
        stdin=None,
        stdout=None,
        stderr=None,
        created_at=0,
        task_type=AsyncTask(max_restart=5, has_restart=0,
                            started_at=0, stopped_at=0),
        pid=None,
        status=None,
        exit_code=None,
    )
    return Response.success([status])


async def add(task: Task) -> Response:
    if tasks.check(task.id):
        return Response.failed(f"Task [{task.id}] already exists")
    tp = TaskProcess(task)
    tasks.add(task.id, tp)
    return Response.success(f"Task [{task.id}] added")


async def re_load(task: Task) -> Response:
    """
    Run task.
    :param task: Task
    :return: Response
    """
    status = Status(
        id=1,
        name="watchmen",
        command="watchmen",
        args=["--config"],
        dir=None,
        env={},
        stdin=None,
        stdout=None,
        stderr=None,
        created_at=0,
        task_type=AsyncTask(max_restart=5, has_restart=0,
                            started_at=0, stopped_at=0),
        pid=None,
        status=None,
        exit_code=None,
    )
    return Response.success([status])


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

        jh = asyncio.create_task(child.wait())

        tp.joinhandle = jh
        tp.child = child
        tp.task.code = None

        async def watch():
            await child.wait()
            returncode = child.returncode
            await update(tp.task.id, None, "stopped", returncode)

        asyncio.create_task(watch())

        await update(tp.task.id, child.pid, "running", None)

        return Response.success(f"Task [{tf.id}] started")
    elif isinstance(tp.task.task_type, PeriodicTask):
        raise ValueError(f"222")
    elif isinstance(tp.task.task_type, ScheduledTask):
        raise ValueError(f"333")

    raise ValueError(f"444")


async def lst(condition: Optional[TaskFlag]) -> Response:
    """
    List task.
    :param condition: Optional[TaskFlag]
    :return: Response
    """
    if condition is None:
        statuses = []
        for k, v in tasks._tasks.items():
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
        return Response.success(list(tasks._tasks.values()))
