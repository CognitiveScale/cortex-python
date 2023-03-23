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
from typing import Optional, List

from attr import attrs

from cortex_common.constants.types import DESCRIPTIONS
from cortex_common.utils.attr_utils import describableAttrib, attr_class_to_dict, dicts_to_classes
from cortex_common.types.common import ResourceRef

__all__ = [
    "ProfileFeature",
    "ProfileAttribute",
    "BucketAttributeSpec",
    "CustomAttributeSpec",
    "BucketSpec",
]


@attrs(frozen=True)
class ProfileAttribute:
    """
    Represents the profile attribute ...
    """

    group = describableAttrib(
        type=str, description="What is the group of profile attribute?"
    )
    key = describableAttrib(type=str, description=DESCRIPTIONS.ATTRIBUTE_KEY)
    source = describableAttrib(
        type=str, description="What is the source of this attribute?"
    )
    timestamp = describableAttrib(
        type=str, description="When is this Attribute created?"
    )
    type = describableAttrib(
        type=str, description="What is the type of this attribute?"
    )
    value = describableAttrib(
        type=str, description="What is the value of this attribute?"
    )


@attrs(frozen=True)
class ProfileFeature:
    """
    Represents the Profile Feature Summary
    """

    dataType = describableAttrib(type=str, default=None)
    description = describableAttrib(
        type=str, default=None, description=DESCRIPTIONS.DESCRIPTION
    )
    featureName = describableAttrib(type=str, default=None)
    featureType = describableAttrib(type=str, default=None)
    maxValue = describableAttrib(
        type=float, default=None, description="Max Value of the Attribute"
    )
    meanValue = describableAttrib(
        type=float, default=None, description="Mean Value of the Attribute"
    )
    minValue = describableAttrib(
        type=float, default=None, description="Min Value of the Attribute"
    )
    notes = describableAttrib(type=str, default=None)
    observations = describableAttrib(type=str, default=None)
    pctDom = describableAttrib(type=float, default=None)
    pctNull = describableAttrib(type=float, default=None)
    profileGroup = describableAttrib(
        type=str, default=None, description="Profile Group of the Attribute"
    )
    projectName = describableAttrib(
        type=str, default=None, description=DESCRIPTIONS.PROJECT
    )
    sourceName = describableAttrib(type=str, default=None)
    stdDev = describableAttrib(type=float, default=None)
    tableName = describableAttrib(type=str, default=None)
    timestamp = describableAttrib(type=str, default=None)
    uniqueCount = describableAttrib(type=str, default=None)

    def __iter__(self):
        return iter(attr_class_to_dict(self, skip_nulls=True).items())

    def to_dict(self):
        """
        to_dict
        :return:
        :rtype:
        """
        return attr_class_to_dict(self, skip_when_serializing=False, skip_nulls=True)


@attrs(frozen=True)
class AttributeSpec:
    """
    AttributeSpec class
    """
    name = describableAttrib(type=str, description="Attribute Name")
    profileGroup = describableAttrib(
        type=Optional[str], description="Profile Group of the Calculated Attribute"
    )
    source = describableAttrib(
        type=ResourceRef, description="Source of the Calculated Attribute"
    )


@attrs(frozen=True)
class BucketSpec:
    """
    BucketSpec class
    """
    name = describableAttrib(type=str, description="Bucket Name")
    filter = describableAttrib(type=str, description="Bucket Filter")


@attrs(frozen=True)
class BucketAttributeSpec(AttributeSpec):
    """
    BucketAttributeSpec class
    """
    buckets = describableAttrib(
        type=List[BucketSpec],
        converter=lambda l: dicts_to_classes(l, BucketSpec),
        description="Buckets for a Bucketed Attribute",
    )

    def __iter__(self):
        """
        __iter__
        :return:
        :rtype:
        """
        return iter(attr_class_to_dict(self, skip_nulls=True).items())

    def to_dict(self):
        """
        to_dict
        :return:
        :rtype:
        """
        return attr_class_to_dict(self, skip_when_serializing=False, skip_nulls=True)


@attrs(frozen=True)
class CustomAttributeSpec(AttributeSpec):
    """
    CustomAttributeSpec class
    """
    expression = describableAttrib(
        type=str, description="Expression of the Custom Attribute"
    )
    window = describableAttrib(
        type=Optional[str], description="Window of the Custom Attribute"
    )

    def __iter__(self):
        return iter(attr_class_to_dict(self, skip_nulls=True).items())

    def to_dict(self):
        """
        to_dict
        :return:
        :rtype:
        """
        return attr_class_to_dict(self, skip_when_serializing=False, skip_nulls=True)
