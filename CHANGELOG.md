# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## [0.9.1] - 2020-03-19
### Added
- Allow substituting a list of strings

## [0.9.0] - 2020-03-18
### Fixed
- Fix bug when a variable evaluates to a list

### Added
- Allow increasing verbosity
- Variables are evaluated literally unless a `:` is after them
- Add the following functions:
  - sort an array
  - wildcard expansion
  - ternary if
  - existence of a file
  - get the working directory
  - replace parts of a string


## [0.8.0] - 2020-03-09
### Added
- Allow adding variables by passing the -x/--variable argument

### Changed
- Environment variables are now the weakest variables
- A variable can now become weaker, not stronger

## [0.7.0] - 2020-03-05
### Changed
- Fix toml parsing issues

## [0.6.1] - 2020-02-25
### Fixed
- Fix working directory for running commands

## [0.6.0] - 2020-02-25
### Added
- Add ${.target} and ${.requirements} as implicit variables
- Allow aliases for targets

### Changed
- Allow only [a-zA-Z0-9\_.] for variable names

### Fixed
- Fix crashing bug when having lists or dicts as variable values
- Fix crashing bug when specifying recursive targets

## [0.5.0] - 2020-02-20
### Added
- Allow lists and dicts for string replacement
- Allow regex targets

## [0.4.0] - 2020-02-12
### Added
- Allow specifying requirements

### Changed
- Build only if something has actually changed

## [0.3.0] - 2020-02-05
### Added
- Allow specifying a different makefile
- `all` is now the default target

### Changed
- Allow only one target for yamk
- Change the order of variables
- Commands are echoed and failures are allowed only if the respective setting is enabled

## [0.2.0] - 2020-02-03
### Added
- Create yam alias for yamk
- Allow using variables for strings of text

## [0.1.1] - 2020-01-31
### Added
- Allow processing of phony recipes with no requirements

## [0.1.0] - 2020-01-30
### Added
- Add the yamk command as a placeholder
- Initial project structure
