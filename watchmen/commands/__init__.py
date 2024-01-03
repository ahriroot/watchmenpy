from argparse import Namespace

from common import Config
from watchmen.commands.run import run
from watchmen.commands.add import add
from watchmen.commands.reload import reload_task
from watchmen.commands.start import start
from watchmen.commands.restart import restart
from watchmen.commands.stop import stop
from watchmen.commands.remove import remove
from watchmen.commands.pause import pause
from watchmen.commands.resume import resume
from watchmen.commands.list import list_tasks


async def handle_exec(commands: Namespace, config: Config) -> None:
    match commands.subcommand:
        case 'run':
            return await run(commands, config)
        case 'add':
            return await add(commands, config)
        case 'reload':
            return await reload_task(commands, config)
        case 'start':
            return await start(commands, config)
        case 'restart':
            return await restart(commands, config)
        case 'stop':
            return await stop(commands, config)
        case 'remove':
            return await remove(commands, config)
        case 'pause':
            return await pause(commands, config)
        case 'resume':
            return await resume(commands, config)
        case 'list':
            return await list_tasks(commands, config)
        case _:
            raise NotImplementedError(
                f"Command {commands.subcommand} not implemented"
            )
