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

from .utils import get_logger
from .serviceconnector import ServiceConnector
from .camel import CamelResource

log = get_logger(__name__)


class Skill(CamelResource):
    """
     Computational components of an agent; executes an
     atomic unit of work and can be triggered by one or more inputs to produce
     one or more outputs.
    """

    def __init__(self, skill, project, connector: ServiceConnector):
        super().__init__(skill, True)
        self._connector = connector
        self._project = project

    @staticmethod
    def get_skill(name: str, project: str, connector: ServiceConnector):
        raise NotImplementedError()
