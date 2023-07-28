import os
from pathlib import Path


def get_with_home(path: str) -> str:
    home_dir: str = os.path.expanduser("~")
    if path.startswith("$HOME"):
        return path.replace("$HOME", home_dir)
    elif path.startswith("~"):
        return path.replace("~", home_dir)
    else:
        return path


def get_with_home_path(path: str) -> Path:
    return Path(get_with_home(path=path))
