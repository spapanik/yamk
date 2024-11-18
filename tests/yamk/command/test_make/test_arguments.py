from unittest import mock

from tests.conftest import get_make_command, runner_exit_success

COOKBOOK = "arguments.yaml"


@mock.patch("yamk.command.make.print", new_callable=mock.MagicMock)
@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_dry_run(runner: mock.MagicMock, mock_print: mock.MagicMock) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="echo", dry_run=True)
    make_command.make()
    assert runner.call_count == 0
    assert mock_print.call_count == 2
    calls = [
        mock.call("🔧 Running `\x1b[1mecho 'echo'\x1b[0m`"),
        mock.call("✅ `\x1b[1mecho 'echo'\x1b[0m` run successfully!"),
    ]
    assert mock_print.call_args_list == calls


@mock.patch("yamk.command.make.print", new_callable=mock.MagicMock)
@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_verbosity(runner: mock.MagicMock, mock_print: mock.MagicMock) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="echo", verbosity=4)
    make_command.make()
    assert runner.call_count == 1
    assert mock_print.call_count == 9
    calls = [
        mock.call("=== all targets ==="),
        mock.call("- echo:"),
        mock.call("    timestamp: end of time"),
        mock.call("    should_build: True"),
        mock.call("    requires: []"),
        mock.call("    required_by: set()"),
        mock.call("=== target: echo ==="),
        mock.call("🔧 Running `\x1b[1mecho 'echo'\x1b[0m`"),
        mock.call("✅ `\x1b[1mecho 'echo'\x1b[0m` run successfully!"),
    ]
    assert mock_print.call_args_list == calls


@mock.patch("yamk.command.make.print", new_callable=mock.MagicMock)
@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_echo_in_recipe(
    runner: mock.MagicMock, mock_print: mock.MagicMock
) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="echo")
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo 'echo'", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls
    assert mock_print.call_count == 2
    calls = [
        mock.call("🔧 Running `\x1b[1mecho 'echo'\x1b[0m`"),
        mock.call("✅ `\x1b[1mecho 'echo'\x1b[0m` run successfully!"),
    ]
    assert mock_print.call_args_list == calls


@mock.patch("yamk.command.make.print", new_callable=mock.MagicMock)
@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_echo_in_command(
    runner: mock.MagicMock, mock_print: mock.MagicMock
) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="echo_in_command")
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo 'echo_in_command'", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls
    assert mock_print.call_count == 2
    calls = [
        mock.call("🔧 Running `\x1b[1mecho 'echo_in_command'\x1b[0m`"),
        mock.call("✅ `\x1b[1mecho 'echo_in_command'\x1b[0m` run successfully!"),
    ]
    assert mock_print.call_args_list == calls
