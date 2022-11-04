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
from cortex.serviceconnector import _Client
from cortex.utils import get_logger
from .camel import CamelResource
from .utils import raise_for_status_with_detail

log = get_logger(__name__)


class SchemaClient(_Client):
    """
    A client for the Cortex Schema API.
    """

    URIs = {
        'schema': 'projects/{projectId}/types/{name}',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save_schema(self):
        raise NotImplementedError()

    def get_schema(self, name):
        """
        Fetches a schema to work with.
        :param name: The name of the schema to retrieve.
        :return: A schema object.
        """
        uri = self.URIs['schema'].format(projectId=self._project(), name=urllib.parse.quote(name, safe=''))
        log.debug('Getting schema using URI: %s' % uri)
        r = self._serviceconnector.request('GET', uri=uri)
        raise_for_status_with_detail(r)
        return Schema(r.json(), self._serviceconnector)


class Schema(CamelResource):
    """
    Represents a plan for accessing a schema.
    """
    def __init__(self, schema, client: SchemaClient):
        super().__init__(schema, True)
        self._client = client
        self._project = client.project
