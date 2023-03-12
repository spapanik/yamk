import pathlib

import pytest

from yamk import lib

PATH = pathlib.Path(__file__)


def test_recipe_to_str():
    recipe = lib.Recipe("target", {}, pathlib.Path("."), {}, {})
    assert str(recipe) == "Generic recipe for target"
    recipe = recipe.for_target("target")
    assert str(recipe) == "Specified recipe for target"


def test_recipe_for_target():
    recipe = lib.Recipe("target", {}, pathlib.Path("."), {}, {})
    recipe_specified = recipe.for_target("target")
    recipe_specified_again = recipe_specified.for_target("target")
    assert recipe is not recipe_specified
    assert recipe_specified is recipe_specified_again


@pytest.mark.parametrize(
    ("initial", "batch", "expected"),
    [
        ({}, [{"x": "1"}], {"x": "1"}),
        ({}, [{"x": "1"}, {"y": "2"}], {"x": "1", "y": "2"}),
        ({}, [{"x": "1", "y": "0"}, {"y": "2"}], {"x": "1", "y": "2"}),
        ({"x": "0"}, [{"x": "1"}], {"x": "1"}),
        ({"TEST_VAR": "test"}, [{"TEST_VAR": "1"}], {"TEST_VAR": "1"}),
        ({"TEST_VAR": "test"}, [{"[weak]TEST_VAR": "1"}], {"TEST_VAR": "test"}),
    ],
)
def test_update_dictionary(initial, batch, expected):
    lib.update_vars(initial, batch, PATH)
    assert initial == expected


def test_node_to_str():
    node = lib.Node(target="target")
    assert str(node) == "target"
    assert str([node]) == "[Node <target>]"


def test_node_equals():
    node = lib.Node(target="target")

    class FakeNode:
        target = "target"

    other = FakeNode()
    assert node != other
    assert other != node


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
    assert pytest.raises(ValueError, dag.topological_sort)  # noqa: PT011


def test_c3_sort_detects_cycles():
    root = lib.Node(target="target")
    node = lib.Node(target="requirement")
    root.add_requirement(node)
    node.add_requirement(root)
    dag = lib.DAG(root)
    dag.add_node(node)
    assert pytest.raises(ValueError, dag.c3_sort)  # noqa: PT011


@pytest.mark.parametrize("obj", [1, ("string in a tuple",), {"nested integer": 1}])
def test_parser_evaluation_raises(obj):
    parser = lib.Parser({}, PATH)
    assert pytest.raises(TypeError, parser.evaluate, obj)


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
def test_parser_evaluation(obj, variables, expected):
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
def test_extract_options(string, expected_options, expected_string):
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
def test_timestamp_to_dt(timestamp, dt):
    assert lib.human_readable_timestamp(timestamp) == dt
