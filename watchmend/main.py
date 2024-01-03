import asyncio

from .engine import start
from .monitor import run_monitor
from common import Config, DaemonArgs, ExitCode, VERSION


async def _main(config: Config, load: bool) -> int:
    asyncio.create_task(run_monitor())
    await start(config=config, load_cache=load)


def main() -> int:
    clargs = DaemonArgs.parse()
    if clargs.version:
        print(f"\033[32mWatchmen python {VERSION}\033[0m")
        return ExitCode.SUCCESS

    load: bool = clargs.load

    config: Config = Config.init(path=clargs.config)

    try:
        asyncio.run(_main(config=config, load=load))
    except KeyboardInterrupt:
        return ExitCode.SUCCESS
