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
def test_substite_vars(string, variables, expected):
    assert lib.substitute_vars(string, variables) == expected
