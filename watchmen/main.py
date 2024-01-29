import asyncio
from argparse import Namespace

from common import Config, TaskArgs, ExitCode, VERSION
from watchmen.args import generate
from watchmen.commands import handle_exec
from watchmen.utils import output
from watchmen.utils.types import String


async def _main() -> int:
    """
    主函数，处理命令行参数并执行相应的命令
    
    Returns:
        int: 返回一个退出码, 成功为0, 失败其他
    """
    # 解析命令行参数
    clargs: Namespace = TaskArgs.parse()
    # 输出版本号
    if clargs.version:
        output(String(f"Watchmen python {VERSION}").green())
        return ExitCode.SUCCESS

    # 生成配置文件
    if clargs.generate is not None:
        try:
            return generate(path=clargs.generate)
        except ValueError as e:
            output(String(e).red())
            return ExitCode.ERROR

    # 初始化配置
    config: Config = Config.init(path=clargs.config)

    # 子命令
    if clargs.subcommand is not None:
        if clargs.engine is not None:
            config.watchmen.engine = clargs.engine

        try:
            await handle_exec(clargs, config)
            return ExitCode.SUCCESS
        except Exception as e:
            output(String(e).red())
            return ExitCode.ERROR


def main():
    asyncio.run(_main())
