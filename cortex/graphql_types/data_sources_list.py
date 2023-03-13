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


# pylint: disable=missing-class-docstring
class DataSourcesList(BaseModel):
    data_sources: List["DataSourcesListDataSources"] = Field(alias="dataSources")


class DataSourcesListDataSources(BaseModel):
    attributes: Optional[List[str]]
    connection: Optional["DataSourcesListDataSourcesConnection"]
    name: str
    primary_key: Optional[str] = Field(alias="primaryKey")
    title: Optional[str]


class DataSourcesListDataSourcesConnection(BaseModel):
    name: str


DataSourcesList.update_forward_refs()
DataSourcesListDataSources.update_forward_refs()
DataSourcesListDataSourcesConnection.update_forward_refs()
# pylint: enable=missing-class-docstring
