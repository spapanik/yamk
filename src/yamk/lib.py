import os
import re

VAR = re.compile(r"(?P<dollars>\$+){(?P<variable>\w+(:\w+)?)}")
OPTIONS = re.compile(r"\[(?P<options>.*?)\](?P<string>.*)")


class Variables(dict):
    def add_batch(self, batch):
        new_vars = self.__class__(**self)
        for var_block in batch:
            for key, value in var_block.items():
                key = substitute_vars(key, new_vars)
                key, options = extract_options(key)
                if key in os.environ and "strong" not in options:
                    continue
                value = substitute_vars(value, new_vars)
                new_vars[key] = value
        return new_vars


def _stringify(value):
    if isinstance(value, list):
        return " ".join(value)
    return str(value)


def substitute_vars(string, variables):
    def repl(matchobj):
        dollars = matchobj.group("dollars")
        variable = matchobj.group("variable")
        if len(dollars) % 2:
            key = None
            if ":" in variable:
                variable, key = variable.split(":")
            value = variables[variable]
            if key is None:
                return _stringify(value)
            if isinstance(value, list):
                key = int(key)
            return _stringify(value[key])
        return f"{'$'*(len(dollars)//2)}{{{variable}}}"

    return re.sub(VAR, repl, string)


def extract_options(string):
    match = re.fullmatch(OPTIONS, string)
    if match is None:
        return string.strip(), set()

    options = match.group("options")
    string = match.group("string")
    return (
        string,
        set(map(lambda s: s.strip(), options.split(","))),
    )


def extract_regex_vars(regex, sample):
    match = re.fullmatch(regex, sample)
    if match is None:
        return {}

    return match.groupdict()
