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

import time
import json
from .message import Message
from .utils import get_logger
from .serviceconnector import ServiceConnector
from .camel import Document, CamelResource
from .utils import raise_for_status_with_detail

log = get_logger(__name__)


class ServiceActivation(Document):
    """
    Gets the activation status for a service activation.
    """
    URIS = {'activation': 'agents/services/activations/{activation_id}'}

    def __init__(self, activation, connector: ServiceConnector):
        super().__init__(activation, True)
        self._activation_id = activation.get('activationId')
        self._session_id = activation.get('sessionId')
        self._instance_id = activation.get('instanceId')
        self._connector = connector
        self._start = activation.get('start') or time.time()
        self._end = activation.get('end') or -1

    def result(self, timeout=0):
        now = time.time()
        end = now + timeout

        while now <= end:
            activation = self._fetch_activation()
            if activation.get('status') == 'COMPLETE':
                params = {
                    'payload': activation.get('response'),
                    'instanceId': activation.get('instanceId'),
                    'channelId': activation.get('channelId'),
                    'sessionId': activation.get('sessionId')
                }

                return Message(params)
            elif activation.get('status') == 'ERROR':
                params = {
                    'payload': activation.get('response') or activation.get('error'),
                    'instanceId': activation.get('instanceId'),
                    'channelId': activation.get('channelId'),
                    'sessionId': activation.get('sessionId'),
                    'error': True
                }

                return Message(params)
            else:
                time.sleep(1)
                now = time.time()

        raise TimeoutError('Timeout waiting for result')

    def get_status(self):
        activation = self._fetch_activation()
        return activation.get('status')

    def _fetch_activation(self):
        uri = self.URIS['activation'].format(activation_id=self._activation_id)
        r = self._connector.request('GET', uri)
        raise_for_status_with_detail(r)

        rsp = r.json()
        return rsp.get('activation')


class Agent(CamelResource):
    """
    A Cortex5 agent, which represents the deployable applications
    that aggregate the skills, inputs and outputs, and data flows.
    """
    URIS = {
        'get_agent': 'catalog/agents/{name}',
        'invoke_service': 'agents/{agent_name}/services/{service_name}'
    }

    def __init__(self, agent, connector: ServiceConnector):
        super().__init__(agent, True)
        self._connector = connector

    def invoke_service(self, service_name: str, message: Message, timeout=30):
        """
        Invokes a service, polling for a result for the number of seconds specified when the service times out.

        :param service_name: The name of the service to invoke.
        :param message: The payload for the service invocation.
        :param timeout: Number of seconds to poll for a result.
        :return: Service activation result.
        """
        activation = self.invoke_service_async(service_name, message)
        return activation.result(timeout)


    def invoke_service_async(self, service_name: str, message: Message) -> ServiceActivation:
        """
        Invokes a service.

        :param service_name: The name of the service to invoke.
        :param message: The payload for the service invocation.
        :return: Service activation.
        """
        uri = self.URIS['invoke_service'].format(agent_name=self.name, service_name=service_name)
        r = self._connector.request(method='POST', uri=uri, body=json.dumps(message.to_params()), headers={'Content-Type': 'application/json'})
        raise_for_status_with_detail(r)

        return ServiceActivation(r.json(), self._connector)

    @staticmethod
    def get_agent(name: str, connector: ServiceConnector):
        """
        Fetches an agent to work with.

        :param name: The name of the agent to retrieve.
        :param connector: A service connector.
        :return: An agent object.
        """
        uri = Agent.URIS['get_agent'].format(name=name)
        log.debug('Getting agent using URI: %s' % uri)
        r = connector.request('GET', uri)
        raise_for_status_with_detail(r)

        return Agent(r.json(), connector)
