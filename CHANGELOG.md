# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

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
