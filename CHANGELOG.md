This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Upgrades from major to major versions, such a change from version `5.6.0` to `6.0.0`, might require local configuration updates to ensure compatibility with your current scripts. Make sure you have the latest version of the SDK using `pip install -U cortex-python`.

## [6.1.0] - 2021-11-18
### Added

- Support for Model CRUD methods
- Configurable artifact key for loading a Model from an Experiment
- Support for creating Experiments using Model


## [6.4.0] - 2023-07-13
### Changed

- The top level `cortex` package acts a namespace and no longer exports the `Cortex` or `Message` types.
  - Update any instances of `from cortex import Cortex` to `from cortex.client import Cortex`
  - Update any instances of `from cortex import Message` to `from cortex.message import Message`
  - Update any instances of `from cortex import __version__` to `from cortex.__version__ import __version__`
