from unittest import mock

import pytest

from tests.helpers import get_make_command, runner_exit_failure, runner_exit_success

COOKBOOK = "exceptions.yaml"


def test_make_raises_on_missing_target() -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="missing_target")
    with pytest.raises(ValueError):
        make_command.make()


def test_make_raises_on_missing_requirement() -> None:
    make_command = get_make_command(
        cookbook_name=COOKBOOK, target="missing_requirement"
    )
    with pytest.raises(ValueError):
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
