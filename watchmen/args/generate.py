import os
from pathlib import Path

from common import ExitCode
from watchmen.utils import output


CONFIG = """[watchmen]
# The engine to use for the watchmen server
# Valid values are "sock", "socket", "http", "redis"
# sock: Unix socket
# socket: TCP socket
# http: HTTP Api (Include Web panel)
# redis: Redis pub/sub
engines = ["sock"]

# The default engine to use for connecting to the watchmen server
engine = "sock"

# The log directory of the watchmen server
log_dir = "$HOME/.watchmen/logs"

# The log level of the watchmen server
# Valid values are "debug", "info", "warn", "error". Default is "info"
log_level = "info"

# The standard output of the watchmen server
# Default is None
stdout = "$HOME/.watchmen/watchmen.stdout.log"

# The standard error of the watchmen server
# Default is None
stderr = "$HOME/.watchmen/watchmen.stderr.log"

# The pid file of the watchmen server
# Default is `$HOME/.watchmen/watchmen.pid`
pid = "$HOME/.watchmen/watchmen.pid"

# The task config file name matching pattern
# Default is `^.*\\.(toml|ini|json)$`
mat = "^.*\\.(toml|ini|json)$"

# Tasks cache file, json format
cache = "$HOME/.watchmen/cache.json"

# Monitor interval for rerun tasks, u64: second
interval = 5


[sock]
# The unix socket path of the watchmen server
path = "/tmp/watchmen.sock"


[socket]
host = "127.0.0.1"
port = 1949


[http]
host = "127.0.0.1"
port = 1997


[redis]
host = "localhost"
port = 6379
username = ""
password = ""
queue_index = 0
queue_name = "watchmen"
subscribe_channels = ["watchmen"]
subscribe_name = "watchmen"
"""


def generate(path: str) -> int:
    config_path = None
    if path == "":
        home = os.path.expanduser("~")
        config_path = Path(os.path.join(home, ".watchmen", "config.toml"))
    else:
        config_path = Path(os.getcwd()).joinpath(path)
        if config_path.is_dir():
            config_path = config_path.joinpath("config.toml")
        else:
            ext = config_path.suffix
            if ext != ".toml":
                raise ValueError("Config file must be toml")

    parent = config_path.parent
    if not parent.exists():
        parent.mkdir(parents=True)

    output(f"Generate config file to {config_path}")

    with open(config_path, "w") as f:
        f.write(CONFIG)

    return ExitCode.SUCCESS
