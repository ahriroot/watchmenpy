# Watchmen (0.0.2)

`
Watchmen is a daemon process manager that for you manage and keep your application online 24/7
`

[中文简体](README.md) | [English](README_EN.md)

## Install

### Build from source

```shell
# Clone the repository
git clone https://git.ahriknow.com/ahriknow/watchmenpy.git

# Go into the repository
cd watchmenpy

# Install watchmen daemon and cli tool
pip install -e .
```

### Install from pypi

```shell
# Install watchmen daemon
pip install watchmen
```

## Getting Started

### Generate config file

> "" Default is ${HOME}/.watchmen/config.toml

`watchmen -g ""`

```toml
[watchmen]
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
```

### Start watchmen daemon

`watchmend`

### Task Config file

```toml
[[task]]
id = 1
name = "Async Task 1"
command = "command"
args = ["arg1", "arg2"]
dir = "/path/to/directory"
env = { key1 = "value1", key2 = "value2" }
stdin = true
stdout = "output.txt"
stderr = "error.txt"
task_type = { Async = { max_restart = 2, has_restart = 0, started_at = 0, stopped_at = 0 } }
```

```ini
[Async Task]
id = 2
name = Async Task 2
command = command
args = arg1 arg2
dir = /path/to/directory
env = key1=value1 key2=value2
stdin = true
stdout = "output.txt"
stderr = "error.txt"
task_type = async
max_restart = 2
```

```json
[
    {
        "id": 3,
        "name": "Async Task 3",
        "command": "command",
        "args": ["arg1", "arg2"],
        "dir": "/path/to/directory",
        "env": {},
        "stdin": true,
        "stdout": "output.txt",
        "stderr": "error.txt",
        "created_at": 0,
        "task_type": { "Async": { "max_restart": 2, "has_restart": 0, "started_at": 0, "stopped_at": 0 } }
    }
]
```

## Command

### watchmen -h

```shell
usage: watchmen [OPTIONS] [COMMAND]

Watchmen (Python) is a daemon process manager that for you manage and keep your application online 24/7

options:
  -h, --help            show this help message and exit
  -c <CONFIG>, --config <CONFIG>
                        Config file path. Default: $HOME/.watchmen/config.toml
  -g <GENERATE>, --generate <GENERATE>
                        Generate config file
  -e <ENGINE>, --engine <ENGINE>
                        Engine for send message
  -v, --version         Print version

Sub Commands:
  {run,add,reload,start,restart,stop,remove,pause,resume,list}
    run                 Add and run tasks
    add                 Add tasks
    reload              Reload tasks
    start               Start tasks
    restart             Restart tasks
    stop                Stop tasks
    remove              Remove tasks
    pause               Pause tasks
    resume              Resume tasks
    list                Get tasks list

See "watchmen COMMAND --help" for more information on a specific command.
```

### watchmen run -h

```shell
usage: watchmen run [OPTIONS]

options:
  -h, --help            show this help message and exit
  -p <PATH>, --path <PATH>
                        Task config directory
  -r <REGEX>, --regex <REGEX>
                        Task config filename regex pattern
  -f <CONFIG>, --config <CONFIG>
                        Task config file
  -n <NAME>, --name <NAME>
                        Task name (unique)
  -c <COMMAND>, --command <COMMAND>
                        Task command
  -a <ARGS> [<ARGS> ...], --args <ARGS> [<ARGS> ...]
                        Task arguments
  -d <DIR>, --dir <DIR>
                        Task working directory
  -e <ENV> [<ENV> ...], --env <ENV> [<ENV> ...]
                        Task environment variables
  -i, --stdin           Task standard input
  -o <STDOUT>, --stdout <STDOUT>
                        Task standard output
  -w <STDERR>, --stderr <STDERR>
                        Task standard error
```

### watchmen add -h

```shell
usage: watchmen add [OPTIONS]

options:
  -h, --help            show this help message and exit
  -p <PATH>, --path <PATH>
                        Task config directory
  -r <REGEX>, --regex <REGEX>
                        Task config filename regex pattern
  -f <CONFIG>, --config <CONFIG>
                        Task config file
  -n <NAME>, --name <NAME>
                        Task name (unique)
  -c <COMMAND>, --command <COMMAND>
                        Task command
  -a <ARGS> [<ARGS> ...], --args <ARGS> [<ARGS> ...]
                        Task arguments
  -d <DIR>, --dir <DIR>
                        Task working directory
  -e <ENV> [<ENV> ...], --env <ENV> [<ENV> ...]
                        Task environment variables
  -i, --stdin           Task standard input
  -o <STDOUT>, --stdout <STDOUT>
                        Task standard output
  -w <STDERR>, --stderr <STDERR>
                        Task standard error
```

### watchmen reload -h

```shell
usage: watchmen reload [OPTIONS]

options:
  -h, --help            show this help message and exit
  -p <PATH>, --path <PATH>
                        Task config directory
  -r <REGEX>, --regex <REGEX>
                        Task config filename regex pattern
  -f <CONFIG>, --config <CONFIG>
                        Task config file
  -n <NAME>, --name <NAME>
                        Task name (unique)
  -c <COMMAND>, --command <COMMAND>
                        Task command
  -a <ARGS> [<ARGS> ...], --args <ARGS> [<ARGS> ...]
                        Task arguments
  -d <DIR>, --dir <DIR>
                        Task working directory
  -e <ENV> [<ENV> ...], --env <ENV> [<ENV> ...]
                        Task environment variables
  -i, --stdin           Task standard input
  -o <STDOUT>, --stdout <STDOUT>
                        Task standard output
  -w <STDERR>, --stderr <STDERR>
                        Task standard error
```

### watchmen start -h

```shell
usage: watchmen start [OPTIONS]

options:
  -h, --help            show this help message and exit
  -p <PATH>, --path <PATH>
                        Task config directory
  -r <REGEX>, --regex <REGEX>
                        Task config filename regex pattern
  -f <CONFIG>, --config <CONFIG>
                        Task config file
  -i <ID>, --id <ID>    Task id (unique)
  -n <NAME>, --name <NAME>
                        Task name (unique)
  -m, --mat             Is match regex pattern by namae
```

### watchmen restart -h

```shell
usage: watchmen restart [OPTIONS]

options:
  -h, --help            show this help message and exit
  -p <PATH>, --path <PATH>
                        Task config directory
  -r <REGEX>, --regex <REGEX>
                        Task config filename regex pattern
  -f <CONFIG>, --config <CONFIG>
                        Task config file
  -i <ID>, --id <ID>    Task id (unique)
  -n <NAME>, --name <NAME>
                        Task name (unique)
  -m, --mat             Is match regex pattern by namae
```

### watchmen stop -h

```shell
usage: watchmen stop [OPTIONS]

options:
  -h, --help            show this help message and exit
  -p <PATH>, --path <PATH>
                        Task config directory
  -r <REGEX>, --regex <REGEX>
                        Task config filename regex pattern
  -f <CONFIG>, --config <CONFIG>
                        Task config file
  -i <ID>, --id <ID>    Task id (unique)
  -n <NAME>, --name <NAME>
                        Task name (unique)
  -m, --mat             Is match regex pattern by namae
```

### watchmen remove -h

```shell
usage: watchmen remove [OPTIONS]

options:
  -h, --help            show this help message and exit
  -p <PATH>, --path <PATH>
                        Task config directory
  -r <REGEX>, --regex <REGEX>
                        Task config filename regex pattern
  -f <CONFIG>, --config <CONFIG>
                        Task config file
  -i <ID>, --id <ID>    Task id (unique)
  -n <NAME>, --name <NAME>
                        Task name (unique)
  -m, --mat             Is match regex pattern by namae
```

### watchmen pause -h

```shell
usage: watchmen pause [OPTIONS]

options:
  -h, --help            show this help message and exit
  -p <PATH>, --path <PATH>
                        Task config directory
  -r <REGEX>, --regex <REGEX>
                        Task config filename regex pattern
  -f <CONFIG>, --config <CONFIG>
                        Task config file
  -i <ID>, --id <ID>    Task id (unique)
  -n <NAME>, --name <NAME>
                        Task name (unique)
  -m, --mat             Is match regex pattern by namae
```

### watchmen resume -h

```shell
usage: watchmen resume [OPTIONS]

options:
  -h, --help            show this help message and exit
  -p <PATH>, --path <PATH>
                        Task config directory
  -r <REGEX>, --regex <REGEX>
                        Task config filename regex pattern
  -f <CONFIG>, --config <CONFIG>
                        Task config file
  -i <ID>, --id <ID>    Task id (unique)
  -n <NAME>, --name <NAME>
                        Task name (unique)
  -m, --mat             Is match regex pattern by namae
```

### watchmen list -h

```shell
usage: watchmen list [OPTIONS]

options:
  -h, --help            show this help message and exit
  -p <PATH>, --path <PATH>
                        Task config directory
  -r <REGEX>, --regex <REGEX>
                        Task config filename regex pattern
  -f <CONFIG>, --config <CONFIG>
                        Task config file
  -i <ID>, --id <ID>    Task id (unique)
  -n <NAME>, --name <NAME>
                        Task name (unique)
  -R, --mat             Is match regex pattern by name
  -m, --more            Show more info
  -l, --less            Show less info
```

## License Apache Licence 2.0
[License](./LICENSE)

## Copyright ahriknow 2022
