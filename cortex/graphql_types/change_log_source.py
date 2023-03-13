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
class ChangeLogSource(BaseModel):
    source_history: List["ChangeLogSourceSourceHistory"] = Field(alias="sourceHistory")


class ChangeLogSourceSourceHistory(BaseModel):
    commit_info: "ChangeLogSourceSourceHistoryCommitInfo" = Field(alias="commitInfo")
    project: str
    source_name: str = Field(alias="sourceName")


class ChangeLogSourceSourceHistoryCommitInfo(BaseModel):
    cluster_id: Optional[str] = Field(alias="clusterId")
    operation: Optional[str]
    user_id: Optional[str] = Field(alias="userId")
    timestamp: Any
    version: Any


ChangeLogSource.update_forward_refs()
ChangeLogSourceSourceHistory.update_forward_refs()
ChangeLogSourceSourceHistoryCommitInfo.update_forward_refs()
# pylint: enable=missing-class-docstring
