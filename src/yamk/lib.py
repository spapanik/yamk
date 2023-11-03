from __future__ import annotations

import math
import os
import re
import shlex
import warnings
from dataclasses import dataclass
from datetime import datetime, timezone
from math import ceil, floor
from pathlib import Path
from typing import Any, Iterator, Literal, Match, cast

from yamk.functions import functions

VAR = re.compile(
    r"(?P<dollars>\$+){(?P<variable>[a-zA-Z0-9_.]+)(?P<sep>:)?(?P<key>[a-zA-Z0-9_.]+)?}"
)
OPTIONS = re.compile(r"\[(?P<options>.*?)\](?P<string>.*)")
FUNCTION = re.compile(r"\$\(\((?P<name>\w+) *(?P<args>.*)\)\)")
SUPPORTED_FILE_EXTENSIONS = {
    ".toml": "toml",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".json": "json",
}


class ANSIEscape:
    __slots__: list[str] = []

    ENDC = "\033[0m"
    BOLD = "\033[1m"
    FAIL = "\033[31m"
    OKGREEN = "\033[32m"
    OKBLUE = "\033[34m"
    WARNING = "\033[33m"


class Recipe:
    def __init__(
        self,
        target: str,
        raw_recipe: dict[str, Any],
        base_dir: Path,
        file_vars: dict[str, Any],
        arg_vars: dict[str, Any],
        extra: list[str],
        original_regex: str | None = None,
        *,
        new_order: bool,
        specified: bool = False,
    ):
        self.new_order = new_order
        self.extra = extra
        self._specified = specified
        self._raw_recipe = raw_recipe
        self.base_dir = base_dir
        self.phony = raw_recipe.get("phony", False)
        self.requires = raw_recipe.get("requires", [])
        self.commands = raw_recipe.get("commands", [])
        self.echo = raw_recipe.get("echo", False)
        self.regex = raw_recipe.get("regex", False)
        self.allow_failures = raw_recipe.get("allow_failures", False)
        self.exists_only = raw_recipe.get("exists_only", False)
        self.keep_ts = raw_recipe.get("keep_ts", False)
        self.existence_command = raw_recipe.get("existence_command", "")
        self.recursive = raw_recipe.get("recursive", False)
        self.update = raw_recipe.get("update", False)
        temp_vars = {
            "global": file_vars,
            "env": dict(**os.environ),
            "arg": arg_vars,
        }
        self.alias = self._alias(raw_recipe.get("alias", False), temp_vars)
        self.target = self._target(target, temp_vars)
        temp_vars["local"] = raw_recipe.get("vars", {})
        if self._specified:
            temp_vars["implicit"] = {
                ".target": self.target,
                ".requirements": self.requires,
                ".extra": self.extra,
            }
            if self.regex:
                if original_regex is None:
                    raise RuntimeError(
                        "original_regex must be specified when target is specific"
                    )
                match_obj = re.fullmatch(original_regex, self.target)
                if match_obj is None:
                    raise RuntimeError(
                        f"original_regex {original_regex} does not match {self.target}"
                    )
                temp_vars["regex"] = match_obj.groupdict()
            else:
                temp_vars["regex"] = {}
        else:
            temp_vars["regex"] = {}
            temp_vars["implicit"] = {}
        self.vars = temp_vars
        if self._specified:
            self._re_evaluate()

    def __str__(self) -> str:
        if self._specified:
            return f"Specified recipe for {self.target}"
        return f"Generic recipe for {self.target}"

    def for_target(self, target: str, extra: list[str]) -> Recipe:
        if self._specified:
            return self
        return self.__class__(
            target,
            self._raw_recipe,
            self.base_dir,
            self.vars["global"],
            self.vars["arg"],
            extra,
            new_order=self.new_order,
            original_regex=self.target,
            specified=True,
        )

    def _evaluate(
        self, obj: Any, variables: dict[str, dict[str, Any]] | None = None
    ) -> Any:
        if variables is None:
            variables = self.vars
        flat_vars = flatten_vars(variables, self.base_dir, new_order=self.new_order)
        parser = Parser(flat_vars, self.base_dir)
        return parser.evaluate(obj)

    def _re_evaluate(self) -> None:
        self.requires = self._evaluate(self.requires)
        self.commands = self._evaluate(self.commands)
        self.existence_command = self._evaluate(self.existence_command)

    def _alias(self, alias: str | Literal[False], variables: dict[str, Any]) -> Any:
        if alias is False:
            return alias
        return self._evaluate(alias, variables)

    def _target(self, target: str, variables: dict[str, Any]) -> Any:
        if not self._specified:
            target = self._evaluate(target, variables)
        if not self.phony and not self.alias:
            target = self.base_dir.joinpath(target).as_posix()
        if self.regex and not self._specified:
            return re.compile(target)
        return target


class Parser:
    def __init__(self, variables: dict[str, Any], base_dir: Path):
        self.vars = variables
        self.base_dir = base_dir

    @staticmethod
    def _stringify(value: Any) -> str:
        if isinstance(value, list):
            return " ".join(map(str, value))
        return str(value)

    def expand_function(self, name: str, args: str) -> Any:
        split_args = shlex.split(args)
        for i, arg in enumerate(split_args):
            split_args[i] = self.evaluate(arg)
        function = functions[name](self.base_dir)
        return function(*split_args)

    def repl(self, match_obj: re.Match[str]) -> str:
        dollars = match_obj.group("dollars")
        variable = match_obj.group("variable")
        key = match_obj.group("key")
        if len(dollars) % 2:
            value = self.vars.get(variable, "")
            if key is None:
                return self._stringify(value)
            if isinstance(value, list):
                key = int(key)
            return self._stringify(value[key])
        return f"{'$'*(len(dollars)//2)}{{{variable}}}"

    def substitute(self, string: str) -> Any:
        function = re.fullmatch(FUNCTION, string)
        if function is not None:
            return self.expand_function(**function.groupdict())

        if (
            string.startswith("$")
            and not string.startswith("$$")
            and re.fullmatch(VAR, string)
        ):
            match = cast(Match[str], re.fullmatch(VAR, string))
            if match["sep"] is None:
                return self.vars[match["variable"]]
        return re.sub(VAR, self.repl, string)

    def evaluate(self, obj: str | list[Any] | dict[str, Any]) -> Any:
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
    recipe: Recipe | None
    target: str
    timestamp: float
    should_build: bool
    required_by: set[Node]
    requires: list[Node]

    def __init__(self, recipe: Recipe | None = None, *, target: str | None = None):
        self.recipe = recipe
        self.target = target if self.recipe is None else self.recipe.target
        self.requires = []
        self.required_by = set()

    def __str__(self) -> str:
        return self.target

    def __repr__(self) -> str:
        return f"Node <{self}>"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.target == other.target

    def __hash__(self) -> int:
        return hash(self.target)

    def add_requirement(self, other: Node) -> None:
        if other in self.requires:
            warnings.warn(
                f"`{other}` is included twice in `{self}` requirements, "
                "only the first will be considered",
                RuntimeWarning,
                stacklevel=3,
            )
            return
        self.requires.append(other)
        other.required_by.add(self)


class DAG:
    ordered: list[Node]

    def __init__(self, root: Node):
        self.root = root
        self._mapping = {root.target: root}

    def __getitem__(self, item: str) -> Node:
        return self._mapping[item]

    def __contains__(self, item: str) -> bool:
        return item in self._mapping

    def __iter__(self) -> Iterator[Node]:
        if hasattr(self, "ordered"):
            return iter(self.ordered)
        return iter(self._mapping.values())

    def sort(self) -> None:
        try:
            self.c3_sort()
        except ValueError:
            self.topological_sort()

    def c3_sort(self) -> None:
        self.ordered = self._node_s3_sort(self.root)
        self.ordered.reverse()

    def topological_sort(self) -> None:
        self.ordered = []
        unordered_nodes = self._mapping.copy()
        while unordered_nodes:
            for target, node in unordered_nodes.items():
                if all((parent in self.ordered) for parent in node.requires):
                    del unordered_nodes[target]
                    self.ordered.append(node)
                    break
            else:
                raise ValueError("Cyclic dependencies detected. Cowardly aborting...")
        warnings.warn(
            "The requirements order didn't allow the deterministic order; "
            "fell back to old-style dependency resolution",
            RuntimeWarning,
            stacklevel=3,
        )

    def add_node(self, node: Node) -> None:
        self._mapping[node.target] = node

    def _node_s3_sort(self, node: Node) -> list[Node]:
        out = [node]
        if requirements := node.requires:
            try:
                out.extend(
                    self._merge(
                        *[
                            self._node_s3_sort(requirements)
                            for requirements in requirements
                        ],
                        requirements,
                    )
                )
            except RecursionError as exc:
                raise ValueError("Cannot compute c3_sort") from exc
        return out

    def _merge(self, *node_lists: list[Node]) -> list[Node]:
        result: list[Node] = []
        unmerged = [*node_lists]

        while True:
            if not unmerged:
                return result

            heads = [node_list[0] for node_list in unmerged if node_list]
            tails = [node_list[1:] for node_list in unmerged if len(node_list) > 1]
            for head in heads:
                if head and all(head not in tail for tail in tails):
                    result.append(head)
                    unmerged = self._clean_head(unmerged, head)
                    break
            else:
                raise ValueError("Cannot compute c3_sort")

    @staticmethod
    def _clean_head(unmerged: list[list[Node]], head: Node) -> list[list[Node]]:
        new_list = []
        for original_node_list in unmerged:
            if head == original_node_list[0]:
                if node_list := original_node_list[1:]:
                    new_list.append(node_list)
            else:
                new_list.append(original_node_list)
        return new_list


@dataclass(frozen=True)
class CommandReport:
    command: str
    retries: int
    timing_ns: int
    success: bool

    def _formatted_timing(self) -> str:
        if self.timing_ns < 1000:
            return f"{self.timing_ns} ns"
        timing: float = self.timing_ns
        timing /= 1000
        if timing < 1000:
            return f"{timing:.1f} µs"
        timing /= 1000
        if timing < 1000:
            return f"{timing:.1f} ms"
        timing /= 1000
        return f"{timing:.2f} s"

    def print(self, cols: int) -> None:  # noqa: A003
        if not self.success:
            indicator = "🔴"
            timing_colour = ANSIEscape.FAIL
        elif self.retries:
            indicator = "🟠"
            timing_colour = ANSIEscape.WARNING
        else:
            indicator = "🟢"
            timing_colour = ANSIEscape.OKGREEN
        timing = self._formatted_timing()
        padding = " " * (cols - len(self.command) - len(timing) - 7)
        print(
            indicator,
            f"`{self.command}`",
            padding,
            f"{timing_colour}{timing}{ANSIEscape.ENDC}",
        )


def flatten_vars(
    variables: dict[str, dict[str, Any]], base_dir: Path, *, new_order: bool
) -> dict[str, Any]:
    if new_order:
        order = [
            "env",
            "arg",
            "global",
            "local",
            "global",
            "implicit",
            "regex",
            "local",
            "env",
            "arg",
        ]
    else:
        order = ["env", "global", "regex", "local", "arg", "implicit"]
    output: dict[str, Any] = {}
    strong_keys: set[str] = set()
    for var_type in order:
        var_block = variables.get(var_type, {})
        parser = Parser(output, base_dir)
        for raw_key, raw_value in var_block.items():
            key = parser.evaluate(raw_key)
            key, options = extract_options(key)
            if key in strong_keys:
                continue
            if "weak" in options and key in output:
                continue
            if "strong" in options:
                strong_keys.add(key)
            value = parser.evaluate(raw_value)
            output[key] = value
    return output


def extract_options(string: str) -> tuple[str, set[str]]:
    match = re.fullmatch(OPTIONS, string)
    if match is None:
        return string.strip(), set()

    options = match["options"]
    string = match["string"]
    return string, {s.strip() for s in options.split(",")}


def human_readable_timestamp(timestamp: float) -> str:
    if math.isinf(timestamp):
        return "end of time"
    return str(datetime.fromtimestamp(timestamp, tz=timezone.utc))


def print_reports(reports: list[CommandReport]) -> None:
    cols = os.get_terminal_size().columns
    report_title = " Yam Report "
    padding = "="
    half = (cols - len(report_title)) / 2
    print(
        f"{ANSIEscape.BOLD}{padding * ceil(half)}{report_title}{padding * floor(half)}{ANSIEscape.ENDC}"
    )
    for report in reports:
        report.print(cols)


class RemovedIn60Warning(FutureWarning):
    pass
