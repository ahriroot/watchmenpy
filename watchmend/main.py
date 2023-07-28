import asyncio

from .engine import start
from common import Config, DaemonArgs, ExitCode, VERSION, Request, Task


async def _main(config: Config, load: bool) -> int:
    # TODO: start monitor

    await start(config=config, load=load)


def main() -> int:
    clargs = DaemonArgs.parse()
    if clargs.version:
        print(f"\033[32mWatchmen python {VERSION}\033[0m")
        return ExitCode.SUCCESS

    load = clargs.load

    config: Config = Config.init(path=clargs.config)

    try:
        asyncio.run(_main(config=config, load=load))
    except KeyboardInterrupt:
        return ExitCode.SUCCESS
