import datetime
import math
import os
import re
import shlex

from yamk.functions import functions

VAR = re.compile(
    r"(?P<dollars>\$+){(?P<variable>[a-zA-Z0-9_.]+)(?P<sep>:)?(?P<key>[a-zA-Z0-9_.]+)?}"
)
OPTIONS = re.compile(r"\[(?P<options>.*?)\](?P<string>.*)")
FUNCTION = re.compile(r"\$\(\((?P<name>\w+) *(?P<args>.*)\)\)")


class Recipe:
    def __init__(self, target, raw_recipe, base_dir, variables, *, specified=False):
        self._specified = specified
        self._raw_recipe = raw_recipe
        self.base_dir = base_dir
        self.file_vars = variables["file_vars"]
        self.arg_vars = variables["arg_vars"]
        self.local_vars = raw_recipe.get("vars", [])
        self.vars = (
            Variables(self.base_dir, **os.environ)
            .add_batch(self.file_vars)
            .add_batch(self.local_vars)
            .add_batch(self.arg_vars)
        )
        self.alias = self._alias(raw_recipe.get("alias", False))
        self.phony = raw_recipe.get("phony", False)
        self.requires = raw_recipe.get("requires", [])
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

    def for_target(self, target):
        if self._specified:
            return self
        variables = {"file_vars": self.file_vars, "arg_vars": self.arg_vars}
        new_recipe = self.__class__(
            target, self._raw_recipe, self.base_dir, variables, specified=True
        )
        if new_recipe.regex:
            groups = re.fullmatch(self.target, new_recipe.target).groupdict()
        else:
            groups = {}
        new_recipe._update_variables(groups)
        new_recipe._update_requirements()
        new_recipe._update_commands()
        return new_recipe

    def _update_variables(self, groups):
        self.vars = self.vars.add_batch([groups, {".target": self.target}])

    def _update_requirements(self):
        parser = Parser(self.vars, self.base_dir)
        self.requires = parser.evaluate(self.requires)

    def _update_commands(self):
        extra_vars = [{".requirements": self.requires}]
        self.vars = self.vars.add_batch(extra_vars)
        parser = Parser(self.vars, self.base_dir)
        self.commands = parser.evaluate(self.commands)

    def _alias(self, alias):
        if alias is False:
            return alias
        parser = Parser(self.vars, self.base_dir)
        return parser.evaluate(alias)

    def _target(self, target):
        if not self._specified:
            parser = Parser(self.vars, self.base_dir)
            target = parser.evaluate(target)
        if not self.phony and not self.alias:
            target = self.base_dir.joinpath(target).as_posix()
        if self.regex and not self._specified:
            target = re.compile(target)
        return target


class Variables(dict):
    def __init__(self, base_dir, **kwargs):
        super().__init__(**kwargs)
        self.base_dir = base_dir

    def add_batch(self, batch):
        new_vars = self.__class__(self.base_dir, **self)
        for var_block in batch:
            parser = Parser(new_vars, self.base_dir)
            for key, value in var_block.items():
                key = parser.evaluate(key)
                key, options = extract_options(key)
                if "weak" in options:
                    continue
                value = parser.evaluate(value)
                new_vars[key] = value
        return new_vars


class Parser:
    def __init__(self, variables, base_dir):
        self.vars = variables
        self.base_dir = base_dir

    @staticmethod
    def _stringify(value):
        if isinstance(value, list):
            return " ".join(map(str, value))
        return str(value)

    def expand_function(self, name, args):
        args = shlex.split(args)
        for i, arg in enumerate(args):
            args[i] = self.evaluate(arg)
        function = functions.get(name)(self.base_dir)
        return function(*args)

    def repl(self, matchobj):
        dollars = matchobj.group("dollars")
        variable = matchobj.group("variable")
        key = matchobj.group("key")
        if len(dollars) % 2:
            value = self.vars[variable]
            if key is None:
                return self._stringify(value)
            if isinstance(value, list):
                key = int(key)
            return self._stringify(value[key])
        return f"{'$'*(len(dollars)//2)}{{{variable}}}"

    def substitute(self, string):
        function = re.fullmatch(FUNCTION, string)
        if function is not None:
            return self.expand_function(**function.groupdict())

        if (
            string.startswith("$")
            and not string.startswith("$$")
            and re.fullmatch(VAR, string)
        ):
            match = re.fullmatch(VAR, string)
            if match.group("sep") is None:
                return self.vars[match.group("variable")]
        return re.sub(VAR, self.repl, string)

    def evaluate(self, obj):
        if isinstance(obj, str):
            return self.substitute(obj)
        if isinstance(obj, list):
            out = []
            for string in obj:
                evaluated = self.evaluate(string)
                if isinstance(evaluated, list):
                    out.extend(evaluated)
                else:
                    out.append(evaluated)
            return out
        if isinstance(obj, dict):
            return {
                self.evaluate(key): self.evaluate(value) for key, value in obj.items()
            }
        raise TypeError(f"{obj.__class__.__name__} is not supported for evaluation")


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


def timestamp_to_dt(timestamp):
    if math.isinf(timestamp):
        return datetime.datetime.max
    return datetime.datetime.utcfromtimestamp(timestamp)
