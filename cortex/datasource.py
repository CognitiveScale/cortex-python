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

from typing import Optional

from cortex.graphql_types.change_log_source import ChangeLogSource
from cortex.graphql_types.create_bucket_attribute import CreateBucketAttribute
from cortex.graphql_types.create_custom_attribute import CreateCustomAttribute
from cortex.graphql_types.create_data_source import CreateDataSource
from cortex.graphql_types.data_source_list import DataSourceList
from cortex.graphql_types.data_source_summary import DataSourceSummary
from cortex.graphql_types.data_sources_list import DataSourcesList
from cortex.graphql_types.delete_bucket_attribute import DeleteBucketAttribute
from cortex.graphql_types.delete_custom_attribute import DeleteCustomAttribute
from cortex.graphql_types.delete_data_source import DeleteDataSource
from cortex.graphql_types.features_from_preview import FeaturesFromPreview
from cortex.graphql_types.ingest_source import IngestSource
from cortex.graphql_types.input_types import (
    CreateBucketAttributeInput,
    CreateCustomAttributeInput,
    DataSourceInput,
    DeleteBucketAttributeInput,
    DeleteCustomAttributeInput,
    DeleteDataSourceInput,
    UpdateBucketAttributeInput,
    UpdateCustomAttributeInput,
)
from cortex.graphql_types.update_bucket_attribute import UpdateBucketAttribute
from cortex.graphql_types.update_custom_attribute import UpdateCustomAttribute
from cortex.graphql_types.update_data_source import UpdateDataSource

from .base_client import BaseClient


def gql(query: str) -> str:
    """
    It takes a string and returns a string

    :param query: The GraphQL query to be executed
    :type query: str
    :return: A string
    """
    return query


class DatasourceClient(BaseClient):
    """A client used to manage datasources using graphql.

    :param BaseClient: _description_
    :type BaseClient: _type_
    :return: An instance of a DatasourceClient
    """

    def create_data_source(self, data_source: DataSourceInput) -> CreateDataSource:
        """
        It creates a data source

        :param data_source: DataSourceInput - This is the data source object that we want to create
        :type data_source: DataSourceInput
        :return: CreateDataSource
        """
        query = gql(
            """
            mutation CreateDataSource($input: DataSourceInput!) {
              createDataSource(input: $input) {
                name
              }
            }
            """
        )
        variables: dict[str, object] = {"input": data_source}
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateDataSource.parse_obj(data)

    def update_data_source(self, data_source: DataSourceInput) -> UpdateDataSource:
        """
        It updates the data source.

        :param data_source: DataSourceInput
        :type data_source: DataSourceInput
        :return: UpdateDataSource
        """
        query = gql(
            """
            mutation UpdateDataSource($input: DataSourceInput!) {
              updateDataSource(input: $input) {
                name
              }
            }
            """
        )
        variables: dict[str, object] = {"input": data_source}
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateDataSource.parse_obj(data)

    def ingest_source(self, project: str, source: str) -> IngestSource:
        """
        It takes a project and source as input, and returns a jobId

        :param project: The name of the project to ingest the source into
        :type project: str
        :param source: The source to ingest
        :type source: str
        :return: IngestSource
        """
        query = gql(
            """
            mutation IngestSource($project: String!, $source: String!) {
              ingestSource(project: $project, source: $source) {
                jobId
              }
            }
            """
        )
        variables: dict[str, object] = {"project": project, "source": source}
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return IngestSource.parse_obj(data)

    def features_from_preview(self, project: str, source: str) -> FeaturesFromPreview:
        """
        It takes a project name and a source name as input, and returns a list of features and their data types

        :param project: The name of the project you want to query
        :type project: str
        :param source: The name of the source you want to get the features from
        :type source: str
        :return: FeaturesFromPreview
        """  # pylint: disable=line-too-long
        query = gql(
            """
            query FeaturesFromPreview($project: String!, $source: String!) {
              previewSource(project: $project, source: $source) {
                features {
                  featureName
                  dataType
                  sourceName
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"project": project, "source": source}
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return FeaturesFromPreview.parse_obj(data)

    def change_log_source(
        self, project: str, source: str, limit: Optional[int]
    ) -> ChangeLogSource:
        """
        It returns a list of changes to a source

        :param project: The name of the project
        :type project: str
        :param source: The name of the source you want to get the change log for
        :type source: str
        :param limit: The number of results to return
        :type limit: Optional[int]
        :return: ChangeLogSource
        """
        query = gql(
            """
            query ChangeLogSource($project: String!, $source: String!, $limit: Int) {
              sourceHistory(project: $project, source: $source, limit: $limit) {
                commitInfo {
                  clusterId
                  operation
                  userId
                  timestamp
                  version
                }
                project
                sourceName
              }
            }
            """
        )
        variables: dict[str, object] = {
            "project": project,
            "source": source,
            "limit": limit,
        }
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ChangeLogSource.parse_obj(data)

    def data_source_list(self, project: str) -> DataSourceList:
        """
        > This function returns a list of data sources for a given project

        :param project: The name of the project you want to query
        :type project: str
        :return: A list of data sources.
        """
        query = gql(
            """
            query DataSourceList($project: String!) {
              profileSources(project: $project) {
                description
                name
                title
              }
            }
            """
        )
        variables: dict[str, object] = {"project": project}
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DataSourceList.parse_obj(data)

    def data_source_summary(self, name: str, project: str) -> DataSourceSummary:
        """
        It takes a name and a project and returns a DataSourceSummary object

        :param name: The name of the data source
        :type name: str
        :param project: The project name
        :type project: str
        :return: DataSourceSummary
        """
        query = gql(
            """
            query DataSourceSummary($name: String!, $project: String!) {
              dataSourceByName(name: $name, project: $project) {
                attributes
                connection {
                  name
                }
                description
                kind
                name
                primaryKey
                title
              }
            }
            """
        )
        variables: dict[str, object] = {"name": name, "project": project}
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DataSourceSummary.parse_obj(data)

    def delete_data_source(
        self, data_source: DeleteDataSourceInput
    ) -> DeleteDataSource:
        """
        It deletes a data source

        :param data_source: DeleteDataSourceInput
        :type data_source: DeleteDataSourceInput
        :return: DeleteDataSource
        """
        query = gql(
            """
            mutation DeleteDataSource($input: DeleteDataSourceInput!) {
              deleteDataSource(input: $input)
            }
            """
        )
        variables: dict[str, object] = {"input": data_source}
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteDataSource.parse_obj(data)

    def create_bucket_attribute(
        self, bucket_attribute: CreateBucketAttributeInput
    ) -> CreateBucketAttribute:
        """
        It creates a bucket attribute

        :param bucket_attribute: CreateBucketAttributeInput
        :type bucket_attribute: CreateBucketAttributeInput
        :return: CreateBucketAttribute
        """
        query = gql(
            """
            mutation CreateBucketAttribute($input: CreateBucketAttributeInput!) {
              createBucketAttribute(input: $input) {
                name
                ...bucketAttributes
              }
            }

            fragment bucketAttributes on ProfileSchema {
              bucketAttributes {
                name
                buckets {
                  filter
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": bucket_attribute}
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateBucketAttribute.parse_obj(data)

    def delete_bucket_attribute(
        self, bucket_attribute: DeleteBucketAttributeInput
    ) -> DeleteBucketAttribute:
        """
        It deletes a bucket attribute

        :param bucket_attribute: DeleteBucketAttributeInput
        :type bucket_attribute: DeleteBucketAttributeInput
        :return: DeleteBucketAttribute
        """
        query = gql(
            """
            mutation DeleteBucketAttribute($input: DeleteBucketAttributeInput!) {
              deleteBucketAttribute(input: $input) {
                name
                ...bucketAttributes
              }
            }

            fragment bucketAttributes on ProfileSchema {
              bucketAttributes {
                name
                buckets {
                  filter
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": bucket_attribute}
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteBucketAttribute.parse_obj(data)

    def update_bucket_attribute(
        self, bucket_attribute: UpdateBucketAttributeInput
    ) -> UpdateBucketAttribute:
        """
        It updates a bucket attribute

        :param bucket_attribute: UpdateBucketAttributeInput
        :type bucket_attribute: UpdateBucketAttributeInput
        :return: UpdateBucketAttribute
        """
        query = gql(
            """
            mutation UpdateBucketAttribute($input: UpdateBucketAttributeInput!) {
              updateBucketAttribute(input: $input) {
                name
                ...bucketAttributes
              }
            }

            fragment bucketAttributes on ProfileSchema {
              bucketAttributes {
                name
                buckets {
                  filter
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": bucket_attribute}
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateBucketAttribute.parse_obj(data)

    def data_sources_list(self, project: str) -> DataSourcesList:
        """
        > This function returns a list of data sources for a given project

        :param project: The name of the project you want to query
        :type project: str
        :return: A list of data sources.
        """
        query = gql(
            """
            query DataSourcesList($project: String!) {
              dataSources(project: $project) {
                attributes
                connection {
                  name
                }
                name
                primaryKey
                title
              }
            }
            """
        )
        variables: dict[str, object] = {"project": project}
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DataSourcesList.parse_obj(data)

    def create_custom_attribute(
        self, custom_attribute: CreateCustomAttributeInput
    ) -> CreateCustomAttribute:
        """
        It creates a custom attribute

        :param custom_attribute: CreateCustomAttributeInput
        :type custom_attribute: CreateCustomAttributeInput
        :return: CreateCustomAttribute
        """
        query = gql(
            """
            mutation CreateCustomAttribute($input: CreateCustomAttributeInput!) {
              createCustomAttribute(input: $input) {
                name
                ...customAttributes
              }
            }

            fragment customAttributes on ProfileSchema {
              customAttributes {
                name
                expression
              }
            }
            """
        )
        variables: dict[str, object] = {"input": custom_attribute}
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateCustomAttribute.parse_obj(data)

    def delete_custom_attribute(
        self, custom_attribute: DeleteCustomAttributeInput
    ) -> DeleteCustomAttribute:
        """
        It deletes a custom attribute

        :param custom_attribute: DeleteCustomAttributeInput
        :type custom_attribute: DeleteCustomAttributeInput
        :return: DeleteCustomAttribute
        """
        query = gql(
            """
            mutation DeleteCustomAttribute($input: DeleteCustomAttributeInput!) {
              deleteCustomAttribute(input: $input) {
                name
                ...customAttributes
              }
            }

            fragment customAttributes on ProfileSchema {
              customAttributes {
                name
                expression
              }
            }
            """
        )
        variables: dict[str, object] = {"input": custom_attribute}
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteCustomAttribute.parse_obj(data)

    def update_custom_attribute(
        self, custom_attribute: UpdateCustomAttributeInput
    ) -> UpdateCustomAttribute:
        """
        It updates a custom attribute

        :param custom_attribute: UpdateCustomAttributeInput
        :type custom_attribute: UpdateCustomAttributeInput
        :return: UpdateCustomAttribute
        """
        query = gql(
            """
            mutation UpdateCustomAttribute($input: UpdateCustomAttributeInput!) {
              updateCustomAttribute(input: $input) {
                name
                ...customAttributes
              }
            }

            fragment customAttributes on ProfileSchema {
              customAttributes {
                name
                expression
              }
            }
            """
        )
        variables: dict[str, object] = {"input": custom_attribute}
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateCustomAttribute.parse_obj(data)
