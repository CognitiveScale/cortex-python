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

from typing import List, Optional

from cortex.graphql_types.build_profile import BuildProfile
from cortex.graphql_types.create_profile_schema import CreateProfileSchema
from cortex.graphql_types.delete_profile_schema import DeleteProfileSchema
from cortex.graphql_types.input_types import (
    DeleteProfileSchemaInput,
    ProfileSchemaInput,
)
from cortex.graphql_types.profile_features import ProfileFeatures
from cortex.graphql_types.profile_group_count import ProfileGroupCount
from cortex.graphql_types.profile_job_list import ProfileJobList
from cortex.graphql_types.profile_list import ProfileList
from cortex.graphql_types.profile_schema_by_name import ProfileSchemaByName
from cortex.graphql_types.profile_schema_change_log import ProfileSchemaChangeLog
from cortex.graphql_types.profile_schema_list import ProfileSchemaList
from cortex.graphql_types.profile_schema_summary import ProfileSchemaSummary
from cortex.graphql_types.profile_viewer import ProfileViewer
from cortex.graphql_types.profiles_for_plan import ProfilesForPlan
from cortex.graphql_types.update_profile_schema import UpdateProfileSchema

from .base_client import BaseClient


def gql(query: str) -> str:
    """
    `gql` is a function that takes a string and returns a string

    :param query: The GraphQL query to be executed
    :type query: str
    :return: A string
    """
    return query


class ProfileClient(BaseClient):
    """A client used to manage profiles using graphql.

    :param BaseClient: _description_
    :type BaseClient: _type_
    :return: An instance of a ProfileClient
    """

    def create_profile_schema(
            self, profile_schema: ProfileSchemaInput
    ) -> CreateProfileSchema:
        """
        It creates a profile schema

        :param profile_schema: ProfileSchemaInput
        :type profile_schema: ProfileSchemaInput
        :return: CreateProfileSchema
        """
        query = gql(
            """
            mutation CreateProfileSchema($input: ProfileSchemaInput!) {
              createProfileSchema(input: $input) {
                name
              }
            }
            """
        )
        variables: dict[str, object] = {"input": profile_schema}
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateProfileSchema.parse_obj(data)

    def update_profile_schema(
            self, profile_schema: ProfileSchemaInput
    ) -> UpdateProfileSchema:
        """
        It takes a `ProfileSchemaInput` object and returns a `UpdateProfileSchema` object

        :param profile_schema: ProfileSchemaInput
        :type profile_schema: ProfileSchemaInput
        :return: UpdateProfileSchema
        """
        query = gql(
            """
            mutation UpdateProfileSchema($input: ProfileSchemaInput!) {
              updateProfileSchema(input: $input) {
                name
              }
            }
            """
        )
        variables: dict[str, object] = {"input": profile_schema}
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateProfileSchema.parse_obj(data)

    def profile_schema_by_name(self, project: str, name: str) -> ProfileSchemaByName:
        """
        It returns the profile schema by name.

        :param project: The name of the project you want to query
        :type project: str
        :param name: The name of the profile schema
        :type name: str
        :return: ProfileSchemaByName
        """
        query = gql(
            """
            query ProfileSchemaByName($project: String!, $name: String!) {
              profileSchemaByName(project: $project, name: $name) {
                primarySource {
                  name
                  attributes
                  name
                  profileGroup
                }
                joins {
                  name
                  attributes
                  profileGroup
                }
                customAttributes {
                  name
                  expression
                  window
                }
                bucketAttributes {
                  name
                  buckets {
                    name
                    filter
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"project": project, "name": name}
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ProfileSchemaByName.parse_obj(data)

    def build_profile(self, project: str, profile_schema: str) -> BuildProfile:
        """
        It builds a profile.

        :param project: The name of the project you want to build a profile for
        :type project: str
        :param profile_schema: The name of the profile schema to build
        :type profile_schema: str
        :return: A BuildProfile object
        """
        query = gql(
            """
            mutation BuildProfile($project: String!, $profileSchema: String!) {
              buildProfile(project: $project, profileSchema: $profileSchema) {
                jobId
              }
            }
            """
        )
        variables: dict[str, object] = {
            "project": project,
            "profileSchema": profile_schema,
        }
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return BuildProfile.parse_obj(data)

    def profile_schema_change_log(
            self, project: str, profile_schema: str, limit: Optional[int]
    ) -> ProfileSchemaChangeLog:
        """
        `profile_schema_change_log` returns a `ProfileSchemaChangeLog` object

        :param project: The project name
        :type project: str
        :param profile_schema: The name of the profile schema
        :type profile_schema: str
        :param limit: The number of changes to return
        :type limit: Optional[int]
        :return: ProfileSchemaChangeLog
        """
        query = gql(
            """
            query ProfileSchemaChangeLog($project: String!, $profileSchema: String!, $limit: Int) {
              profileHistory(project: $project, profileSchema: $profileSchema, limit: $limit) {
                commitInfo {
                  operation
                  timestamp
                  version
                  userId
                }
                project
              }
            }
            """
        )
        variables: dict[str, object] = {
            "project": project,
            "profileSchema": profile_schema,
            "limit": limit,
        }
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ProfileSchemaChangeLog.parse_obj(data)

    def delete_profile_schema(
            self, profile_schema: DeleteProfileSchemaInput
    ) -> DeleteProfileSchema:
        """
        It deletes a profile schema.

        :param profile_schema: DeleteProfileSchemaInput
        :type profile_schema: DeleteProfileSchemaInput
        :return: DeleteProfileSchema
        """
        query = gql(
            """
            mutation DeleteProfileSchema($input: DeleteProfileSchemaInput!) {
              deleteProfileSchema(input: $input)
            }
            """
        )
        variables: dict[str, object] = {"input": profile_schema}
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteProfileSchema.parse_obj(data)

    def profile_features(
            self, project: str, profile_schema: str, campaign: Optional[str]
    ) -> ProfileFeatures:
        """
        This function returns a list of profile features for a given project, profile schema, and campaign

        :param project: The name of the project you want to query
        :type project: str
        :param profile_schema: The name of the profile schema you want to get the features for
        :type profile_schema: str
        :param campaign: Optional[str]
        :type campaign: Optional[str]
        :return: ProfileFeatures
        """  # pylint: disable=line-too-long
        query = gql(
            """
            query ProfileFeatures($project: String!, $profileSchema: String!, $campaign: String) {
              profileFeatures(
                project: $project
                profileSchema: $profileSchema
                campaign: $campaign
              ) {
                dataType
                featureName
                featureType
                maxValue
                meanValue
                minValue
                pctDom
                pctNull
                profileGroup
                observations
                sourceName
                stdDev
                uniqueCount
              }
            }
            """
        )
        variables: dict[str, object] = {
            "project": project,
            "profileSchema": profile_schema,
            "campaign": campaign,
        }
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ProfileFeatures.parse_obj(data)

    def profile_group_count(
            self,
            project: str,
            schema: str,
            filter_arg: Optional[str],
            group_by: List[str],
            limit: Optional[int],
    ) -> ProfileGroupCount:
        """
        `profile_group_count` returns a list of `ProfileGroupCount` objects, each of which contains a `key` and `count`

        :param project: The project name
        :type project: str
        :param schema: The name of the profile schema you want to query
        :type schema: str
        :param filter_arg: This is the filter string that you can use to filter the profiles
        :type filter_arg: Optional[str]
        :param group_by: List[str]
        :type group_by: List[str]
        :param limit: Optional[int]
        :type limit: Optional[int]
        :return: ProfileGroupCount
        """  # pylint: disable=line-too-long
        query = gql(
            """
            query ProfileGroupCount($project: String!, $schema: String!, $filter: String, $groupBy: [String!]!, $limit: Int) {
              profileGroupCount(
                project: $project
                profileSchema: $schema
                filter: $filter
                groupBy: $groupBy
                limit: $limit
              ) {
                key
                count
              }
            }
            """  # pylint: disable=line-too-long
        )
        variables: dict[str, object] = {
            "project": project,
            "schema": schema,
            "filter": filter_arg,
            "groupBy": group_by,
            "limit": limit,
        }
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ProfileGroupCount.parse_obj(data)

    def profile_job_list(self, project: str) -> ProfileJobList:
        """
        It takes a project name as input, and returns a list of jobs associated with that project

        :param project: The project name
        :type project: str
        :return: A ProfileJobList object
        """
        query = gql(
            """
            query ProfileJobList($project: String!) {
              jobs(project: $project) {
                jobId
                isActive
                isCancelled
                isComplete
                status
              }
            }
            """
        )
        variables: dict[str, object] = {"project": project}
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ProfileJobList.parse_obj(data)

    def profile_list(
            self,
            attributes: Optional[List[str]],
            filter_arg: Optional[str],
            limit: Optional[int],
            profile_schema: str,
            project: str,
    ) -> ProfileList:
        """
        `profile_list` returns a list of profiles that match the given filter

        :param attributes: Optional[List[str]]
        :type attributes: Optional[List[str]]
        :param filter_arg: A string that filters the results
        :type filter_arg: Optional[str]
        :param limit: The maximum number of profiles to return
        :type limit: Optional[int]
        :param profile_schema: The name of the profile schema you want to query
        :type profile_schema: str
        :param project: The project you want to query
        :type project: str
        :return: ProfileList
        """
        query = gql(
            """
            query ProfileList($attributes: [String!], $filter: String, $limit: Int, $profileSchema: String!, $project: String!) {
              profiles(
                attributes: $attributes
                filter: $filter
                limit: $limit
                profileSchema: $profileSchema
                project: $project
              ) {
                attributes {
                  key
                  source
                  type
                  value
                }
                profileID
              }
            }
            """  # pylint: disable=line-too-long
        )
        variables: dict[str, object] = {
            "attributes": attributes,
            "filter": filter_arg,
            "limit": limit,
            "profileSchema": profile_schema,
            "project": project,
        }
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ProfileList.parse_obj(data)

    def profiles_for_plan(
            self,
            project: str,
            simulation_id: str,
            profile_schema: str,
            plan_id: str,
            filter_arg: Optional[str],
            limit: Optional[int],
    ) -> ProfilesForPlan:
        """
        `profiles_for_plan` returns a list of profiles for a given plan

        :param project: The project ID
        :type project: str
        :param simulation_id: The simulation ID of the simulation you want to get profiles for
        :type simulation_id: str
        :param profile_schema: The name of the profile schema
        :type profile_schema: str
        :param plan_id: The plan ID of the plan you want to get profiles for
        :type plan_id: str
        :param filter_arg: Optional[str]
        :type filter_arg: Optional[str]
        :param limit: Optional[int]
        :type limit: Optional[int]
        :return: A list of profiles for a plan.
        """
        query = gql(
            """
            query profilesForPlan($project: String!, $simulationId: String!, $profileSchema: String!, $planId: String!, $filter: String, $limit: Int) {
              profilesForPlan(
                project: $project
                simulationId: $simulationId
                profileSchema: $profileSchema
                planId: $planId
                filter: $filter
                limit: $limit
              ) {
                profileID
                profileSchema
                attributes {
                  group
                  key
                  source
                  timestamp
                  type
                  value
                }
              }
            }
            """  # pylint: disable=line-too-long
        )
        variables: dict[str, object] = {
            "project": project,
            "simulationId": simulation_id,
            "profileSchema": profile_schema,
            "planId": plan_id,
            "filter": filter_arg,
            "limit": limit,
        }
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ProfilesForPlan.parse_obj(data)

    def profile_schema_list(self, project: str) -> ProfileSchemaList:
        """
        This function returns a list of profile schemas for a given project

        :param project: The name of the project you want to query
        :type project: str
        :return: ProfileSchemaList
        """
        query = gql(
            """
            query ProfileSchemaList($project: String!) {
              profileSchemas(project: $project) {
                name
                project {
                  name
                }
                names {
                  title
                }
                joins {
                  name
                }
                primarySource {
                  attributes
                  name
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"project": project}
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ProfileSchemaList.parse_obj(data)

    def profile_schema_summary(self, project: str, name: str) -> ProfileSchemaSummary:
        """
        This function takes in a project name and a profile schema name and returns a ProfileSchemaSummary object.

        :param project: The name of the project you want to query
        :type project: str
        :param name: The name of the profile schema
        :type name: str
        :return: ProfileSchemaSummary
        """  # pylint: disable=line-too-long
        query = gql(
            """
            query ProfileSchemaSummary($project: String!, $name: String!) {
              profileSchemaByName(project: $project, name: $name) {
                name
                title
                names {
                  title
                }
                description
                primarySource {
                  attributes
                  name
                  profileGroup
                  profileKey
                  timestamp {
                    auto
                    field
                    fixed {
                      format
                      value
                    }
                    format
                  }
                }
                joins {
                  attributes
                  join {
                    joinSourceColumn
                    primarySourceColumn
                  }
                  name
                  profileGroup
                  timestamp {
                    auto
                    field
                    fixed {
                      format
                      value
                    }
                    format
                  }
                }
                attributeTags {
                  attributes {
                    name
                    sourceName
                  }
                  name
                }
                bucketAttributes {
                  name
                  profileGroup
                  source {
                    name
                  }
                  buckets {
                    filter
                    name
                  }
                }
                customAttributes {
                  expression
                  name
                  profileGroup
                  source {
                    name
                  }
                  window
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"project": project, "name": name}
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ProfileSchemaSummary.parse_obj(data)

    def profile_viewer(self, project: str, schema: str, profile: str) -> ProfileViewer:
        """
        It takes in a project, schema, and profile, and returns a ProfileViewer object

        :param project: The name of the project you want to query
        :type project: str
        :param schema: The name of the profile schema
        :type schema: str
        :param profile: profileById(project: $project, profileSchema: $schema, id: $profile)
        :type profile: str
        :return: A ProfileViewer object
        """
        query = gql(
            """
            query ProfileViewer($project: String!, $schema: String!, $profile: ID!) {
              schema: profileSchemaByName(project: $project, name: $schema) {
                name
                title
                description
                attributeTags {
                  attributes {
                    name
                    sourceName
                  }
                  name
                }
              }
              features: profileFeatures(project: $project, profileSchema: $schema) {
                dataType
                featureName
                featureType
                profileGroup
                sourceName
              }
              profile: profileById(project: $project, profileSchema: $schema, id: $profile) {
                attributes {
                  group
                  key
                  source
                  timestamp
                  type
                  value
                }
                profileID
              }
            }
            """
        )
        variables: dict[str, object] = {
            "project": project,
            "schema": schema,
            "profile": profile,
        }
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ProfileViewer.parse_obj(data)
