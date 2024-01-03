import asyncio
from argparse import Namespace

from common import Config, TaskArgs, ExitCode, VERSION
from watchmen.args import generate
from watchmen.commands import handle_exec
from watchmen.utils import output
from watchmen.utils.types import String


async def _main() -> int:
    clargs: Namespace = TaskArgs.parse()
    if clargs.version:
        output(String(f"Watchmen python {VERSION}").green())
        return ExitCode.SUCCESS

    if clargs.generate is not None:
        try:
            return generate(path=clargs.generate)
        except ValueError as e:
            output(String(e).red())
            return ExitCode.ERROR

    config: Config = Config.init(path=clargs.config)

    if clargs.subcommand is not None:
        if clargs.engine is not None:
            config.watchmen.engine = clargs.engine

        await handle_exec(clargs, config)

        # try:
        #     await handle_exec(clargs, config)
        # except Exception as e:
        #     output(String(e).red())
        #     return ExitCode.ERROR


def main() -> int:
    asyncio.run(_main())
