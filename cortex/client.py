"""
Copyright 2023 Cognitive Scale, Inc. All Rights Reserved.

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
from .exceptions import (
    ProjectException,
    InvalidMessageTypeException,
    IncompleteMessageKeysException,
)
from .message import Message
from .utils import decode_JWT, get_logger, generate_token

log = get_logger(__name__)


class _Token:
    def __init__(self, token: str):
        self._token = token
        self._jwt = None
        if token:
            self._jwt = decode_JWT(self._token)

    def is_expired(self) -> bool:
        """Checks if the token's JWT has expired

        :return: A boolean indicating if the JWT has expired
        :rtype: bool
        """
        current_time = time.time()
        return not self._jwt or (self._jwt[0].get("exp", current_time) < current_time)

    @property
    def token(self) -> str:
        """Returns the token

        :return: The token
        :rtype: str
        """
        return self._token


class Client:
    """
    API client used to access Connections, Managed Content, Experiments, Secrets, Models, Sessions, Skills and Types in a Fabric cluster. Experiments also have a `local client` (:class:`cortex.experiment.local.LocalExperiment`) for data scientists to work without access to a Fabric cluster.

    Create an instance of the Cortex Fabric client. There are a few different ways in which you can instantiate a Client

    1. If the user has the Cortex CLI installed and configured to a Fabric environment, AND a default project is set, they can do the following:

    >>> from cortex.client import Cortex; client = Cortex.client()

    2. If the user has the Cortex CLI installed and configured, but a default project is not set:

    >>> from cortex.client import Cortex; client = Cortex.client(project="some-project")

    3. If the user does not have the Cortex CLI installed, or is using the cortex-python package from within a Skill (Daemon) running inside a Fabric cluster, they can simply extract the required parameters from the request object and create a Cortex client like below:

    .. code-block::

        from cortex.client import Cortex

        @app.post('/invoke')
        def start(req: dict):
            payload = req['payload']
            client = Cortex.client(api_endpoint=req["apiEndpoint"], project=req["projectId"], token=req["token"])
            client.experiments.list_experiments()
            ....

    4. If the user does not have the Cortex CLI installed, or is using the cortex-python package from within a **Skill(Job)** running inside a Fabric cluster, they can simply pass the `params` object passed into the Job script and create a Cortex client:

    .. code-block:: python

        # contents of main.py for a Skill (job)
        from cortex.client import Cortex

        def main(params):
            client = Cortex.from_message(params)

        if __name__ == "__main__":
            if len(sys.argv)<2:
                print("Message/payload argument is required")
                exit(1)
            # The last argument in sys.argv is the payload from cortex
            main(json.loads(sys.argv[-1]))


    :param url: Cortex fabric url
    :param token: (optional) Use JWT token to authenticate requests, will default to settings in ~/.cortex/config if not provided to generate JWT tokens
    :param project: (optional) Project name, must specify project for each request
    :param version: (optional) Fabric API version (default: 4)
    """  # pylint: disable=line-too-long

    def __init__(
        self,
        url: str,
        token: _Token = None,
        config: dict = None,
        project: str = None,
        version: int = VERSION,
        verify_ssl_cert: bool = False,
    ):
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
            from cortex.client import Cortex
            client = Cortex.client()
            client.experiments.list_experiments()
            client.experiments.save_experiment()
            client.experiments.list_runs()
            client.experiments.delete_runs()

        Refer to the documentation of :class:`cortex.experiment.ExperimentClient` to learn more about the methods available on the ExperimentClient

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
            from cortex.client import Cortex
            client = Cortex.client()
            client.connections.save_connection
            client.connections.get_connection

        Refer to the documentation of :class:`cortex.connection.ConnectionClient` to learn more about the methods available on the ConnectionClient

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
            from cortex.client import Cortex
            client = Cortex.client()
            client.content.list
            client.content.upload
            client.content.exists
            .....

        Refer to the documentation of :class:`cortex.content.ManagedContentClient` to learn more about the methods available on the ManagedContentClient

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
        different from the one configured with Cortex.client, please use :meth:`cortex.client.Client.models_client` instead

        .. code-block::

            ## use default .models client helper
            from cortex.client import Cortex
            client = Cortex.client()
            client.models.list_models()
            client.models.get_model()
            client.models.save_model()
            .....

        Refer to the documentation of :class:`cortex.model.ModelClient` to learn more about the methods available on the ModelClient

        :returns: An instance of this helper class that enables access to the Fabric Models API.
        :rtype: :class:`cortex.model.ModelClient`
        """  # pylint: disable=line-too-long
        return self._service_clients.get("models")

    def models_client(self, project: str = None) -> ModelClient:
        """Helper method to create a new :class:`cortex.model.ModelClient` instance that is configured to talk to another `project` than the default :attr:`cortex.client.Client._project`

        >>> modelc = client.models_client(project="another-project")

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
        """Returns a pre-initialised SecretsClient whose project has been set to the project configured for the Cortex.client.

        .. important::

            Note that, as of Fabric 6.3.3 and Fabric 6.4.0., you can only call :meth:`cortex.secrets.SecretsClient.get_secret` from within a skill running inside the Fabric cluster (won't work locally)

        If you want to access secrets for a project that is
        different from the one configured with Cortex.client, please use :meth:`cortex.client.Client.secrets_client` instead

        .. code-block::

            ## use default .secrets client helper
            from cortex.client import Cortex
            client = Cortex.client()
            client.models.get_secret()
            client.models.post_secret()
            .....

        Refer to the documentation of :class:`cortex.secrets.SecretsClient` to learn more about the methods available on the SecretsClient

        :returns: An instance of this helper class that enables access to the Fabric Secrets API.
        :rtype: :class:`cortex.secrets.SecretsClient`
        """  # pylint: disable=line-too-long
        return self._service_clients.get("secrets")

    def secrets_client(self, project: str = None) -> SecretsClient:
        """Helper method to create a new :class:`cortex.secrets.SecretsClient` instance that is configured to talk to another `project` than the default :attr:`cortex.client.Client._project`

        >>> secretsc = client.secrets_client(project="another-project")

        :param project: Project for which a secrets client is to be created, defaults to (the project configured with cortex.client.Client)
        :type project: str, optional
        :return: A secrets client
        :rtype: :class:`cortex.secrets.SecretsClient`
        """  # pylint: disable=line-too-long
        if project is not None:
            return SecretsClient(project=project)
        return self.secrets

    @property
    def skills(self) -> SkillClient:
        """Returns a pre-initialised SkillClient whose project has been set to the project configured for the Cortex.client.Client

        If you want to access Skills for a project that is
        different from the one configured with Cortex.client, please use :meth:`cortex.client.Client.skills_client` instead

        .. code-block::

            ## use default .skills client helper
            from cortex.client import Cortex
            client = Cortex.client()
            client.skills.get_skill()
            client.skills.save_skill()
            client.skills.delete_skill()
            client.skills.get_logs()
            client.skills.deploy()
            client.skills.undeploy()
            .....

        Refer to the documentation of :class:`cortex.skill.SkillClient` to learn more about the methods available on the SkillClient

        :returns: An instance of this helper class that enables access to the Fabric SKills API.
        :rtype: :class:`cortex.skill.SkillClient`
        """  # pylint: disable=line-too-long
        return self._service_clients.get("skills")

    def skills_client(self, project: str = None) -> SkillClient:
        """Helper method to create a new :class:`cortex.skill.SkillClient` instance that is configured to talk to another `project` than the default :attr:`cortex.client.Client._project`

        >>> skillsc = client.skills_client(project="another-project")

        :param project: Project for which a Skill client is to be created, defaults to (the project configured with cortex.client.Client)
        :type project: str, optional
        :return: A Skills client
        :rtype: :class:`cortex.skill.SkillClient`
        """  # pylint: disable=line-too-long
        if project is not None:
            return SkillClient(project=project)
        return self.skills

    @property
    def sessions(self) -> SessionClient:
        """Returns a pre-initialised SessionClient whose project has been set to the project configured for the Cortex.client.Client

        If you want to access Sessions for a project that is
        different from the one configured with Cortex.client, please use :meth:`cortex.client.Client.sessions_client` instead

        .. code-block::

            ## use default .sessions client helper
            from cortex.client import Cortex
            client = Cortex.client()
            client.sessions.start_session()
            client.sessions.get_session_data()
            client.sessions.put_session_data()
            client.sessions.delete_session()
            .....

        Refer to the documentation of :class:`cortex.session.SessionClient` to learn more about the methods available on the SessionClient

        :returns: An instance of this helper class that enables access to the Fabric Sessions API.
        :rtype: :class:`cortex.session.SessionClient`
        """  # pylint: disable=line-too-long
        return self._service_clients.get("sessions")

    def sessions_client(self, project: str = None) -> SessionClient:
        """Helper method to create a new :class:`cortex.session.SessionClient` instance that is configured to talk to another `project` than the default :attr:`cortex.client.Client._project`

        >>> sessionsc = client.sessions_client(project="another-project")

        :param project: Project for which a Sessions client is to be created, defaults to (the project configured with cortex.client.Client)
        :type project: str, optional
        :return: A Sessions client
        :rtype: :class:`cortex.session.SessionClient`
        """  # pylint: disable=line-too-long
        if project is not None:
            return SessionClient(project=project)
        return self.sessions

    @property
    def types(self) -> TypeClient:
        """Returns a pre-initialised TypeClient whose project has been set to the project configured for the Cortex.client.Client

        If you want to access Types for a project that is
        different from the one configured with Cortex.client, please use :meth:`cortex.client.Client.types_client` instead

        .. code-block::

            ## use default .types client helper
            from cortex.client import Cortex
            client = Cortex.client()
            client.types.get_type()
            client.types.save_type()
            .....

        Refer to the documentation of :class:`cortex.types.TypeClient` to learn more about the methods available on the TypeClient

        :returns: An instance of this helper class that enables access to the Fabric Types API.
        :rtype: :class:`cortex.types.TypeClient`
        """  # pylint: disable=line-too-long
        return self._service_clients.get("types")

    def types_client(self, project: str = None) -> TypeClient:
        """Helper method to create a new :class:`cortex.types.TypeClient` instance that is configured to talk to another `project` than the default :attr:`cortex.client.Client._project`

        >>> typesc = client.types_client(project="another-project")

        :param project: Project for which a Types client is to be created, defaults to (the project configured with cortex.client.Client)
        :type project: str, optional
        :return: A Types client
        :rtype: :class:`cortex.types.TypeClient`
        """  # pylint: disable=line-too-long
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
        """Return the configured base directory of this :class:`cortex.client.Local` instance

        :return: configured base directory
        :rtype: _type_
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
    ) -> Client:
        """
        Gets a client with the provided parameters. All parameters are optional and default to environment variable values if not specified. Client creation can fail if you don't have a default project set in your environment variables or the Cortex config file.

        .. important::

            You can also set a default project when configuring your Cortex CLI using `cortex configure --project <your-project>`.

            This value will be updated into the `$HOME/.cortex/config` file. If your Cortex config file `$HOME/.cortex/config` does not contain a default `project` set for the profile being used as the default one, you will need to set the project key when instantiating a :class:`cortex.client.Client`.

        **Example**

        >>> from cortex.client import Cortex
        >>> cortex = Cortex.client(project='example-project')

        :param api_endpoint: The Cortex URL.
        :param api_version: The version of the API to use with this client.
        :param verify_ssl_cert: A boolean to enable/disable SSL validation, or path to a CA_BUNDLE file or directory with certificates of trusted CAs (default: True)
        :param project: Cortex Project that you want to use.
        :param token: (optional) Use JWT token for authenticating requests, will default to settings in ~/.cortex/config if not provided
        :param config: (optional) Use Cortex personal access token config file to generate JWT tokens.

        :returns: An instance of :class:`cortex.client.Client`
        :rtype: :class:`cortex.client.Client`
        """  # pylint: disable=line-too-long
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
    def from_message(msg, verify_ssl_cert=None) -> Client:
        """Creates a Cortex client from a skill's input message, expects

        .. code-block::

            { api_endpoint:"..", token:"..", projectId:".."}

        :param msg: A message for constructing a Cortex Client.
        :param verify_ssl_cert: A boolean to enable/disable SSL validation, or path to a CA_BUNDLE file or directory with certificates of trusted CAs (default: True)

        :returns: A Cortex Client
        :rtype: :class:`cortex.client.Client`
        """  # pylint: disable=line-too-long
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
        """Create a Local Cortex implementation (mock)

        :param basedir: Root filesystem location, defaults to None
        :type basedir: str, optional
        :return: an instance of :class:`cortex.client.Local`
        :rtype: :class:`cortex.client.Local`
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
