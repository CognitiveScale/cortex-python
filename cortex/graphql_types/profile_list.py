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
from typing import Any, List

from pydantic import Field

from .base_model import BaseModel


# pylint: disable=missing-class-docstring
class ProfileList(BaseModel):
    profiles: List["ProfileListProfiles"]


class ProfileListProfiles(BaseModel):
    attributes: List["ProfileListProfilesAttributes"]
    profile_i_d: str = Field(alias="profileID")


class ProfileListProfilesAttributes(BaseModel):
    key: str
    source: str
    type: str
    value: Any


ProfileList.update_forward_refs()
ProfileListProfiles.update_forward_refs()
ProfileListProfilesAttributes.update_forward_refs()
# pylint: enable=missing-class-docstring
