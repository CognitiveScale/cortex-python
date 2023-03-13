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
from typing import Any, List, Optional

from pydantic import Field

from .base_model import BaseModel


# pylint: disable=missing-class-docstring
class ProfileViewer(BaseModel):
    schema: "ProfileViewerSchema"
    features: List["ProfileViewerFeatures"]
    profile: Optional["ProfileViewerProfile"]


class ProfileViewerSchema(BaseModel):
    name: str
    title: Optional[str]
    description: Optional[str]
    attribute_tags: Optional[List["ProfileViewerSchemaAttributeTags"]] = Field(
        alias="attributeTags"
    )


class ProfileViewerSchemaAttributeTags(BaseModel):
    attributes: List["ProfileViewerSchemaAttributeTagsAttributes"]
    name: str


class ProfileViewerSchemaAttributeTagsAttributes(BaseModel):
    name: str
    source_name: str = Field(alias="sourceName")


class ProfileViewerFeatures(BaseModel):
    data_type: Optional[str] = Field(alias="dataType")
    feature_name: str = Field(alias="featureName")
    feature_type: Optional[str] = Field(alias="featureType")
    profile_group: str = Field(alias="profileGroup")
    source_name: str = Field(alias="sourceName")


class ProfileViewerProfile(BaseModel):
    attributes: List["ProfileViewerProfileAttributes"]
    profile_i_d: str = Field(alias="profileID")


class ProfileViewerProfileAttributes(BaseModel):
    group: Optional[str]
    key: str
    source: str
    timestamp: Optional[Any]
    type: str
    value: Any


ProfileViewer.update_forward_refs()
ProfileViewerSchema.update_forward_refs()
ProfileViewerSchemaAttributeTags.update_forward_refs()
ProfileViewerSchemaAttributeTagsAttributes.update_forward_refs()
ProfileViewerFeatures.update_forward_refs()
ProfileViewerProfile.update_forward_refs()
ProfileViewerProfileAttributes.update_forward_refs()
# pylint: enable=missing-class-docstring
