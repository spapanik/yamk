import subprocess

import toml


class MakeCommand:
    def __init__(self, args):
        self.targets = args.targets
        with open("make.toml") as file:
            self.recipes = toml.load(file)

    def make(self):
        for target in self.targets:
            try:
                recipe = self.recipes[target]
            except KeyError:
                raise ValueError
        commands = recipe.get("commands", [])
        for command in commands:
            subprocess.run(command, shell=True)
