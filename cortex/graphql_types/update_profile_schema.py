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
from pydantic import Field

from .base_model import BaseModel


class UpdateProfileSchema(BaseModel):
    """This class is used to validate the data sent to
    the API when a user wants to update their profile."""

    update_profile_schema: "UpdateProfileSchemaUpdateProfileSchema" = Field(
        alias="updateProfileSchema"
    )


class UpdateProfileSchemaUpdateProfileSchema(BaseModel):
    """A class that inherits from the BaseModel class."""

    name: str


UpdateProfileSchema.update_forward_refs()
UpdateProfileSchemaUpdateProfileSchema.update_forward_refs()
