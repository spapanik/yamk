import shutil
from pathlib import Path
from unittest import mock

import pytest

from yamk.lib.utils import Node

from tests.helpers import (
    TEST_DATA_ROOT,
    get_make_command,
    runner_exit_failure,
    runner_exit_success,
)

COOKBOOK = "exceptions.yaml"


def test_make_raises_on_newer_cookbook_version() -> None:
    with pytest.raises(RuntimeError, match="requires an yamk"):
        get_make_command(cookbook_name="future.yaml", target="phony")


def test_make_raises_on_missing_version() -> None:
    with pytest.raises(RuntimeError, match=r"missing the required \$globals.version"):
        get_make_command(cookbook_name="no_version.yaml", target="phony")


def test_make_raises_on_missing_target() -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="missing_target")
    with pytest.raises(ValueError, match="No recipe to build missing_target"):
        make_command.make()


def test_make_raises_on_missing_requirement() -> None:
    make_command = get_make_command(
        cookbook_name=COOKBOOK, target="missing_requirement"
    )
    with pytest.raises(ValueError, match=r"No recipe to build .*missing_target"):
        make_command.make()


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_failure)
def test_make_builds_wrong_command_breaks(runner: mock.MagicMock) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="failure")
    with pytest.raises(SystemExit) as exc_info:
        make_command.make()
    assert exc_info.value.code == 42
    assert runner.call_count == 1
    calls = [mock.call("false", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_failure)
def test_make_allowed_failure(runner: mock.MagicMock) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="allowed_failure")
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("false", **make_command.subprocess_kwargs),
        mock.call("echo allowed_failure", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_failure)
def test_make_allowed_failure_in_command(runner: mock.MagicMock) -> None:
    make_command = get_make_command(
        cookbook_name=COOKBOOK, target="allowed_failure_in_command"
    )
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("false", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.sleep")
@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_failure)
def test_make_retries_failed_commands(
    runner: mock.MagicMock, sleep: mock.MagicMock
) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="failure", retries=2)
    with pytest.raises(SystemExit) as exc_info:
        make_command.make()
    assert exc_info.value.code == 42
    assert runner.call_count == 3
    assert sleep.call_args_list == [mock.call(1), mock.call(2)]


@mock.patch("yamk.command.make.print_reports")
@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_failure)
def test_make_failure_prints_timing_report(
    runner: mock.MagicMock, print_reports: mock.MagicMock
) -> None:
    make_command = get_make_command(
        cookbook_name=COOKBOOK, target="failure", print_timing_report=True
    )
    with pytest.raises(SystemExit) as exc_info:
        make_command.make()
    assert exc_info.value.code == 42
    assert runner.call_count == 1
    assert print_reports.call_count == 1


def test_make_raises_on_existence_check_without_phony() -> None:
    make_command = get_make_command(
        cookbook_name=COOKBOOK, target="existence_not_phony"
    )
    with pytest.raises(ValueError, match="Existence commands need to be phony"):
        make_command.make()


def test_make_raises_on_existence_check_without_exists_only() -> None:
    make_command = get_make_command(
        cookbook_name=COOKBOOK, target="existence_not_exists_only"
    )
    with pytest.raises(ValueError, match="Existence commands need exists_only"):
        make_command.make()


def test_make_raises_on_existing_target_without_requirements(tmp_path: Path) -> None:
    cookbook = tmp_path.joinpath(COOKBOOK)
    shutil.copy(TEST_DATA_ROOT.joinpath(COOKBOOK), cookbook)
    target = tmp_path.joinpath("dir/file_in_dir")
    target.parent.mkdir()
    target.touch()
    make_command = get_make_command(cookbook=cookbook, target="dir/file_in_dir")
    with pytest.raises(ValueError, match="Consider marking it with exists_only"):
        make_command.make()


def test_update_ts_raises_without_recipe() -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="failure")
    node = Node(target="orphan")
    with pytest.raises(ValueError, match="No recipe to build orphan"):
        make_command._update_ts(node)


def test_make_target_raises_without_recipe() -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="failure")
    node = Node(target="orphan")
    with pytest.raises(ValueError, match="No recipe to build orphan"):
        make_command._make_target(node)


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_duplicate_requirements_warning(runner: mock.MagicMock) -> None:
    make_command = get_make_command(
        cookbook_name=COOKBOOK, target="duplicate_requirement"
    )
    with pytest.warns(RuntimeWarning):
        make_command.make()
    assert runner.call_count == 1
    calls = [
        mock.call("echo phony_requirement", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls
