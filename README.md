# Python Module for the Cortex Cognitive Platform

The Cortex Python module provides an API client library to easily integrate with the Cortex Cognitive Platform. 
Refer to the Cortex documentation for details on how to use the library: 

- Developer guide: https://cognitivescale.github.io/cortex-fabric/
- Cortex Python references: https://cognitivescale.github.io/cortex-python/master/

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
```

## Development 

### Setup

When developing, it's a best practice to work in a virtual environment. Create and activate a virtual environment:
```
  > virtualenv --python=python3.10 _venv
  > source _venv/bin/activate
```

Install developer dependencies:

```
  > git clone git@github.com:CognitiveScale/cortex-python.git
  > cd cortex-python
  > make dev.install
```

Run Developer test and linting tasks:
Three types of checks are configured for this:
1. [symilar](https://pylint.readthedocs.io/en/v2.16.2/symilar.html) - to test code duplication
2. [pylint](https://pylint.readthedocs.io/en/v2.16.2/) - for linting
3. [pytest](https://docs.pytest.org/en/7.2.x/) - for running the unit tests. These are orchestrated through [tox](https://tox.wiki/en/3.27.1/). The tox configuration is available at [`tox.ini`](/tox.ini)

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

Set up your environment, if you have not done so:
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


## TODO
- [x] extending the client with helpers for cortex resources 
- [x] camelcase in pylinyrc
- [ ] Update all documentation with proper Sphinx formatting
  - [x] Most of the major modules have been fixed except skill.py, model.py
- [x] use exceptions defined in `cortex/exceptions.py`
- [ ] integrate the cortex-python-profiles package back into the python SDK