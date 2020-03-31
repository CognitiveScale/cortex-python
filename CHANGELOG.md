This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Upgrades from major to major versions, such a change from version `5.6.0` to `6.0.0`, might require local configuration updates to ensure compatibility with your current scripts. Make sure you have the latest version of the SDK using `pip install -U cortex-python`.

## [1.3.1] - 2020-03-31
### Added
* Add retry logic when invoking action to overcome the time it takes to spin up an action pod.

## [1.3.0] - 2020-03-19
### Added
* Bumped pyyaml to 5.3.1 for high level vulnerability CVE-2020-1747.

## [1.2.1] - 2020-03-05
### Added
* Wrapped status check of requests library to provide more details of when an error occurs.

## [1.2.0] - 2019-10-01
### Added
* All HTTP requests now send a User-Agent header including distribution name and version.

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
