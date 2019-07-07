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

from .message import Message
from .utils import get_logger
from .action import ActionClient
from .serviceconnector import ServiceConnector
from .camel import CamelResource

log = get_logger(__name__)


class Skill(CamelResource):
    """
     Computational components of an agent; executes an
     atomic unit of work and can be triggered by one or more inputs to produce
     one or more outputs.
    """

    def __init__(self, skill, connector: ServiceConnector):
        super().__init__(skill, True)
        self._connector = connector

    def _merge_properties(self, msg_props):
        if self.properties:
            for prop in self.properties:
                name = prop.get('name')
                value = prop.get('value', prop.get('defaultValue'))

                if name in msg_props or not value:
                    continue

                msg_props[name] = value

        return msg_props

    def invoke(self, input_name: str, message: Message, timeout=30):
        """
        Invokes the skill with a given message.

        :param input_name: Identifier for an input to this skill.
        :param message: The message used for the invocation.
        """
        for input in self.inputs:
            if input['name'] == input_name:
                routing = input['routing']
                action_name = routing.get('all', {}).get('action')
                if action_name:
                    action_client = ActionClient(self._connector.url, self._connector.version, self._connector.token)

                    # Prepare message properties
                    if not message.properties:
                        message.properties = {}

                    # Add Skill properties that are set to the message
                    message.properties = self._merge_properties(message.properties)

                    return Message(action_client.invoke_action(action_name, message.to_params()))
                else:
                    raise Exception('Skill invoke only works with "all" routing')
        else:
            raise Exception('No inputs defined')

    @staticmethod
    def get_skill(name: str, connector: ServiceConnector):
        """
        Fetches a skill to work with.

        :param name: The name of the skill to retrieve.
        :param connector: connector to use
        :return: A skill object.
        """
        uri = 'catalog/skills/{name}'.format(name=name)
        log.debug('Getting skill using URI: %s' % uri)
        r = connector.request('GET', uri)
        r.raise_for_status()

        return Skill(r.json(), connector)
