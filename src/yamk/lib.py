import re

VAR = re.compile(r"(?P<dollars>\$+){(?P<variable>[a-zA-Z0-9_.]+(:[a-zA-Z0-9_.]+)?)}")
OPTIONS = re.compile(r"\[(?P<options>.*?)\](?P<string>.*)")


class Recipe:
    def __init__(self, target, raw_recipe, base_dir, arg_vars):
        self._specified = False
        self.base_dir = base_dir
        self.vars: Variables
        self.arg_vars = arg_vars
        self.phony = raw_recipe.get("phony", False)
        self.requires = raw_recipe.get("requires", [])
        self.variable_list = raw_recipe.get("vars", [])
        self.commands = raw_recipe.get("commands", [])
        self.echo = raw_recipe.get("echo", False)
        self.regex = raw_recipe.get("regex", False)
        self.allow_failures = raw_recipe.get("allow_failures", False)
        self.target = self._target(target)
        if self.phony:
            self.keep_ts = raw_recipe.get("keep_ts", False)
            self.exists_only = False
            self.recursive = False
        else:
            self.keep_ts = False
            self.exists_only = raw_recipe.get("exists_only", False)
            self.recursive = raw_recipe.get("recursive", False)

    def __str__(self):
        if self._specified:
            return f"Specified recipe for {self.target}"
        return f"Generic recipe for {self.target}"

    def specify(self, target, globs):
        if self._specified:
            return
        self._specified = True
        if self.regex:
            groups = re.fullmatch(self.target, target).groupdict()
            self.target = target
        else:
            groups = {}
        self._update_variables(globs, groups)
        self._update_requirements()
        self._update_commands()

    def _update_variables(self, globs, groups):
        extra_vars = [groups, *self.arg_vars, {".target": self.target}]
        self.vars = globs.add_batch(self.variable_list).add_batch(extra_vars)

    def _update_requirements(self):
        self.requires = substitute_vars(self.requires, self.vars)

    def _update_commands(self):
        extra_vars = [{".requirements": self.requires}]
        self.vars = self.vars.add_batch(extra_vars)
        self.commands = substitute_vars(self.commands, self.vars)

    def _target(self, target):
        if not self.phony:
            target = self.base_dir.joinpath(target).as_posix()
        if self.regex:
            target = re.compile(target)
        return target


class Variables(dict):
    def add_batch(self, batch):
        new_vars = self.__class__(**self)
        for var_block in batch:
            for key, value in var_block.items():
                key = substitute_vars(key, new_vars)
                key, options = extract_options(key)
                if "weak" in options:
                    continue
                value = substitute_vars(value, new_vars)
                new_vars[key] = value
        return new_vars


def _stringify(value):
    if isinstance(value, list):
        return " ".join(value)
    return str(value)


def substitute_vars(obj, variables):
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

    if isinstance(obj, str):
        return re.sub(VAR, repl, obj)
    if isinstance(obj, list):
        return [re.sub(VAR, repl, string) for string in obj]
    return {
        re.sub(VAR, repl, key): re.sub(VAR, repl, value) for key, value in obj.items()
    }


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
