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

import urllib.parse
from cortex.serviceconnector import _Client, ServiceConnector
from cortex.utils import get_logger
from .camel import CamelResource
from .utils import raise_for_status_with_detail

log = get_logger(__name__)


class SchemaClient(_Client):
    """
    A client for the Cortex Actions API.
    """

    URIs = {
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._serviceconnector.version = 4

    def save_schema(self):
        raise NotImplementedError()


class Schema(CamelResource):
    """
    Represents a plan for accessing a service.
    """
    def __init__(self, schema, connector: ServiceConnector):
        super().__init__(schema, True)
        self._connector = connector

    @staticmethod
    def get_schema(name, project, client: SchemaClient):
        """
        Fetches a schema to work with.
        :param name: The name of the schema to retrieve.
        :param project; Project to get the schema from
        :param client: The client instance to use.
        :return: A schema object.
        """
        uri = 'projects/{projectId}/types/{name}'.format(projectId=project, name=urllib.parse.quote(name, safe=''))
        log.debug('Getting schema using URI: %s' % uri)
        r = client._serviceconnector.request('GET', uri)
        raise_for_status_with_detail(r)

        return Schema(r.json(), client._serviceconnector)
