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

import json
import os
import urllib.parse
from .serviceconnector import _Client
from .camel import CamelResource
from .utils import get_logger, raise_for_status_with_detail

log = get_logger(__name__)


class ConnectionClient(_Client):
    """A client used to manage connections on a Fabric server.

    :param _Client: _description_
    :type _Client: _type_
    :return: An instance of a ConnectionClient
    """

    URIs = {"connections": "projects/{projectId}/connections"}

    def save_connection(self, connection: dict) -> dict:
        """Saves the provided `connection` dictionary to the Fabric API server.

        :param connection: A Python dictionary containing specification for one of the `supported Fabric connection types <https://cognitivescale.github.io/cortex-fabric/docs/reference-guides/connection-types>`_
        :type connection: dict
        :return: A dictionary containing metadata about the saved connection
        :rtype: dict
        """  # pylint: disable=line-too-long
        uri = self.URIs["connections"].format(projectId=self._project())
        data = json.dumps(connection)
        headers = {"Content-Type": "application/json"}
        res = self._serviceconnector.request("POST", uri, data, headers)
        raise_for_status_with_detail(res)
        return res.json()

    def get_connection(self, name: str) -> dict:
        """Fetch the specific connection in the `name` argument and return the details as a python dictionary

        :param name: Name of the connection to be fetched from the Fabric API
        :type name: str
        :return: A python dictionary containing the specified connection details
        :rtype: dict
        """  # pylint: disable=line-too-long
        port = (
            os.getenv("CORTEX_CONNECTIONS_SERVICE_PORT_HTTP_CORTEX_CONNECTIONS")
            or "4450"
        )
        conn_svc_url = f'{self._serviceconnector.url.replace("cortex-internal", "cortex-connections")}:{port}'  # pylint: disable=line-too-long
        uri = f'{conn_svc_url}/internal/projects/{self._project()}/connections/{urllib.parse.quote(name, safe="")}'  # pylint: disable=line-too-long
        log.debug("Getting connection using URI: {}", uri)
        res = self._serviceconnector.request("GET", uri=uri, is_internal_url=True)
        raise_for_status_with_detail(res)

        return res.json()

    def _bootstrap(self):
        uri = self.URIs["connections"] + "/_/bootstrap"
        res = self._serviceconnector.request("GET", uri=uri)
        raise_for_status_with_detail(res)
        return res.json()


class Connection(CamelResource):
    """
    Defines the connection for a dataset.
    """

    def __init__(self, connection, client: ConnectionClient):
        super().__init__(connection, True)
        self._client = client
        self._project = client._project
