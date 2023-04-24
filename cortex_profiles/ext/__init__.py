"""
Copyright 2021 Cognitive Scale, Inc. All Rights Reserved.

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

from cortex_profiles.ext import clients
from cortex_profiles.ext.rest import *

from cortex.utils import get_logger
from cortex.client import Client

log = get_logger(__name__)

__all__ = ["ProfileClient"]

# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name


class ProfileClient:
    """
    Extends the Client Pattern for Profiles with regards to the cortex-python package.
    """

    def __init__(self, client: Client):
        """
        Initialize Instance
        :param client: Cortex Client
        """
        self.project = client._project
        self.profile_client = ProfilesRestClient(client)

    def profile(self, profile_id: str, schema_id: str) -> Optional[clients.Profile]:
        """
        Returns the latest version of the profile against a specific schema
        :param profile_id: Profile ID
        :param schema_id: Profile Schema Name
        :return: clients.Profile
        """
        return clients.Profile.get_profile(profile_id, schema_id, self.profile_client)

    def profile_schema(self, schema_id: str) -> Optional[clients.ProfileSchema]:
        """
        Returns the Latest version of Profile Schema
        :param schema_id: Profile Schema Name
        :return: clients.ProfileSchema
        """
        return clients.ProfileSchema.get_schema(schema_id, self.profile_client)


if __name__ == "__main__":
    from cortex import Cortex
    import json
    import attr

    endpoint = "https://api.dci-dev.dev-eks.insights.ai"
    token = ""
    project = ""
    client = Cortex.client(api_endpoint=endpoint, token=token, project=project)
    pc = ProfileClient(client=client)
    profile = pc.profile("07C68D9A1FC5", "member-stream2-8d02a")

    if profile is not None:
        print(json.dumps(attr.asdict(profile.latest()), indent=4))
