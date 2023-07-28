import asyncio
from asyncio.subprocess import Process
from io import TextIOWrapper
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ScheduledTask(BaseModel):
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    hour: Optional[int] = None
    minute: Optional[int] = None
    second: Optional[int] = None


class AsyncTask(BaseModel):
    max_restart: int
    has_restart: int
    started_at: int
    stopped_at: int


class PeriodicTask(BaseModel):
    started_after: int
    interval: int
    last_run: int
    sync: bool


class Task(BaseModel):
    id: int
    name: str
    command: str
    args: List[str]
    dir: Optional[str] = None
    env: Dict[str, str]
    stdin: Optional[bool] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    created_at: int
    task_type: Any
    pid: Optional[int] = None
    status: Optional[str] = "added"
    code: Optional[int] = None

    @classmethod
    def default(cls) -> "Task":
        return cls(
            id=0,
            name="Default",
            command="",
            args=[],
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
            code=None,
        )

    async def start(self) -> Process:
        stdin_file = None
        stdout_file = None
        stderr_file = None

        if self.stdin is not None:
            stdin_file: int = asyncio.subprocess.PIPE

        if self.stdout is not None:
            path = Path(self.stdout)
            parent = path.parent
            if not parent.exists():
                parent.mkdir(parents=True)
            stdout_file: TextIOWrapper = open(file=self.stdout, mode="a+")

        if self.stderr is not None:
            path = Path(self.stderr)
            parent = path.parent
            if not parent.exists():
                parent.mkdir(parents=True)
            stderr_file: TextIOWrapper = open(file=self.stderr, mode="a+")

        env: os._Environ[str] = os.environ
        if self.env is not None:
            env.update(self.env)

        child = await asyncio.create_subprocess_exec(
            *[self.command, *self.args],
            stdin=stdin_file,
            stdout=stdout_file,
            stderr=stderr_file,
            env=os.environ,
            cwd=self.dir,
            preexec_fn=subprocess.os.setsid,
        )

        return child


class TaskFlag(BaseModel):
    id: int
    name: str
    mat: bool
