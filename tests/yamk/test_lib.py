import pathlib
from datetime import datetime

import pytest

from yamk import lib

PATH = pathlib.Path(__file__)


def test_recipe_to_str():
    variables = {"file_vars": [], "arg_vars": []}
    recipe = lib.Recipe("target", {}, pathlib.Path("."), variables)
    assert str(recipe) == "Generic recipe for target"
    recipe = recipe.for_target("target")
    assert str(recipe) == "Specified recipe for target"


def test_recipe_for_target():
    variables = {"file_vars": [], "arg_vars": []}
    recipe = lib.Recipe("target", {}, pathlib.Path("."), variables)
    recipe_specified = recipe.for_target("target")
    recipe_specified_again = recipe_specified.for_target("target")
    assert recipe is not recipe_specified
    assert recipe_specified is recipe_specified_again


@pytest.mark.parametrize(
    ["initial", "batch", "expected"],
    [
        [{}, [{"x": "1"}], {"x": "1"}],
        [{}, [{"x": "1"}, {"y": "2"}], {"x": "1", "y": "2"}],
        [{}, [{"x": "1", "y": "0"}, {"y": "2"}], {"x": "1", "y": "2"}],
        [{"x": "0"}, [{"x": "1"}], {"x": "1"}],
        [{"TEST_VAR": "test"}, [{"TEST_VAR": "1"}], {"TEST_VAR": "1"}],
        [{"TEST_VAR": "test"}, [{"[weak]TEST_VAR": "1"}], {"TEST_VAR": "test"}],
    ],
)
def test_add_batch_to_variables(initial, batch, expected):
    variables = lib.Variables(PATH, **initial)
    assert variables.add_batch(batch) == expected


def test_node_to_str():
    node = lib.Node(target="target")
    assert str(node) == "target"
    assert str([node]) == "[Node <target>]"


def test_node_equals():
    node = lib.Node(target="target")

    class FakeNode:
        target = "target"

    other = FakeNode()
    assert (node == other) is False
    assert (other == node) is False


def test_missing_topological_sort():
    root = lib.Node(target="target")
    dag = lib.DAG(root)
    assert list(dag) == [root]


def test_topological_sort_detects_cycles():
    root = lib.Node(target="target")
    node = lib.Node(target="requirement")
    root.add_requirement(node)
    node.add_requirement(root)
    dag = lib.DAG(root)
    dag.add_node(node)
    assert pytest.raises(ValueError, dag.sort)


@pytest.mark.parametrize("obj", [1, ("string in a tuple",), {"nested integer": 1}])
def test_parser_evaluation_raises(obj):
    parser = lib.Parser({}, PATH)
    assert pytest.raises(TypeError, parser.evaluate, obj)


@pytest.mark.parametrize(
    ["obj", "variables", "expected"],
    [
        ["string", {"x": 1}, "string"],
        ["string_${x}", {"x": 1}, "string_1"],
        ["string_$${x}", {"x": 1}, "string_${x}"],
        ["${dict:key}", {"dict": {"key": "value"}}, "value"],
        ["${list:0}", {"list": ["spam", "eggs"]}, "spam"],
        ["${dict:}", {"dict": {"key": "value"}}, "{'key': 'value'}"],
        ["${list:}", {"list": ["spam", "eggs"]}, "spam eggs"],
        ["${dict}", {"dict": {"key": "value"}}, {"key": "value"}],
        ["${list}", {"list": ["spam", "eggs"]}, ["spam", "eggs"]],
        [["${nested}"], {"nested": ["spam"]}, ["spam"]],
        [["string_${x}"], {"x": 1}, ["string_1"]],
        [
            {"string_${key}": "string_${value}"},
            {"key": 1, "value": 2},
            {"string_1": "string_2"},
        ],
        ["$((sort ${x}))", {"x": [3, 1, 2]}, [1, 2, 3]],
    ],
)
def test_parser_evaluation(obj, variables, expected):
    parser = lib.Parser(variables, PATH)
    assert parser.evaluate(obj) == expected


@pytest.mark.parametrize(
    ["dict_1", "dict_2", "expected"],
    [
        [{1: 2}, {2: 3}, {1: 2, 2: 3}],
        [{1: 2}, {1: 3}, {1: 3}],
        [{1: {2: 3}}, {1: 2}, {1: 2}],
        [{1: 2}, {1: {2: 3}}, {1: {2: 3}}],
        [{1: {2: 3, 3: 4}}, {1: {2: 4, 4: 5}}, {1: {2: 4, 3: 4, 4: 5}}],
    ],
)
def test_deep_merge(dict_1, dict_2, expected):
    assert lib.deep_merge(dict_1, dict_2) == expected


@pytest.mark.parametrize(
    ["string", "expected_options", "expected_string"],
    [
        ["string", set(), "string"],
        ["[english]string", {"english"}, "string"],
        ["[english, utf-8]string", {"english", "utf-8"}, "string"],
        [
            "[more_brackets]string_with_]_in_it",
            {"more_brackets"},
            "string_with_]_in_it",
        ],
    ],
)
def test_extract_options(string, expected_options, expected_string):
    string, options = lib.extract_options(string)
    assert string == expected_string
    assert options == expected_options


@pytest.mark.parametrize(
    ["timestamp", "dt"],
    [
        [0, datetime(1970, 1, 1)],
        [1584704491.4541745, datetime(2020, 3, 20, 11, 41, 31, 454175)],
        [float("inf"), datetime(9999, 12, 31, 23, 59, 59, 999999)],
    ],
)
def test_timestamp_to_dt(timestamp, dt):
    assert lib.timestamp_to_dt(timestamp) == dt
