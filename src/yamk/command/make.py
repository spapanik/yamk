from __future__ import annotations

import itertools
import pathlib
import re
import subprocess
import sys
from time import sleep
from typing import TYPE_CHECKING, Any, cast

from dj_settings import ConfigParser
from pyutilkit.term import SGRCodes, SGRString
from pyutilkit.timing import Stopwatch

from yamk.__version__ import __version__
from yamk.lib.utils import (
    DAG,
    SUPPORTED_FILE_EXTENSIONS,
    CommandReport,
    Node,
    Recipe,
    Version,
    extract_options,
    human_readable_timestamp,
    print_reports,
)

if TYPE_CHECKING:
    import argparse
    from collections.abc import Iterator

    from yamk.lib.types import ExistenceCheck


class MakeCommand:
    def __init__(self, args: argparse.Namespace) -> None:
        self.verbosity = args.verbosity
        self.regex_recipes: dict[str, Recipe] = {}
        self.static_recipes: dict[str, Recipe] = {}
        self.aliases: dict[str, str] = {}
        self.target = args.target
        self.bare = args.bare
        self.force_make = args.force
        self.extra = args.extra
        self.retries = args.retries
        self.dry_run = args.dry_run
        self.echo_override = args.echo
        cookbook = self.find_cookbook(args)
        self.base_dir = cookbook.parent
        self.phony_dir = self.base_dir.joinpath(".yamk")
        self.arg_vars = dict(var.split("=", maxsplit=1) for var in args.variables)
        parsed_cookbook = ConfigParser([cookbook], force_type=args.cookbook_type).data
        self.globals = parsed_cookbook.pop("$globals", {})
        self.version = self._get_version()
        if self.version > Version.from_string(__version__):
            msg = f"This cookbook requires an yamk >= v{self.version}"
            raise RuntimeError(msg)
        self.up_to_date = args.assume
        self._parse_recipes(parsed_cookbook)
        self.subprocess_kwargs = {
            "shell": True,
            "cwd": self.base_dir,
            "executable": self.globals.get("shell") or args.shell,
        }
        self.print_timing_report = args.time
        self.reports: list[CommandReport] = []

    @staticmethod
    def find_cookbook(args: argparse.Namespace) -> pathlib.Path:
        absolute_path = pathlib.Path(args.directory).absolute()
        if args.cookbook:
            return absolute_path.joinpath(args.cookbook)

        cookbooks = (
            absolute_path.joinpath("cookbook").with_suffix(suffix)
            for suffix in SUPPORTED_FILE_EXTENSIONS
        )
        for cookbook in cookbooks:
            if cookbook.exists():
                return cookbook
        msg = f"No candidate cookbook found in {args.directory}"
        raise FileNotFoundError(msg)

    def make(self) -> None:
        dag = self._preprocess_target()
        for node in filter(lambda x: x.should_build, dag):
            self._make_target(node)
        if self.print_timing_report:
            print_reports(self.reports)

    def _run_command(self, command: str) -> int:
        status = 0
        if self.dry_run:
            return status

        a, b = 1, 1
        stopwatch = Stopwatch()
        for i in range(self.retries + 1):
            with stopwatch:
                result = subprocess.run(  # noqa: PLW1510, S603
                    command, **self.subprocess_kwargs
                )
            status = result.returncode
            if status == 0:
                break

            if i != self.retries:
                a, b = b, a + b
                print(f"{command} failed. Retrying in {a}s...")
                sleep(a)

        report = CommandReport(
            command=command, timing=stopwatch.elapsed, retries=i, success=False
        )
        self.reports.append(report)
        return status

    def _check_command(self, check: ExistenceCheck) -> bool:
        if self.dry_run:
            return True

        command = check["command"]
        result = subprocess.run(  # noqa: PLW1510, S603
            command, capture_output=True, text=True, **self.subprocess_kwargs
        )
        if check["stdout"] is not None and result.stdout != check["stdout"]:
            return False
        if check["stderr"] is not None and result.stderr != check["stdout"]:
            return False
        return result.returncode == check["returncode"]

    def _parse_recipes(self, parsed_cookbook: dict[str, dict[str, Any]]) -> None:
        for target, raw_recipe in parsed_cookbook.items():
            recipe = Recipe(
                target,
                raw_recipe,
                self.base_dir,
                self.globals.get("vars", {}),
                self.arg_vars,
                extra=[],
            )

            if recipe.alias:
                self.aliases[recipe.target] = recipe.alias
            elif recipe.regex:
                self.regex_recipes[recipe.target] = recipe
            else:
                self.static_recipes[recipe.target] = recipe

    def _preprocess_target(self) -> DAG:
        recipe = self._extract_recipe(self.target, use_extra=True)
        if recipe is None:
            msg = f"No recipe to build {self.target}"
            raise ValueError(msg)

        root = Node(recipe)
        unprocessed = {root.target: root}
        dag = DAG(root)
        while unprocessed and not self.bare:
            target, target_node = unprocessed.popitem()
            dag.add_node(target_node)
            target_recipe = cast(Recipe, target_node.recipe)
            target_recipe.requires.reverse()
            for index, raw_requirement in enumerate(target_recipe.requires):
                recipe = self._extract_recipe(raw_requirement)
                if recipe is None:
                    requirement_path = self._file_path(raw_requirement)
                    requirement = requirement_path.as_posix()
                    if not requirement_path.exists():
                        msg = f"No recipe to build {requirement}"
                        raise ValueError(msg)
                else:
                    requirement = recipe.target
                target_recipe.requires[index] = requirement

                if requirement in dag:
                    node = dag[requirement]
                elif requirement in unprocessed:
                    node = unprocessed[requirement]
                elif recipe is None:
                    node = Node(target=requirement)
                    dag.add_node(node)
                else:
                    node = Node(recipe)
                    unprocessed[requirement] = node
                target_node.add_requirement(node)

        dag.sort()
        self._mark_unchanged(dag)
        if self.verbosity > 3:  # noqa: PLR2004
            print("=== all targets ===")
            for node in dag:
                print(f"- {node.target}:")
                print(f"    timestamp: {human_readable_timestamp(node.timestamp)}")
                print(f"    should_build: {node.should_build}")
                print(f"    requires: {node.requires}")
                print(f"    required_by: {node.required_by}")
        return dag

    def _update_ts(self, node: Node) -> None:
        path = self._path(node)
        recipe = node.recipe
        if recipe is None:
            msg = f"No recipe to build {node.target}"
            raise ValueError(msg)
        if recipe.phony and recipe.keep_ts:
            self.phony_dir.mkdir(exist_ok=True)
            path.touch()
        if not recipe.phony and recipe.update:
            pathlib.Path(recipe.target).touch()

    def _make_target(self, node: Node) -> None:
        recipe = node.recipe
        if recipe is None:
            msg = f"No recipe to build {node.target}"
            raise ValueError(msg)

        if self.verbosity > 1:
            print(f"=== target: {recipe.target} ===")

        n = len(recipe.commands)
        for i, raw_command in enumerate(recipe.commands):
            command, options = extract_options(raw_command)
            should_echo = any(self._print_reasons(recipe, options))
            if should_echo:
                self._print_command(command)
            return_code = self._run_command(command)
            if should_echo:
                self._print_result(command, return_code)
            if (
                return_code
                and not recipe.allow_failures
                and "allow_failures" not in options
            ):
                if self.print_timing_report:
                    print_reports(self.reports)
                sys.exit(return_code)
            if i != n - 1:
                print()
        self._update_ts(node)

    def _extract_recipe(self, target: str, *, use_extra: bool = False) -> Recipe | None:
        if target in self.aliases:
            target = self.aliases[target]

        absolute_path_target = self.base_dir.joinpath(target).as_posix()
        if target in self.static_recipes:
            recipe = self.static_recipes[target]
        elif absolute_path_target in self.static_recipes:
            recipe = self.static_recipes[absolute_path_target]
        else:
            for regex, recipe in self.regex_recipes.items():  # noqa: B007
                if re.fullmatch(regex, target) or re.fullmatch(
                    regex, absolute_path_target
                ):
                    break
            else:
                return None
        extra = self.extra if use_extra else []
        return recipe.for_target(target, extra)

    def _mark_unchanged(self, dag: DAG) -> None:
        for node in dag:
            node.should_build, node.timestamp = self._should_build(node)

    def _phony_path(self, target: str) -> pathlib.Path:
        encoded_target = target.replace(".", ".46").replace("/", ".47")
        return self.phony_dir.joinpath(encoded_target)

    def _file_path(self, target: str) -> pathlib.Path:
        return self.base_dir.joinpath(target)

    def _path(self, node: Node) -> pathlib.Path:
        recipe = node.recipe
        if recipe is None or not recipe.phony:
            return self._file_path(node.target)

        return self._phony_path(node.target)

    def _path_exists(self, node: Node) -> bool:
        recipe = node.recipe
        path = self._path(node)
        if recipe is not None and recipe.existence_check:
            if not recipe.phony:
                msg = "Existence commands need to be phony"
                raise ValueError(msg)
            if not recipe.exists_only:
                msg = "Existence commands need exists_only"
                raise ValueError(msg)
            return self._check_command(recipe.existence_check)

        return path.exists()

    def _should_build(self, node: Node) -> tuple[bool, float]:
        recipe = node.recipe
        path = self._path(node)
        if recipe is None:
            return False, path.stat().st_mtime
        if self.force_make:
            return True, float("inf")
        if recipe.phony and recipe.target in self.up_to_date:
            return False, float("inf")
        if not self._path_exists(node):
            return True, float("inf")
        if recipe.existence_check:
            self._update_ts(node)
            return False, float("inf")

        if not recipe.phony and recipe.recursive:
            mtime = max(
                p.stat().st_mtime for p in itertools.chain([path], path.rglob("*"))
            )
        else:
            mtime = path.stat().st_mtime

        if recipe.exists_only:
            return False, mtime

        if not node.requires:
            msg = (
                "This target already exists and has no requirements. "
                "Consider marking it with exists_only"
            )
            raise ValueError(msg)

        if any(child.should_build for child in node.requires):
            return True, mtime

        req_ts = max(child.timestamp for child in node.requires)
        return req_ts > mtime, mtime

    def _print_reasons(self, recipe: Recipe, options: set[str]) -> Iterator[bool]:
        yield "echo" in options
        yield recipe.echo
        yield self.verbosity > 2  # noqa: PLR2004
        yield self.echo_override

    def _print_command(self, command: str) -> None:
        bold_command = SGRString(command, params=[SGRCodes.BOLD])
        print(f"🔧 Running `{bold_command}`")

    def _print_result(self, command: str, return_code: int) -> None:
        bold_command = SGRString(command, params=[SGRCodes.BOLD])
        if return_code:
            prefix = "❌"
            suffix = f"failed with exit code {return_code}"
        else:
            prefix = "✅"
            suffix = "run successfully!"
        print(f"{prefix} `{bold_command}` {suffix}")

    def _get_version(self) -> Version:
        return Version.from_string(self.globals["version"])
