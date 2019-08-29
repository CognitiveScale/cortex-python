# Migration steps from cortex-client to cortex-python

## Uninstalling the old library

To use this new library you must uninstall the old `cortex-client` library. Both `cortex-client` and `cortex-python`
**cannot** be installed simultaneously in your python environment.

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

Use `ManagedContentClient` to upload and download to your account's managed content. In cortex-client, ConnectionClient was used for these functionalities. The methods to upload and download remain the same.

To import ManagedContentClient:

```
> from cortex.content import ManagedContentClient
``` 
ConnectionClient can be used to save and retrieve connections. 

## Usage of Cortex magics

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
you can manage secrets through the Cortex Vault in the Cortex Console.

5. `Message.with_payload()` has been removed. This method was previously deprecated in `cortex-client` v5.5.4.
Instead use the `Client.message()` method:

```
> from cortex import Cortex

> cortex = Cortex.client()
> message = cortex.message(payload={'value': 'hello world'})
```

6. `LocalExperiment.set_pipeline()` has been removed. This method was previously deprecated in `cortex-client` v5.5.0.
There is no replacement method for this functionality.
