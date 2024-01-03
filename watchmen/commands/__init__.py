from argparse import Namespace

from common import Config
from watchmen.commands.run import run
from watchmen.commands.add import add
from watchmen.commands.remove import remove
from watchmen.commands.list import list_tasks


async def handle_exec(commands: Namespace, config: Config) -> None:
    match commands.subcommand:
        case 'run':
            return await run(commands, config)
        case 'add':
            return await add(commands, config)
        case 'reload':
            return
        case 'start':
            return
        case 'restart':
            return
        case 'stop':
            return
        case 'remove':
            return await remove(commands, config)
        case 'pause':
            return
        case 'resume':
            return
        case 'list':
            return await list_tasks(commands, config)
    return
