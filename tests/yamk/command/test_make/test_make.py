from unittest import mock

from tests.conftest import get_make_command, runner_exit_success

COOKBOOK = "make.yaml"


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_builds_with_no_commands(runner: mock.MagicMock) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="no_commands")
    make_command.make()
    assert runner.call_count == 0


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_builds_with_two_commands(runner: mock.MagicMock) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="two_commands")
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("echo two_commands", **make_command.subprocess_kwargs),
        mock.call("echo 42", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_alias(runner: mock.MagicMock) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="alias")
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("echo two_commands", **make_command.subprocess_kwargs),
        mock.call("echo 42", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_with_requirements(runner: mock.MagicMock) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="with_requirements")
    make_command.make()
    assert runner.call_count == 3
    calls = [
        mock.call("echo two_commands", **make_command.subprocess_kwargs),
        mock.call("echo 42", **make_command.subprocess_kwargs),
        mock.call("echo with_requirements", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls
