from unittest import mock

from tests.helpers import get_make_command, runner_exit_success

COOKBOOK = "functions.yaml"


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_sort_variable(runner: mock.MagicMock) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="sort_variable")
    make_command.make()
    assert runner.call_count == 1
    path = make_command.base_dir.joinpath("functions.yaml").as_posix()
    calls = [mock.call(f"echo {path}", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_sort_function(runner: mock.MagicMock) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="sort_function")
    make_command.make()
    assert runner.call_count == 1
    path = make_command.base_dir.joinpath("functions.yaml").as_posix()
    calls = [mock.call(f"echo {path}", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_pwd(runner: mock.MagicMock) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="pwd")
    make_command.make()
    assert runner.call_count == 1
    path = make_command.base_dir.as_posix()
    calls = [mock.call(f"echo {path}", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_ternary_if_true(runner: mock.MagicMock) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="ternary_if_true")
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo 42", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_ternary_if_false(runner: mock.MagicMock) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="ternary_if_false")
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo 1024", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_ternary_if_function(runner: mock.MagicMock) -> None:
    make_command = get_make_command(
        cookbook_name=COOKBOOK, target="ternary_if_function"
    )
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo 42", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_substitution(runner: mock.MagicMock) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="substitute")
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo the new version", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_merge(runner: mock.MagicMock) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="merge")
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo one two three four", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls
