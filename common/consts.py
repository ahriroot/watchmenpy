from dataclasses import dataclass


@dataclass
class ExitCode:
    SUCCESS = 0
    ERROR = 1
    FAILURE = 2
