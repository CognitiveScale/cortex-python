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

import warnings
from typing import Optional, Union

from cortex_profiles.ext.rest import ProfilesRestClient

from cortex_common.types import (
    ProfileSchema as ProfileSchemaType,
    ProfileAttribute as ProfileAttributeType,
    Profile as ProfileType,
    JobInfo,
)

from cortex.camel import Document



class ProfileAttribute(Document):
    """
    Accessing an existent attribute within a Cortex Profile.
    Not meant to be explicitly instantiated by sdk users.
    """

    def __init__(self, params: dict, profile_client: ProfilesRestClient):
        super().__init__(params, True)
        self._profile_client = profile_client

    @staticmethod
    def get_attribute(
        profile_id: str, attribute_key: str, profile_client: ProfilesRestClient
    ) -> Optional["ProfileAttribute"]:
        """
        Fetches a profile adhering to a specific schema ...
        :param profile_id: ProfileId
        :param attribute_key: Attribute Key of a Profile Attribute
        :param profile_client: ProfileRestClient instance
        :return: ProfileAttribute
        """
        return ProfileAttribute(
            {
                "attribute_key": attribute_key,
                "profile_id": profile_id,
            },
            profile_client,
        )

    def latest(self, schema_id: str) -> Optional[ProfileAttributeType]:
        """
        Returns the latest version of the profile against a specific schema ...
        :param schema_id: Profile Schema Name
        :return: ProfileAttribute Instance
        """
        return self._profile_client.describe_attribute_by_key(
            self.profile_id, schema_id, self.attribute_key
        )

    def __repr__(self):
        return "<Attribute: {}, profile_id: {}>".format(
            self.attribute_key, self.profile_id
        )


class Profile(Document):
    """
    Accessing an existent Cortex Profile.
    Not meant to be explicitly instantiated by sdk users.
    """

    def __init__(
        self, profile: Union[dict, ProfileType], profile_client: ProfilesRestClient
    ):
        """
        Initialize Instance
        :param profile: ProfileInstance or Dict
        :param profile_client: ProfilesRestClient Instance
        """
        super().__init__(dict(profile), True)
        self._profile_client = profile_client

    @staticmethod
    def get_profile(
        profile_id: str, schema_id: str, profile_client: ProfilesRestClient
    ) -> Optional["Profile"]:
        """
        Fetches a profile adhering to a specific schema ...
        :param profile_id: Profile Id
        :param schema_id: Schema ID
        :param profile_client: ProfilesRestClient Instance
        :return: Profile Instance
        """
        return Profile(
            {"profile_id": profile_id, "schema_id": schema_id}, profile_client
        )

    def attribute(self, attribute_key: str) -> Optional[ProfileAttribute]:
        """
        Get Profile Attribute Value By Key
        :param attribute_key: Attribute Name of the Profile
        :return: ProfileAttribute Instance
        """
        return ProfileAttribute.get_attribute(
            self.profile_id, attribute_key, self._profile_client
        )

    def latest(self) -> Optional[ProfileType]:
        """
        Returns the latest version of the profile against a specific schema ...
        :return: Profile Instance
        """
        return self._profile_client.describe_profile(self.profile_id, self.schema_id)

    def delete(self) -> Optional[JobInfo]:
        """
        Deletes the profile built against a specific schema.
        :return: JobInfo
        """
        if self.schema_id is None:
            warnings.warn(
                "SchemaId must be provided to delete profile against a specific schema."
            )
            return None
        return self._profile_client.delete_profile(self.profile_id, self.schema_id)

    def delete_all(self) -> Optional[JobInfo]:
        """
        Deletes all instances of the profile against all schemas.
        :return: JobInfo
        """
        return self._profile_client.delete_all_profiles(profile_schema=self.schema_id)

    def __repr__(self):
        return "<Profile: {}>".format(self.profile_id)


class ProfileSchema(Document):
    """
    Accessing an existent Cortex ProfileSchema.
    """

    def __init__(self, schema_name_or_id: str, profile_client: ProfilesRestClient):
        self._schema_requested = schema_name_or_id
        self._profile_client = profile_client
        self._refresh_schema()
        super().__init__(self._schema.to_dict() if self._exists else {}, True)

    @staticmethod
    def get_schema(schema_id, profile_client) -> Optional["ProfileSchema"]:
        """
        Fetches the requested schema by id ...
        :param schema_id:
        :param profile_client:
        :return: self
        """
        return ProfileSchema(schema_id, profile_client)

    def _refresh_schema(self):
        """
        Refreshes the internal state of the schema ...
        This is only really needed prior to deleting ...
        Or ... prior to getting the latest versions of an updated schema
        :return: None
        """
        self._schema = self._profile_client.describe_schema(self._schema_requested)
        self._exists = self._schema is not None

    def latest(self) -> Optional[ProfileSchemaType]:
        """
        Get the Latest Profile Schema
        :return: ProfileSchema
        """
        self._refresh_schema()
        return self._schema

    def delete(self) -> bool:
        """
        Delete the Profile Schema
        :return: Status(True/False)
        """
        return self._profile_client.delete_schema(self._schema_requested)

    def exists(self) -> bool:
        """
        Returns whether or not the schema requested actually exists ...
        :return: Status(True/False) if a Profile Schema Exists or Not
        """
        self._refresh_schema()
        return self._exists

    def __repr__(self):
        return repr(self._schema) if self._exists else repr(None)
