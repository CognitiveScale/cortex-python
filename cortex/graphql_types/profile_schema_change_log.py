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
class ProfileSchemaChangeLog(BaseModel):
    profile_history: List["ProfileSchemaChangeLogProfileHistory"] = Field(
        alias="profileHistory"
    )


class ProfileSchemaChangeLogProfileHistory(BaseModel):
    commit_info: "ProfileSchemaChangeLogProfileHistoryCommitInfo" = Field(
        alias="commitInfo"
    )
    project: str


class ProfileSchemaChangeLogProfileHistoryCommitInfo(BaseModel):
    operation: Optional[str]
    timestamp: Any
    version: Any
    user_id: Optional[str] = Field(alias="userId")


ProfileSchemaChangeLog.update_forward_refs()
ProfileSchemaChangeLogProfileHistory.update_forward_refs()
ProfileSchemaChangeLogProfileHistoryCommitInfo.update_forward_refs()
# pylint: enable=missing-class-docstring
