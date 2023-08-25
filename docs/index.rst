**Home:** `Cortex Fabric Documentation <https://cognitivescale.github.io/cortex-fabric/>`_

Cortex Python Reference
=======================

This reference guide describes the base API client library to integrate with Cortex Fabric.
Refer to the `Cortex Fabric documentation <https://cognitivescale.github.io/cortex-fabric/>`_ for more info about how to use the library.

Cortex Client
-------------

.. autoclass:: cortex.client.Client
    :members:
    :exclude-members: to_connector

Cortex
------

.. autoclass:: cortex.client.Cortex
    :members:


CortexEnv
---------

.. autoclass:: cortex.env.CortexEnv
    :members:

Cortex Local Experiments
------------------------

.. autoclass:: cortex.experiment.local.LocalExperiment
    :members:

Cortex Experiment
-----------------

.. autoclass:: cortex.experiment.Experiment
    :members:

Cortex Experiment Run
---------------------

.. autoclass:: cortex.experiment.Run
    :members:

Cortex Experiment RemoteRun
----------------------------

.. autoclass:: cortex.experiment.RemoteRun
    :members:


REST API Clients
==========================

AuthenticationClient
--------------------
.. autoclass:: cortex.auth.AuthenticationClient
 :members:

ConnectionClient
----------------
.. autoclass:: cortex.connection.ConnectionClient
    :members:

ExperimentClient
----------------
.. autoclass:: cortex.experiment.ExperimentClient
    :members:

ManagedContentClient
--------------------
.. autoclass:: cortex.content.ManagedContentClient
    :members:

SessionClient
-------------
.. autoclass:: cortex.session.SessionClient
    :members:

SecretsClient
-------------
.. autoclass:: cortex.secrets.SecretsClient
    :members:

SkillClient
-----------
.. autoclass:: cortex.skill.SkillClient
    :members:

Messages
--------
.. autoclass:: cortex.message.Message
    :members:

Exceptions
----------
.. autoclass:: cortex.exceptions.CortexException
   :members:
.. autoclass:: cortex.exceptions.AuthenticationException
   :members:
.. autoclass:: cortex.exceptions.BadTokenException
   :members:
.. autoclass:: cortex.exceptions.ConfigurationException
   :members:
.. autoclass:: cortex.exceptions.APIException
   :members:

Related Projects
================================

Cortex Fabric
--------------

Cortex Fabric provides a collaborative platform for building, deploying, and managing trusted AI systems.

See the `Cortex Fabric documentation. <https://cognitivescale.github.io/cortex-fabric>`_

Cortex Python Builders
------------------------

The sensa-python-builders library is an add-on library for use with the base sensa-python library that helps with building actions and skills.

See the `Cortex Python Builders Reference documentation. <https://cognitivescale.github.io/sensa-python-builders>`_

Cortex Python Profiles
-------------------------

The sensa-python-profiles library is an add-on for use with the base sensa-python library that helps with building and managing Profile-of-One profiles and schemas.

See the `Cortex Python Profiles Reference documentation. <https://cognitivescale.github.io/sensa-python-profiles>`_

