
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

import json
from .serviceconnector import _Client, ServiceConnector
from .camel import CamelResource
from .utils import get_logger
from .utils import raise_for_status_with_detail

log = get_logger(__name__)


class ConnectionClient(_Client):
    """
    A client used to manage connections.
    """
    URIs = {'connections': 'connections'}

    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Content apis only have v2..
        self._serviceconnector.version = 2

    def save_connection(self, connection: object):
        """
        Posts the connection client information.
        """
        uri  = self.URIs['connections']
        data = json.dumps(connection)
        headers = {'Content-Type': 'application/json'}
        r = self._serviceconnector.request('POST', uri, data, headers)
        raise_for_status_with_detail(r)
        return r.json()

    ## Private ##

    def _bootstrap(self):
        uri  = self.URIs['connections'] + '/_/bootstrap'
        r = self._serviceconnector.request('GET', uri)
        raise_for_status_with_detail(r)
        return r.json()


class Connection(CamelResource):

    """
    Defines the connection for a dataset.
    """

    def __init__(self, connection, connector: ServiceConnector):
        super().__init__(connection, True)
        self._connector = connector

    @staticmethod
    def get_connection(name, client: ConnectionClient):
        """
        Fetches a Connection to work with.

        :param client: The client instance to use.
        :param name: The name of the connection to retrieve.
        :return: A Connection object.
        """
        uri = 'connections/{name}'.format(name=name)
        log.debug('Getting connection using URI: %s' % uri)
        r = client._serviceconnector.request('GET', uri)
        raise_for_status_with_detail(r)

        return Connection(r.json(), client._serviceconnector)
