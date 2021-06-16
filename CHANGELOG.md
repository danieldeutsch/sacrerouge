# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## [v0.2.2](https://github.com/danieldeutsch/sacrerouge/releases/tag/0.2.2) - 2021-06-16
### Added
- Added a `verbose` option to QAEval

### Changed
- Changed QAEval to use the updated `qaeval` interface with version 0.0.8.
The QA results will now include the answer offsets.

## [v0.2.1](https://github.com/danieldeutsch/sacrerouge/releases/tag/0.2.1) - 2021-05-06
### Added
- Added the New York Times dataset. See [here](doc/datasets/nytimes.md).
- Added better tutorials for using the library.

### Changed
- Added an exception with an error message if PyrEval is used with a single reference summary.

### Fixed
- Fix the `overrides` package to version 3.1.0 to fix a bug that was caused in the `Params` class in `overrides` version 6.0.0

## [v0.2.0](https://github.com/danieldeutsch/sacrerouge/releases/tag/0.2.0) - 2021-03-26
### Added
- Added the annotations collected by [Bhandari et al., (2020)](https://www.aclweb.org/anthology/2020.emnlp-main.751/).
- Added [BLANC](https://github.com/PrimerAI/blanc)
- Added the annotations collected by the [BLANC paper](https://www.aclweb.org/anthology/2020.eval4nlp-1.2.pdf).
- Added a wrapper around the implementation of APES.
- Added the [Multi-News dataset](https://www.aclweb.org/anthology/P19-1102/).
- Added the [WCEP dataset](https://arxiv.org/pdf/2005.10070.pdf)
- Added confidence interval calculation and running hypothesis tests for the correlation coefficients

### Changed
- Changed the backend for the correlation calculation to use matrices instead of the `MetricsDict`s

### Fixed
- Fixed a bug in which QAEval would crash if you don't use LERC

## [v0.1.5](https://github.com/danieldeutsch/sacrerouge/releases/tag/0.1.5) - 2021-01-02
### Fixed
- Including the LERC output from the individual QA pairs in QAEval

## [v0.1.4](https://github.com/danieldeutsch/sacrerouge/releases/tag/0.1.4) - 2021-01-02
### Added
- Added scoring QAEval predictions with [LERC](https://arxiv.org/abs/2010.03636) 

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
