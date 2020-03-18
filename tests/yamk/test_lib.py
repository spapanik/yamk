import pathlib

import pytest

from yamk import lib

PATH = pathlib.Path(__file__)


def test_recipe_to_str():
    recipe = lib.Recipe("target", {}, pathlib.Path("."), [{}])
    assert str(recipe) == "Generic recipe for target"
    recipe.specify("target", lib.Variables(PATH))
    assert str(recipe) == "Specified recipe for target"


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
