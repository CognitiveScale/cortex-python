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
from .utils import get_sensa_profile
from .exceptions import BadTokenException


BAD_TOKEN_MSG = (
    "Your Cortex credentials cannot be retrieved.",
    "Check your profile settings with `cortex configure`.",
)


class SensaEnv:
    """
    Sets environment variables for Cortex.
    """

    def __init__(
        self,
        api_endpoint: str = None,
        token: str = None,
        config: dict = None,
        project: str = None,
        profile: str = None,
    ):
        profile_inst = SensaEnv.get_sensa_profile(profile)

        sensa_token = token or os.getenv("CORTEX_TOKEN")
        sensa_config = config or json.loads(
            os.getenv("CORTEX_PERSONAL_ACCESS_CONFIG", json.dumps(profile_inst))
        )
        if not sensa_token and not sensa_config:
            raise BadTokenException(BAD_TOKEN_MSG)

        self.api_endpoint = api_endpoint or os.getenv(
            "CORTEX_URL", sensa_config.get("url", None)
        )
        self.token = sensa_token
        self.config = sensa_config
        self.project = project or os.getenv(
            "CORTEX_PROJECT", sensa_config.get("project", None)
        )

    @staticmethod
    def get_token():
        """
        gets the token from either the sensa_token env variable or the profile's token.
        if sensa_token and both sensa_profile are falsey, then sensaToken will be None
        """
        sensa_token = (
                SensaEnv.get_sensa_token() or SensaEnv.get_sensa_profile().get("token")
        )
        return sensa_token

    @staticmethod
    def get_sensa_profile(profile: str = None):
        """
        gets the configured sensa profile from the local machine
        """
        return get_sensa_profile(profile)

    @staticmethod
    def get_sensa_token() -> str:
        """
        gets the sensa token from the local machine
        """
        return os.getenv("CORTEX_TOKEN")
