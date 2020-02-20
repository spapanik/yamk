import pytest

from yamk import lib


@pytest.mark.parametrize(
    ["string", "variables", "expected"],
    [
        ["string", {"x": 1}, "string"],
        ["string_${x}", {"x": 1}, "string_1"],
        ["string_$${x}", {"x": 1}, "string_${x}"],
        ["${dict:key}", {"dict": {"key": "value"}}, "value"],
        ["${list:0}", {"list": ["spam", "eggs"]}, "spam"],
        ["${list}", {"list": ["spam", "eggs"]}, "spam eggs"],
    ],
)
def test_substitute_vars(string, variables, expected):
    assert lib.substitute_vars(string, variables) == expected


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
