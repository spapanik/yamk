import os
from unittest import mock

from tests.helpers import get_make_command, runner_exit_success

COOKBOOK = "requirements.yaml"


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_requirement_from_argv(runner: mock.MagicMock) -> None:
    make_command = get_make_command(
        cookbook_name=COOKBOOK,
        target="requirement_ext",
        variables=["EXT_VARIABLE=echo"],
    )
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("echo 'target=echo'", **make_command.subprocess_kwargs),
        mock.call("echo 'echo'", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_requires_from_env(runner: mock.MagicMock) -> None:
    os.environ["EXT_VARIABLE"] = "echo"
    make_command = get_make_command(cookbook_name=COOKBOOK, target="requirement_ext")
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("echo 'target=echo'", **make_command.subprocess_kwargs),
        mock.call("echo 'echo'", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_requires_from_local(runner: mock.MagicMock) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="requirement_local")
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("echo 'target=echo'", **make_command.subprocess_kwargs),
        mock.call("echo 'echo'", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_requires_from_regex(runner: mock.MagicMock) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="requirement_echo")
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("echo 'target=echo'", **make_command.subprocess_kwargs),
        mock.call("echo 'echo'", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_requires_from_global(runner: mock.MagicMock) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="requirement")
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("echo 'target=echo'", **make_command.subprocess_kwargs),
        mock.call("echo 'echo'", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls
