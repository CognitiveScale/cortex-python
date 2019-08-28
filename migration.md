# Migration steps from cortex-client to cortex-python

## To use the new library, uninstall the old library

```
  > pip uninstall cortex-client
```


## Installation

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

## Client Functionality Import
We have updated the way Client functionalities can be imported

Examples of importing some functionalities

To import cortex :

```
> import cortex
```
To import ConnectionClient :

```
> from cortex.connection import ConnectionClient
```

## Upload to Managed Content

Use `ManagedContentClient` to upload or download to your account's Managed. In cortex-client library ConnectionClient was used for these functionalities. The methods to upload ad download remain the same

To import ManagedContentClient :
```
> from cortex.content import ManagedContentClient
```
ConnectionClient can still be used to save and get the connections. 

## Usage of Cortex magics

Usage of cortex magics (Can be used only when optional dependency of builders is installed) :

```
> %reload_ext cortex_builders
```
## Deprecations from cortex-client

1. InputMessage and OutputMessage classes have been deprecated. Instead use `Message`.

```
> from cortex import Message
```

2. ModelClient, ModelProcess and ModelRouter have been deprecated. Instead use the `experiment` API in client
class to run experiments, save and retrieve your models.

3. JobsClient has been deprecated. Instead use `action` API in client class to save or retrieve actions.
Also, you can use the `action` in builder class inside client class to build your actions. (Can be used only when optional dependency of builders is installed)

4. SecretsClient has been deprecated. There is no equivalent replacement functionality in the python library, but
you can manage secrets through the Cortex Vault in the Cortex Console.

5. `Message.with_payload()` has been removed. This method was previously deprecated in `cortex-client` v5.5.4.
Instead use the `Client.message()` method.

```
> from cortex import Cortex
> cortex = Cortex.client()
> message = cortex.message(payload={'value': 'hello world'})
```

6. `LocalExperiment.set_pipeline()` has been removed. This method was previously deprecated in `cortex-client` v5.5.0.
There is no replacement method for this functionality.
