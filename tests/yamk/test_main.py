import json
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

from yamk.__main__ import main


@mock.patch("sys.argv", ["yamk", "phony"])
@mock.patch("yamk.__main__.MakeCommand")
def test_main(mock_make: mock.MagicMock) -> None:
    main()
    assert mock_make.call_count == 1
    assert mock_make().make.call_count == 1


@pytest.mark.parametrize(("exit_code", "indicator"), [(0, "🟢"), (7, "🔴")])
def test_timing_report_cli(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, exit_code: int, indicator: str
) -> None:
    command = f"exit {exit_code}"
    cookbook = tmp_path / "cookbook.json"
    cookbook.write_text(
        json.dumps(
            {
                "$globals": {"version": "8.1"},
                "target": {"phony": True, "commands": [command]},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("PY_UTIL_FORCE_PREFIX", "true")
    result = subprocess.run(  # noqa: S603
        [
            sys.executable,
            "-c",
            "from yamk.__main__ import main; main()",
            "-c",
            str(cookbook),
            "-T",
            "target",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == exit_code
    assert "Yam Report" in result.stdout
    assert f"{indicator}`{command}`" in result.stdout
    assert result.stderr == ""
