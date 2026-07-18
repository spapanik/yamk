from pathlib import Path

import pytest

from yamk.lib.cli import CliArgs


def test_find_cookbook_with_explicit_name(tmp_path: Path) -> None:
    cookbook = CliArgs.find_cookbook(str(tmp_path), "mk.toml")
    assert cookbook == tmp_path.joinpath("mk.toml")


def test_find_cookbook_without_candidates(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="No candidate cookbook found"):
        CliArgs.find_cookbook(str(tmp_path), None)
