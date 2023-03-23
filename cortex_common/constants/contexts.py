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

# pylint: disable=too-few-public-methods
__all__ = [
    "ProfileAttributeClassifications",
    "SchemaContexts",
    "ATTRIBUTES",
    "AttributeValues",
    "CONTEXTS",
]


class SchemaContexts(AttrsAsDict):
    """
    An "Enum" like class capturing the contexts of classes relevant to profile schemas.
    """

    PROFILE_SCHEMA = "cortex/profile-schema"
    PROFILE_ATTRIBUTE_TAG = "cortex/profile-attribute-tag"
    PROFILE_ATTRIBUTE_GROUP = "cortex/profile-attribute-group"
    PROFILE_ATTRIBUTE_FACET = "cortex/profile-attribute-facet"
    PROFILE_ATTRIBUTE_TAXONOMY = "cortex/profile-attribute-taxonomy"


class ATTRIBUTES(AttrsAsDict):
    """
    An "Enum" like class capturing the contexts of classes relevant to different types of profile attributes.
    """  # pylint: disable=line-too-long

    DECLARED_PROFILE_ATTRIBUTE = "cortex/attributes-declared"
    OBSERVED_PROFILE_ATTRIBUTE = "cortex/attributes-observed"
    INFERRED_PROFILE_ATTRIBUTE = "cortex/attributes-inferred"
    ASSIGNED_PROFILE_ATTRIBUTE = "cortex/attributes-assigned"


class AttributeValues(AttrsAsDict):
    """
    An "Enum" like class capturing the contexts of classes relevant to different types of values that can be captured in
    profile attributes.
    """  # pylint: disable=line-too-long

    STRING_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-string"
    BOOLEAN_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-boolean"
    NUMBER_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-number"
    WEIGHT_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-weight"
    DATETIME_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-datetime"

    TOTAL_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-total"
    STATISTICAL_SUMMARY_ATTRIBUTE_VALUE = "cortex/attribute-value-statsummary"
    PERCENTILE_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-percentile"
    PERCENTAGE_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-percentage"

    DIMENSIONAL_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-dimensional"
    LIST_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-list"

    ENTITY_ATTRIBUTE_VALUE = "cortex/attribute-value-entity"
    ENTITY_REL_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-entity-rel"
    PROFILE_REL_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-profile-rel"

    # Depricated ...

    COUNTER_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-counter"
    INTEGER_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-integer"
    DECIMAL_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-decimal"

    # CLASSIFICATION_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-classification"
    # RELATIONSHIP_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-relationship"
    # INSIGHT_ATTRIBUTE_VALUE = "cortex/attribute-value-insight"
    # WEIGHTED_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-weighted"
    # PRIMITIVE_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-primitive"
    # OBJECT_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-object"
    # AVERAGE_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-average"
    # CONCEPT_ATTRIBUTE_VALUE = "cortex/attribute-value-concept"


class CONTEXTS(AttrsAsDict):
    """
    An "Enum" like class capturing the contexts of general classes
    """

    PROFILE = "cortex/profile"
    PROFILE_LINK = "cortex/profile-link"
    PROFILE_ATTRIBUTE_HISTORIC = "cortex/profile-attribute-historic"
    LINK = "cortex/link"

    SESSION = "cortex/session"
    INSIGHT = "cortex/insight"
    CANDIDATE_INSIGHT = "cortex/candidate-insight"

    INSIGHT_CONCEPT_TAG = "cortex/insight-concept-tag"
    INSIGHT_TAG_RELATIONSHIP = "cortex/insight-concept-relationship"
    INSIGHT_TAG_RELATED_TO_RELATIONSHIP = "cortex/insight-relatedTo-concept"
    INTERACTION = "cortex/interaction"
    INSIGHT_INTERACTION = "cortex/insight-interaction"


class ProfileAttributeClassifications(AttrsAsDict):
    """
    An "Enum" like class capturing the different classifications of attributes.
    """

    inferred = "inferred"
    declared = "declared"
    observed = "observed"
    assigned = "assigned"
