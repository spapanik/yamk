import os
import pathlib
import re
import subprocess
import sys
from string import Template

import toml


class MakeCommand:
    def __init__(self, args):
        self.target = args.target
        self.makefile = args.makefile
        with open(self.makefile) as file:
            self.recipes = toml.load(file)
        self.globals = self.recipes.get("$globals", {})
        self.vars = dict(**os.environ)
        self._update_variables(self.vars, self.globals.get("vars", []))

    def make(self):
        preprocessed = self._preprocess_target()
        for target, info in filter(
            lambda x: x[1]["should_build"],
            sorted(preprocessed.items(), key=lambda x: x[1]["priority"], reverse=True),
        ):
            self._make_target(target, info["recipe"])

    def _preprocess_target(self):
        recipe = self._extract_recipe(self.target)
        if recipe is None:
            raise ValueError(f"No recipe to build {self.target}")

        unprocessed = {self.target: {"recipe": recipe, "priority": 0}}
        preprocessed = {}
        while unprocessed:
            target, info = unprocessed.popitem()
            priority = info["priority"] + 1
            recipe = info["recipe"]
            preprocessed[target] = info
            for requirement in recipe.get("requires", []):
                recipe = self._extract_recipe(requirement)
                path = pathlib.Path(requirement)
                if requirement in preprocessed:
                    current_priority = preprocessed[requirement]["priority"]
                    preprocessed[requirement]["priority"] = max(
                        priority, current_priority
                    )
                elif recipe is not None:
                    unprocessed[requirement] = {
                        "recipe": recipe,
                        "priority": priority,
                    }
                elif path.exists():
                    preprocessed[requirement] = {"priority": priority}
                else:
                    raise ValueError(f"No recipe to build {requirement}")

        self._mark_unchanged(preprocessed)
        return preprocessed

    def _make_target(self, target, recipe):
        variables = self.vars.copy()
        self._update_variables(variables, recipe.get("vars", []))
        commands = recipe.get("commands", [])
        for command in commands:
            command = self._substitute_vars(command, variables)
            command, options = self._parse_string(command)
            if recipe.get("echo") or options.get("echo"):
                print(command)
            result = subprocess.run(command, shell=True)
            if not result.returncode and recipe.get("phony") and recipe.get("keep_ts"):
                path = self._phony_path(target)
                path.touch()
            if (
                result.returncode
                and not recipe.get("allow_failures")
                and not options.get("allow_failures")
            ):
                sys.exit(result.returncode)

    def _extract_recipe(self, target):
        try:
            return self.recipes[target]
        except KeyError:
            return None

    def _mark_unchanged(self, preprocessed):
        for target, info in sorted(
            preprocessed.items(), key=lambda x: x[1]["priority"], reverse=True
        ):
            ts = self._infer_timestamp(target, info)
            info["timestamp"] = ts
            should_build = self._should_build(target, preprocessed)
            info["should_build"] = should_build

    def _phony_path(self, target):
        phony_dir = pathlib.Path(self.makefile).parent
        encoded_target = target.replace('.', '.46').replace('/', '.47')
        return phony_dir.joinpath(encoded_target)

    def _should_build(self, target, preprocessed):
        info = preprocessed[target]
        recipe = info.get("recipe")
        if recipe is None:
            return False
        if recipe.get("phony"):
            if not recipe.get("keep_ts"):
                return True
            path = self._phony_path(target)
            if not path.exists():
                return True
        else:
            path = pathlib.Path(target)
            if not path.exists():
                return True
            if recipe.get("exists_only"):
                return False

        if any(
            preprocessed[requirement]["should_build"]
            for requirement in recipe["requires"]
        ):
            return True
        ts = info["timestamp"]

        req_ts = max(
            preprocessed[requirement]["timestamp"]
            for requirement in recipe["requires"]
        )
        return req_ts > ts

    def _infer_timestamp(self, target, info):
        recipe = info.get("recipe")
        path = pathlib.Path(target)
        if recipe is None:
            return path.stat().st_mtime
        if recipe.get("phony"):
            path = self._phony_path(target)
            if recipe.get("keep_ts") and path.exists():
                return path.stat().st_mtime
            return float("inf")
        if recipe.get("exists_only"):
            return 0
        if path.exists():
            if recipe.get("recursive"):
                return max(p.stat().st_mtime for p in path)
            return path.stat().st_mtime
        return float("inf")

    @staticmethod
    def _parse_string(string):
        match = re.match(r"\[.*?\]", string)
        if match is None:
            return string.strip(), {}

        end = match.end()
        options = string[1 : end - 1]
        string = string[end:]
        return (
            string.strip(),
            dict.fromkeys(map(lambda s: s.strip(), options.split(",")), True),
        )

    def _update_variables(self, variables, new_variables):
        for var_block in new_variables:
            for key, value in var_block.items():
                key = self._substitute_vars(key, variables)
                key, options = self._parse_string(key)
                if key in os.environ and not options.get("strong"):
                    continue
                value = self._substitute_vars(value, variables)
                variables[key] = value

    @staticmethod
    def _substitute_vars(string, variables):
        return Template(string).substitute(**variables)
