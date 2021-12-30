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

from .serviceconnector import _Client
from .camel import CamelResource
from .utils import get_logger
from .utils import raise_for_status_with_detail

log = get_logger(__name__)


class SecretsClient(_Client):
    """
    A client for the Cortex Secrets API.
    """
    URIs = {'secret': 'projects/{projectId}/secrets/{secretName}'}

    def __init__(self, project: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._serviceconnector.version = 4
        self._project = project

    def post_secret(self):
        raise NotImplementedError()

    def get_secret(self, name: str):
        """
        Fetches a secret to work with.

        :param name: The name of the connection to retrieve.
        :return: A Connection object.
        """
        uri = self.URIs['secret'].format(projectId=self._project, secretName=name)
        log.debug('Getting Secret using URI: %s' % uri)
        r = self._serviceconnector.request('GET', uri)
        raise_for_status_with_detail(r)

        return r.json()

    @property
    def project(self):
        return self._project


class Secret(CamelResource):
    """
    Defines the secret for a dataset.
    """

    def __init__(self, secret, client: SecretsClient):
        super().__init__(secret, True)
        self._client = client
        self._project = client.project
