import logging
import logging.handlers
from pathlib import Path


class Logger:
    __instance = None

    def __new__(cls, path: Path) -> "Logger":
        if not Logger.__instance:
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)

            path = path.joinpath("watchmen.log")

            Logger.__instance = object.__new__(cls)
            Logger.__instance.logger = logging.getLogger('watchmen')
            Logger.__instance.logger.setLevel(logging.DEBUG)

            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)

            time_rotating_handler = logging.handlers.TimedRotatingFileHandler(
                filename=path, when='midnight', interval=1, backupCount=7, encoding='utf-8')
            time_rotating_handler.setLevel(logging.INFO)

            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s')

            console_handler.setFormatter(formatter)
            time_rotating_handler.setFormatter(formatter)

            Logger.__instance.logger.addHandler(console_handler)
            Logger.__instance.logger.addHandler(time_rotating_handler)
        return Logger.__instance

    def debug(self, *args, **kwargs):
        self.logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        self.logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        self.logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        self.logger.error(*args, **kwargs)

    def critical(self, *args, **kwargs):
        self.logger.critical(*args, **kwargs)

    def exception(self, *args, **kwargs):
        self.logger.exception(*args, **kwargs)


def get_logger(log_dir: str) -> Logger:
    return Logger(path=Path(log_dir))
