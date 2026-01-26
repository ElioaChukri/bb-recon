import logging
import sys
from typing import Literal

LogLevel = Literal[
    "CRITICAL",
    "ERROR",
    "WARNING",
    "INFO",
    "DEBUG",
]


class ColoredFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: "\033[36m",  # cyan
        logging.INFO: "\033[32m",  # green
        logging.WARNING: "\033[33m",  # yellow
        logging.ERROR: "\033[31m",  # red
        logging.CRITICAL: "\033[35m",  # magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, self.RESET)
        record.levelname = f"{color}{record.levelname:<8}{self.RESET}"
        record.name = f"\033[34m{record.name}{self.RESET}"  # blue
        return super().format(record)


def setup_logging(level: LogLevel) -> None:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(ColoredFormatter("%(asctime)s │ %(levelname)s │ %(name)s │ %(message)s"))
    logging.root.handlers = [handler]
    logging.root.setLevel(level)
