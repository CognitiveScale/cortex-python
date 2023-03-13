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

from pydantic import Field

from .base_model import BaseModel
from .enums import MeasureFrequency


# pylint: disable=missing-class-docstring


class ProfileSchemaSummary(BaseModel):
    profile_schema_by_name: "ProfileSchemaSummaryProfileSchemaByName" = Field(
        alias="profileSchemaByName"
    )


class ProfileSchemaSummaryProfileSchemaByName(BaseModel):
    name: str
    title: Optional[str]
    names: "ProfileSchemaSummaryProfileSchemaByNameNames"
    description: Optional[str]
    primary_source: "ProfileSchemaSummaryProfileSchemaByNamePrimarySource" = Field(
        alias="primarySource"
    )
    joins: Optional[List["ProfileSchemaSummaryProfileSchemaByNameJoins"]]
    attribute_tags: Optional[
        List["ProfileSchemaSummaryProfileSchemaByNameAttributeTags"]
    ] = Field(alias="attributeTags")
    bucket_attributes: List[
        "ProfileSchemaSummaryProfileSchemaByNameBucketAttributes"
    ] = Field(alias="bucketAttributes")
    custom_attributes: List[
        "ProfileSchemaSummaryProfileSchemaByNameCustomAttributes"
    ] = Field(alias="customAttributes")


class ProfileSchemaSummaryProfileSchemaByNameNames(BaseModel):
    title: str


class ProfileSchemaSummaryProfileSchemaByNamePrimarySource(BaseModel):
    attributes: Optional[List[str]]
    name: str
    profile_group: Optional[str] = Field(alias="profileGroup")
    profile_key: str = Field(alias="profileKey")
    timestamp: "ProfileSchemaSummaryProfileSchemaByNamePrimarySourceTimestamp"


class ProfileSchemaSummaryProfileSchemaByNamePrimarySourceTimestamp(BaseModel):
    auto: Optional[bool]
    field: Optional[str]
    fixed: Optional[
        "ProfileSchemaSummaryProfileSchemaByNamePrimarySourceTimestampFixed"
    ]
    format: Optional[str]


class ProfileSchemaSummaryProfileSchemaByNamePrimarySourceTimestampFixed(BaseModel):
    format: Optional[str]
    value: str


class ProfileSchemaSummaryProfileSchemaByNameJoins(BaseModel):
    attributes: Optional[List[str]]
    join: "ProfileSchemaSummaryProfileSchemaByNameJoinsJoin"
    name: str
    profile_group: Optional[str] = Field(alias="profileGroup")
    timestamp: "ProfileSchemaSummaryProfileSchemaByNameJoinsTimestamp"


class ProfileSchemaSummaryProfileSchemaByNameJoinsJoin(BaseModel):
    join_source_column: str = Field(alias="joinSourceColumn")
    primary_source_column: str = Field(alias="primarySourceColumn")


class ProfileSchemaSummaryProfileSchemaByNameJoinsTimestamp(BaseModel):
    auto: Optional[bool]
    field: Optional[str]
    fixed: Optional["ProfileSchemaSummaryProfileSchemaByNameJoinsTimestampFixed"]
    format: Optional[str]


class ProfileSchemaSummaryProfileSchemaByNameJoinsTimestampFixed(BaseModel):
    format: Optional[str]
    value: str


class ProfileSchemaSummaryProfileSchemaByNameAttributeTags(BaseModel):
    attributes: List["ProfileSchemaSummaryProfileSchemaByNameAttributeTagsAttributes"]
    name: str


class ProfileSchemaSummaryProfileSchemaByNameAttributeTagsAttributes(BaseModel):
    name: str
    source_name: str = Field(alias="sourceName")


class ProfileSchemaSummaryProfileSchemaByNameBucketAttributes(BaseModel):
    name: str
    profile_group: Optional[str] = Field(alias="profileGroup")
    source: Optional["ProfileSchemaSummaryProfileSchemaByNameBucketAttributesSource"]
    buckets: List["ProfileSchemaSummaryProfileSchemaByNameBucketAttributesBuckets"]


class ProfileSchemaSummaryProfileSchemaByNameBucketAttributesSource(BaseModel):
    name: str


class ProfileSchemaSummaryProfileSchemaByNameBucketAttributesBuckets(BaseModel):
    filter: str
    name: str


class ProfileSchemaSummaryProfileSchemaByNameCustomAttributes(BaseModel):
    expression: str
    name: str
    profile_group: Optional[str] = Field(alias="profileGroup")
    source: Optional["ProfileSchemaSummaryProfileSchemaByNameCustomAttributesSource"]
    window: Optional[MeasureFrequency]


class ProfileSchemaSummaryProfileSchemaByNameCustomAttributesSource(BaseModel):
    name: str


ProfileSchemaSummary.update_forward_refs()
ProfileSchemaSummaryProfileSchemaByName.update_forward_refs()
ProfileSchemaSummaryProfileSchemaByNameNames.update_forward_refs()
ProfileSchemaSummaryProfileSchemaByNamePrimarySource.update_forward_refs()
ProfileSchemaSummaryProfileSchemaByNamePrimarySourceTimestamp.update_forward_refs()
ProfileSchemaSummaryProfileSchemaByNamePrimarySourceTimestampFixed.update_forward_refs()
ProfileSchemaSummaryProfileSchemaByNameJoins.update_forward_refs()
ProfileSchemaSummaryProfileSchemaByNameJoinsJoin.update_forward_refs()
ProfileSchemaSummaryProfileSchemaByNameJoinsTimestamp.update_forward_refs()
ProfileSchemaSummaryProfileSchemaByNameJoinsTimestampFixed.update_forward_refs()
ProfileSchemaSummaryProfileSchemaByNameAttributeTags.update_forward_refs()
ProfileSchemaSummaryProfileSchemaByNameAttributeTagsAttributes.update_forward_refs()
ProfileSchemaSummaryProfileSchemaByNameBucketAttributes.update_forward_refs()
ProfileSchemaSummaryProfileSchemaByNameBucketAttributesSource.update_forward_refs()
ProfileSchemaSummaryProfileSchemaByNameBucketAttributesBuckets.update_forward_refs()
ProfileSchemaSummaryProfileSchemaByNameCustomAttributes.update_forward_refs()
ProfileSchemaSummaryProfileSchemaByNameCustomAttributesSource.update_forward_refs()
# pylint: enable=missing-class-docstring
