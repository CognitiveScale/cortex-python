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
from typing import Dict
from .serviceconnector import _Client
from .utils import get_logger, generate_token

log = get_logger(__name__)


class AuthenticationClient(_Client):
    """Client authentication.

    :param _Client: :py:class:`cortex.serviceconnector._Client`
    :type _Client: _type_
    :return: Instance of AuthenticationClient
    :rtype: AuthenticationClient
    """

    def fetch_auth_token(self, config: Dict, validity=2) -> str:
        """
        Generates JWT token from the personal access token provided via the `config` parameter

        :param config: A Personal access token provided by the Cortex Console,represented as a python dict
        :type config: Dict

        :param validity: The validity of the JWT token in minutes, defaults to 2 minutes
        :type validity: float, optional

        :return: A JWT token in string form
        :rtype: str
        """  # pylint: disable=line-too-long
        token = generate_token(config, validity=validity)
        return token
