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
from typing import List
import attr

from cortex_common.utils.attr_utils import dict_to_attr_class
from cortex_common.types.schemas import (
    ProfileNames,
    DataSourceSelection,
    JoinSourceSelection,
    ProfileSchema,
)

# pylint: disable=line-too-long


class ProfileSchemaBuilder:
    """
    ProfileSchemaBuilder class
    """
    @staticmethod
    def append_from_schema_json(filepath):
        """
        Appends Schema from JSON file
        :param filepath:
        :return: Profile Schema
        """
        with open(filepath, "rb") as file:
            schema = json.load(file)
        return dict_to_attr_class(schema, ProfileSchema)

    def __init__(self, name: str, schema: ProfileSchema = ProfileSchema()):
        """
        Initializes the builder from the profile schema type ...
        :param schema:
        :return:
        """
        self._schema = attr.evolve(schema, name=name)

    def name(self, name: str) -> "ProfileSchemaBuilder":
        """
        Sets the name of the schema ...
        :param name:
        :return:
        """
        self._schema = attr.evolve(self._schema, name=name)
        return self

    def title(self, title: str) -> "ProfileSchemaBuilder":
        """
        Sets the title of the schema ...
        :param title:
        :return:
        """
        self._schema = attr.evolve(self._schema, title=title)
        return self

    def description(self, description: str) -> "ProfileSchemaBuilder":
        """
        Sets the description of the schema ...
        :param description:
        :return:
        """
        self._schema = attr.evolve(self._schema, description=description)
        return self

    def project(self, project: str) -> "ProfileSchemaBuilder":
        """
        Sets the project of the schema ...
        :param project:
        :return:
        """
        self._schema = attr.evolve(self._schema, project=project)
        return self

    def primary_source(
        self, primary_source: DataSourceSelection
    ) -> "ProfileSchemaBuilder":
        """
        Sets the primary_source of the schema ...
        :param primary_source:
        :return:
        """
        self._schema = attr.evolve(self._schema, primarySource=primary_source)
        return self

    def joins(self, joins: List[JoinSourceSelection]) -> "ProfileSchemaBuilder":
        """
        Sets the JoinSourceSelections of the schema ...
        :param joins:
        :return:
        """
        self._schema = attr.evolve(self._schema, joins=joins)
        return self

    def names(self, names: ProfileNames) -> "ProfileSchemaBuilder":
        """
        Sets the names of the schema ...
        :param names:
        :return:
        """
        self._schema = attr.evolve(self._schema, names=names)
        return self

    def custom_attributes(self, custom_attributes) -> "ProfileSchemaBuilder":
        """
        Sets the Custom Attributes
        :param custom_attributes:
        :return:
        """
        self._schema = attr.evolve(self._schema, customAttributes=custom_attributes)
        return self

    def bucket_attributes(self, bucket_attributes: object) -> object:
        """
        Sets the Bucketed Attributes
        :param bucket_attributes:
        :return:
        """
        self._schema = attr.evolve(self._schema, bucketAttributes=bucket_attributes)
        return self

    def build(self) -> ProfileSchema:
        """
        Builds a new Profile Schema using the attributes added to the builder
        :return:
        """
        return self._schema
