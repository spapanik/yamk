from unittest import mock

import pytest

from tests.helpers import get_make_command, runner_exit_success

COOKBOOK = "dag.yaml"


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_with_dag_target(runner: mock.MagicMock) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="dag_target_1")
    make_command.make()

    assert runner.call_count == 5
    expected_calls = [
        mock.call("echo dag_target_5", **make_command.subprocess_kwargs),
        mock.call("echo dag_target_2", **make_command.subprocess_kwargs),
        mock.call("echo dag_target_3", **make_command.subprocess_kwargs),
        mock.call("echo dag_target_4", **make_command.subprocess_kwargs),
        mock.call("echo dag_target_1", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == expected_calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_with_dag_target_no_c3(runner: mock.MagicMock) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="dag_target_no_c3_1")

    with pytest.warns(RuntimeWarning):
        make_command.make()

    assert runner.call_count == 5
    expected_calls = [
        mock.call("echo dag_target_no_c3_1", **make_command.subprocess_kwargs),
        mock.call("echo dag_target_no_c3_2", **make_command.subprocess_kwargs),
        mock.call("echo dag_target_no_c3_3", **make_command.subprocess_kwargs),
        mock.call("echo dag_target_no_c3_4", **make_command.subprocess_kwargs),
        mock.call("echo dag_target_no_c3_5", **make_command.subprocess_kwargs),
    ]
    assert sorted(runner.call_args_list) == sorted(expected_calls)
