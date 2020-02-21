import os

import pytest

from yamk import lib


@pytest.mark.parametrize(
    ["initial", "batch", "expected"],
    [
        [{}, [{"x": "1"}], {"x": "1"}],
        [{}, [{"x": "1"}, {"y": "2"}], {"x": "1", "y": "2"}],
        [{}, [{"x": "1", "y": "0"}, {"y": "2"}], {"x": "1", "y": "2"}],
        [{"x": "0"}, [{"x": "1"}], {"x": "1"}],
        [{"TEST_VAR": "test"}, [{"TEST_VAR": "1"}], {"TEST_VAR": "test"}],
        [{"TEST_VAR": "test"}, [{"[strong]TEST_VAR": "1"}], {"TEST_VAR": "1"}],
    ],
)
def test_add_batch_to_variables(initial, batch, expected):
    os.environ["TEST_VAR"] = "test"
    variables = lib.Variables(**initial)
    assert variables.add_batch(batch) == expected


@pytest.mark.parametrize(
    ["obj", "variables", "expected"],
    [
        ["string", {"x": 1}, "string"],
        ["string_${x}", {"x": 1}, "string_1"],
        ["string_$${x}", {"x": 1}, "string_${x}"],
        ["${dict:key}", {"dict": {"key": "value"}}, "value"],
        ["${list:0}", {"list": ["spam", "eggs"]}, "spam"],
        ["${list}", {"list": ["spam", "eggs"]}, "spam eggs"],
        [["string_${x}"], {"x": 1}, ["string_1"]],
        [
            {"string_${key}": "string_${value}"},
            {"key": 1, "value": 2},
            {"string_1": "string_2"},
        ],
    ],
)
def test_substitute_vars(obj, variables, expected):
    assert lib.substitute_vars(obj, variables) == expected


@pytest.mark.parametrize(
    ["regex", "sample", "variables"],
    [
        [r"./path/to/(?P<daemon>\w+).conf", "./path/not/to/sqld.conf", {}],
        [r"./path/to/(?P<daemon>\w+).conf", "./path/to/sqld.conf", {"daemon": "sqld"}],
        [
            r"(.+)/path/to/(?P<daemon>\w+).conf",
            "./path/to/sqld.conf",
            {"daemon": "sqld"},
        ],
    ],
)
def test_extract_regex_vars(regex, sample, variables):
    assert lib.extract_regex_vars(regex, sample) == variables


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
