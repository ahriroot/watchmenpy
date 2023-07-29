import asyncio

from common import Config, get_logger
from watchmend.lib import load


async def start(config: Config, load_cache: bool) -> None:
    logger = get_logger(log_dir=config.watchmen.log_dir)
    if load_cache:
        try:
            await load(path=config.watchmen.cache)
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")

    task_sock = None
    if "sock" in config.watchmen.engines:
        from .sock import start as start_sock
        logger.info("Starting sock...")
        task_sock = await start_sock(config=config)

    tasks = []
    if task_sock is not None:
        tasks.append(task_sock)

    await asyncio.gather(*tasks)
