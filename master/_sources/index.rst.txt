**Home:** `Cortex Fabric Documentation <https://cognitivescale.github.io/cortex-fabric/>`_

Cortex Python Reference
=======================

This reference guide describes the base API client library to integrate with Cortex Fabric.
Refer to the `Cortex Fabric documentation <https://cognitivescale.github.io/cortex-fabric/>`_ for more info about how to use the library.

Cortex
------

.. autoclass:: cortex.client.Cortex
    :members:

CortexEnv
---------

.. autoclass:: cortex.env.CortexEnv
    :members:

Cortex Client
-------------

.. autoclass:: cortex.client.Client
    :members:

Cortex Experiment
-----------------

.. autoclass:: cortex.experiment.Experiment
    :members:

Cortex Skill
-------------

.. autoclass:: cortex.skill.Skill
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

ManagedContentClient
--------------------
.. autoclass:: cortex.content.ManagedContentClient
    :members:

SessionClient
-------------
.. autoclass:: cortex.session.SessionClient
    :members:

Types
-----
.. autoclass:: cortex.message.Message

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

The cortex-python-builders library is an add-on library for use with the base cortex-python library that helps with building actions and skills.

See the `Cortex Python Builders Reference documentation. <https://cognitivescale.github.io/cortex-python-builders>`_

Cortex Python Profiles
-------------------------

The cortex-python-profiles library is an add-on for use with the base cortex-python library that helps with building and managing Profile-of-One profiles and schemas.

See the `Cortex Python Profiles Reference documentation. <https://cognitivescale.github.io/cortex-python-profiles>`_

