import os
import re
from argparse import Namespace
from pathlib import Path
from typing import List

import toml

from common import Config
from common.handle import Request, Response, Status
from common.task import TaskFlag
from watchmen.engine import send
from watchmen.utils import output
from watchmen.utils.file import recursive_search_files
from watchmen.utils.print_result import print_result as pr
from watchmen.utils.types import String


async def list_tasks(args: Namespace, config: Config) -> None:
    reqs: List[Request] = []

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
                        reqs.append(
                            Request(command="List", data=TaskFlag.from_dict(t)))
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
                    reqs.append(
                        Request(command="List", data=TaskFlag.from_dict(t)))
                pass
            elif ext == ".ini":
                pass
            elif ext == ".json":
                pass
            else:
                raise Exception(
                    f'File [{path}] is not a TOML or INI or JSON file'
                )
    elif args.task_id is not None:
        if args.task_name is not None:
            raise Exception("Cannot use '--id' and '--name' at the same time")

        reqs.append(Request(command="List", data=TaskFlag(
            id=args.task_id,
            name=None,
            group=None,
            mat=args.task_mat,
        )))
    elif args.task_name is not None:
        reqs.append(Request(command="List", data=TaskFlag(
            id=0,
            name=args.task_name,
            group=None,
            mat=args.task_mat,
        )))
    elif args.task_group is not None:
        reqs.append(Request(command="List", data=TaskFlag(
            id=0,
            name=None,
            group=args.task_group,
            mat=args.task_mat,
        )))
    else:
        reqs.append(Request(command="List", data=None))

    if args.task_less:
        print_result_less(await send(config, reqs))
    elif args.task_more:
        print_result_more(await send(config, reqs))
    else:
        print_result(await send(config, reqs))


def print_result(res: List[Response]) -> None:
    status: List[Status] = []
    for r in res:
        if r.code != 10000:
            pr([r])
            return
        if r.data is not None and 'Status' in r.data:
            for i in r.data['Status']:
                status.append(Status(**i))

    total = 0
    total_added = 0
    total_running = 0
    total_stopped = 0
    total_waiting = 0
    total_interval = 0
    total_paused = 0

    column_id: List[str] = ["ID"]
    column_name: List[str] = ["Name"]
    column_status: List[str] = [String.white("Status")]
    column_command: List[str] = ["Command"]
    column_pid: List[str] = ["Pid"]
    column_code: List[str] = ["ExitCode"]
    column_type: List[str] = ["Type"]

    for s in status:
        total += 1
        column_id.append(s.id)
        column_name.append(s.name)
        if s.status == "added":
            total_added += 1
            column_status.append(String.magenta("added"))
        elif s.status == "running":
            total_running += 1
            column_status.append(String.green("running"))
        elif s.status == "stopped":
            total_stopped += 1
            column_status.append(String.red("stopped"))
        elif s.status == "auto restart":
            column_status.append(String.rgb("auto restart", 128, 128, 128))
        elif s.status == "waiting":
            total_waiting += 1
            column_status.append(String.blue("waiting"))
        elif s.status == "interval":
            total_interval += 1
            column_status.append(String.cyan("interval"))
        elif s.status == "paused":
            total_paused += 1
            column_status.append(String.yellow("paused"))
        elif s.status == "executing":
            column_status.append(String.green("executing"))
        else:
            column_status.append(s.status)
        cmd = s.command.split('/')
        column_command.append(cmd[-1] if len(cmd) > 0 else s.command)
        column_pid.append(s.pid or "")
        column_code.append(s.pid if s.pid is not None else "")
        column_type.append(list(s.task_type.keys())[0])

    pattern = re.compile(r'\033\[[0-9;]*m')
    max_id = max([len(pattern.sub('', str(i))) for i in column_id])
    max_name = max([len(pattern.sub('', i)) for i in column_name])
    max_status = max([len(i) for i in column_status])
    max_command = max([len(pattern.sub('', i)) for i in column_command])
    max_pid = max([len(pattern.sub('', str(i))) for i in column_pid])
    max_code = max([len(pattern.sub('', str(i))) for i in column_code])
    max_type = max([len(pattern.sub('', i)) for i in column_type])

    max_status_onlytext = max([len(pattern.sub('', i)) for i in column_status])

    max_sum = max_id + max_name + max_status_onlytext + \
        max_command + max_pid + max_code + max_type + 3 * (7 - 1) + 4

    for i in range(len(column_id)):
        output("{:-<{width}}".format("", width=max_sum))
        row = "| {: <{max_id}} | {: <{max_name}} | {: <{max_status}} | {: <{max_command}} | {: <{max_pid}} | {: <{max_code}} | {: <{max_type}} |"
        output(
            row.format(column_id[i], column_name[i], column_status[i], column_command[i], column_pid[i], column_code[i], column_type[i],
                       max_id=max_id, max_name=max_name, max_status=max_status, max_command=max_command, max_pid=max_pid, max_code=max_code, max_type=max_type)
        )
    output("{:-<{width}}".format("", width=max_sum))

    total = String.purple(total)
    total_running = String.green(total_running)
    total_stopped = String.red(total_stopped)
    total_added = String.magenta(total_added)
    total_waiting = String.blue(total_waiting)
    total_interval = String.cyan(total_interval)
    total_paused = String.yellow(total_paused)
    output(f'{total} Total: {total_running} running, {total_stopped} stopped, {total_added} added, {total_waiting} waiting, {total_interval} interval, {total_paused} paused')


def print_result_more(res: List[Response]) -> None:
    status: List[Status] = []
    for r in res:
        if r.code != 10000:
            pr([r])
            return
        if r.data is not None and 'Status' in r.data:
            for i in r.data['Status']:
                status.append(Status(**i))

    total = 0
    total_added = 0
    total_running = 0
    total_stopped = 0
    total_waiting = 0
    total_interval = 0
    total_paused = 0

    column_id: List[str] = ["ID"]
    column_group: List[str] = ["Group"]
    column_name: List[str] = ["Name"]
    column_status: List[str] = [String.white("Status")]
    column_command: List[str] = ["Command"]
    column_args: List[str] = ["Args"]
    column_pid: List[str] = ["Pid"]
    column_code: List[str] = ["ExitCode"]
    column_type: List[str] = ["Type"]

    for s in status:
        total += 1
        column_id.append(s.id)
        column_group.append(s.group or "")
        column_name.append(s.name)
        if s.status == "added":
            total_added += 1
            column_status.append(String.magenta("added"))
        elif s.status == "running":
            total_running += 1
            column_status.append(String.green("running"))
        elif s.status == "stopped":
            total_stopped += 1
            column_status.append(String.red("stopped"))
        elif s.status == "auto restart":
            column_status.append(String.rgb("auto restart", 128, 128, 128))
        elif s.status == "waiting":
            total_waiting += 1
            column_status.append(String.blue("waiting"))
        elif s.status == "interval":
            total_interval += 1
            column_status.append(String.cyan("interval"))
        elif s.status == "paused":
            total_paused += 1
            column_status.append(String.yellow("paused"))
        elif s.status == "executing":
            column_status.append(String.green("executing"))
        else:
            column_status.append(s.status)
        cmd = s.command.split('/')
        column_command.append(cmd[-1] if len(cmd) > 0 else s.command)
        column_args.append(" ".join(s.args))
        column_pid.append(s.pid or "")
        column_code.append(s.pid if s.pid is not None else "")
        column_type.append(list(s.task_type.keys())[0])

    pattern = re.compile(r'\033\[[0-9;]*m')
    max_id = max([len(pattern.sub('', str(i))) for i in column_id])
    max_group = max([len(pattern.sub('', i)) for i in column_group])
    max_name = max([len(pattern.sub('', i)) for i in column_name])
    max_status = max([len(i) for i in column_status])
    max_command = max([len(pattern.sub('', i)) for i in column_command])
    max_args = max([len(pattern.sub('', str(i))) for i in column_args])
    max_pid = max([len(pattern.sub('', str(i))) for i in column_pid])
    max_code = max([len(pattern.sub('', str(i))) for i in column_code])
    max_type = max([len(pattern.sub('', i)) for i in column_type])

    max_status_onlytext = max([len(pattern.sub('', i)) for i in column_status])

    max_sum = max_id + max_group + max_name + max_status_onlytext + \
        max_command + max_args + max_pid + \
        max_code + max_type + 3 * (9 - 1) + 4

    for i in range(len(column_id)):
        output("{:-<{width}}".format("", width=max_sum))
        row = "| {: <{max_id}} | {: <{max_group}} | {: <{max_name}} | {: <{max_status}} | {: <{max_command}} | {: <{max_args}} | {: <{max_pid}} | {: <{max_code}} | {: <{max_type}} |"
        output(
            row.format(column_id[i], column_group[i], column_name[i], column_status[i], column_command[i], column_args[i], column_pid[i], column_code[i], column_type[i],
                       max_id=max_id, max_group=max_group, max_name=max_name, max_status=max_status, max_command=max_command, max_args=max_args, max_pid=max_pid, max_code=max_code, max_type=max_type)
        )
    output("{:-<{width}}".format("", width=max_sum))

    total = String.purple(total)
    total_running = String.green(total_running)
    total_stopped = String.red(total_stopped)
    total_added = String.magenta(total_added)
    total_waiting = String.blue(total_waiting)
    total_interval = String.cyan(total_interval)
    total_paused = String.yellow(total_paused)
    output(f'{total} Total: {total_running} running, {total_stopped} stopped, {total_added} added, {total_waiting} waiting, {total_interval} interval, {total_paused} paused')


def print_result_less(res: List[Response]) -> None:
    status: List[Status] = []
    for r in res:
        if r.code != 10000:
            pr([r])
            return
        if r.data is not None and 'Status' in r.data:
            for i in r.data['Status']:
                status.append(Status(**i))

    total = 0
    total_added = 0
    total_running = 0
    total_stopped = 0
    total_waiting = 0
    total_interval = 0
    total_paused = 0

    column_id: List[str] = ["ID"]
    column_name: List[str] = ["Name"]
    column_status: List[str] = [String.white("Status")]

    for s in status:
        total += 1
        column_id.append(s.id)
        column_name.append(s.name)
        if s.status == "added":
            total_added += 1
            column_status.append(String.magenta("added"))
        elif s.status == "running":
            total_running += 1
            column_status.append(String.green("running"))
        elif s.status == "stopped":
            total_stopped += 1
            column_status.append(String.red("stopped"))
        elif s.status == "auto restart":
            column_status.append(String.rgb("auto restart", 128, 128, 128))
        elif s.status == "waiting":
            total_waiting += 1
            column_status.append(String.blue("waiting"))
        elif s.status == "interval":
            total_interval += 1
            column_status.append(String.cyan("interval"))
        elif s.status == "paused":
            total_paused += 1
            column_status.append(String.yellow("paused"))
        elif s.status == "executing":
            column_status.append(String.green("executing"))
        else:
            column_status.append(s.status)

    pattern = re.compile(r'\033\[[0-9;]*m')
    max_id = max([len(pattern.sub('', str(i))) for i in column_id])
    max_name = max([len(pattern.sub('', i)) for i in column_name])
    max_status = max([len(i) for i in column_status])

    max_status_onlytext = max([len(pattern.sub('', i)) for i in column_status])

    max_sum = max_id + max_name + max_status_onlytext + 3 * (4 - 1) + 1

    for i in range(len(column_id)):
        output("{:-<{width}}".format("", width=max_sum))
        row = "| {: <{max_id}} | {: <{max_name}} | {: <{max_status}} |"
        output(
            row.format(column_id[i], column_name[i], column_status[i],
                       max_id=max_id, max_name=max_name, max_status=max_status)
        )
    output("{:-<{width}}".format("", width=max_sum))

    total = String.purple(total)
    total_running = String.green(total_running)
    total_stopped = String.red(total_stopped)
    total_added = String.magenta(total_added)
    total_waiting = String.blue(total_waiting)
    total_interval = String.cyan(total_interval)
    total_paused = String.yellow(total_paused)
    output(f'{total} Total: {total_running} running, {total_stopped} stopped, {total_added} added, {total_waiting} waiting, {total_interval} interval, {total_paused} paused')
