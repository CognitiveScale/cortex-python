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

import os
import json
from .utils import get_cortex_profile
from .exceptions import BadTokenException


class CortexEnv:
    """
    Sets environment variables for Cortex.
    """

    def __init__(self, api_endpoint: str=None, token: str=None, config: dict=None, project: str=None, profile: str = None):
        profile_inst = CortexEnv.get_cortex_profile(profile)

        cortexToken = token or os.getenv('CORTEX_TOKEN')
        cortexConfig = config or json.loads(os.getenv('CORTEX_PERSONAL_ACCESS_CONFIG', json.dumps(profile_inst)))
        if not cortexToken and not cortexConfig:
            raise BadTokenException(
                'Your Cortex credentials cannot be retrieved. Check your profile settings with `cortex configure`.')

        self.api_endpoint = api_endpoint or os.getenv('CORTEX_URL', cortexConfig.get('url', None))
        self.token = cortexToken
        self.config = cortexConfig
        self.project = project or os.getenv('CORTEX_PROJECT', cortexConfig.get('project', None))

    @staticmethod
    def get_token():
        """
        gets the token from either the cortex_token env variable or the profile's token.
        if cortex_token and both cortex_profile are falsey, then cortexToken will be None
        """
        cortexToken = CortexEnv.get_cortex_token() or CortexEnv.get_cortex_profile().get('token')
        return cortexToken

    @staticmethod
    def get_cortex_profile(profile: str = None):
        """
        gets the configured cortex profile from the local machine
        """
        return get_cortex_profile(profile)

    @staticmethod
    def get_cortex_token():
        """
        gets the cortex token from the local machine
        """
        return os.getenv('CORTEX_TOKEN')
