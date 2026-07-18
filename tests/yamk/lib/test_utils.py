from __future__ import annotations

import os
import pathlib
from typing import TYPE_CHECKING
from unittest import mock

import pytest
from pyutilkit.timing import Timing

from yamk.lib.utils import (
    DAG,
    CommandReport,
    Node,
    Parser,
    Recipe,
    Version,
    extract_options,
    flatten_vars,
    human_readable_timestamp,
    print_reports,
)

if TYPE_CHECKING:
    from yamk.lib.type_defs import RawRecipe

PATH = pathlib.Path(__file__)


def test_recipe_to_str() -> None:
    recipe = Recipe("target", {}, pathlib.Path(), {}, {}, extra=[])
    assert str(recipe) == "Generic recipe for target"
    recipe = recipe.for_target("target", extra=[])
    assert str(recipe) == "Specified recipe for target"


def test_recipe_for_target() -> None:
    recipe = Recipe("target", {}, pathlib.Path(), {}, {}, extra=[])
    recipe_specified = recipe.for_target("target", extra=[])
    recipe_specified_again = recipe_specified.for_target("target", extra=[])
    assert recipe is not recipe_specified
    assert recipe_specified is recipe_specified_again


def test_recipe_existence_command_creates_check() -> None:
    raw_recipe: RawRecipe = {
        "phony": True,
        "exists_only": True,
        "existence_command": "cmd",
    }
    recipe = Recipe("target", raw_recipe, pathlib.Path(), {}, {}, extra=[])
    assert recipe.existence_check == {"command": "cmd"}


def test_recipe_existence_command_overrides_check() -> None:
    raw_recipe: RawRecipe = {
        "phony": True,
        "exists_only": True,
        "existence_check": {"command": "old", "stdout": "out"},
        "existence_command": "new",
    }
    recipe = Recipe("target", raw_recipe, pathlib.Path(), {}, {}, extra=[])
    assert recipe.existence_check == {"command": "new", "stdout": "out"}


def test_specified_regex_recipe_needs_original_regex() -> None:
    raw_recipe: RawRecipe = {"phony": True, "regex": True}
    with pytest.raises(RuntimeError, match="original_regex must be specified"):
        Recipe("target", raw_recipe, pathlib.Path(), {}, {}, extra=[], specified=True)


def test_specified_regex_recipe_needs_matching_regex() -> None:
    raw_recipe: RawRecipe = {"phony": True, "regex": True}
    with pytest.raises(RuntimeError, match="does not match"):
        Recipe(
            "target",
            raw_recipe,
            pathlib.Path(),
            {},
            {},
            extra=[],
            original_regex="mismatch",
            specified=True,
        )


@pytest.mark.parametrize(
    ("initial", "expected"),
    [
        ({"regex": {}, "local": {"x": "1"}}, {"x": "1"}),
        ({"regex": {}, "local": {"x": "1", "y": "2"}}, {"x": "1", "y": "2"}),
        (
            {"global": {}, "regex": {"x": "1", "y": "0"}, "local": {"y": "2"}},
            {"x": "1", "y": "2"},
        ),
        ({"regex": {"x": "0"}, "local": {"x": "1"}}, {"x": "1"}),
        (
            {"regex": {"TEST_VAR": "test"}, "local": {"TEST_VAR": "1"}},
            {"TEST_VAR": "1"},
        ),
        (
            {"regex": {"TEST_VAR": "test"}, "local": {"[weak]TEST_VAR": "1"}},
            {"TEST_VAR": "test"},
        ),
    ],
)
def test_flatten_vars(
    initial: dict[str, dict[str, str]], expected: dict[str, str]
) -> None:
    assert flatten_vars(initial, PATH) == expected


def test_node_to_str() -> None:
    node = Node(target="target")
    assert str(node) == "target"
    assert str([node]) == "[Node <target>]"


def test_node_equals() -> None:
    node = Node(target="target")

    class FakeNode:
        target = "target"

    other = FakeNode()
    assert node != other
    assert other != node


def test_missing_topological_sort() -> None:
    root = Node(target="target")
    dag = DAG(root)
    assert list(dag) == [root]


def test_topological_sort_detects_cycles() -> None:
    root = Node(target="target")
    node = Node(target="requirement")
    root.add_requirement(node)
    node.add_requirement(root)
    dag = DAG(root)
    dag.add_node(node)
    with pytest.raises(ValueError, match="Cyclic dependencies detected"):
        dag.topological_sort()


def test_c3_sort_detects_cycles() -> None:
    root = Node(target="target")
    node = Node(target="requirement")
    root.add_requirement(node)
    node.add_requirement(root)
    dag = DAG(root)
    dag.add_node(node)
    with pytest.raises(ValueError, match="Cannot compute c3_sort"):
        dag.c3_sort()


def test_c3_sort_reraises_recursion_error() -> None:
    root = Node(target="target")
    node = Node(target="requirement")
    root.add_requirement(node)
    dag = DAG(root)
    dag.add_node(node)
    with (
        mock.patch.object(DAG, "_merge", side_effect=RecursionError),
        pytest.raises(ValueError, match="Cannot compute c3_sort"),
    ):
        dag.c3_sort()


def test_flatten_vars_raises_on_dotted_var() -> None:
    with pytest.raises(ValueError, match="Only implicit vars can start with a dot"):
        flatten_vars({"local": {".x": "1"}}, PATH)


@pytest.mark.parametrize(
    ("success", "retries"),
    [
        (False, 0),
        (True, 1),
        (True, 0),
    ],
)
def test_command_report_print(
    success: bool,
    retries: int,
    capsys: mock.MagicMock,  # upgrade: pytest: check for isatty
) -> None:
    report = CommandReport(
        command="ls", retries=retries, timing=Timing(seconds=1), success=success
    )
    report.print(cols=80)
    captured = capsys.readouterr()
    assert captured.out == "`ls`1.00s" + os.linesep
    assert captured.err == ""


@mock.patch(
    "os.get_terminal_size", new=mock.MagicMock(return_value=os.terminal_size((80, 24)))
)
def test_print_reports(
    capsys: mock.MagicMock,  # upgrade: pytest: check for isatty
) -> None:
    report = CommandReport(
        command="ls", retries=0, timing=Timing(seconds=1), success=True
    )
    print_reports([report])
    captured = capsys.readouterr()
    assert "Yam Report" in captured.out
    assert "`ls`" in captured.out


@pytest.mark.parametrize("obj", [("string in a tuple",), None])
def test_parser_evaluation_raises(obj: object) -> None:
    parser = Parser({}, PATH)
    with pytest.raises(TypeError):
        parser.evaluate(obj)


@pytest.mark.parametrize(
    ("obj", "variables", "expected"),
    [
        ("string", {"x": 1}, "string"),
        ("string_${x}", {"x": 1}, "string_1"),
        ("string_$${x}", {"x": 1}, "string_${x}"),
        ("${dict:key}", {"dict": {"key": "value"}}, "value"),
        ("${list:0}", {"list": ["spam", "eggs"]}, "spam"),
        ("${dict:}", {"dict": {"key": "value"}}, "{'key': 'value'}"),
        ("${list:}", {"list": ["spam", "eggs"]}, "spam eggs"),
        ("${dict}", {"dict": {"key": "value"}}, {"key": "value"}),
        ("${list}", {"list": ["spam", "eggs"]}, ["spam", "eggs"]),
        (["${nested}"], {"nested": ["spam"]}, ["spam"]),
        (["string_${x}"], {"x": 1}, ["string_1"]),
        (
            {"string_${key}": "string_${value}"},
            {"key": 1, "value": 2},
            {"string_1": "string_2"},
        ),
        ("$((sort ${x}))", {"x": [3, 1, 2]}, [1, 2, 3]),
    ],
)
def test_parser_evaluation(
    obj: str | list[str], variables: dict[str, object], expected: str | list[str]
) -> None:
    parser = Parser(variables, PATH)
    assert parser.evaluate(obj) == expected


@pytest.mark.parametrize(
    ("string", "expected_options", "expected_string"),
    [
        ("string", set(), "string"),
        ("[english]string", {"english"}, "string"),
        ("[english, utf-8]string", {"english", "utf-8"}, "string"),
        (
            "[more_brackets]string_with_]_in_it",
            {"more_brackets"},
            "string_with_]_in_it",
        ),
    ],
)
def test_extract_options(
    string: str, expected_options: set[str], expected_string: str
) -> None:
    string, options = extract_options(string)
    assert string == expected_string
    assert options == expected_options


@pytest.mark.parametrize(
    ("timestamp", "dt"),
    [
        (0, "1970-01-01 00:00:00+00:00"),
        (1584704491.4541745, "2020-03-20 11:41:31.454175+00:00"),
        (float("inf"), "end of time"),
    ],
)
def test_timestamp_to_dt(timestamp: float, dt: str) -> None:
    assert human_readable_timestamp(timestamp) == dt


@pytest.mark.parametrize(
    ("version", "major", "minor", "patch"),
    [
        ("1", 1, 0, 0),
        ("1.2", 1, 2, 0),
        ("1.2.3", 1, 2, 3),
        ("5.1.0dev1", 5, 1, 0),
        ("5.1.0dev1+2020-01-01", 5, 1, 0),
        ("5.1.0dev1+2020-01-01.1", 5, 1, 0),
        ("5.1.0dev1+2020-01-01.1.2", 5, 1, 0),
        ("1.1a1", 1, 1, 0),
        ("1.1a1+2020-01-01", 1, 1, 0),
        ("1.1-a1", 1, 1, 0),
    ],
)
def test_version_parsing(version: str, major: int, minor: int, patch: int) -> None:
    parsed_version = Version.from_string(version)
    assert parsed_version.major == major
    assert parsed_version.minor == minor
    assert parsed_version.patch == patch


@pytest.mark.parametrize(
    ("old_version", "new_version"),
    [
        ("1.0.0", "1.0.1"),
        ("0.0.1", "0.1.0"),
        ("0.0.0.post1", "0.0.1"),
    ],
)
def test_version_comparison(old_version: str, new_version: str) -> None:
    assert Version.from_string(old_version) < Version.from_string(new_version)
