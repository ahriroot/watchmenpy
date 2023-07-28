import os
from pathlib import Path
from typing import List, Optional

import toml
from pydantic import BaseModel

from common.utils import get_with_home_path


class Watchmen(BaseModel):
    engine: str
    engines: List[str] = None
    log_dir: Optional[str] = None
    log_level: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    pid: Optional[str] = None
    mat: Optional[str] = None
    cache: Optional[str] = None


class Sock(BaseModel):
    path: str


class Socket(BaseModel):
    host: str
    port: int


class Http(BaseModel):
    host: str
    port: int


class Redis(BaseModel):
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    queue_index: Optional[int] = None
    queue_name: Optional[str] = None
    subscribe_channels: Optional[List[str]] = None
    subscribe_name: Optional[str] = None


class Config(BaseModel):
    watchmen: Watchmen
    sock: Sock
    socket: Socket
    http: Http
    redis: Redis

    @classmethod
    def init(cls, path: Optional[str] = None) -> "Config":
        """
        Initialize config from path.
        :param path: path to config file (default: "$HOME/.watchmen/config.toml")
        :return: Config
        """
        if path is None:
            home = os.path.expanduser("~")
            path = Path(os.path.join(home, ".watchmen", "config.toml"))
        return cls.from_path(path=Path(path))

    @classmethod
    def from_path(cls, path: str) -> "Config":
        config = cls.model_validate(toml.load(path))

        # "$HOME" or "~" -> "/home/username" and create parent if not exists
        if config.watchmen.log_dir is not None:
            log_dir = get_with_home_path(path=config.watchmen.log_dir)
            parent = log_dir.parent
            if not parent.exists():
                parent.mkdir(parents=True)
            config.watchmen.log_dir = str(log_dir)

        # default log level is "info"
        if config.watchmen.log_level is not None:
            allowed = ["debug", "info", "warn", "error"]
            if config.watchmen.log_level not in allowed:
                config.watchmen.log_level = "info"

        # "$HOME" or "~" -> "/home/username" and create parent if not exists
        if config.watchmen.stdout is not None:
            stdout = get_with_home_path(path=config.watchmen.stdout)
            parent = stdout.parent
            if not parent.exists():
                parent.mkdir(parents=True)
            config.watchmen.stdout = str(stdout)

        # "$HOME" or "~" -> "/home/username" and create parent if not exists
        if config.watchmen.stderr is not None:
            stderr = get_with_home_path(path=config.watchmen.stderr)
            parent = stderr.parent
            if not parent.exists():
                parent.mkdir(parents=True)
            config.watchmen.stderr = str(stderr)

        # "$HOME" or "~" -> "/home/username" and create parent if not exists
        if config.watchmen.pid is not None:
            pid = get_with_home_path(path=config.watchmen.pid)
            parent = pid.parent
            if not parent.exists():
                parent.mkdir(parents=True)
            config.watchmen.pid = str(pid)

        # default regex pattern for task config filename is "r'^.*\.(toml|ini|json)$'"
        if config.watchmen.mat is None:
            config.watchmen.mat = r"^.*\.(toml|ini|json)$"

        # "$HOME" or "~" -> "/home/username" and create parent if not exists
        if config.sock.path is not None:
            path = get_with_home_path(path=config.sock.path)
            parent = path.parent
            if not parent.exists():
                parent.mkdir(parents=True)
            config.sock.path = str(path)

        return config
