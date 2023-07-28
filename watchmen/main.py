from .args import generate
from .utils.types import String
from common import Config, TaskArgs, ExitCode, VERSION


def main() -> int:
    clargs = TaskArgs.parse()
    if clargs.version:
        print(String(f"Watchmen python {VERSION}").green())
        return ExitCode.SUCCESS

    if clargs.generate is not None:
        try:
            return generate(path=clargs.generate)
        except ValueError as e:
            print(String(e).red())
            return ExitCode.ERROR
        
    config: Config = Config.init(path=clargs.config)
    
    if clargs.subcommand is not None:
        if clargs.engine is not None:
            config.watchmen.engine = clargs.engine

    print(clargs)
