"""One logging setup for the whole project.

Stage timings and counts recorded here become the raw material for the Week 2
ablation table, so keep the emitted fields stable.
"""

import logging
import sys

_CONFIGURED = False


def configure_logging(level: str = "INFO") -> None:
    """Install a single stderr handler. Safe to call more than once."""

    global _CONFIGURED
    resolved = getattr(logging, level.upper(), logging.INFO)
    root = logging.getLogger("cs30")
    if not _CONFIGURED:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)-8s %(name)s | %(message)s")
        )
        root.addHandler(handler)
        root.propagate = False
        _CONFIGURED = True
    root.setLevel(resolved)


def get_logger(name: str) -> logging.Logger:
    """Return a logger under the shared ``cs30`` namespace."""

    return logging.getLogger(f"cs30.{name}")
