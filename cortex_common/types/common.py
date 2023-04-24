"""
Copyright 2021 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
# pylint: disable=cyclic-import
from typing import Optional

from attr import attrs

from cortex_common.utils.attr_utils import describableAttrib, dict_to_attr_class

__all__ = [
    "JobInfo",
    "TimestampSpec",
    "FixedTimestampSpec",
    "CommitInfo",
    "ResourceRef",
]


@attrs(frozen=True)
class JobInfo:
    """
    JobInfo class
    """
    endTime = describableAttrib(
        type=str, default=None, description="End Time of the Job"
    )
    errorMessage = describableAttrib(
        type=str, default=None, description="Job Error Message"
    )
    isActive = describableAttrib(
        type=bool, default=False, description="Is the Job still running?"
    )
    isCancelled = describableAttrib(
        type=bool, default=False, description="Is the Job Cancelled?"
    )
    isComplete = describableAttrib(
        type=bool, default=False, description="Does the Job Complete?"
    )
    isError = describableAttrib(
        type=bool, default=False, description="Does the Job fail?"
    )
    jobId = describableAttrib(type=str, default=None, description="Job Identifier")
    jobType = describableAttrib(type=str, default=None, description="Type of Job")
    project = describableAttrib(type=str, default=None, description="Project Name")
    resourceName = describableAttrib(
        type=str, default=None, description="Resource Name"
    )
    resourceType = describableAttrib(
        type=str, default=None, description="Resource Type"
    )
    startTime = describableAttrib(
        type=str, default=None, description="Start Time of the Job"
    )


@attrs(frozen=True)
class FixedTimestampSpec:
    """
    Represents the type of a value an attribute can hold
    """

    value = describableAttrib(type=Optional[str], description="Value of the Timestamp")
    format = describableAttrib(
        type=Optional[str], description="Format of the Timestamp"
    )


@attrs(frozen=True)
class TimestampSpec:
    """
    Represents the type of a value an attribute can hold
    """

    auto = describableAttrib(
        type=Optional[bool],
        default=None,
        description="Is the Timestamp Auto Generated?",
    )
    fixed = describableAttrib(
        type=Optional[FixedTimestampSpec],
        default=None,
        converter=lambda l: dict_to_attr_class(l, FixedTimestampSpec),
        description="Fixed Timestamp Value and Format",
    )
    field = describableAttrib(
        type=Optional[str], default=None, description="Field of the timestamp"
    )
    format = describableAttrib(
        type=Optional[str], default=None, description="Format of the timestamp"
    )


@attrs(frozen=True)
class CommitInfo:
    """
    Represents the type of a value an attribute can hold
    """

    clusterId = describableAttrib(type=str, default=None)
    isBlindAppend = describableAttrib(type=bool, default=None)
    isolationLevel = describableAttrib(type=str, default=None)
    operation = describableAttrib(type=str, default=None)
    operationMetrics = describableAttrib(type=dict, default=None)
    operationParams = describableAttrib(type=dict, default=None)
    readVersion = describableAttrib(type=int, default=None)
    timestamp = describableAttrib(type=str, default=None)
    userId = describableAttrib(type=str, default=None)
    userMetadata = describableAttrib(type=str, default=None)
    version = describableAttrib(type=int, default=None)


@attrs(frozen=True)
class ResourceRef:
    """
    Represents the type of a value an attribute can hold
    """

    name = describableAttrib(type=str, description="Resource Name")
