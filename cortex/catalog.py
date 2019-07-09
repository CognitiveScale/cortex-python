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

from typing import Dict
from .serviceconnector import _Client


class CatalogClient(_Client):
    """
    A client for the catalog REST API.
    """

    URIs = {'types': 'catalog/types',
            'agents': 'catalog/agents',
            'skills': 'catalog/skills'
            }

    def save_schema(self, type: Dict[str, object]):
        """
        Saves a schema.

        :param type: A Cortex schema as dict.
        """
        return self._post_json(self.URIs['types'], type)

    def save_agent(self, agent: Dict[str, object]):
        """
        Saves an agent.

        :param agent: A Cortex agent as dict.
        """
        return self._post_json(self.URIs['agents'], agent)

    def save_skill(self, skill: Dict[str, object]):
        """
        Saves a skill.

        :param skill: A Cortex skill as dict.
        """
        return self._post_json(self.URIs['skills'], skill)
