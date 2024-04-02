from __future__ import annotations

import pathlib
from typing import Any

import pytest

from yamk import lib

PATH = pathlib.Path(__file__)


def test_recipe_to_str() -> None:
    recipe = lib.Recipe("target", {}, pathlib.Path(), {}, {}, extra=[])
    assert str(recipe) == "Generic recipe for target"
    recipe = recipe.for_target("target", extra=[])
    assert str(recipe) == "Specified recipe for target"


def test_recipe_for_target() -> None:
    recipe = lib.Recipe("target", {}, pathlib.Path(), {}, {}, extra=[])
    recipe_specified = recipe.for_target("target", extra=[])
    recipe_specified_again = recipe_specified.for_target("target", extra=[])
    assert recipe is not recipe_specified
    assert recipe_specified is recipe_specified_again


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
    assert lib.flatten_vars(initial, PATH) == expected


def test_node_to_str() -> None:
    node = lib.Node(target="target")
    assert str(node) == "target"
    assert str([node]) == "[Node <target>]"


def test_node_equals() -> None:
    node = lib.Node(target="target")

    class FakeNode:
        target = "target"

    other = FakeNode()
    assert node != other
    assert other != node


def test_missing_topological_sort() -> None:
    root = lib.Node(target="target")
    dag = lib.DAG(root)
    assert list(dag) == [root]


def test_topological_sort_detects_cycles() -> None:
    root = lib.Node(target="target")
    node = lib.Node(target="requirement")
    root.add_requirement(node)
    node.add_requirement(root)
    dag = lib.DAG(root)
    dag.add_node(node)
    with pytest.raises(ValueError):
        dag.topological_sort()


def test_c3_sort_detects_cycles() -> None:
    root = lib.Node(target="target")
    node = lib.Node(target="requirement")
    root.add_requirement(node)
    node.add_requirement(root)
    dag = lib.DAG(root)
    dag.add_node(node)
    with pytest.raises(ValueError):
        dag.c3_sort()


@pytest.mark.parametrize("obj", [1, ("string in a tuple",), {"nested integer": 1}])
def test_parser_evaluation_raises(obj: Any) -> None:
    parser = lib.Parser({}, PATH)
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
    obj: str | list[str], variables: dict[str, Any], expected: str | list[str]
) -> None:
    parser = lib.Parser(variables, PATH)
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
    string, options = lib.extract_options(string)
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
def test_timestamp_to_dt(timestamp: int | float, dt: str) -> None:
    assert lib.human_readable_timestamp(timestamp) == dt


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
    parsed_version = lib.Version.from_string(version)
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
    assert lib.Version.from_string(old_version) < lib.Version.from_string(new_version)
