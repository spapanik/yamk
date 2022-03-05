import datetime
import json
import math
import os
import re
import shlex
from pathlib import Path
from typing import Any, Dict, cast

import tomli
import yaml

from yamk.functions import functions

VAR = re.compile(
    r"(?P<dollars>\$+){(?P<variable>[a-zA-Z0-9_.]+)(?P<sep>:)?(?P<key>[a-zA-Z0-9_.]+)?}"
)
OPTIONS = re.compile(r"\[(?P<options>.*?)\](?P<string>.*)")
FUNCTION = re.compile(r"\$\(\((?P<name>\w+) *(?P<args>.*)\)\)")


class RemovedInYam3(Warning):
    pass


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
        self.exists_only = raw_recipe.get("exists_only", False)
        self.keep_ts = raw_recipe.get("keep_ts", False)
        self.existence_command = raw_recipe.get("existence_command", "")
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

    def _evaluate(self, obj):
        parser = Parser(self.vars, self.base_dir)
        return parser.evaluate(obj)

    def _update_variables(self, groups):
        extra_vars = [groups, *self.local_vars, {".target": self.target}]
        self.vars = self.vars.add_batch(extra_vars)

    def _update_requirements(self):
        self.requires = self._evaluate(self.requires)

    def _update_commands(self):
        extra_vars = [{".requirements": self.requires}]
        self.vars = self.vars.add_batch(extra_vars)
        self.commands = self._evaluate(self.commands)
        self.existence_command = self._evaluate(self.existence_command)

    def _alias(self, alias):
        if alias is False:
            return alias
        return self._evaluate(alias)

    def _target(self, target):
        if not self._specified:
            target = self._evaluate(target)
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
                if "weak" in options and key in self:
                    continue
                value = parser.evaluate(value)
                new_vars[key] = value
        return new_vars

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        if self.base_dir != other.base_dir:
            return False

        return super().__eq__(other)


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
            value = self.vars.get(variable, "")
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


class Node:
    recipe: Recipe
    target: str
    timestamp: float
    should_build: bool
    required_by: set
    requires: set

    def __init__(self, recipe=None, *, target=None):
        self.recipe = recipe
        self.target = target if self.recipe is None else self.recipe.target
        self.requires = set()
        self.required_by = set()

    def __str__(self):
        return self.target

    def __repr__(self):
        return f"Node <{self}>"

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.target == other.target

    def __hash__(self):
        return hash(self.target)

    def add_requirement(self, other):
        self.requires.add(other)
        other.required_by.add(self)


class DAG:
    ordered: list

    def __init__(self, root):
        self.root = root
        self.nodes = {root}
        self._mapping = {root.target: root}

    def __getitem__(self, item):
        return self._mapping[item]

    def __contains__(self, item):
        return item in self._mapping

    def __iter__(self):
        if hasattr(self, "ordered"):
            return iter(self.ordered)
        return iter(self._mapping.values())

    def sort(self):
        self.ordered = []
        unordered_nodes = self.nodes.copy()
        while unordered_nodes:
            for node in unordered_nodes:
                if all((parent in self.ordered) for parent in node.requires):
                    unordered_nodes.remove(node)
                    break
            else:
                raise ValueError("Cyclic dependencies detected. Cowardly aborting...")
            self.ordered.append(node)

    def add_node(self, node):
        self.nodes.add(node)
        self._mapping[node.target] = node


class CookbookParser:
    __slots__ = ["cookbook"]

    def __init__(self, cookbook: Path):
        self.cookbook = cookbook

    def load(self, path: Path) -> dict:
        suffix = self.cookbook.suffix
        if suffix == ".toml":
            with open(path, "rb") as binary_file:
                return tomli.load(binary_file)

        if suffix in (".yaml", ".yml"):
            with open(path) as file:
                return cast(Dict[str, Any], yaml.safe_load(file))

        if suffix == ".json":
            with open(path) as file:
                return cast(Dict[str, Any], json.load(file))

        raise ValueError(f"{suffix} is not a supported extension (yet)")

    def parse(self) -> dict:
        parsed_cookbook = self.load(self.cookbook)
        cookbook_dir = self.cookbook.with_suffix(self.cookbook.suffix + ".d")
        for path in sorted(cookbook_dir.glob(f"*{self.cookbook.suffix}")):
            parsed_cookbook = deep_merge(parsed_cookbook, self.load(path))
        return parsed_cookbook


def deep_merge(dict_1, dict_2):
    output = dict_1.copy()
    for key, value in dict_2.items():
        if isinstance(dict_1.get(key), dict) and isinstance(value, dict):
            output[key] = deep_merge(dict_1[key], value)
        else:
            output[key] = value
    return output


def extract_options(string):
    match = re.fullmatch(OPTIONS, string)
    if match is None:
        return string.strip(), set()

    options = match.group("options")
    string = match.group("string")
    return string, set(map(lambda s: s.strip(), options.split(",")))


def timestamp_to_dt(timestamp):
    if math.isinf(timestamp):
        return datetime.datetime.max
    return datetime.datetime.utcfromtimestamp(timestamp)


def change_default(args):
    old_cookbook = Path(args.directory).joinpath("make.toml").absolute()
    new_cookbook = Path(args.directory).joinpath("cookbook.yml").absolute()
    if not os.access(old_cookbook, os.R_OK):
        raise PermissionError(f"{old_cookbook} is not readable")
    if not os.access(new_cookbook.parent, os.W_OK, dir_fd=True):
        raise PermissionError(f"{new_cookbook} is not writeable")
    if new_cookbook.exists():
        raise PermissionError(f"{new_cookbook} already exists")
    with open(old_cookbook, "rb") as old_file:
        data = tomli.load(old_file)
    with open(new_cookbook, "w") as new_file:
        yaml.dump(data, new_file, explicit_start=True)
    print(f"{new_cookbook} is ready.")
    print("Comments are not transferred, so you need to manually add them back.")
