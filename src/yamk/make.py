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
        for info in filter(
            lambda x: x["should_build"],
            sorted(preprocessed.values(), key=lambda x: x["priority"], reverse=True),
        ):
            self._make_target(info["recipe"])

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
                    preprocessed[requirement] = {
                        "priority": priority,
                        "timestamp": path.stat().st_mtime,
                    }
                else:
                    raise ValueError(f"No recipe to build {requirement}")

        self._mark_unchanged(preprocessed)
        return preprocessed

    def _make_target(self, recipe):
        variables = self.vars.copy()
        self._update_variables(variables, recipe.get("vars", []))
        commands = recipe.get("commands", [])
        for command in commands:
            command = self._substitute_vars(command, variables)
            command, options = self._parse_string(command)
            if recipe.get("echo") or options.get("echo"):
                print(command)
            result = subprocess.run(command, shell=True)
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
            target_path = pathlib.Path(target)
            if "recipe" not in info:
                info["should_build"] = False
            elif info["recipe"].get("phony"):
                info["should_build"] = True
            elif not target_path.exists():
                info["should_build"] = True
            elif any(
                preprocessed[requirement]["should_build"]
                for requirement in info["recipe"]["requires"]
            ):
                info["should_build"] = True
            else:
                ts = target_path.stat().st_mtime
                req_ts = max(
                    pathlib.Path(requirement).stat().st_mtime
                    for requirement in info["recipe"]["requires"]
                )
                info["should_build"] = req_ts > ts

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
