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


class DataSourceList(BaseModel):
    """This class is a list of DataSource objects"""

    profile_sources: List["DataSourceListProfileSources"] = Field(
        alias="profileSources"
    )


class DataSourceListProfileSources(BaseModel):
    """A class that is used to create a list of data sources."""

    description: Optional[str]
    name: str
    title: Optional[str]


DataSourceList.update_forward_refs()
DataSourceListProfileSources.update_forward_refs()
