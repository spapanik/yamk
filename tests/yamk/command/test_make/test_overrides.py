from unittest import mock

from tests.helpers import get_make_command, runner_exit_success

COOKBOOK = "overrides.yaml"


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_with_d_override(runner: mock.MagicMock) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target=".d_override")
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo tail", **make_command.subprocess_kwargs)]
    assert sorted(runner.call_args_list) == sorted(calls)


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_with_d_override_vars(runner: mock.MagicMock) -> None:
    make_command = get_make_command(
        cookbook_name=COOKBOOK, target=".d_override_variables"
    )
    make_command.make()
    assert runner.call_count == 3
    calls = [
        mock.call("echo 3 4", **make_command.subprocess_kwargs),
        mock.call(
            "echo {'x': 'a', 'y': '2', 'z': 'final'}", **make_command.subprocess_kwargs
        ),
        mock.call("echo 3", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls
