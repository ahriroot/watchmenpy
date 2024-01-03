class String(str):
    def rgb(self, r, g, b) -> str:
        return f"\033[38;2;{r};{g};{b}m{self}\033[0m"

    def red(self) -> str:
        return f"\033[31m{self}\033[0m"

    def green(self) -> str:
        return f"\033[32m{self}\033[0m"

    def yellow(self) -> str:
        return f"\033[33m{self}\033[0m"

    def blue(self) -> str:
        return f"\033[34m{self}\033[0m"

    def purple(self) -> str:
        return f"\033[35m{self}\033[0m"

    def cyan(self) -> str:
        return f"\033[36m{self}\033[0m"

    def white(self) -> str:
        return f"\033[37m{self}\033[0m"

    def black(self) -> str:
        return f"\033[38m{self}\033[0m"

    def magenta(self) -> str:
        return f"\033[95m{self}\033[0m"

    def bold(self) -> str:
        return f"\033[1m{self}\033[0m"

    def italic(self) -> str:
        return f"\033[3m{self}\033[0m"

    def underline(self) -> str:
        return f"\033[4m{self}\033[0m"

    def blink(self) -> str:
        return f"\033[5m{self}\033[0m"

    def reverse(self) -> str:
        return f"\033[7m{self}\033[0m"

    def invisible(self) -> str:
        return f"\033[8m{self}\033[0m"

    def strikethrough(self) -> str:
        return f"\033[9m{self}\033[0m"
