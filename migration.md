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
## Usage of Cortex magics

Usage of cortex magics (Can be used only when optional dependency of builders is installed) :

```
> %reload_ext cortex_builders
```
## Deprecations from cortex-client

1. InputMessage and OutputMessage classes have been deprecated.Instead use `Message`. 

```
> from cortex import Message
```

2. ModelClient, ModelProcess and ModelRouter have been deprecated. Instead use the `experiment` API in client
class to run experiments, save and retrieve your models. 

3. JobsClient has been deprecated. Instead use  `action` API in client class to save or retrieve actions. 
Also, you can use the `action` in builder class inside client class to build your actions.  (Can be used only when optional dependency of builders is installed)
