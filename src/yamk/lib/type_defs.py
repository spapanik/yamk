from __future__ import annotations

from pathlib import Path
from typing import Protocol, Required, Self, TypedDict

Pathlike = str | Path


class Comparable(Protocol):
    def __lt__(self, other: Self, /) -> bool: ...


class SubprocessKwargs(TypedDict):
    shell: bool
    cwd: Path
    executable: str | None


class ExistenceCheck(TypedDict, total=False):
    command: Required[str]
    returncode: int
    stdout: str | None
    stderr: str | None


class RawRecipe(TypedDict, total=False):
    update: bool
    phony: bool
    echo: bool
    keep_ts: bool
    regex: bool
    exists_only: bool
    allow_failures: bool
    alias: str
    existence_command: str
    existence_check: ExistenceCheck
    requires: list[str]
    commands: list[str]
    vars: dict[str, str]
