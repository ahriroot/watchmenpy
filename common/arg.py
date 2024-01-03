from argparse import _SubParsersAction, ArgumentParser, Namespace


DESCRIPTION = """Watchmen (Python) is a daemon process manager that for you manage and keep your application online 24/7"""
EPILOG = """See "watchmen COMMAND --help" for more information on a specific command."""


class TaskArgs:

    def __init__(self) -> None:
        self._parser: ArgumentParser = self._create_parser()

        self._subparser = self._create_subparser()

        self._create_task_command("run", "Add and run tasks")
        self._create_task_command("add", "Add tasks")
        self._create_task_command("reload", "Reload tasks")

        self._create_flag_command("start", "Start tasks")
        self._create_flag_command("restart", "Restart tasks")
        self._create_flag_command("stop", "Stop tasks")
        self._create_flag_command("remove", "Remove tasks")

        self._create_flag_command("pause", "Pause tasks")
        self._create_flag_command("resume", "Resume tasks")

        self._create_list_command("list", "Get tasks list")

    def _create_parser(self) -> ArgumentParser:
        parser = ArgumentParser(description=DESCRIPTION,
                                usage="watchmen [OPTIONS] [COMMAND]", epilog=EPILOG)
        parser.add_argument("-c", "--config", type=str, metavar="<CONFIG>",
                                  default=None, help="Config file path. Default: $HOME/.watchmen/config.toml")
        parser.add_argument("-g", "--generate", type=str, metavar="<GENERATE>",
                                  default=None, help="Generate config file")
        parser.add_argument("-e", "--engine", type=str, metavar="<ENGINE>",
                                  default=None, help="Engine for send message", choices=["sock", "socket", "http", "redis"])
        parser.add_argument("-v", "--version", action="store_true",
                                  default=False, help="Print version")
        return parser

    def _create_subparser(self):
        subparser: _SubParsersAction[ArgumentParser] = self._parser.add_subparsers(
            title="Sub Commands", dest="subcommand")
        return subparser

    def _create_task_command(self, name: str, help_text: str) -> None:
        parser: ArgumentParser = self._subparser.add_parser(name=name, help=help_text,
                                                            usage=f"watchmen {name} [OPTIONS]")
        parser.add_argument("-p", "--path", type=str, metavar="<PATH>",
                            default=None, help="Task config directory", dest=f"task_path")
        parser.add_argument("-r", "--regex", type=str, metavar="<REGEX>",
                            default=r"^.*\.(toml|ini|json)$", help="Task config filename regex pattern", dest=f"task_regex")
        parser.add_argument("-f", "--config", type=str, metavar="<CONFIG>",
                            default=None, help="Task config file", dest=f"task_config")
        parser.add_argument("-n", "--name", type=str, metavar="<NAME>",
                            default=None, help="Task name (unique)", dest=f"task_name")
        parser.add_argument("-c", "--command", type=str, metavar="<COMMAND>",
                            default=None, help="Task command", dest=f"task_command")
        parser.add_argument("-a", "--args", nargs="+", metavar="<ARGS>",
                            default=None, help="Task arguments", dest=f"task_args")
        parser.add_argument("-d", "--dir", type=str, metavar="<DIR>",
                            default=None, help="Task working directory", dest=f"task_dir")
        parser.add_argument("-e", "--env", nargs="+", metavar="<ENV>",
                            default=None, help="Task environment variables", dest=f"task_env")
        parser.add_argument("-i", "--stdin", action="store_true",
                            default=False, help="Task standard input", dest=f"task_stdin")
        parser.add_argument("-o", "--stdout", type=str, metavar="<STDOUT>",
                            default=None, help="Task standard output", dest=f"task_stdout")
        parser.add_argument("-w", "--stderr", type=str, metavar="<STDERR>",
                            default=None, help="Task standard error", dest=f"task_stderr")

    def _create_flag_command(self, name: str, help_text: str) -> None:
        parser: ArgumentParser = self._subparser.add_parser(name=name, help=help_text,
                                                            usage=f"watchmen {name} [OPTIONS]")
        parser.add_argument("-p", "--path", type=str, metavar="<PATH>",
                            default=None, help="Task config directory", dest=f"task_path")
        parser.add_argument("-r", "--regex", type=str, metavar="<REGEX>",
                            default=r"^.*\.(toml|ini|json)$", help="Task config filename regex pattern", dest=f"task_regex")
        parser.add_argument("-f", "--config", type=str, metavar="<CONFIG>",
                            default=None, help="Task config file", dest=f"task_config")
        parser.add_argument("-i", "--id", type=int, metavar="<ID>",
                            default=None, help="Task id (unique)", dest=f"task_id")
        parser.add_argument("-n", "--name", type=str, metavar="<NAME>",
                            default=None, help="Task name (unique)", dest=f"task_name")
        parser.add_argument("-m", "--mat", action="store_true",
                            default=False, help="Is match regex pattern by namae", dest=f"task_mat")

    def _create_list_command(self, name: str, help_text: str) -> None:
        parser: ArgumentParser = self._subparser.add_parser(name=name, help=help_text,
                                                            usage=f"watchmen {name} [OPTIONS]")
        parser.add_argument("-p", "--path", type=str, metavar="<PATH>",
                            default=None, help="Task config directory", dest=f"task_path")
        parser.add_argument("-r", "--regex", type=str, metavar="<REGEX>",
                            default=r"^.*\.(toml|ini|json)$", help="Task config filename regex pattern", dest=f"task_regex")
        parser.add_argument("-f", "--config", type=str, metavar="<CONFIG>",
                            default=None, help="Task config file", dest=f"task_config")
        parser.add_argument("-i", "--id", type=int, metavar="<ID>",
                            default=None, help="Task id (unique)", dest=f"task_id")
        parser.add_argument("-n", "--name", type=str, metavar="<NAME>",
                            default=None, help="Task name (unique)", dest=f"task_name")
        parser.add_argument("-g", "--group", type=str, metavar="<GROUP>",
                            default=None, help="Task group", dest=f"task_group")
        parser.add_argument("-R", "--mat", action="store_true",
                            default=False, help="Is match regex pattern by name", dest=f"task_mat")
        parser.add_argument("-m", "--more", action="store_true",
                            default=False, help="Show more info", dest=f"task_more")
        parser.add_argument("-l", "--less", action="store_true",
                            default=False, help="Show less info", dest=f"task_less")

    @classmethod
    def parse(cls) -> Namespace:
        this = cls()
        return this._parser.parse_args()


class DaemonArgs:

    def __init__(self) -> None:
        self._parser: ArgumentParser = self._create_parser()

    def _create_parser(self) -> ArgumentParser:
        parser = ArgumentParser(description=DESCRIPTION,
                                usage="watchmen [OPTIONS]")
        parser.add_argument("-c", "--config", type=str, metavar="<CONFIG>",
                                  default=None, help="Config file path. Default: $HOME/.watchmen/config.toml")
        parser.add_argument("-l", "--load", action="store_true",
                                  default=True, help="Load cached tasks")
        parser.add_argument("-v", "--version", action="store_true",
                                  default=False, help="Print version")
        return parser

    @classmethod
    def parse(cls) -> Namespace:
        this = cls()
        return this._parser.parse_args()
