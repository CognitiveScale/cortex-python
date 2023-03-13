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
from typing import List

from pydantic import Field

from .base_model import BaseModel


# pylint: disable=missing-class-docstring
# pylint: disable=empty-docstring

class UpdateCustomAttribute(BaseModel):
    """This class is used to update a custom attribute"""
    update_custom_attribute: "UpdateCustomAttributeUpdateCustomAttribute" = Field(
        alias="updateCustomAttribute"
    )


class UpdateCustomAttributeUpdateCustomAttribute(BaseModel):
    """A class that is used to update the custom attribute of a user."""
    name: str
    custom_attributes: List[
        "UpdateCustomAttributeUpdateCustomAttributeCustomAttributes"
    ] = Field(alias="customAttributes")


class UpdateCustomAttributeUpdateCustomAttributeCustomAttributes(BaseModel):
    """

    """
    name: str
    expression: str


UpdateCustomAttribute.update_forward_refs()
UpdateCustomAttributeUpdateCustomAttribute.update_forward_refs()
UpdateCustomAttributeUpdateCustomAttributeCustomAttributes.update_forward_refs()
# pylint: enable=missing-class-docstring
# pylint: enable=empty-docstring
