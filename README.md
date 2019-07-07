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
- run `make dev.push TAG=<alpha release number>`. Example: `make dev.push TAG=1`

### Contribution 

After contributing to the library, and before you submit changes as a PR, please do the following

1. Run unit tests via `make test`
2. Manually verification (i.e. try the new changes out in Cortex) to make sure everything is going well. Not required, but highly encouraged.
3. Bump up `setup.py` version and update the `CHANGELOG.md` 

### Documentation

The package documentation is built with Sphinx. To build the documentation:

```
> make docs
```
The documentation will be rendered in HTML format under the `docs/_build/html` directory.

Activate your virtual environment:
```
> source _venv/bin/activate
```

Setup your environment, if you have not done so:
```
> make dev.install 
```

### Pre-release to staging

1. Create and push an alpha release:
    ```
    > make dev.push TAG=1
    ```
    Where `TAG` is the alpha version number. This will build an alpha-tagged package.
2. Merge `develop` to `staging` branch:
    ```
    > make stage
    ```
3. In GitHub, create a pull request from `staging` to `master`.
