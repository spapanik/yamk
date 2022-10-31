=========
Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_, and this project adheres to `Semantic Versioning`_.

`Unreleased`_
-------------

Fixed
^^^^^
* If the command is assumed up to date, don't check the path

`4.1.0`_ - 2022-10-28
---------------------

Added
^^^^^
* Allow assuming phony dependencies as up-to-date

`4.0.0`_ - 2022-09-27
---------------------

Added
^^^^^
* Allow setting the parser version

Changed
^^^^^^^
* The variables are now a dict, not a list of dicts

`3.0.1`_ - 2022-07-21
---------------------

Fixed
^^^^^
* Fixed the order of execution with the default sorter

`3.0.0`_ - 2022-07-20
---------------------

Added
^^^^^
* Duplicate requirements emit a warning

Changed
^^^^^^^
* Only cookbooks are supported
* Requirements are now deterministic if the order allows it

`2.4.1`_ - 2022-04-28
---------------------

Fixed
^^^^^
* Fixed dj_settings dependency

`2.4.0`_ - 2022-04-28
---------------------

Added
^^^^^
* The default cookbook is can be named cookbook.suffix with any of the supported suffixes
* Allow setting the filetype for the cookbook
* Support more extensions for cookbooks

`2.3.3`_ - 2022-03-05
---------------------

Fixed
^^^^^^^
* Fixed parsing weak variables

`2.3.2`_ - 2022-02-28
---------------------

Fixed
^^^^^^^
* Fix version when called with --version

`2.3.1`_ - 2022-02-25
---------------------

Changed
^^^^^^^
* Use explicit start when auto creating a cookbook

`2.3.0`_ - 2022-02-25
---------------------

Added
^^^^^
* Added a method to update the make.toml to cookbook.yml
Changed
^^^^^^^
* Deprecated the make.toml file as default in favour of cookbook.yml

`2.2.0`_ - 2022-02-14
---------------------

Added
^^^^^
* Allow using yaml for cookbooks
* Allow using json for cookbooks

Changed
^^^^^^^
* The command line interface for passing a cookbook is now -c/--cookbook
* Change toml parser to tomli

`2.1.0`_ - 2022-01-10
---------------------

Removed
^^^^^^^
* Removed changelog from the published wheel

Added
^^^^^
* Upgraded TOML library to be compliant with TOML 1.0.0

`2.0.0`_ - 2021-12-25
---------------------

Added
^^^^^
* Added python310 support

Removed
^^^^^^^
* Dropped python36 support

`1.3.1`_ - 2021-04-14
---------------------

Fixed
^^^^^
* Existence commands are now evaluated

`1.3.0`_ - 2021-04-14
---------------------

Added
^^^^^
* Allow exists_only for phony targets
* Allow checking existence with a custom command

`1.2.0`_ - 2021-03-08
---------------------

Changed
^^^^^^^
* Treat undefined variables as empty strings
* Allow specifying a make.toml.d/ for extra configuration files

`1.1.0`_ - 2021-02-26
---------------------

Added
^^^^^
* Add the ability to specify the shell

`1.0.0`_ - 2020-09-04
---------------------

Added
^^^^^
* Add a filter-out function

`0.16.0`_ - 2020-05-12
----------------------

Fixed
^^^^^
* Fix the order of the requirements

`0.15.0`_ - 2020-05-07
----------------------

Added
^^^^^
* Add the option to rebuild even if it's not needed
* Add the option to specify the path to the directory

Changed
^^^^^^^
* Regex variables are now weaker than local ones

Fixed
^^^^^
* Fix return type of functions

`0.14.0`_ - 2020-05-05
----------------------

Added
^^^^^
* Add the following functions:
  - get the name of a file
  - get the suffix of a file
  - change the suffix of a file
  - change the parent of a file

Fixed
^^^^^
* Fix strength of variables

`0.13.1`_ - 2020-05-04
----------------------

Fixed
^^^^^
* Allow expansion of variables in aliases

`0.13.0`_ - 2020-05-02
----------------------

Fixed
^^^^^
* Allow expansion of variables in targets

`0.12.0`_ - 2020-05-01
----------------------

Added
^^^^^
* Add function to get the name of a stem of a file
* Add function to get the parent directory of a file
* Existence of files, stem, and parent functions now can operate on a list

`0.11.0`_ - 2020-03-26
----------------------

Added
^^^^^
* Add function to merge lists together

Fixed
^^^^^
* Fix if-clause

`0.10.1`_ - 2020-03-26
----------------------

Fixed
^^^^^
* Fix issue with conflicting absolute and relative requirement names

`0.10.0`_ - 2020-03-23
----------------------

Added
^^^^^
* Add two more verbosity levels

Fixed
^^^^^
* Fix the issue that was preventing regex file targets

`0.9.3`_ - 2020-03-20
---------------------

Fixed
^^^^^
* Fix bug with multiple targets for the same regex

`0.9.1`_ - 2020-03-19
---------------------

Added
^^^^^
* Allow substituting a list of strings

`0.9.0`_ - 2020-03-18
---------------------

Fixed
^^^^^
* Fix bug when a variable evaluates to a list

Added
^^^^^
* Allow increasing verbosity
* Variables are evaluated literally unless a ``:`` is after them
* Add the following functions:
  - sort an array
  - wildcard expansion
  - ternary if
  - existence of a file
  - get the working directory
  - replace parts of a string


`0.8.0`_ - 2020-03-09
---------------------

Added
^^^^^
* Allow adding variables by passing the -x/--variable argument

Changed
^^^^^^^
* Environment variables are now the weakest variables
* A variable can now become weaker, not stronger

`0.7.0`_ - 2020-03-05
---------------------

Changed
^^^^^^^
* Fix toml parsing issues

`0.6.1`_ - 2020-02-25
---------------------

Fixed
^^^^^
* Fix working directory for running commands

`0.6.0`_ - 2020-02-25
---------------------

Added
^^^^^
* Add ${.target} and ${.requirements} as implicit variables
* Allow aliases for targets

Changed
^^^^^^^
* Allow only [a-zA-Z0-9\_.] for variable names

Fixed
^^^^^
* Fix crashing bug when having lists or dicts as variable values
* Fix crashing bug when specifying recursive targets

`0.5.0`_ - 2020-02-20
---------------------

Added
^^^^^
* Allow lists and dicts for string replacement
* Allow regex targets

`0.4.0`_ - 2020-02-12
---------------------

Added
^^^^^
* Allow specifying requirements

Changed
^^^^^^^
* Build only if something has actually changed

`0.3.0`_ - 2020-02-05
---------------------

Added
^^^^^
* Allow specifying a different makefile
* ``all`` is now the default target

Changed
^^^^^^^
* Allow only one target for yamk
* Change the order of variables
* Commands are echoed and failures are allowed only if the respective setting is enabled

`0.2.0`_ - 2020-02-03
---------------------

Added
^^^^^
* Create yam alias for yamk
* Allow using variables for strings of text

`0.1.1`_ - 2020-01-31
---------------------

Added
^^^^^
* Allow processing of phony recipes with no requirements

`0.1.0`_ - 2020-01-30
---------------------

Added
^^^^^
* Add the yamk command as a placeholder
* Initial project structure


.. _`unreleased`: https://github.com/spapanik/yamk/compare/v4.1.0...main
.. _`4.1.0`: https://github.com/spapanik/yamk/compare/v4.0.0...v4.1.0
.. _`4.0.0`: https://github.com/spapanik/yamk/compare/v3.0.1...v4.0.0
.. _`3.0.1`: https://github.com/spapanik/yamk/compare/v3.0.0...v3.0.1
.. _`3.0.0`: https://github.com/spapanik/yamk/compare/v2.4.1...v3.0.0
.. _`2.4.1`: https://github.com/spapanik/yamk/compare/v2.4.0...v2.4.1
.. _`2.4.0`: https://github.com/spapanik/yamk/compare/v2.3.3...v2.4.0
.. _`2.3.3`: https://github.com/spapanik/yamk/compare/v2.3.2...v2.3.3
.. _`2.3.2`: https://github.com/spapanik/yamk/compare/v2.3.1...v2.3.2
.. _`2.3.1`: https://github.com/spapanik/yamk/compare/v2.3.0...v2.3.1
.. _`2.3.0`: https://github.com/spapanik/yamk/compare/v2.2.0...v2.3.0
.. _`2.2.0`: https://github.com/spapanik/yamk/compare/v2.1.0...v2.2.0
.. _`2.1.0`: https://github.com/spapanik/yamk/compare/v2.0.0...v2.1.0
.. _`2.0.0`: https://github.com/spapanik/yamk/compare/v1.3.0...v2.0.0
.. _`1.3.1`: https://github.com/spapanik/yamk/compare/v1.3.0...v1.3.1
.. _`1.3.0`: https://github.com/spapanik/yamk/compare/v1.3.0...v1.3.0
.. _`1.2.0`: https://github.com/spapanik/yamk/compare/v1.1.0...v1.2.0
.. _`1.1.0`: https://github.com/spapanik/yamk/compare/v1.0.0...v1.1.0
.. _`1.0.0`: https://github.com/spapanik/yamk/compare/v0.16.0...v1.0.0
.. _`0.16.0`: https://github.com/spapanik/yamk/compare/v0.15.0...v0.16.0
.. _`0.15.0`: https://github.com/spapanik/yamk/compare/v0.14.0...v0.15.0
.. _`0.14.0`: https://github.com/spapanik/yamk/compare/v0.13.1...v0.14.0
.. _`0.13.1`: https://github.com/spapanik/yamk/compare/v0.13.0...v0.13.1
.. _`0.13.0`: https://github.com/spapanik/yamk/compare/v0.12.0...v0.13.0
.. _`0.12.0`: https://github.com/spapanik/yamk/compare/v0.11.0...v0.12.0
.. _`0.11.0`: https://github.com/spapanik/yamk/compare/v0.10.1...v0.11.0
.. _`0.10.1`: https://github.com/spapanik/yamk/compare/v0.10.0...v0.10.1
.. _`0.10.0`: https://github.com/spapanik/yamk/compare/v0.9.3...v0.10.0
.. _`0.9.3`: https://github.com/spapanik/yamk/compare/v0.9.1...v0.9.3
.. _`0.9.1`: https://github.com/spapanik/yamk/compare/v0.9.0...v0.9.1
.. _`0.9.0`: https://github.com/spapanik/yamk/compare/v0.8.0...v0.9.0
.. _`0.8.0`: https://github.com/spapanik/yamk/compare/v0.7.0...v0.8.0
.. _`0.7.0`: https://github.com/spapanik/yamk/compare/v0.6.1...v0.7.0
.. _`0.6.1`: https://github.com/spapanik/yamk/compare/v0.6.0...v0.6.1
.. _`0.6.0`: https://github.com/spapanik/yamk/compare/v0.5.0...v0.6.0
.. _`0.5.0`: https://github.com/spapanik/yamk/compare/v0.4.0...v0.5.0
.. _`0.4.0`: https://github.com/spapanik/yamk/compare/v0.3.0...v0.4.0
.. _`0.3.0`: https://github.com/spapanik/yamk/compare/v0.2.0...v0.3.0
.. _`0.2.0`: https://github.com/spapanik/yamk/compare/v0.1.1...v0.2.0
.. _`0.1.1`: https://github.com/spapanik/yamk/compare/v0.1.0...v0.1.1
.. _`0.1.0`: https://github.com/spapanik/yamk/releases/tag/v0.1.0

.. _`Keep a Changelog`: https://keepachangelog.com/en/1.0.0/
.. _`Semantic Versioning`: https://semver.org/spec/v2.0.0.html
