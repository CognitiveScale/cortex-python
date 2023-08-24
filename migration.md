# Migration steps from `sensa-client` to `sensa-python`

The `sensa-python` library and its optional add-ons are replacing the sensa-client library. The new libraries are more lightweight and use-case focussed. `Sensa-python` may be used for development with or without the add-ons.

## Uninstall the previous library (`sensa-client`)

To use the new Sensa libraries, `sensa-python` and `sensa-python-builders` you must uninstall the `sensa-client` library; `sensa-client` and `sensa-python`**cannot** be installed simultaneously in your python environment.

```
  > pip uninstall sensa-client
```

## Install `sensa-python`

To install:
```
  > pip install sensa-python
```

To install the optional components:
```
  > pip install sensa-python[viz]
  > pip install sensa-python[jupyter]
  > pip install sensa-python[builders]
```

## Import Client functionalities

The way Client functionalities can be imported has changed.

To import sensa :

```
> import sensa
```
To import ConnectionClient :

```
> from sensa.connection import ConnectionClient
```
## Upload to Managed Content

Use `ManagedContentClient` to upload and download to your account's managed content. In sensa-client, ConnectionClient was used for these functionalities. The methods to upload and download remain the same.

To import ManagedContentClient:

```
> from sensa.content import ManagedContentClient
``` 
ConnectionClient can be used to save and retrieve connections. 

## Use Sensa magics

Sensa magics can be used only when the optional `builders` dependency is installed:

```
> %reload_ext sensa_builders
```
## Deprecations and Removals from sensa-client

1. The `InputMessage` and `OutputMessage` classes have been deprecated. Instead, use the `Message` class:

```
> from sensa.message import Message
```

2. `ModelClient`, `ModelProcess`, and `ModelRouter` have been deprecated. Instead, use the `experiment` API in the `Client`
class to run experiments, save and retrieve your models.

3. `JobsClient` has been deprecated. Instead, use the `action` API in `Client` class to save or retrieve actions.
Also, you can use the `action` in the builder class inside client class to build your actions. (Can be used only when optional dependency of builders is installed)

4. `SecretsClient` has been deprecated. There is no equivalent replacement functionality in the python library, but
you can manage secrets through the Sensa Vault in the Sensa Console or via the CLI `sensa variables [command] [options]`.

5. `Message.with_payload()` has been removed. This method was previously deprecated in `sensa-client` v5.5.4.
Instead, use the `Client.message()` method:

```
> from sensa.client import Sensa

> sensa = Sensa.client()
> message = sensa.message(payload={'value': 'hello world'})
```

6. `LocalExperiment.set_pipeline()` has been removed. This method was previously deprecated in `sensa-client` v5.5.0.
There is no replacement method for this functionality.
