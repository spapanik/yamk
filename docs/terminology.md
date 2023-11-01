# Terminology

- **Cookbook**: The configuration file (or collection of files) that defines how `yam`
  operates in a specific directory.
- **Target**: A target is the file that needs to be created, or the task that
  should be done. The first type of targets is called a file target, and the second type,
  a phony target. A file target, is a file in the UNIX sense of what a file is.
- **Recipe**: A recipe is what tells *yam* how to build a target, or do the task specified
  by the target.
- **Requirements**: The targets that should be built before the target is actually built.
