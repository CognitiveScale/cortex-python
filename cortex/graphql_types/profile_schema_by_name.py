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


class ProfileSchemaByName(BaseModel):
    """This class is used to get the profile schema by name"""
    profile_schema_by_name: "ProfileSchemaByNameProfileSchemaByName" = Field(
        alias="profileSchemaByName"
    )


class ProfileSchemaByNameProfileSchemaByName(BaseModel):
    """A class that inherits from BaseModel."""
    primary_source: "ProfileSchemaByNameProfileSchemaByNamePrimarySource" = Field(
        alias="primarySource"
    )
    joins: Optional[List["ProfileSchemaByNameProfileSchemaByNameJoins"]]
    custom_attributes: List[
        "ProfileSchemaByNameProfileSchemaByNameCustomAttributes"
    ] = Field(alias="customAttributes")
    bucket_attributes: List[
        "ProfileSchemaByNameProfileSchemaByNameBucketAttributes"
    ] = Field(alias="bucketAttributes")


class ProfileSchemaByNameProfileSchemaByNamePrimarySource(BaseModel):
    """A class that inherits from the BaseModel class."""
    name: str
    attributes: Optional[List[str]]
    name: str
    profile_group: Optional[str] = Field(alias="profileGroup")


class ProfileSchemaByNameProfileSchemaByNameJoins(BaseModel):
    """A class that inherits from the BaseModel class."""
    name: str
    attributes: Optional[List[str]]
    profile_group: Optional[str] = Field(alias="profileGroup")


class ProfileSchemaByNameProfileSchemaByNameCustomAttributes(BaseModel):
    """A class that inherits from BaseModel."""
    name: str
    expression: str
    window: Optional[MeasureFrequency]


class ProfileSchemaByNameProfileSchemaByNameBucketAttributes(BaseModel):
    """A class that inherits from the BaseModel class."""
    name: str
    buckets: List["ProfileSchemaByNameProfileSchemaByNameBucketAttributesBuckets"]


class ProfileSchemaByNameProfileSchemaByNameBucketAttributesBuckets(BaseModel):
    """A class that is used to create a model for the data that is returned from the API."""
    name: str
    filter: str


ProfileSchemaByName.update_forward_refs()
ProfileSchemaByNameProfileSchemaByName.update_forward_refs()
ProfileSchemaByNameProfileSchemaByNamePrimarySource.update_forward_refs()
ProfileSchemaByNameProfileSchemaByNameJoins.update_forward_refs()
ProfileSchemaByNameProfileSchemaByNameCustomAttributes.update_forward_refs()
ProfileSchemaByNameProfileSchemaByNameBucketAttributes.update_forward_refs()
ProfileSchemaByNameProfileSchemaByNameBucketAttributesBuckets.update_forward_refs()
