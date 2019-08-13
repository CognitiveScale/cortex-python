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

NOTE: setup.py is using setuptools-scm to determine the distribution from SCM tags.  Additionally, it contains a special `get_version()` implementation which determines the PEP440 compatible pre-release suffix based on branch name (e.g. staging branch generates a release candidate).  The CI/CD pipelines in GoCD will automatically build and publish as appropriate the correct versions.  As a developer, you should not need to manually push an alpha build.

### Contribution 

After contributing to the library, and before you submit changes as a PR, please do the following

1. Update the `CHANGELOG.md`
2. Run unit tests via `make test`
3. Manually verify (i.e. try the new changes out in Cortex) to make sure everything is going well. Not required, but highly encouraged.
4. Bump up the distribution version by running `python setup.py --version` to see the current value, then create an annotated tag with the desired next version, for example: `git tag -a v1.2.3 -m "v1.2.3"`.  Be sure to push the new tag to the remove with `git push --follow-tags` or similar.

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

### Develop to staging (pre-release)

1.  Verify the distribution version is what you want via `python setup.py --version`.
2.  Merge `develop` to `staging` branch (can also be done via PR):
    ```
    > make stage
    ```
3. Wait for the CI pipeline to build and publish a pre-release version to PyPi.

### Staging (pre-release) to master (release)

1. In GitHub, create a pull request from `staging` to `master`.
2. Create a Change Management (CM) ticket in JIRA for the release, assigning it to the SOC-compliant release staff member.
3. The release staff will approve and merge the PR and the CI pipeline will build and publish the release distribution to PyPi.
