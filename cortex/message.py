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

from typing import Dict

from .utils import get_logger
from .camel import Document
from .env import CortexEnv

log = get_logger(__name__)


class Message(Document):
    # pylint: disable=line-too-long
    """
    Wraps a set of parameters or a payload when invoking an action, skill, or agent.

    The following keys are valid in the params dictionary

        .. code-block::

            {
                "activationId": "Request ID for the current execution",
                "agentName": "Name of the agent invoking the skill, will be empty for skill invokes",
                "apiEndpoint": "URI of the API server to use when making requests to platform services in processing of this message.",
                "channelId": "ID of the channel (wire) this message was sent on",
                "outputName": "Output name defined in the agent definition, can be overridden",
                "payload": "JSON payload passed to the skill",
                "projectId": "Project to which this skill belongs to",
                "properties": "Properties merged from Skill definition, Skill reference, and Agent definition.",
                "sessionId": "The ID of the session associated with this message, this will be the activationId unless provided externally",
                "skillName": "The name of the skill being invoked.",
                "timestamp": "Timestamp of the invoke",
                "token": " The JWT token to be used for making authenticated requests to APIs needed to process this message."
            }
    """

    def __init__(self, params: Dict = None):
        if params is None:
            params = {}

        super().__init__(params, False)
        self._params = params

    def to_params(self) -> Dict:
        """
        Gets the parameters in the message.
        """
        return self._params

    def __setattr__(self, key, value):
        super().__setattr__(key, value)

        if not key.startswith("_"):
            self._params[key] = value

    @staticmethod
    def from_env(**kwargs):
        """Creates an instance of :class:`cortex.message.Message` by reading from existing environment and cortex profile

        :return: :class:`cortex.message.Message` pre-populated with params loaded from pre-existing Cortex environment variables or Cortex profile
        :rtype: :class:`cortex.message.Message`
        """
        env = CortexEnv(**kwargs)

        params = {}
        if env.api_endpoint:
            params["apiEndpoint"] = env.api_endpoint
        if env.token:
            params["token"] = env.token

        return Message(params)
