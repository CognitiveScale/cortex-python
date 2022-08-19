"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

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

import unittest

from unittest.mock import Mock
from cortex import Cortex
from cortex.message import Message
import pytest
from cortex.connection import ConnectionClient
from cortex.content import ManagedContentClient
from cortex.experiment import ExperimentClient
from cortex.model import ModelClient
from cortex.secrets import SecretsClient
from cortex.session import SessionClient
from cortex.schema import SchemaClient
from cortex.skill import SkillClient

from .fixtures import john_doe_subject, john_doe_token

token = john_doe_token()
api_endpoint = 'https://api.test.cortex'
api_version = 4

class TestCortex(unittest.TestCase):
    def test_client(self):
        account = 'unittest'
        cortex = Cortex.client(
            api_endpoint=api_endpoint,
            api_version=api_version,
            project=account,
            token=token
        )
        assert cortex._url == api_endpoint
        assert cortex._token._token == token
        assert cortex._token._jwt[1]['sub'] == john_doe_subject()

    def test_message_creation(self):
        cortex = Cortex.client(
            api_endpoint=api_endpoint,
            api_version=api_version,
            project='unittest',
            token=token
        )
        message = cortex.message({'foo': 'bar'})
        assert isinstance(message, Message)
        assert message.apiEndpoint == cortex._url
        assert message.token == cortex._token.token
        assert message.token == token

    # Basic test check that skill invoke message creates a client properly
    def test_client_fromMessage(self):
        project = 'msgTest'
        message = {
            'apiEndpoint': api_endpoint,
            'token': token,
            'projectId': project,
            'channelId': 'channel',
            'payload': {'test':'some text'},
            'activationId': 'activation',
            'properties': {'someprop':'propval'},
        }
        client = Cortex.from_message(message)
        # Only these properties are required to create a client
        assert client._project == project
        assert client._url == api_endpoint
        assert client._token.token == token

    # Check message format
    def test_client_fromMessage_errs(self):
        messages = [
            None,
            {},
            'some string',
            12,
            {'apiEndpoint': api_endpoint},
            {'apiEndpoint': api_endpoint, 'projectId': 'project'},
            {'apiEndpoint': api_endpoint, 'token': token},
        ]
        for message in messages:
            with pytest.raises(Exception, match='Skill message'):
                Cortex.from_message(message)

    def test_proj_override(self):
        project = 'clientProj'
        message = {
            'apiEndpoint': api_endpoint,
            'token': token,
            'projectId': project,
        }
        client = Cortex.from_message(message)
        tests =[
            [ConnectionClient(client), project, 'get_connection', ('foo')],
            [ConnectionClient('url', project='noclient'), 'noclient', 'get_connection', ('foo')],
            [ConnectionClient(client, project='withclient'), 'withclient', 'get_connection',('foo')],
            [ManagedContentClient(client), project, 'exists',('key')],
            [ManagedContentClient('url', project='noclient'), 'noclient', 'exists',('key')],
            [ManagedContentClient(client, project='withclient'), 'withclient', 'exists',('key')],
            [ModelClient(client), project, 'get_model', ('model')],
            [ModelClient('url', project='noclient'), 'noclient', 'get_model', ('model')],
            [ModelClient(client, project='withclient'), 'withclient', 'list_models', None],
            [ExperimentClient(client), project, 'list_experiments', None],
            [ExperimentClient('url', project='noclient'),'noclient', 'get_experiment', ('experi')],
            [ExperimentClient(client, project='withclient'),'withclient', 'list_experiments', None],
            [SecretsClient(client), project, 'get_secret', ('secret')],
            [SecretsClient('url', project='noclient'), 'noclient', 'get_secret', ('secret')],
            [SecretsClient(client, project='withclient'), 'withclient', 'get_secret', ('secret')],
            [SchemaClient(client), project, 'get_schema', ('schema')],
            [SchemaClient('url', project='noclient'), 'noclient', 'get_schema', ('schema')],
            [SchemaClient(client, project='withclient'), 'withclient', 'get_schema', ('schema')],
            [SessionClient(client), project, 'get_session_data', ('sess')],
            [SessionClient('url', project='noclient'), 'noclient' , 'get_session_data', ('sess')],
            [SessionClient(client, project='withclient'), 'withclient', 'get_session_data', ('sess')],
            [SkillClient(client), project, 'list_skills', None],
            [SkillClient('url', project='noclient'), 'noclient','get_skill', ('skill')],
            [SkillClient(client, project='withclient'), 'withclient','list_skills', None],
        ]
        for client_inst, project, fun_name, fun_args in tests:
            print(f'Testing project {type(client_inst)}.{fun_name} with {project}')
            mock = Mock()
            client_inst._serviceconnector.request = mock
            func = getattr(client_inst, fun_name)
            if fun_args is None:
                func()
            else:
                func(fun_args)
            uri = mock.call_args.kwargs.get('uri')
            assert project in uri
