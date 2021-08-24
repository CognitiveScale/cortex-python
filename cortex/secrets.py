
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

from .serviceconnector import _Client, ServiceConnector
from .camel import CamelResource
from .utils import get_logger
from .utils import raise_for_status_with_detail

log = get_logger(__name__)


class SecretsClient(_Client):
    """
    A client for the Cortex Actions API.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._serviceconnector.version = 4

    def post_secret(self):
        raise NotImplementedError()


class Secret(CamelResource):

    """
    Defines the connection for a dataset.
    """

    def __init__(self, connection, connector: ServiceConnector):
        super().__init__(connection, True)
        self._connector = connector


    @staticmethod
    def get_secret(name, project, client: SecretsClient):
        """
        Fetches a Connection to work with.

        :param client: The client instance to use.
        :param name: The name of the connection to retrieve.
        :param project: The project from which connection has to be retrieved.
        :return: A Connection object.
        """
        uri = '/internal/projects/{projectId}/secrets/{name}'.format(projectId=project, name=name)
        log.debug('Getting Secret using URI: %s' % uri)
        r = client._serviceconnector.request('GET', uri, is_internal_url=True)
        raise_for_status_with_detail(r)

        return r.json()
