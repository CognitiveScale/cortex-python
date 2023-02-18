"""
Copyright 2021 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import time
from .constant import VERSION
from .experiment.local import LocalExperiment
from .connection import ConnectionClient
from .content import ManagedContentClient
from .model import ModelClient
from .secrets import SecretsClient
from .session import SessionClient
from .skill import SkillClient
from .types import TypeClient
from .experiment import ExperimentClient
from .serviceconnector import ServiceConnector
from .env import CortexEnv
from .exceptions import ProjectException
from .message import Message
from .utils import decode_JWT, get_logger, generate_token

log = get_logger(__name__)


class InvalidMessageTypeException(Exception):
    """_summary_

    :param Exception: _description_
    :type Exception: _type_
    """


class IncompleteMessageKeysException(Exception):
    """_summary_

    :param Exception: _description_
    :type Exception: _type_
    """


class _Token:
    def __init__(self, token: str):
        self._token = token
        self._jwt = None
        if token:
            self._jwt = decode_JWT(self._token)

    def is_expired(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        current_time = time.time()
        return not self._jwt or (self._jwt[0].get("exp", current_time) < current_time)

    @property
    def token(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self._token


class Client:
    """
    API client used to access agents, skills, and datasets.
    """

    def __init__(
        self,
        url: str,
        token: _Token = None,
        config: dict = None,
        project: str = None,
        version: int = VERSION,
        verify_ssl_cert: bool = False,
    ):
        """
        Create an instance of the Cortex Fabric client

        :param url: Cortex fabric url
        :param token: (optional) Use JWT token to authenticate requests,
        will default to settings in ~/.cortex/config if not provided to
        generate JWT tokens
        :param project: (optional) Project name, must specify project for each request
        :param version: (optional) Fabric API version (default: 4)
        """

        self._token = token
        self._config = config
        self._project = project
        self._url = url
        self._version = version
        self._verify_ssl_cert = verify_ssl_cert

        self._service_clients = {
            "connections": ConnectionClient(self),
            "content": ManagedContentClient(self),
            "experiments": ExperimentClient(self),
            "models": ModelClient(self),
            "secrets": SecretsClient(self),
            "sessions": SessionClient(self),
            "skills": SkillClient(self),
            "types": TypeClient(self),
        }

    def message(self, payload: dict, properties: dict = None) -> Message:
        """Constructs a Message from payload and properties if given. This is useful for
        testing skills, as this the message passed when skills are invoked
        :param payload: The payload to include in the Message.
        :param properties: The properties to include in the Message.
        :return: A Message object.
        """
        if not self._token.token:
            self._token = _Token(generate_token(self._config))
        params = {"payload": payload}
        if properties:
            params["properties"] = properties
        params["apiEndpoint"] = self._url
        params["token"] = self._token.token
        return Message(params)

    def _mk_connector(self):
        return ServiceConnector(
            self._url,
            self._version,
            self._token.token,
            self._config,
            self._verify_ssl_cert,
            self._project,
        )

    # expose this to allow developer to pass client instance into Connectors
    def to_connector(self) -> ServiceConnector:
        """_summary_

        :return: _description_
        :rtype: ServiceConnector
        """
        return self._mk_connector()

    def _repr_pretty_(self, p, cycle):
        # pylint: disable=unused-argument,invalid-name
        p.text(str(self))
        p.text(f"Url: {self._url}\n")
        p.text(f"Project: {self._project}\n")

    @property
    def experiments(self) -> ExperimentClient:
        """Returns a pre-initialised ExperimentClient whose project has been set to the project configured for the Cortex.client.

        If you want to access experiments for a project that is
        different from the one configured with Cortex.client, please use :meth:`cortex.client.Client.experiments_client` instead

        .. code-block::

            ## use default .experiments client helper
            from cortex import Cortex
            client = Cortex.client()
            client.experiments.list_experiments()
            client.experiments.save_experiments()
            client.experiments.list_runs()
            client.experiments.delete_runs()
        ::

        Refer to the documentation of :mod:`cortex.experiment.ExperimentClient` to learn more about the methods available on the ExperimentClient

        :returns: An instance of this helper class that enables access to the Fabric Experiments API.
        :rtype: :class:`cortex.experiment.ExperimentClient`
        """  # pylint: disable=line-too-long
        return self._service_clients.get("experiments")

    def experiments_client(self, project: str = None) -> ExperimentClient:
        """Helper method to create a new :class:`cortex.experiment.ExperimentClient` instance that is configured to talk to another `project` than the default :attr:`cortex.client.Client._project`

        >>> expc = client.experiments_client(project="another-project")

        :param project: Project for which an experiments client is to be created, defaults to (the project configured with cortex.client.Client)
        :type project: str, optional
        :return: An experiment client
        :rtype: :class:`cortex.experiment.ExperimentClient`
        """  # pylint: disable=line-too-long
        if project is not None:
            return ExperimentClient(project=project)
        return self.experiments

    @property
    def connections(self) -> ConnectionClient:
        """Returns a pre-initialised ConnectionClient whose project has been set to the project configured for the Cortex.client.

        If you want to access connections for a project that is
        different from the one configured with Cortex.client, please use :meth:`cortex.client.Client.connections_client` instead

        .. code-block::

            ## use default .connections client helper
            from cortex import Cortex
            client = Cortex.client()
            client.connections.save_connection
            client.connections.get_connection
        ::

        Refer to the documentation of :mod:`cortex.connection.ConnectionClient` to learn more about the methods available on the ConnectionClient

        :returns: An instance of this helper class that enables access to the Fabric Connections API.
        :rtype: :class:`cortex.connection.ConnectionClient`
        """  # pylint: disable=line-too-long
        return self._service_clients.get("connections")

    def connections_client(self, project: str = None) -> ConnectionClient:
        """Helper method to create a new :class:`cortex.connection.ConnectionClient` instance that is configured to talk to another `project` than the default :attr:`cortex.client.Client._project`

        >>> connc = client.connections_client(project="another-project")

        :param project: Project for which a connections client is to be created, defaults to (the project configured with cortex.client.Client)
        :type project: str, optional
        :return: A connection client
        :rtype: :class:`cortex.connection.ConnectionClient`
        """  # pylint: disable=line-too-long
        if project is not None:
            return ConnectionClient(project=project)
        return self.connections

    @property
    def content(self) -> ManagedContentClient:
        """Returns a pre-initialised ManagedContentClient whose project has been set to the project configured for the Cortex.client.

        If you want to access managed content for a project that is
        different from the one configured with Cortex.client, please use :meth:`cortex.client.Client.content_client` instead

        .. code-block::

            ## use default .content client helper
            from cortex import Cortex
            client = Cortex.client()
            client.content.list
            client.content.upload
            client.content.exists
            .....
        ::

        Refer to the documentation of :mod:`cortex.content.ManagedContentClient` to learn more about the methods available on the ManagedContentClient

        :returns: An instance of this helper class that enables access to the Fabric Managed Content API.
        :rtype: :class:`cortex.content.ManagedContentClient`
        """  # pylint: disable=line-too-long
        return self._service_clients.get("content")

    def content_client(self, project: str = None) -> ManagedContentClient:
        """Helper method to create a new :class:`cortex.connection.ManagedContentClient` instance that is configured to talk to another `project` than the default :attr:`cortex.client.Client._project`

        >>> contentc = client.content_client(project="another-project")

        :param project: Project for which a managed content client is to be created, defaults to (the project configured with cortex.client.Client)
        :type project: str, optional
        :return: A managed content client
        :rtype: :class:`cortex.connection.ManagedContentClient`
        """  # pylint: disable=line-too-long
        if project is not None:
            return ManagedContentClient(project=project)
        return self.content

    @property
    def models(self) -> ModelClient:
        """Returns a pre-initialised ModelClient whose project has been set to the project configured for the Cortex.client.

        If you want to access models for a project that is
        different from the one configured with Cortex.client, please use :meth:`cortex.client.Client.model_client` instead

        .. code-block::

            ## use default .models client helper
            from cortex import Cortex
            client = Cortex.client()
            client.models.list_models()
            client.models.get_model()
            client.models.save_model()
            .....
        ::

        Refer to the documentation of :mod:`cortex.model.ModelClient` to learn more about the methods available on the ModelClient

        :returns: An instance of this helper class that enables access to the Fabric Models API.
        :rtype: :class:`cortex.model.ModelClient`
        """  # pylint: disable=line-too-long
        return self._service_clients.get("models")

    def models_client(self, project: str = None) -> ModelClient:
        """Helper method to create a new :class:`cortex.model.ModelClient` instance that is configured to talk to another `project` than the default :attr:`cortex.client.Client._project`

        >>> modelc = client.model_client(project="another-project")

        :param project: Project for which a models client is to be created, defaults to (the project configured with cortex.client.Client)
        :type project: str, optional
        :return: A models client
        :rtype: :class:`cortex.model.ModelClient`
        """  # pylint: disable=line-too-long
        if project is not None:
            return ModelClient(project=project)
        return self.models

    @property
    def secrets(self) -> SecretsClient:
        """_summary_

        :return: _description_
        :rtype: SecretsClient
        """
        return self._service_clients.get("secrets")

    def secrets_client(self, project: str = None) -> SecretsClient:
        """_summary_

        Args:
            project (str, optional): _description_. Defaults to None.

        Returns:
            SecretsClient: _description_
        """
        if project is not None:
            return SecretsClient(project=project)
        return self.secrets

    @property
    def skills(self) -> SkillClient:
        """_summary_

        Returns:
            SkillClient: _description_
        """
        return self._service_clients.get("skills")

    def skills_client(self, project: str = None) -> SkillClient:
        """_summary_

        Args:
            project (str, optional): _description_. Defaults to None.

        Returns:
            SkillClient: _description_
        """
        if project is not None:
            return SkillClient(project=project)
        return self.skills

    @property
    def sessions(self) -> SessionClient:
        """_summary_

        Returns:
            SessionClient: _description_
        """
        return self._service_clients.get("sessions")

    def sessions_client(self, project: str = None) -> SessionClient:
        """_summary_

        Args:
            project (str, optional): _description_. Defaults to None.

        Returns:
            SessionClient: _description_
        """
        if project is not None:
            return SessionClient(project=project)
        return self.sessions

    @property
    def types(self) -> TypeClient:
        """_summary_

        Returns:
            TypeClient: _description_
        """
        return self._service_clients.get("types")

    def types_client(self, project: str = None) -> TypeClient:
        """_summary_

        Args:
            project (str, optional): _description_. Defaults to None.

        Returns:
            TypeClient: _description_
        """
        if project is not None:
            return TypeClient(project=project)
        return self.types


class Local:
    """
    Provides local, on-disk implementations of Cortex APIs.
    """

    def __init__(self, basedir=None):
        self._basedir = basedir

    def experiment(self, name: str) -> LocalExperiment:
        """
        Create an experiment without connecting to Cortex fabric
        :param name: Experiment name
        :return: Experiment instance
        """
        return LocalExperiment(name, self.basedir)

    @property
    def basedir(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self._basedir


class Cortex:
    """
    Entry point to the Cortex API.
    """

    @staticmethod
    def client(
        api_endpoint: str = None,
        api_version: int = 4,
        verify_ssl_cert=None,
        token: str = None,
        config: dict = None,
        project: str = None,
        profile: str = None,
    ):
        """
        Gets a client with the provided parameters. All parameters are optional and default to
        environment variable values if not specified.

        **Example**

        >>> from cortex import Cortex
        >>> cortex = Cortex.client(project='example-project')

        :param api_endpoint: The Cortex URL.
        :param api_version: The version of the API to use with this client.
        :param verify_ssl_cert: A boolean to enable/disable SSL validation, or path to a CA_BUNDLE
        file or directory with certificates of trusted CAs (default: True)
        :param project: Cortex Project that you want to use.
        :param token: (optional) Use JWT token for authenticating requests, will default to
        settings in ~/.cortex/config if not provided
        :param config: (optional) Use Cortex personal access token config file to
        generate JWT tokens.
        """
        env = CortexEnv(
            api_endpoint=api_endpoint,
            token=token,
            config=config,
            project=project,
            profile=profile,
        )

        if not api_endpoint:
            api_endpoint = env.api_endpoint

        if not token:
            token = env.token

        if not config:
            config = env.config

        if not project:
            project = env.project

        if not project:
            raise ProjectException(
                "Please Provide Project Name that you want to access Cortex Assets for"
            )

        tkn = _Token(token)

        return Client(
            url=api_endpoint,
            version=api_version,
            token=tkn,
            config=config,
            project=project,
            verify_ssl_cert=verify_ssl_cert,
        )

    @staticmethod
    def from_message(msg, verify_ssl_cert=None):
        """
        Creates a Cortex client from a skill's input message, expects
        { api_endpoint:"..", token:"..", projectId:".."}
        :param msg: A message for constructing a Cortex Client.
        :param verify_ssl_cert: A boolean to enable/disable SSL validation, or path to a CA_BUNDLE
        file or directory with certificates of trusted CAs (default: True)
        """
        if not isinstance(msg, dict):
            raise InvalidMessageTypeException(
                f"Skill message must be a `dict` not a {type(msg)}"
            )
        keys = ("apiEndpoint", "token", "projectId")
        if not all(key in msg for key in keys):
            raise IncompleteMessageKeysException(
                f"Skill message must contain these keys: {keys}"
            )
        return Cortex.client(
            api_endpoint=msg.get("apiEndpoint"),
            token=msg.get("token"),
            project=msg.get("projectId"),
            verify_ssl_cert=verify_ssl_cert,
        )

    @staticmethod
    def local(basedir=None):
        """_summary_

        Args:
            basedir (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        return Local(basedir)

    @staticmethod
    def login():
        """
        Login to Cortex6. The function prompts the caller for Cortex Personal Access Config.

        **Example**

        >>> Cortex.login()
        Cortex Personal Access Config: Cortex Personal Access Config
        Cortex Project: The project that you to start using you Cortex assets from. (Not required)
        """
        config = input("Cortex Personal Access Config: ")
        project = input("Project: ")
        os.environ["CORTEX_PERSONAL_ACCESS_CONFIG"] = config
        if project:
            os.environ["CORTEX_PROJECT"] = project
