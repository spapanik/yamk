## Keys

The following list contains all the valid keys. The list is in the form:

`<key_name>: <value_type> (target types)`.

A target type starting with a tilde(~) is an invalid target, and "any" means that this key
is valid for all target types. Adding an invalid key is undefined behaviour that will either
be ignored, or raise an Exception.

#### phony: boolean (any)

If set to true, it turns the target to a phony target.

#### regex: boolean (any)

If set to true, it turns the target to a regex target.

#### requires: array of strings (any)

An array of all the requirements for the target. The requirements that need to be built,
are guaranteed to be built before the target. If there is a valid way to resolve the whole
cookbook and keep them in order, then their order will be respected too.

#### commands: array of strings (any)

The commands to build the target.

#### vars: table (any)

The variables specific to this target.

#### keep_ts: boolean (phony targets)

If set to true, this phony target will keep the timestamp when it was last built. In general,
a phony target will be built every time, but a phony target with `keep_ts` set to true, will
only be built if the kept timestamp is older than any of the timestamps of the requirements.

#### exists_only: boolean (any)

If set to true, this file will be built only if it doesn't exist. The check for the existence
is happening before any make command is run and there is a de-duplication step, but some care
should be taken into account if it's created as a side-effect of another target.

#### existence_command: string (phony targets)

If set to a non-empty string, it will execute this command to check if the phony target already
"exists". Upon an exit status of 0, the target is assumed to exist.

#### recursive: boolean (file targets)

This makes sense only for directories. In this case, if it's set to true, the timestamp of the
directory is taken to be the maximum of all the timestamps of all files, at any depth, inside it.
Otherwise, the timestamp of the target

#### update: boolean (file targets)

If set to true, then yam will touch the file target after a successful
build. It's meant to be used with lockfiles, that they might not get
touched by the actual command if there is no need to do so.

#### echo: boolean (any)

By default, the commands are not echoed before they are run. If set to
true, they do.

#### allow_failures: boolean (any)

By default, a failing command will halt the execution of the recipe.
This will allow *yam* to try and recover from the error. Allow_failures
doesn't guarantee that the execution will resume, because the nature of
the failure may not allow that.
