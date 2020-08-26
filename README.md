# Python Module for the Cortex Cognitive Platform

The Cortex Python module provides an API client library to easily integrate with the Cortex Cognitive Platform. 
Refer to the Cortex documentation for details on how to use the library: 

- Developer guide: https://docs.cortex.insights.ai/docs/developer-guide/overview/
- Cortex Python references: https://docs.cortex.insights.ai/docs/developer-guide/reference-guides


## Installation

To install: 
```
  > pip install cortex-python
```

or from source code:
```
  > git clone git@github.com:CognitiveScale/cortex-python.git
  > cd cortex-python
  > pip install -e .
```

To install the optional components: 
```
  > pip install cortex-python[viz]
  > pip install cortex-python[jupyter]
  > pip install cortex-python[builders]
```

## Development 

### Setup

When developing, it's a best practice to work in a virtual environment. Create and activate a virtual environment:
```
  > virtualenv --python=python3.6 _venv
  > source _venv/bin/activate
```

Install developer dependencies:

```
  > git clone git@github.com:CognitiveScale/cortex-python.git
  > cd cortex-python
  > make dev.install
```

There's a convenience `Makefile` that has commands to common tasks, such as build, test, etc. Use it!

### Testing

#### Unit Tests

Follow above setup instructions (making sure to be in the virtual environment and having the necessary dependencies)

- `make test` to run test suite

To run an individual file or class method, use pytest. Example tests shown below:

- file: `pytest test/unit/agent_test.py` 
- class method: `pytest test/unit/agent_test.py::TestAgent::test_get_agent`

#### Publishing an alpha build

Suppose you want to release new functionality so it can be installed without releasing a new official version. We need to use an alpha version in PyPi.

- we need to create and publish an alpha release:
- get credentials to the `cortex-python` pypi CognitiveScale account (via lastpass)
- run `make dev.push`. The alpha pre-release number (the N in X.Y.ZaN) with be determined automatically.

### Contribution 

After contributing to the library, and before you submit changes as a PR, please do the following

1. Run unit tests via `make test`
2. Manually verification (i.e. try the new changes out in Cortex) to make sure everything is going well. Not required, but highly encouraged.
3. Bump up `setup.py` version and update the `CHANGELOG.md` 

### Documentation

Activate your virtual environment:
```
> source _venv/bin/activate
```

Setup your environment, if you have not done so:
```
> make dev.install 
```

The package documentation is built with Sphinx and generates versioned documentation for all tag matching the `release/X.Y.Z` pattern and for the `master` branch. To build the documentation:

```
> make docs.multi
```
The documentation will be rendered in HTML format under the `docs/_build/${VERSION}` directory.

### Pre-release to staging

1. Create and push an alpha release:
    ```
    > make dev.push
    ```
    This will build an alpha-tagged package.
2. Merge `develop` to `staging` branch:
    ```
    > make stage
    ```
3. In GitHub, create a pull request from `staging` to `master`.

# Migration steps from `cortex-client` to `cortex-python`

The `cortex-python` library and its optional add-ons are replacing the cortex-client library. The new libraries are more lightweight and use-case focussed. `Cortex-python` may be used for development with or without the add-ons.

## Uninstall the previous library (`cortex-client`)

To use the new Cortex libraries, `cortex-python` and `cortex-python-builders` you must uninstall the `cortex-client` library; `cortex-client` and `cortex-python`**cannot** be installed simultaneously in your python environment.

```
  > pip uninstall cortex-client
```

## Install `cortex-python`

To install:
```
  > pip install cortex-python
```

To install the optional components:
```
  > pip install cortex-python[viz]
  > pip install cortex-python[jupyter]
  > pip install cortex-python[builders]
```

## Import Client functionalities

The way Client functionalities can be imported has changed.

To import cortex :

```
> import cortex
```
To import ConnectionClient :

```
> from cortex.connection import ConnectionClient
```
## Upload to Managed Content

Use `ManagedContentClient` to upload and download to your account's managed content. In cortex-client, ConnectionClient was used for these functionalities. The methods to upload and download remain the same.

To import ManagedContentClient:

```
> from cortex.content import ManagedContentClient
``` 
ConnectionClient can be used to save and retrieve connections. 

## Use Cortex magics

Cortex magics can be used only when the optional `builders` dependency is installed:

```
> %reload_ext cortex_builders
```
## Deprecations and Removals from cortex-client

1. The `InputMessage` and `OutputMessage` classes have been deprecated. Instead use the `Message` class:

```
> from cortex import Message
```

2. `ModelClient`, `ModelProcess` and `ModelRouter` have been deprecated. Instead use the `experiment` API in the `Client`
class to run experiments, save and retrieve your models.

3. `JobsClient` has been deprecated. Instead use the `action` API in `Client` class to save or retrieve actions.
Also, you can use the `action` in the builder class inside client class to build your actions. (Can be used only when optional dependency of builders is installed)

4. `SecretsClient` has been deprecated. There is no equivalent replacement functionality in the python library, but
you can manage secrets through the Cortex Vault in the Cortex Console or via the CLI `cortex variables [command] [options]`.

5. `Message.with_payload()` has been removed. This method was previously deprecated in `cortex-client` v5.5.4.
Instead use the `Client.message()` method:

```
> from cortex import Cortex

> cortex = Cortex.client()
> message = cortex.message(payload={'value': 'hello world'})
```

6. `LocalExperiment.set_pipeline()` has been removed. This method was previously deprecated in `cortex-client` v5.5.0.
There is no replacement method for this functionality.

7. The `cortex-python` package depends on less libraries than `cortex-client`. Users of the cortex-client that have incrementally upgraded to different versions of the cortex-client package in the same environment are likely to have downloaded the following transitive dependencies. When cortex-python is used in place of cortex-client, these transitive dependencies will no longer be included. Accordingly, users that depend on any of the transitive dependencies must explicitly install them. The list of these transitive dependencies includes:

```
Flask==1.0.2
discovery-transitioning-utils>=1.3.50
diskcache>=3.0.5,<3.1
ipython>=6.4.0
matplotlib>=2.2.2
maya==0.5.0
scikit-learn>=0.20.0
seaborn>=0.9.0
tenacity==5.0.2
```
