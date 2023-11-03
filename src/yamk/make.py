from __future__ import annotations

import argparse
import itertools
import pathlib
import re
import subprocess
import sys
import warnings
from time import perf_counter_ns, sleep
from typing import Any, cast

from dj_settings import SettingsParser
from packaging.version import Version

from yamk import __version__, lib


class MakeCommand:
    def __init__(self, args: argparse.Namespace):
        self.verbosity = args.verbose
        if self.verbosity:
            if self.verbosity > 1:
                print(args)
            sys.tracebacklimit = 9999
        self.regex_recipes: dict[str, lib.Recipe] = {}
        self.static_recipes: dict[str, lib.Recipe] = {}
        self.aliases: dict[str, str] = {}
        self.target = args.target
        self.bare = args.bare
        self.force_make = args.force
        self.extra = args.extra
        self.retries = args.retries
        self.dry_run = args.dry_run
        cookbook = self.find_cookbook(args)
        self.base_dir = cookbook.parent
        self.phony_dir = self.base_dir.joinpath(".yamk")
        self.arg_vars = dict(var.split("=", maxsplit=1) for var in args.variables)
        parsed_cookbook = SettingsParser(cookbook, force_type=args.cookbook_type).data
        self.globals = parsed_cookbook.pop("$globals", {})
        self.version = self._get_version()
        if self.version > __version__:
            raise RuntimeError(f"This cookbook requires an yamk >= v{self.version}")
        self.up_to_date = args.assume
        self._parse_recipes(parsed_cookbook)
        self.subprocess_kwargs = {
            "shell": True,
            "cwd": self.base_dir,
            "executable": self.globals.get("shell") or args.shell,
        }
        self.print_timing_report = args.time
        self.reports: list[lib.CommandReport] = []

    @staticmethod
    def find_cookbook(args: argparse.Namespace) -> pathlib.Path:
        absolute_path = pathlib.Path(args.directory).absolute()
        if args.cookbook:
            return absolute_path.joinpath(args.cookbook)

        cookbooks = (
            absolute_path.joinpath("cookbook").with_suffix(suffix)
            for suffix in lib.SUPPORTED_FILE_EXTENSIONS
        )
        for cookbook in cookbooks:
            if cookbook.exists():
                return cookbook
        raise FileNotFoundError(f"No candidate cookbook found in {args.directory}")

    def make(self) -> None:
        dag = self._preprocess_target()
        for node in filter(lambda x: x.should_build, dag):
            self._make_target(cast(lib.Recipe, node.recipe))
        if self.print_timing_report:
            lib.print_reports(self.reports)

    def _run_command(self, command: str) -> int:
        status = 0
        if self.dry_run:
            print(command)
            return status

        a, b = 1, 1
        total = 0
        for i in range(self.retries + 1):
            start = perf_counter_ns()
            result = subprocess.run(  # noqa: PLW1510
                command, **self.subprocess_kwargs  # noqa: S603
            )
            end = perf_counter_ns()
            total += end - start
            status = result.returncode
            if status == 0:
                report = lib.CommandReport(
                    command=command, timing_ns=total, retries=i, success=True
                )
                self.reports.append(report)
                return status

            if i != self.retries:
                a, b = b, a + b
                print(f"{command} failed. Retrying in {a}s...")
                sleep(a)

        report = lib.CommandReport(
            command=command, timing_ns=total, retries=i, success=False
        )
        self.reports.append(report)
        return status

    def _parse_recipes(self, parsed_cookbook: dict[str, dict[str, Any]]) -> None:
        for target, raw_recipe in parsed_cookbook.items():
            recipe = lib.Recipe(
                target,
                raw_recipe,
                self.base_dir,
                self.globals.get("vars", {}),
                self.arg_vars,
                extra=[],
                new_order=self._is_new_order,
            )

            if recipe.alias:
                self.aliases[recipe.target] = recipe.alias
            elif recipe.regex:
                self.regex_recipes[recipe.target] = recipe
            else:
                self.static_recipes[recipe.target] = recipe

    def _preprocess_target(self) -> lib.DAG:
        recipe = self._extract_recipe(self.target, use_extra=True)
        if recipe is None:
            raise ValueError(f"No recipe to build {self.target}")

        root = lib.Node(recipe)
        unprocessed = {root.target: root}
        dag = lib.DAG(root)
        while unprocessed and not self.bare:
            target, target_node = unprocessed.popitem()
            dag.add_node(target_node)
            target_recipe = cast(lib.Recipe, target_node.recipe)
            target_recipe.requires.reverse()
            for index, raw_requirement in enumerate(target_recipe.requires):
                recipe = self._extract_recipe(raw_requirement)
                if recipe is None:
                    requirement_path = self._file_path(raw_requirement)
                    requirement = requirement_path.as_posix()
                    if not requirement_path.exists():
                        raise ValueError(f"No recipe to build {requirement}")
                else:
                    requirement = recipe.target
                target_recipe.requires[index] = requirement

                if requirement in dag:
                    node = dag[requirement]
                elif requirement in unprocessed:
                    node = unprocessed[requirement]
                elif recipe is None:
                    node = lib.Node(target=requirement)
                    dag.add_node(node)
                else:
                    node = lib.Node(recipe)
                    unprocessed[requirement] = node
                target_node.add_requirement(node)

        dag.sort()
        self._mark_unchanged(dag)
        if self.verbosity > 3:
            print("=== all targets ===")
            for node in dag:
                print(f"- {node.target}:")
                print(f"    timestamp: {lib.human_readable_timestamp(node.timestamp)}")
                print(f"    should_build: {node.should_build}")
                print(f"    requires: {node.requires}")
                print(f"    required_by: {node.required_by}")
        return dag

    def _make_target(self, recipe: lib.Recipe) -> None:
        if self.verbosity > 1:
            print(f"=== target: {recipe.target} ===")

        for raw_command in recipe.commands:
            command, options = lib.extract_options(raw_command)
            if recipe.echo or "echo" in options or self.verbosity > 2:
                print(command)
            return_code = self._run_command(command)
            if (
                return_code
                and not recipe.allow_failures
                and "allow_failures" not in options
            ):
                if self.print_timing_report:
                    lib.print_reports(self.reports)
                sys.exit(return_code)
        if recipe.phony and recipe.keep_ts:
            path = self._phony_path(recipe.target)
            self.phony_dir.mkdir(exist_ok=True)
            path.touch()
        if recipe.update and not recipe.phony:
            pathlib.Path(recipe.target).touch()

    def _extract_recipe(
        self, target: str, *, use_extra: bool = False
    ) -> lib.Recipe | None:
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

    def _mark_unchanged(self, dag: lib.DAG) -> None:
        for node in dag:
            node.timestamp = self._infer_timestamp(node)
            node.should_build = self._should_build(node)

    def _phony_path(self, target: str) -> pathlib.Path:
        encoded_target = target.replace(".", ".46").replace("/", ".47")
        return self.phony_dir.joinpath(encoded_target)

    def _file_path(self, target: str) -> pathlib.Path:
        return self.base_dir.joinpath(target)

    def _path(self, node: lib.Node) -> pathlib.Path:
        recipe = node.recipe
        if recipe is None or not recipe.phony:
            return self._file_path(node.target)

        return self._phony_path(node.target)

    def _path_exists(self, node: lib.Node) -> bool:
        recipe = node.recipe
        path = self._path(node)
        if recipe is not None and recipe.phony and recipe.existence_command:
            return not self._run_command(recipe.existence_command)

        return path.exists()

    def _should_build(self, node: lib.Node) -> bool:
        recipe = node.recipe
        if recipe is None:
            return False
        if self.force_make:
            return True
        if recipe.phony and recipe.target in self.up_to_date:
            return False
        if not self._path_exists(node):
            return True
        if recipe.exists_only:
            return False

        if not node.requires:
            raise ValueError(
                "This target already exists and has no requirements. "
                "Consider marking it with exists_only"
            )

        if any(child.should_build for child in node.requires):
            return True

        ts = node.timestamp
        req_ts = max(child.timestamp for child in node.requires)
        return req_ts > ts

    def _infer_timestamp(self, node: lib.Node) -> float:
        recipe = node.recipe
        path = self._path(node)
        if recipe is None:
            return path.stat().st_mtime

        if recipe.phony and recipe.target in self.up_to_date:
            return float("inf")

        if not self._path_exists(node):
            return float("inf")

        if not recipe.phony:
            if recipe.recursive:
                descendants = itertools.chain([path], path.rglob("*"))
                return max(p.stat().st_mtime for p in descendants)
            if recipe.exists_only:
                return 0
            return path.stat().st_mtime

        if recipe.exists_only:
            return 0

        if not recipe.keep_ts:
            raise ValueError("Existence commands needs either exists_only or keep_ts")

        return path.stat().st_mtime

    @property
    def _is_new_order(self) -> bool:
        if (raw_order := self.globals.get("new_order")) is None:
            warnings.warn(_msg, lib.RemovedIn60Warning, stacklevel=3)
            return False
        return bool(raw_order)

    def _get_version(self) -> Version:
        if (manual_version := self.globals.get("version")) is None:
            warnings.warn(
                "Min cookbook versions will become mandatory.",
                lib.RemovedIn60Warning,
                stacklevel=3,
            )
            return Version("4.0.0")
        if not isinstance(manual_version, str):
            warnings.warn(
                "Min cookbook versions will be required to be a string",
                lib.RemovedIn60Warning,
                stacklevel=3,
            )
            return Version(str(manual_version))
        return Version(manual_version)


_msg = """ The relative strength of variables will change.
Please set new_order to false in your cookbook to keep the old behaviour,
or to new to adopt the new one.
The new order is the following (from weakest to strongest):
- global variables
- implicit variables (e.g. ${.target})
- regex variables (the ones that come from the target name)
- local variables
- environment variables
- command line arguments
"""
