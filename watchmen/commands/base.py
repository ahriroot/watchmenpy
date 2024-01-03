import os
import re
from argparse import Namespace
from pathlib import Path
from typing import List

import toml

from common import Config
from common.task import Task, TaskFlag
from watchmen.utils.file import recursive_search_files


async def task_to_request(args: Namespace, config: Config) -> List[Task]:
    tasks: List[Task] = []

    if args.task_path is not None:
        mat: str = ""
        if args.run_regex is not None:
            mat = args.run_regex
        elif config.watchmen.mat is not None:
            mat = config.watchmen.mat
        else:
            mat = "^.*\\.(toml|ini|json)$"
        regex: re.Pattern[str] = re.compile(mat)
        matched_files: List[str] = recursive_search_files(
            args.task_path, regex)

        for configfile in matched_files:
            path = Path(configfile)
            if path.is_file():
                ext = os.path.splitext(path)[1]
                if ext == ".toml":
                    data = toml.load(path)
                    for t in data['task']:
                        tasks.append(Task.from_dict(t))
                    pass
                elif ext == ".ini":
                    pass
                elif ext == ".json":
                    pass
                else:
                    raise Exception(
                        f'File [{path}] is not a TOML or INI or JSON file'
                    )
        return tasks
    elif args.task_config is not None:
        path = Path(args.task_config)
        if path.is_file():
            ext = os.path.splitext(path)[1]
            if ext == ".toml":
                data = toml.load(path)
                for t in data['task']:
                    tasks.append(Task.from_dict(t))
                pass
            elif ext == ".ini":
                pass
            elif ext == ".json":
                pass
            else:
                raise Exception(
                    f'File [{path}] is not a TOML or INI or JSON file'
                )
        return tasks
    else:
        return []


async def taskflag_to_request(args: Namespace, config: Config) -> List[TaskFlag]:
    tfs: List[TaskFlag] = []

    if args.task_path is not None:
        mat: str = ""
        if args.run_regex is not None:
            mat = args.run_regex
        elif config.watchmen.mat is not None:
            mat = config.watchmen.mat
        else:
            mat = "^.*\\.(toml|ini|json)$"
        regex: re.Pattern[str] = re.compile(mat)
        matched_files: List[str] = recursive_search_files(
            args.task_path, regex)

        for configfile in matched_files:
            path = Path(configfile)
            if path.is_file():
                ext = os.path.splitext(path)[1]
                if ext == ".toml":
                    data = toml.load(path)
                    for t in data['task']:
                        tfs.append(TaskFlag.from_dict(t))
                    pass
                elif ext == ".ini":
                    pass
                elif ext == ".json":
                    pass
                else:
                    raise Exception(
                        f'File [{path}] is not a TOML or INI or JSON file'
                    )
    elif args.task_config is not None:
        path = Path(args.task_config)
        if path.is_file():
            ext = os.path.splitext(path)[1]
            if ext == ".toml":
                data = toml.load(path)
                for t in data['task']:
                    tfs.append(TaskFlag.from_dict(t))
                pass
            elif ext == ".ini":
                pass
            elif ext == ".json":
                pass
            else:
                raise Exception(
                    f'File [{path}] is not a TOML or INI or JSON file'
                )
    else:
        tfs.append(TaskFlag.from_args(args))
    return tfs
