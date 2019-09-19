This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Upgrades from major to major versions, such a change from version `5.6.0` to `6.0.0`, might require local configuration updates to ensure compatibility with your current scripts. Make sure you have the latest version of the SDK using `pip install -U cortex-python`.

## [1.1.0] - 2019-09-12
### Added
* Local mode support for user specified base directory that overrides the use of $HOME/.cortex.
* Fixes a bug in remove_step of Pipeline

## [1.0.4] - 2019-08-27
### Removed
* Deprecated methods `Message.with_payload` and `LocalExperiment.set_pipeline`

## [1.0.3] - 2019-08-15
### Modified
* Changes to Makefile in preparation for CI/CD.

## [1.0.1] - 2019-07-09
### Added
* Additional unit tests for connections, content, and environment config
* Fixes for cortex-python-builders unit tests

## [1.0.0] - 2019-07-08
### Added
* First port/extract from the deprecated cortex-client module.
