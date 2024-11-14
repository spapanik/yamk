import os
from unittest import mock

from tests.conftest import get_make_command, runner_exit_success

COOKBOOK = "variables.yaml"


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_extra_vars(runner: mock.MagicMock) -> None:
    os.environ["NON_EXISTING"] = "/this/does/not/exist"
    make_command = get_make_command(cookbook_name=COOKBOOK, target="variables")
    make_command.make()
    assert runner.call_count == 1
    calls = [
        mock.call("echo /etc/service.d/service.conf", **make_command.subprocess_kwargs)
    ]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_with_variable_in_name(runner: mock.MagicMock) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="call")
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("echo 'called with variable'", **make_command.subprocess_kwargs),
        mock.call("echo call", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_variable_strength_argument_vs_env(runner: mock.MagicMock) -> None:
    os.environ["VARIABLE"] = "env"
    make_command = get_make_command(
        cookbook_name=COOKBOOK,
        target="single_variable",
        variables=["VARIABLE=argument"],
    )
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo argument", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_variable_strength_env_vs_local(runner: mock.MagicMock) -> None:
    os.environ["VARIABLE"] = "env"
    make_command = get_make_command(cookbook_name=COOKBOOK, target="single_variable")
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo env", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_variable_strength_local_vs_regex(runner: mock.MagicMock) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="regex_variable_v2")
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo v42", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_variable_strength_regex_vs_global(runner: mock.MagicMock) -> None:
    make_command = get_make_command(
        cookbook_name=COOKBOOK, target="regex_variable_v7.0"
    )
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo v7.0", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_with_implicit_variables(runner: mock.MagicMock) -> None:
    make_command = get_make_command(
        cookbook_name=COOKBOOK, target="implicit_vars", extra=["--implicit-vars", "42"]
    )
    make_command.make()
    assert runner.call_count == 3
    calls = [
        mock.call("echo implicit_vars", **make_command.subprocess_kwargs),
        mock.call("echo no_commands", **make_command.subprocess_kwargs),
        mock.call("echo --implicit-vars 42", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls
