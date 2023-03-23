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
import json
from typing import List, Optional, Union

from cortex_common.utils import dicts_to_classes, dict_to_attr_class, head
import cortex_common.constants.queries as gql_queries
from cortex_common.types import (
    ProfileSchema,
    Profile,
    ProfileFeature,
    GroupCount,
    ProfileCommit,
    ProfileAttribute,
    JobInfo,
    CustomAttributeSpec,
    BucketAttributeSpec,
)

from cortex.serviceconnector import _Client

# pylint: disable=broad-exception-caught
# pylint: disable=broad-exception-raised
# pylint: disable=invalid-name
# pylint: disable=inconsistent-return-statements
# pylint: disable=redefined-builtin
# pylint: disable=consider-using-with
# pylint: disable=too-many-public-methods
# pylint: disable=line-too-long


class ProfilesRestClient(_Client):
    """
    A client used to manage profiles.
    """

    URIs = {"profiles": "graphql"}

    def _query(self, query: str, variables: dict, ip_type: str):
        result = None
        try:
            headers = {"Content-Type": "application/json"}
            result = self._serviceconnector.request(
                "POST",
                uri=self.URIs["profiles"],
                body=json.dumps({"variables": variables, "query": query}),
                headers=headers,
            )
            response = result.json()
            if "data" not in response and "errors" in response:
                raise Exception(response["errors"])
            return response["data"][ip_type]
        except Exception as e:
            print(result, e)

    def describe_schema(self, schema_name: str) -> Optional[ProfileSchema]:
        """
        Describe Profile Schema
        :param schema_name: Profile Schema Name
        :return: ProfileSchema
        """
        schema = self._query(
            gql_queries.PROFILE_SCHEMA_SUMMARY,
            variables={"project": self._project(), "name": schema_name},
            ip_type="profileSchemaByName",
        )
        return dict_to_attr_class(schema, ProfileSchema)

    def list_schemas(self) -> Optional[List[ProfileSchema]]:
        """
        List Profile Schemas in a Project
        :return: List[ProfileSchema]
        """
        schemas = self._query(
            gql_queries.FIND_SCHEMAS,
            variables={"project": self._project()},
            ip_type="profileSchemas",
        )
        return dicts_to_classes(schemas, ProfileSchema)

    def find_profiles(
        self,
        profile_schema: str,
        attributes: List[str] = None,
        filter: str = None,
        limit: int = None,
    ) -> Optional[List[Profile]]:
        """
        Find Profiles in a Project
        :param profile_schema: Profile Schema Name
        :param attributes: Profile Schema Attributes
        :param filter: filter
        :param limit: limit
        :return: List[ProfileSummary]
        """
        variables = {
            "project": self._project(),
            "profileSchema": profile_schema,
            "attributes": attributes,
        }
        if filter:
            variables.update({"filter": filter})
        if limit:
            variables.update({"limit": limit})
        profiles = self._query(
            gql_queries.FIND_PROFILES, variables=variables, ip_type="profiles"
        )
        return dicts_to_classes(profiles, Profile)

    def describe_profile(
        self, profile_id: str, profile_schema: str
    ) -> Optional[Profile]:
        """
        Describe Profile

        :param profile_schema: Profile Schema Name
        :param profile_id: Profile ID
        :return: Profile
        """
        schema = self._query(
            gql_queries.PROFILE_BY_ID,
            variables={
                "project": self._project(),
                "profile": profile_id,
                "schema": profile_schema,
            },
            ip_type="profile",
        )
        return dict_to_attr_class(schema, Profile)

    def describe_attribute_by_key(
        self, profile_id: str, profile_schema: str, attribute_key: str
    ) -> Optional[ProfileAttribute]:
        """
        Describe a specific attribute in the profile ...

        :param profile_id: Profile ID
        :param profile_schema: Profile Schema Name
        :param attribute_key: Attribute Key
        :return: ProfileAttribute
        """
        profile = self.describe_profile(profile_id, profile_schema)
        if not profile:
            return None
        return head([a for a in profile.attributes if a.key == attribute_key])

    def get_profile_count(self, profile_schema: str, filter: str = None) -> int:
        """
        Get Profiles Count for a Schema

        :param profile_schema: Profile Schema Name
        :param filter: Query Filter
        :return: Count
        """
        variables = {"project": self._project(), "schema": profile_schema}
        if filter:
            variables.update({"filter": filter})
        return self._query(
            gql_queries.PROFILE_COUNT, variables=variables, ip_type="profileCount"
        )

    def list_profile_features(
        self, profile_schema: str
    ) -> Optional[List[ProfileFeature]]:
        """
        List Profile Features

        :param profile_schema: Profile Schema Name
        :return: List[ProfileFeature]
        """
        profile_features = self._query(
            gql_queries.PROFILE_FEATURES,
            variables={"project": self._project(), "profileSchema": profile_schema},
            ip_type="profileFeatures",
        )
        return dicts_to_classes(profile_features, ProfileFeature)

    def profile_group_count(
        self,
        profile_schema: str,
        group_by: List[str],
        filter: str = None,
        limit: int = None,
    ) -> Optional[List[GroupCount]]:
        """

        :param profile_schema: Profile Schema Name
        :param group_by: GroupBy Key
        :param filter: Query Filter
        :param limit: Limit
        :return: Grouped Count for each Attribute Value
        """
        variables = {
            "project": self._project(),
            "schema": profile_schema,
            "groupBy": group_by,
        }
        if filter:
            variables.update({"filter": filter})
        if limit:
            variables.update({"limit": limit})

        group_count = self._query(
            gql_queries.PROFILE_GROUP_COUNT,
            variables=variables,
            ip_type="profileGroupCount",
        )
        return dicts_to_classes(group_count, GroupCount)

    def find_profiles_history(
        self, profile_schema: str, limit: int = None
    ) -> Optional[List[ProfileCommit]]:
        """
        Find Profiles History

        :param profile_schema: Profile Schema Name
        :param limit
        :return: List[ProfileCommit]
        """
        variables = {"project": self._project(), "profileSchema": profile_schema}
        if limit:
            variables.update({"limit": limit})

        group_count = self._query(
            gql_queries.PROFILE_HISTORY, variables=variables, ip_type="profileHistory"
        )
        return dicts_to_classes(group_count, ProfileCommit)

    def find_profiles_for_plan(
        self,
        simulation_id: str,
        profile_schema: str,
        plan_id: str,
        filter: str = None,
        limit: int = None,
    ) -> Optional[List[Profile]]:
        """
        Find Profiles for a Plan by SimulationId and PlanId

        :param simulation_id: Campaign SimulationId
        :param profile_schema: Profile Schema Name
        :param plan_id: PlanID
        :param filter
        :param limit
        :return: List of Profiles
        """
        variables = {
            "project": self._project(),
            "profileSchema": profile_schema,
            "simulationId": simulation_id,
            "planId": plan_id,
        }
        if filter:
            variables.update({"filter": filter})
        if limit:
            variables.update({"limit": limit})

        profiles = self._query(
            gql_queries.PROFILES_FOR_PLAN, variables=variables, ip_type="profilesForPlan"
        )
        return dicts_to_classes(profiles, Profile)

    def save_profile_schema(self, schema: ProfileSchema) -> Optional[ProfileSchema]:
        """
        Saves a new profile schema ...

        :param schema:
        :return: Profile Schema as dict
        """
        # As Save Profile Schema GQL doesn't support saving bucketAttributes
        # and customAttributes, we have to save them separately
        schema_dict = schema.to_dict()
        bucket_attributes = schema_dict.pop("bucketAttributes")
        custom_attributes = schema_dict.pop("customAttributes")
        # Save Schema without Calculated Attributes
        r = self._query(
            gql_queries.CREATE_PROFILE_SCHEMA,
            variables={"input": schema_dict},
            ip_type="createProfileSchema",
        )

        # Save Bucket Attributes
        if bucket_attributes:
            self.save_bucket_attributes(schema.name, bucket_attributes)

        # Save Custom Attributes
        if custom_attributes:
            self.save_custom_attributes(schema.name, custom_attributes)

        # Build Profiles
        self.build_profiles_from_schema(schema.name)
        return dict_to_attr_class(r, ProfileSchema)

    def save_profile_schema_from_json(
        self, schema_json: Union[str, dict]
    ) -> Optional[ProfileSchema]:
        """
        Saves a profile schema accepting input as Dictionary

        :param schema_json: Dictionary Object or Filepath
        :return: Profile Schema as dict
        """
        # As Save Profile Schema GQL doesn't support saving bucketAttributes
        # and customAttributes, we have to save them separately
        if isinstance(schema_json, str):
            # Read file if filepath is Received
            try:
                schema_json = json.load(open(schema_json, "rb"))
            except Exception as e:
                print("Error Reading Schema File with Message: {}".format(e))
                return None
        bucket_attributes = schema_json.pop("bucketAttributes")
        custom_attributes = schema_json.pop("customAttributes")

        # Save Schema without Calculated Attributes
        r = self._query(
            gql_queries.CREATE_PROFILE_SCHEMA,
            variables={"input": schema_json},
            ip_type="createProfileSchema",
        )

        # Save Bucket Attributes
        if bucket_attributes:
            self.save_bucket_attributes(schema_json.get("name"), bucket_attributes)

        # Save Custom Attributes
        if custom_attributes:
            self.save_custom_attributes(schema_json.get("name"), custom_attributes)

        # Build Profiles
        self.build_profiles_from_schema(schema_json.get("name"))
        return dict_to_attr_class(r, ProfileSchema)

    def save_bucket_attributes(
        self,
        profile_schema: str,
        bucket_attributes: List[Union[BucketAttributeSpec, dict]],
    ):
        """
        Save Multiple Bucket Attributes for a Profile Schema
        :param profile_schema:
        :param bucket_attributes:
        """
        for attribute in bucket_attributes:
            self.save_bucket_attribute(profile_schema, attribute)

    def save_custom_attributes(
        self,
        profile_schema: str,
        custom_attributes: List[Union[CustomAttributeSpec, dict]],
    ):
        """
        Save Multiple Custom Attributes for a Profile Schema

        :param profile_schema:
        :param custom_attributes:
        """
        for attribute in custom_attributes:
            self.save_custom_attribute(profile_schema, attribute)

    def save_custom_attribute(
        self, profile_schema: str, custom_attribute: Union[CustomAttributeSpec, dict]
    ) -> Optional[ProfileSchema]:
        """
        Create custom attribute for a profile schema

        :param profile_schema: Profile Schema
        :param custom_attribute: CustomAttributeSpec
        :return: ProfileSchema
        """
        r = self._query(
            gql_queries.CREATE_CUSTOM_ATTRIBUTE,
            variables={
                "input": {
                    "profileSchema": profile_schema,
                    "project": self._project(),
                    "attribute": custom_attribute.to_dict()
                    if isinstance(custom_attribute, CustomAttributeSpec)
                    else custom_attribute,
                }
            },
            ip_type="createCustomAttribute",
        )
        return dict_to_attr_class(r, ProfileSchema)

    def save_bucket_attribute(
        self, profile_schema: str, bucket_attribute: Union[BucketAttributeSpec, dict]
    ) -> Optional[ProfileSchema]:
        """
        Create bucket attribute for a profile schema

        :param profile_schema: Profile Schema
        :param bucket_attribute: BucketAttributeSpec
        :return: ProfileSchema
        """
        r = self._query(
            gql_queries.CREATE_BUCKET_ATTRIBUTE,
            variables={
                "input": {
                    "profileSchema": profile_schema,
                    "project": self._project(),
                    "attribute": bucket_attribute.to_dict()
                    if isinstance(bucket_attribute, BucketAttributeSpec)
                    else bucket_attribute,
                }
            },
            ip_type="createBucketAttribute",
        )
        return dict_to_attr_class(r, ProfileSchema)

    def build_profiles_from_schema(self, profile_schema: str):
        """
        Build profiles according to the specified ProfileSchema

        :param profile_schema: Profile Schema
        :return: JobInfo
        """
        job_info = self._query(
            gql_queries.BUILD_PROFILES_FROM_SCHEMA,
            variables={"project": self._project(), "profileSchema": profile_schema},
            ip_type="buildProfile",
        )
        return dict_to_attr_class(job_info, JobInfo)

    def update_profiles(self, profile_schema: str, profiles: List[str]):
        """
        Update Profiles by Profile Schema

        :param profile_schema: Profile Schema Name
        :param profiles: List of Profiles as JSON Strings
        :return: JobInfo

        Example Usage:
            update_profiles(profile_schema="schema-name",
             profiles="{'profile_id':'1D9A521F-8722-AF89-5CD5-37BC3D11111','Gender':'F', 'Phone':'(111) 555-7777',
             'Email':'cogntidsfk@email.com','ZipCode':'707009','State':'Texas','Date':'01/01/2000','Age':'41'}")

        """
        job_info = self._query(
            gql_queries.UPDATE_PROFILES,
            variables={
                "project": self._project(),
                "profileSchema": profile_schema,
                "profiles": profiles,
            },
            ip_type="updateProfiles",
        )
        return dict_to_attr_class(job_info, JobInfo)

    def update_custom_attribute(
        self, profile_schema: str, custom_attribute: CustomAttributeSpec
    ) -> Optional[ProfileSchema]:
        """
        Update custom attribute for a profile schema

        :param profile_schema:
        :param custom_attribute: CustomAttributeSpec
        :return: ProfileSchema
        """
        r = self._query(
            gql_queries.UPDATE_CUSTOM_ATTRIBUTE,
            variables={
                "input": {
                    "profileSchema": profile_schema,
                    "project": self._project(),
                    "attribute": custom_attribute.to_dict()
                    if isinstance(custom_attribute, CustomAttributeSpec)
                    else custom_attribute,
                }
            },
            ip_type="updateCustomAttribute",
        )
        return dict_to_attr_class(r, ProfileSchema)

    def update_bucket_attribute(
        self, profile_schema: str, bucket_attribute: BucketAttributeSpec
    ) -> Optional[ProfileSchema]:
        """
        Update bucket attribute for a profile schema

        :param profile_schema:
        :param bucket_attribute: BucketAttributeSpec
        :return: ProfileSchema
        """
        r = self._query(
            gql_queries.UPDATE_BUCKET_ATTRIBUTE,
            variables={
                "input": {
                    "profileSchema": profile_schema,
                    "project": self._project(),
                    "attribute": bucket_attribute.to_dict()
                    if isinstance(bucket_attribute, BucketAttributeSpec)
                    else bucket_attribute,
                }
            },
            ip_type="updateBucketAttribute",
        )
        return dict_to_attr_class(r, ProfileSchema)

    def update_bucket_attributes(
        self,
        profile_schema: str,
        bucket_attributes: List[Union[BucketAttributeSpec, dict]],
    ):
        """
        Update Multiple Bucket Attributes for a Profile Schema
        :param profile_schema:
        :param bucket_attributes:
        """
        for attribute in bucket_attributes:
            self.update_bucket_attribute(profile_schema, attribute)

    def update_custom_attributes(
        self,
        profile_schema: str,
        custom_attributes: List[Union[CustomAttributeSpec, dict]],
    ):
        """
        Update Multiple Custom Attributes for a Profile Schema

        :param profile_schema:
        :param custom_attributes:
        """
        for attribute in custom_attributes:
            self.update_custom_attribute(profile_schema, attribute)

    def update_profile_schema(self, schema: ProfileSchema) -> Optional[ProfileSchema]:
        """
        Updates an existing profile schema ...

        :param schema: ProfileSchema Object
        :return: Profile Schema as dictionary
        """
        # As Save Profile Schema GQL doesn't support saving bucketAttributes
        # and customAttributes, we have to save them separately
        schema_dict = schema.to_dict()
        bucket_attributes = schema_dict.pop("bucketAttributes")
        custom_attributes = schema_dict.pop("customAttributes")
        r = self._query(
            gql_queries.UPDATE_PROFILE_SCHEMA,
            variables={"input": schema_dict},
            ip_type="updateProfileSchema",
        )
        # Update Bucket Attributes
        if bucket_attributes:
            self.update_bucket_attributes(schema.name, bucket_attributes)
        # Update Custom Attributes
        if custom_attributes:
            self.update_custom_attributes(schema.name, custom_attributes)
        # Build Profiles
        self.build_profiles_from_schema(schema.name)
        return dict_to_attr_class(r, ProfileSchema)

    def update_profile_schema_from_json(
        self, schema_json: Union[str, dict]
    ) -> Optional[dict]:
        """
        Updates an existing profile schema accepting input as Dictionary or Filepath

        :param schema_json: Dictionary Object or Filepath
        :return: Profile Schema as dict
        """
        if isinstance(schema_json, str):
            # Read file from the path
            try:
                schema_json = json.load(open(schema_json, "rb"))
            except Exception as e:
                print("Error Reading Schema File with Message: {}".format(e))
                return None
        bucket_attributes = schema_json.pop("bucketAttributes")
        custom_attributes = schema_json.pop("customAttributes")
        r = self._query(
            gql_queries.UPDATE_PROFILE_SCHEMA,
            variables={"input": schema_json},
            ip_type="updateProfileSchema",
        )
        # Update Bucket Attributes
        if bucket_attributes:
            self.update_bucket_attributes(r.get("name"), bucket_attributes)
        # Update Custom Attributes
        if custom_attributes:
            self.update_custom_attributes(r.get("name"), custom_attributes)
        # Build Profiles
        self.build_profiles_from_schema(r.get("name"))
        return dict_to_attr_class(r, ProfileSchema)

    def delete_custom_attribute(
        self, attribute_name, profile_schema
    ) -> Optional[ProfileSchema]:
        """
        Delete Custom Attribute by Name and Schema
        :param attribute_name: Custom Attribute name
        :param profile_schema: Profile Schema
        :return: ProfileSchema
        """
        r = self._query(
            gql_queries.DELETE_CUSTOM_ATTRIBUTE,
            variables={
                "input": {
                    "attributeName": attribute_name,
                    "profileSchema": profile_schema,
                    "project": self._project(),
                }
            },
            ip_type="createBucketAttribute",
        )
        return dict_to_attr_class(r, ProfileSchema)

    def delete_bucket_attribute(
        self, attribute_name, profile_schema
    ) -> Optional[ProfileSchema]:
        """
        Delete Bucket Attribute by Name and Schema
        :param attribute_name: Bucket Attribute Name
        :param profile_schema: Profile Schema Name
        :return: ProfileSchema
        """
        r = self._query(
            gql_queries.DELETE_BUCKET_ATTRIBUTE,
            variables={
                "input": {
                    "attributeName": attribute_name,
                    "profileSchema": profile_schema,
                    "project": self._project(),
                }
            },
            ip_type="createBucketAttribute",
        )
        return dict_to_attr_class(r, ProfileSchema)

    def delete_schema(self, profile_schema: str) -> bool:
        """
        Delete Profile Schema by Name

        :param profile_schema: Profile Schema Name
        :return: True/False
        """
        return self._query(
            gql_queries.DELETE_PROFILE_SCHEMA,
            variables={"input": {"project": self._project(), "name": profile_schema}},
            ip_type="deleteProfileSchema",
        )

    def delete_profile(self, profile_id: str, profile_schema: str) -> Optional[JobInfo]:
        """
        Delete Profile by profileId and profileSchema

        :param profile_id: Profile Schema Name
        :param profile_schema: Profile Schema Name
        :return: True/False
        """
        return self.delete_profiles(
            profile_schema=profile_schema,
            filter='profile_id.eq("{}")'.format(profile_id),
        )

    def delete_profiles(self, profile_schema: str, filter: str) -> Optional[JobInfo]:
        """
        Delete Profiles by Profiles Schema and filter

        :param profile_schema: Profile Schema Name
        :param filter: filter
        :return: JobInfo

        Usage:
            delete_profiles(profile_schema="abc", filter="profile_id.eq(10000800)")
            delete_profiles(profile_schema="abc", filter="profile_id.isIn([10000800, 10001334,10001689,10002757])")

        """
        variables = {"project": self._project(), "profileSchema": profile_schema}
        if filter:
            variables.update({"filter": filter})

        job_info = self._query(
            gql_queries.DELETE_PROFILES, variables=variables, ip_type="deleteProfiles"
        )
        return dict_to_attr_class(job_info, JobInfo)

    def delete_all_profiles(self, profile_schema: str) -> Optional[JobInfo]:
        """
        Delete All Profiles for a Profiles Schema

        :param profile_schema: Profile Schema Name
        :return: JobInfo
        """
        job_info = self._query(
            gql_queries.DELETE_ALL_PROFILES,
            variables={"project": self._project(), "profileSchema": profile_schema},
            ip_type="deleteAllProfiles",
        )
        return dict_to_attr_class(job_info, JobInfo)
