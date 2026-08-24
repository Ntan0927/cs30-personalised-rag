"""Small, non-sensitive integration fixtures shipped with the package.

Fixtures live inside the package so the demo entry point works from any
installation, not only from an editable checkout of the repository.
"""

import json
from importlib.resources import files
from typing import Any

__all__ = ["load_fixture"]


def load_fixture(name: str) -> Any:
    """Load one packaged JSON fixture by file name."""

    resource = files(__package__).joinpath(name)
    return json.loads(resource.read_text(encoding="utf-8"))
