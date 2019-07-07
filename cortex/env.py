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

import os
from .utils import get_cortex_profile
from .exceptions import BadTokenException

DEFAULT_API_ENDPOINT = 'https://api.cortex.insights.ai'


class CortexEnv:
    """
    Sets environment variables for Cortex.
    """

    def __init__(self, api_endpoint=None, token=None, account=None, username=None, password=None):
        profile = CortexEnv.get_cortex_profile()

        cortexToken = token or CortexEnv.get_token()

        if not cortexToken:
            raise BadTokenException(
                'Your Cortex credentials cannot be retrieved. For more information, go to Cortex Docs > Cortex Tools > Access')

        self.api_endpoint = api_endpoint or os.getenv('CORTEX_URI', profile.get('url'))
        self.token = cortexToken
        self.account = account or os.getenv('CORTEX_ACCOUNT', profile.get('account'))
        self.username = username or os.getenv('CORTEX_USERNAME', profile.get('username'))
        self.password = password or os.getenv('CORTEX_PASSWORD')

    @staticmethod
    def get_token():
        """
        gets the token from either the cortex_token env variable or the profile's token.
        if cortex_token and both cortex_profile are falsey, then cortexToken will be None

        :param profile: configured cortex profile from the local machine
        """
        cortexToken = CortexEnv.get_cortex_token() or CortexEnv.get_cortex_profile().get('token')
        return cortexToken

    @staticmethod
    def get_cortex_profile():
        """
        gets the configured cortex profile from the local machine
        """
        return get_cortex_profile()

    @staticmethod
    def get_cortex_token():
        """
        gets the cortex token from the local machine
        """
        return os.getenv('CORTEX_TOKEN')
