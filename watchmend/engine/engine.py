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

    tasks = []
        
    if "sock" in config.watchmen.engines:
        from .sock import start as start_sock
        logger.info("Starting sock...")
        tasks.append(await start_sock(config=config))

    if "socket" in config.watchmen.engines:
        from .socket import start as start_socket
        logger.info("Starting socket...")
        tasks.append(await start_socket(config=config))

    if "http" in config.watchmen.engines:
        from .http import start as start_http
        logger.info("Starting http...")
        tasks.append(await start_http(config=config))

    if len(tasks) == 0:
        raise Exception("No engine started")

    await asyncio.gather(*tasks)
