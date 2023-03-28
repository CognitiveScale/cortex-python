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


from cortex_common.utils.config_utils import AttrsAsDict

# - [ ] Function to auto derive df schema from name ...
# - [ ] Detail df schemas - Mark Unique Keys Mark Foreign Keys

# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods

__all__ = [
    "TAGGED_CONCEPT",
    "INTERACTION_DURATIONS_COLS"
]


class TAGGED_CONCEPT(AttrsAsDict):
    """
    Schema of DF capturing a tagged concept
    """

    TYPE = "taggedConceptType"
    RELATIONSHIP = "taggedConceptRelationship"
    ID = "taggedConceptId"
    TITLE = "taggedConceptTitle"
    TAGGEDON = "taggedOn"


class INTERACTION_DURATIONS_COLS(AttrsAsDict):
    """
    Columns expected of DFs that capture records that lasted a specific duration.
    """

    STARTED_INTERACTION = "startedInteractionISOUTC"
    STOPPED_INTERACTION = "stoppedInteractionISOUTC"
