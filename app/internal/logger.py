"""
Simple always-colored console logging.

Usage:
    # at the very top of app/main.py (before other imports that log):
    import app.internal.logger  # configures logging on import
    # then use standard logging everywhere:
    import logging
    log = logging.getLogger(__name__)
    log.info("hello")


    inspired by https://pypi.org/project/coloredlogs/
    recommended if you don't mind the dependency, want more edge cases, and likely better performance at high QPS (scale)
"""

import logging
import sys
from typing import Optional


class ColorFormatter(logging.Formatter):
    RESET = "\033[0m"
    BOLD = "\033[1m"

    COLORS = {
        logging.DEBUG: "\033[36m",  # cyan
        logging.INFO: "\033[32m",  # green
        logging.WARNING: "\033[33m",  # yellow
        logging.ERROR: "\033[31m",  # red
        logging.CRITICAL: "\033[41m",  # red background
    }

    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None):
        if fmt is None:
            fmt = (
                "%(asctime)s | %(levelname)s | %(name)s: Line %(lineno)d | %(message)s"
            )
        super().__init__(fmt=fmt, datefmt=datefmt)
        self._always_color = True

    def format(self, record: logging.LogRecord) -> str:
        orig_levelname = record.levelname
        orig_name = record.name
        orig_msg = record.msg
        orig_args = record.args

        try:
            if self._always_color:
                color = self.COLORS.get(record.levelno, "")
                if color:
                    record.levelname = f"{self.BOLD}{color}{orig_levelname}{self.RESET}"
                    record.name = f"{color}{orig_name}{self.RESET}"
                    if not record.args:
                        record.msg = f"{color}{orig_msg}{self.RESET}"

            formatted = super().format(record)

            if self._always_color and (
                "Traceback (most recent call last):" in formatted
            ):
                marker = "Traceback (most recent call last):"
                idx = formatted.find(marker)
                if idx != -1:
                    before = formatted[:idx]
                    tb = formatted[idx:]
                    tb_color = self.COLORS.get(logging.ERROR, "\033[31m")
                    formatted = before + f"{tb_color}{tb}{self.RESET}"

            return formatted
        finally:
            record.levelname = orig_levelname
            record.name = orig_name
            record.msg = orig_msg
            record.args = orig_args

    def formatException(self, ei) -> str:
        exc_text = super().formatException(ei)
        if not self._always_color:
            return exc_text
        color = self.COLORS.get(logging.ERROR, "")
        return f"{color}{exc_text}{self.RESET}" if color else exc_text


def _configure_root_logger():
    # Avoid double-configuration if module is imported multiple times
    # Detect an existing colored handler marker on any root handler
    for h in logging.getLogger().handlers:
        if getattr(h, "_is_colored_handler", False):
            return h

    # Create handler writing to stdout (matches your original)
    stream = sys.stdout
    handler = logging.StreamHandler(stream=stream)
    handler._is_colored_handler = True  # marker to avoid duplicate setup

    fmt = "%(asctime)s | %(levelname)s | %(name)s: Line %(lineno)d | %(message)s"
    formatter = ColorFormatter(fmt=fmt, datefmt="%H:%M:%S")
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(logging.DEBUG)
    root.addHandler(handler)

    # ensure basicConfig elsewhere doesn't add another handler unexpectedly
    logging.basicConfig(level=logging.DEBUG, handlers=[handler])

    # Attach same handler to common server loggers so uvicorn/gunicorn lines are colored
    for name in (
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
    ):
        lg = logging.getLogger(name)
        lg.handlers.clear()
        lg.propagate = False
        lg.addHandler(handler)
        if lg.level == logging.NOTSET:
            # keep uvicorn/gunicorn at INFO by default to avoid noisy DEBUG logs
            lg.setLevel(logging.INFO)

    return handler


# run configuration when module is imported
_configured_handler = _configure_root_logger()


# ----------------------------
# Convenience accessor (optional)
# ----------------------------
def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a logger — identical to logging.getLogger but provided for convenience."""
    return logging.getLogger(name) if name else logging.getLogger()


# expose module-level names
__all__ = ("get_logger",)
