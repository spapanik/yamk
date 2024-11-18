from unittest import mock

from tests.conftest import get_make_command, runner_exit_success

COOKBOOK = "regex.yaml"


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_regex_target(runner: mock.MagicMock) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="echo_1024")
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo 1024", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_regex_target_strength(runner: mock.MagicMock) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="echo_42")
    make_command.make()
    assert runner.call_count == 1
    calls = [
        mock.call(
            "echo 'The answer to life, the universe, and everything'",
            **make_command.subprocess_kwargs,
        )
    ]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_multiple_regex_targets(runner: mock.MagicMock) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="multiple_regex")
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call(
            "echo 'The answer to life, the universe, and everything'",
            **make_command.subprocess_kwargs,
        ),
        mock.call("echo 1024", **make_command.subprocess_kwargs),
    ]
    assert sorted(runner.call_args_list) == sorted(calls)
