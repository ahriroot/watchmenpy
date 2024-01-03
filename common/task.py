import asyncio
import os
import subprocess
from argparse import Namespace
from asyncio.subprocess import Process
from io import TextIOWrapper
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
    started_after: int = 0
    interval: int
    last_run: int = 0
    sync: bool = False


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

    def into_dict(self) -> Dict[str, Any]:
        """
        Convert task to dict.
        Reconstruct data to facilitate communication with 'rust' 
        :return: Dict[str, Any]
        """
        data = self.model_dump()

        if "max_restart" in data["task_type"]:
            data["task_type"] = {"Async": data["task_type"]}
        elif "started_after" in data["task_type"]:
            data["task_type"] = {"Periodic": data["task_type"]}
        elif "year" in data["task_type"]:
            data["task_type"] = {"Scheduled": data["task_type"]}
        else:
            raise Exception("Unknown task type")
        return data

    @classmethod
    def from_args(cls, args):
        result = cls(**args)
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """
        Convert dict to task.
        Reconstruct data to facilitate communication with 'rust'
        :param data: Dict[str, Any]
        :return: Task
        """
        result = cls(**data)
        if "Async" in result.task_type:
            result.task_type = AsyncTask(**result.task_type["Async"])
        elif "Periodic" in result.task_type:
            result.task_type = PeriodicTask(
                **result.task_type["Periodic"])
        elif "Scheduled" in result.task_type:
            result.task_type = ScheduledTask(
                **result.task_type["Scheduled"])
        else:
            raise Exception("Unknown task type")
        return result

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
    name: Optional[str] = None
    group: Optional[str] = None
    mat: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """
        Convert dict to task.
        Reconstruct data to facilitate communication with 'rust'
        :param data: Dict[str, Any]
        :return: Task
        """
        result = cls(**data)
        return result

    @classmethod
    def from_args(cls, args: Namespace) -> "Task":
        """
        Convert args to task.
        Reconstruct data to facilitate communication with 'rust'
        :param args: Dict[str, Any]
        :return: Task
        """
        if args.task_id is not None:
            return cls(id=args.task_id, mat=args.task_mat)
        elif args.task_name is not None:
            return cls(id=0, name=args.task_name, mat=args.task_mat)
        elif args.task_group is not None:
            return cls(id=0, group=args.task_group, mat=args.task_mat)
        raise Exception("Task is none")
