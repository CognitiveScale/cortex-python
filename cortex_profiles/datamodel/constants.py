"""
Copyright 2019 Cognitive Scale, Inc. All Rights Reserved.

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

from cortex_common.constants.contexts import CONTEXTS
from cortex_common.utils.config_utils import AttrsAsDict

# pylint: disable=too-few-public-methods
# pylint: disable=invalid-name

__all__ = [
    "TIMEFRAMES",
    "PROFILE_TYPES",
    "UNIVERSAL_ATTRIBUTES",
    "DOMAIN_CONCEPTS",
    "INTERACTIONS",
]


class TIMEFRAMES(AttrsAsDict):
    """
    Built in Time Frames
    """

    HISTORIC = "eternally"
    RECENT = "recently"


class PROFILE_TYPES(AttrsAsDict):
    """
    Built in Profile Types
    """

    INSIGHT_CONSUMER = "profile/insight-consumer"
    ENTITY_TAGGED_IN_INSIGHTS = "profile/entity-in-insight"
    APP_USER = "profile/app-user"


class UNIVERSAL_ATTRIBUTES(AttrsAsDict):
    """
    Built in Universal Attributes
    """

    TYPES = "profile.types"

    @staticmethod
    def keys():
        """
        keys
        :return:
        :rtype:
        """
        return list(filter(lambda x: x[0] != "_", CONTEXTS.__dict__.keys()))


class DOMAIN_CONCEPTS(AttrsAsDict):
    """
    Built in Concept Types
    """

    PERSON = "cortex/person"
    COUNTRY = "cortex/country"
    CURRENCY = "cortex/currency"
    COMPANY = "cortex/company"
    WEBSITE = "cortex/website"


class INTERACTIONS(AttrsAsDict):
    """
    Built in Interactions
    """

    CONTEXT = CONTEXTS.INSIGHT_INTERACTION
    PRESENTED = "presented"
    VIEWED = "viewed"
    IGNORED = "ignored"
