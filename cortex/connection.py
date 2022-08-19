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

import json
import os
import urllib.parse
from .serviceconnector import _Client
from .camel import CamelResource
from .utils import get_logger, raise_for_status_with_detail, Constants

log = get_logger(__name__)


class ConnectionClient(_Client):
    """
    A client used to manage connections.
    """
    URIs = {'connections': 'projects/{projectId}/connections'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._serviceconnector.version = Constants.default_api_version

    def save_connection(self, connection: object):
        """
        Posts the connection client information.
        :param connection: Connection object
        :return: status
        """
        uri = self.URIs['connections'].format(projectId=self._project())
        data = json.dumps(connection)
        headers = {'Content-Type': 'application/json'}
        r = self._serviceconnector.request('POST', uri, data, headers)
        raise_for_status_with_detail(r)
        return r.json()

    def get_connection(self, name: str):
        """
        Fetches a Connection to work with.
        :param name: The name of the connection to retrieve.
        :return: A Connection object.
        """
        port = os.getenv('CORTEX_CONNECTIONS_SERVICE_PORT_HTTP_CORTEX_CONNECTIONS') or '4450'
        conn_svc_url = f'{self._serviceconnector.url.replace("cortex-internal", "cortex-connections")}:{port}'
        uri = f'{conn_svc_url}/internal/projects/{self._project()}/connections/{urllib.parse.quote(name, safe="")}'
        log.debug('Getting connection using URI: %s' % uri)
        r = self._serviceconnector.request('GET', uri=uri, is_internal_url=True)
        raise_for_status_with_detail(r)

        return r.json()

    def _bootstrap(self):
        uri = self.URIs['connections'] + '/_/bootstrap'
        r = self._serviceconnector.request('GET', uri=uri)
        raise_for_status_with_detail(r)
        return r.json()


class Connection(CamelResource):
    """
    Defines the connection for a dataset.
    """

    def __init__(self, connection, client: ConnectionClient):
        super().__init__(connection, True)
        self._client = client
        self._project = client.project
