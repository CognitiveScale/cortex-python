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

from typing import Optional

from attr import attrs

from cortex_common.utils.attr_utils import describableAttrib

__all__ = [
    "MessageResponse",
    "ErrorResponse",
]


@attrs(frozen=True)
class MessageResponse:
    """
    General Success Message Returned from the Cortex APIs
    """

    message = describableAttrib(
        type=str, description="What is the status of the version increment request?"
    )
    version = describableAttrib(
        type=Optional[int],
        default=None,
        description="What is the current version of the resource?",
    )


@attrs(frozen=True)
class ErrorResponse:
    """
    General Error Message Returned from the Cortex APIs
    """

    error = describableAttrib(
        type=str, description="What is the error message associated with the request?"
    )
