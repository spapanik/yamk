import re

VAR = re.compile(r"(?P<dollars>\$+){(?P<variable>\w+(:\w+)?)}")


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
