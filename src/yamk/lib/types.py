from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Union

Pathlike = Union[str, Path]


class ExistenceCheck(TypedDict):
    command: str
    returncode: int
    stdout: str | None
    stderr: str | None
