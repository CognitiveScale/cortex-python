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
from .serviceconnector import ServiceConnector
from .env import CortexEnv
from .exceptions import ProjectException
from .experiment import Experiment, LocalExperiment, ExperimentClient
from .message import Message
from .connection import Connection, ConnectionClient
from .secrets import SecretsClient, Secret
from .session import Session, SessionClient
from .utils import decode_JWT, get_logger, generate_token

_DEFAULT_API_VERSION = 4

_msg_token_exp_no_creds = """
Your Cortex token is expired, and the required credentials for auto-refresh have not been provided. Supply these credentials; account, username,
and password.  Please login again to retrieve a valid token.
"""

log = get_logger(__name__)


class _Token(object):

    def __init__(self, token: str):
        self._token = token
        self._jwt = None
        if token:
            self._jwt = decode_JWT(self._token)

    def is_expired(self):
        current_time = time.time()
        return not self._jwt or (self._jwt.get('exp', current_time) < current_time)

    @property
    def token(self):
        return self._token


class Client(object):
    """
    API client used to access agents, skills, and datasets.
    """

    def __init__(self, url: str, token: _Token = None, config: dict = None, project: str = None, version: int = 4,
                 verify_ssl_cert: bool = False):

        self._token = token
        self._config = config
        self._project = project
        self._url = url
        self._version = version
        self._verify_ssl_cert = verify_ssl_cert

    def get_connection(self, name: str, version: str = '4'):
        """
        Gets an connection with the specified name.
        """
        if not self._token.token:
            self._token = _Token(generate_token(self._config))
        conn_client = ConnectionClient(self._url, version, self._token.token, self._config)
        return Connection.get_connection(name, self._project, conn_client)

    def get_secret(self, name: str, version: str = '4'):
        """
        Gets a secret with the specified name.
        """
        if not self._token.token:
            self._token = _Token(generate_token(self._config))
        sec_client = SecretsClient(self._url, version, self._token.token, self._config)
        return Secret.get_secret(name, self._project, sec_client)

    def session(self, session_id=None, ttl=None) -> Session:
        """
        Gets a session with the specified identifier.
        """
        if not self._token.token:
            self._token = _Token(generate_token(self._config))
        session_client = SessionClient(self._url, self._version, self._token.token, self._config)
        if not session_id:
            return Session.start(session_client, self._project, ttl)
        return Session(session_id, session_client, self._project)

    def experiment(self, name: str, version: str = '4', model_id=None):
        """
        Gets an experiment with the specified name.
        """
        if not self._token.token:
            self._token = _Token(generate_token(self._config))
        exp_client = ExperimentClient(self._url, version, self._token.token, self._config)
        return Experiment.get_experiment(name, self._project, exp_client, model_id)

    def message(self, payload: dict, properties: dict = None) -> Message:
        """Constructs a Message from payload and properties if given.

        :param payload: The payload to include in the Message.
        :param properties: The properties to include in the Message.
        :return: A Message object.
        """
        if not self._token.token:
            self._token = _Token(generate_token(self._config))
        params = {'payload': payload}
        if properties:
            params['properties'] = properties
        params['apiEndpoint'] = self._url
        params['token'] = self._token.token
        return Message(params)

    def _mk_connector(self):
        return ServiceConnector(self._url, self._version,
                                self._token.token, self._config,
                                self._verify_ssl_cert, self._project)

    # expose this to allow developer to pass client instance into Connectors
    def to_connector(self):
        return self._mk_connector()


class Local:
    """
    Provides local, on-disk implementations of Cortex APIs.
    """

    def __init__(self, basedir=None):
        self._basedir = basedir

    def experiment(self, name: str) -> LocalExperiment:
        return LocalExperiment(name, self._basedir)


class Cortex(object):
    """
    Entry point to the Cortex API.
    """

    @staticmethod
    def client(api_endpoint: str = None, api_version: int = _DEFAULT_API_VERSION, verify_ssl_cert=None,
               token: str = None, config: dict = None, project: str = None):
        """
        Gets a client with the provided parameters. All parameters are optional and default to environment variable values if not specified.

        **Example**

        >>> from cortex import Cortex
        >>> cortex = Cortex.client(project='example-project')

        :param api_endpoint: The Cortex URL.
        :param api_version: The version of the API to use with this client.
        :param verify_ssl_cert: A boolean to enable/disable SSL validation, or path to a CA_BUNDLE file or directory with certificates of trusted CAs (default: True)
        :param project: Cortex Project that you want to use.
        """
        env = CortexEnv(api_endpoint=api_endpoint, token=token, config=config, project=project)

        if not api_endpoint:
            api_endpoint = env.api_endpoint

        if not token:
            token = env.token

        if not config:
            config = env.config

        if not project:
            project = env.project

        if not project:
            raise ProjectException('Please Provide Project Name that you want to access Cortex Assets for')

        t = _Token(token)

        return Client(url=api_endpoint, version=api_version, token=t, config=config, project=project,
                      verify_ssl_cert=verify_ssl_cert)

    @staticmethod
    def from_message(msg, verify_ssl_cert=None):
        """
        Creates a Cortex client from a skill's input message, expects { api_endpoint:'..', token:'..', projectId:'..' }
        :param msg: A message for constructing a Cortex Client.
        :param verify_ssl_cert: A boolean to enable/disable SSL validation, or path to a CA_BUNDLE file or directory with certificates of trusted CAs (default: True)
        """
        keys = ('apiEndpoint', 'token', 'projectId')
        if not all(key in msg for key in keys):
            raise Exception(f'Skill message must contain these keys: {keys}')
        return Cortex.client(api_endpoint=msg.get('apiEndpoint'), token=msg.get('token'), project=msg.get('projectId'), verify_ssl_cert=verify_ssl_cert)

    @staticmethod
    def local(basedir=None):
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
        config = input('Cortex Personal Access Config: ')
        project = input('Project: ')
        os.environ['CORTEX_PERSONAL_ACCESS_CONFIG'] = config
        if project:
            os.environ['CORTEX_PROJECT'] = project
