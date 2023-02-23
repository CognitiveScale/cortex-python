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

import urllib.parse
from cortex.serviceconnector import _Client
from cortex.utils import get_logger
from .camel import CamelResource
from .utils import raise_for_status_with_detail

log = get_logger(__name__)


class TypeClient(_Client):
    """
    A client for the Cortex Types API.
    """

    URIs = {
        "type": "projects/{projectId}/types/{name}",
    }

    def save_type(self):
        """_summary_

        :raises NotImplementedError: _description_
        """
        raise NotImplementedError()

    def get_type(self, name: str):
        """Fetches a type to work with.

        :param name: The name of the type to retrieve.
        :type name: str
        :return: An instance of :class:`cortex.types.Type`
        :rtype: :class:`cortex.types.Type`
        """
        uri = self.URIs["type"].format(
            projectId=self._project(), name=urllib.parse.quote(name, safe="")
        )
        log.debug("Getting type using URI: {}", uri)
        res = self._serviceconnector.request("GET", uri=uri)
        raise_for_status_with_detail(res)
        return Type(res.json(), self)


class Type(CamelResource):
    """
    Represents a plan for accessing a schema.
    """

    def __init__(self, schema, client: TypeClient):
        super().__init__(schema, True)
        self._client = client
        self._project = client._project
