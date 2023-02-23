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
import os
import json

from .serviceconnector import _Client
from .camel import CamelResource
from .utils import get_logger, raise_for_status_with_detail, parse_string

log = get_logger(__name__)


class SecretsClient(_Client):
    """
    A client for the Cortex Secrets API.
    """

    URIs = {"secret": "projects/{projectId}/secrets/{secretName}"}

    def post_secret(self, name: str, value: object):
        """
        Posts the secret information.
        :param name: Secret name
        :param value: Secret value
        :return: status
        """
        uri = self.URIs["secret"].format(
            secretName=parse_string(name), projectId=self._project()
        )
        data = json.dumps(value)
        headers = {"Content-Type": "application/json"}
        res = self._serviceconnector.request(
            "POST", uri=uri, body=data, headers=headers
        )
        raise_for_status_with_detail(res)
        return res.json()

    def get_secret(self, name: str):
        """
        Fetches a secret to work with.

        :param name: The name of the Secret to retrieve.
        :return: A Secret object.
        """
        port = os.getenv("CORTEX_ACCOUNTS_SERVICE_PORT_HTTP_CORTEX_ACCOUNTS") or "5000"
        conn_svc_url = f'{self._serviceconnector.url.replace("cortex-internal", "cortex-accounts")}:{port}'  # pylint: disable=line-too-long
        uri = f"{conn_svc_url}/internal/projects/{self._project()}/secrets/{parse_string(name)}"
        log.debug("Getting Secret using URI: {}", uri)
        res = self._serviceconnector.request("GET", uri=uri, is_internal_url=True)
        raise_for_status_with_detail(res)

        return res.json()


class Secret(CamelResource):
    """
    Defines the secret for a dataset.
    """

    def __init__(self, secret, client: SecretsClient):
        super().__init__(secret, True)
        self._client = client
        self._project = client._project
