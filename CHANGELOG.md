# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased
### Fixed
- Creating the `.sacrerouge/metrics` directory in the BLEURT setup script if it doesn't exist.

## [v0.1.3](https://github.com/danieldeutsch/sacrerouge/releases/tag/v0.1.3) - 2020-11-25
### Added
- Added ability to skip calculating specific correlation levels (summary, system, and global)
- Added optionally generating plots of the system-level and global metric values
- Added passing a `List[Metrics]` to the correlation calculation instead of just a file or list of files

### Changed
- Updating `spacy` package version to `2.3.3` and model version to `2.3.1`.
`DecomposedRouge`'s unit tests and experiments subsequently updated.
- Changed all positional arguments to commands to non-positional for improved readability of the commands.
