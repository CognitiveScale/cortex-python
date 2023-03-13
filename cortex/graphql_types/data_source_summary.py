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
from .enums import SourceKind


class DataSourceSummary(BaseModel):
    """A class that represents a data source summary."""

    data_source_by_name: "DataSourceSummaryDataSourceByName" = Field(
        alias="dataSourceByName"
    )


class DataSourceSummaryDataSourceByName(BaseModel):
    """This class is used to create a DataSourceSummaryDataSourceByName with a name property"""

    attributes: Optional[List[str]]
    connection: Optional["DataSourceSummaryDataSourceByNameConnection"]
    description: Optional[str]
    kind: SourceKind
    name: str
    primary_key: Optional[str] = Field(alias="primaryKey")
    title: Optional[str]


class DataSourceSummaryDataSourceByNameConnection(BaseModel):
    """A class that is used to create a connection to the database."""

    name: str


DataSourceSummary.update_forward_refs()
DataSourceSummaryDataSourceByName.update_forward_refs()
DataSourceSummaryDataSourceByNameConnection.update_forward_refs()
