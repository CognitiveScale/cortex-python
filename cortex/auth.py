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

from .serviceconnector import _Client
from .utils import get_logger, generate_token

log = get_logger(__name__)


class AuthenticationClient(_Client):
    """
    Client authentication.
    """

    def fetch_auth_token(self, config):
        """
        Retrieves the JWT token for a given user..

        :param config: The ID of the tenant/account to authenticate to.
        :return: A JWT string.
        """
        token = generate_token(config, validity=1440)
        return token

