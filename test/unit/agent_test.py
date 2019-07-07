"""
Copyright 2019 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import json
import unittest

from mocket.mockhttp import Entry
from mocket import mocketize

from cortex import Cortex, Message
from cortex.agent import Agent, ServiceActivation
from .fixtures import john_doe_token, build_mock_url, mock_api_endpoint


class TestAgent(unittest.TestCase):

    def setUp(self):
        self.cortex = Cortex.client(api_endpoint=mock_api_endpoint(), api_version=3, token=john_doe_token())

    def register_entry(self, verb, url, body):
        print('Registering mock for', verb, url)
        Entry.single_register(verb,
                              url,
                              status=200,
                              body=json.dumps(body))

    @mocketize
    def test_get_agent(self):
        agent_name = 'unittest/agent1'
        uri = Agent.URIS['get_agent'].format(name=agent_name)
        returns = {"name": agent_name}
        self.register_entry(Entry.GET, build_mock_url(uri), returns)

        agent = self.cortex.agent(agent_name)
        self.assertEqual(agent.name, agent_name)

    @mocketize
    def test_invoke_sync(self):
        agent_name = 'unittest/agent1'
        service_name = 'input1'
        activation_id = '123456789'
        activation = {'activationId': activation_id, 'status': 'COMPLETE', 'response': {'text': 'It works'}}
        activation_msg = {'activation': activation}

        agent_uri = Agent.URIS['get_agent'].format(name=agent_name)
        self.register_entry(Entry.GET, build_mock_url(agent_uri), {"name": agent_name})

        invoke_uri = Agent.URIS['invoke_service'].format(agent_name=agent_name, service_name=service_name)
        self.register_entry(Entry.POST, build_mock_url(invoke_uri), activation)

        activation_uri = ServiceActivation.URIS['activation'].format(activation_id=activation_id)
        self.register_entry(Entry.GET, build_mock_url(activation_uri), activation_msg)

        agent = self.cortex.agent(agent_name)
        self.assertEqual(agent.name, agent_name)

        msg = agent.invoke_service(service_name, self.cortex.message({'text': 'Testing...'}))
        self.assertEqual(msg.payload.get('text'), 'It works')

    @mocketize
    def test_invoke_async(self):
        agent_name = 'unittest/agent1'
        service_name = 'input1'
        activation_id = '123456789'
        activation = {'activationId': activation_id, 'status': 'COMPLETE', 'response': {'text': 'It works'}}
        activation_msg = {'activation': activation}

        agent_uri = Agent.URIS['get_agent'].format(name=agent_name)
        self.register_entry(Entry.GET, build_mock_url(agent_uri), {"name": agent_name})

        invoke_uri = Agent.URIS['invoke_service'].format(agent_name=agent_name, service_name=service_name)
        self.register_entry(Entry.POST, build_mock_url(invoke_uri), activation)

        activation_uri = ServiceActivation.URIS['activation'].format(activation_id=activation_id)
        self.register_entry(Entry.GET, build_mock_url(activation_uri), activation_msg)

        agent = self.cortex.agent(agent_name)
        self.assertEqual(agent.name, agent_name)

        service_activation = agent.invoke_service_async(service_name, self.cortex.message({'text': 'Testing...'}))
        self.assertEqual(service_activation._activation_id, activation_id)
