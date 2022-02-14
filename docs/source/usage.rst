=====
Usage
=====

*yam*'s behaviour is defined in a toml file, called a cookbook. The expected name is *make.toml*, but you can specify a different file if you want. Specifying a name *<name.toml>* will also parse all the *.toml* files in the directory named *<name.toml>.d*.


*yam* can be invoked by using the command *yam*, which is also aliased to *yamk*. *yam* follows the GNU recommendations for command line interfaces, and offers:

-h/--help
    show this help message and exit
-d/--directory  dir
    the path to the directory that contains the cookbook
-f/--force
    rebuild all dependencies and the target
-m/--makefile   Makefile
    the path to the makefile (defaults to *./make.toml*)
-c/--cookbook   cookbook
    the path to the cookbook (defaults to *./make.toml*)
-s/--shell      shell
    the path to the shell to execute the commands (defaults to */bin/sh*)
-V/--version
    print the version and exit
-v/--verbose
    increase the level of verbosity
-x/--variable   KEY=value
    a list of variables to override the ones set in the cookbook, which should be in the form <variable>=<value>


Recipes
-------

A cookbook is a collection of recipes. A recipe has the following format:

.. code-block:: toml

    [target_name]
    "<key_1>" = "<value_1>"
    "<key_2>" = "<value_2>"
    # ...
    "<key_n>" = "<value_n>"


Targets
-------

There are two groups of mutually exclusive types of targets: File/phony targets and static/regex targets. There are also two more cases, but they are not targets: Aliases and meta-targets.

Meta-targets
    A target starting with a single dollar sign is reserved by *yam* itself, for meta-targets. If the target starts with more than one dollar sign, a single dollar sign is stripped, and it's a normal target or an alias. Currently the only meta-target is *$globals*, that has two valid keys: *vars*. *vars* is the same as the key with the same name if static and regex targets, but weaker. *shell* can override the default shell used to execute the commands, which is */bin/sh*.
Aliases
    An alias has a single key, named *alias*, and the value of the key is the name of the target it aliases.
File targets
    A file target is a target who doesn't have the *phony* key, or that the *phony* key is specifically set to a false value. The path can be with its absolute path, or the path relative to the cookbook. Absolute paths are discouraged, as they limit the users ability to choose.
Phony targets
    A target that contains the *phony* key set to a true value, is a phony target.
Static targets
    A static target is a target who doesn't have the *regex* key, or that the *regex* key is specifically set to a false value.
Regex targets
    A target that contains the *regex* key set to a true value, is a regex target. A regex target is assumed to be a file target. In case the target matches a regex target, any name that was matched via a named grouped will be available as a variable. Regex targets are weaker than static ones.

Keys
----

The following list contains all the valid keys. The list is in the form <key_name>: <value_type> (target types). A target type starting with a tilde(~) is an invalid target, and "any" means that this key is valid for all target types. Adding an invalid key is undefined behaviour that will most probably be ignored, or crash.

phony: boolean (~regex targets)
    If set to true, it turns the target to a phony target.
regex: boolean (~phony targets)
    If set to true, it turns the target to a regex target.
requires: array of strings (any)
    An array of all the requirements for the target. The requirements that need to be built, are guaranteed to be built before the target, but there are no guarantees on the order that the requirements will be built.
commands: array of strings (any)
    The commands to build the target.
vars: array of tables (any)
    The variables specific to this target.
keep_ts: boolean (phony targets)
    If set to true, this phony target will keep the timestamp when it was last built. In general, a phony target will be built every time, but a phony target with *keep_ts* set to true, will only be built if the kept timestamp is newer than the timestamp of the requirements.
exists_only: boolean (any)
    If set to true, this file will be built only if it doesn't exist. The check for the existence is happening before any make command is run and there is a de-duplication step, but some care should be taken into account if it's created as a side-effect of another target.
existence_command: string (phony targets)
    If to a non-empty string, it will execute this command to check if the phony target already "exists". Upon an exit status of 0, the target is assumed to exist.
recursive: boolean (file targets)
    This makes sense only for directories. In this case, if it's set to true, the timestamp of the directory is taken to be the maximum of all the timestamps of all files, at any depth, inside it.
echo: boolean (any)
    By default, the commands are not echoed before they are run. If set to true, they do.
allow_failures: boolean (any)
    By default, a failing command will halt the execution of the recipe. This will allow *yam* to try and recover from the error. Allow_failures doesn't guarantee that the execution will resume, because the nature of the failure may not allow that.

Variables
---------

A variable is defined in the key *vars*. The variables are parsed in order, so a variable, once defined can be used later. An example of *vars*:

.. code-block:: toml

    [target_name]
    vars = [
        {"[variable_options]var_1": "<value_1>"},
        {"[variable_options]var_2": "<value_2>"},
        # ...
        {"[variable_options]var_n": "<value_n>"},
    ]


The options are completely optional, and they are comma separated.

A variable that resolves to a list or a dictionary will be treated as such. If it should be treated as a string instead instead of "${variable}", the form "${variable:}" should be used. If a variable is a part of a string, it will always be transformed into a string first. A key can be passed to pick up a specific value from a list or a dictionary, for example, "${list_var:0}" or "${dict_var:key}".

Variable types
--------------

There are six types of variables: environment variables, argument, global, local, regex and implicit ones. If a variable is being used within a command and it's not set, it will be treated as the empty string. With an increasing strength order:

Environment
    All the environment variables gathered at the beginning of the execution of *yam* are gathered into variables. They are the weakest variables.
Global
    A global variable is a variable specified in the *$global* meta-target.
Regex
    In the case of a regex target, any named group is a regex variable, which has the value of the matched text.
Local
    A local variable is a variable specified by the *vars* key inside a target.
Argument
    An argument variable is a variable defined with the --variable option when *yam* was invoked.
Implicit
    The implicit variables are variables created by the target itself, implicitly. They are guarded against overriding, as they start with a dot. This dot acts as a safeguard so they cannot mix with environment and regex ones. At the moment, the following two implicit variables exist:

    * *.target*: the name of the target. In case of a file target, it's the absolute path to the file, regardless of they way it was defined.
    * *.requirements*: the array of the requirements. All the file requirements are given as their absolute paths.

    All the implicit variables, they are specific to the target that it's being built, i.e. if the file target is specified as a regular expression, the absolute path to the specific file, not the regex path.

Variable options
----------------

The only option at the moment is *weak*.

Weak
    Weak can be used to make the variable keep its value if it's not unset

Commands
--------

Command options
^^^^^^^^^^^^^^^

There are two command options: *echo* and *allow_failures*. These commands can be used to customise the specific command, as if the respective variable was set.
