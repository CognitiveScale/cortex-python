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
from typing import List, Optional

from attr import attrs

from cortex_common.constants.types import DESCRIPTIONS
from cortex_common.types.attributes import (
    CustomAttributeSpec,
    BucketAttributeSpec,
    ProfileAttribute,
)
from cortex_common.types.common import TimestampSpec, CommitInfo
from cortex_common.utils.attr_utils import (
    describableAttrib,
    dicts_to_classes,
    attr_class_to_dict,
    dict_to_attr_class,
)

__all__ = [
    "ProfileSchema",
    "ProfileNames",
    "DataSourceSelection",
    "GroupCount",
    "ProfileCommit",
    "JoinSourceSelection",
    "Profile",
    "JoinSpec",
]


@attrs(frozen=True)
class JoinSpec:
    """
    JoinSpec class
    """
    joinSourceColumn = describableAttrib(
        type=str, description="Secondary source key to Join the Columns"
    )
    primarySourceColumn = describableAttrib(
        type=str, description="Primary source key to Join the Columns"
    )
    joinType = describableAttrib(type=str, default=None, description="Type of Join")


@attrs(frozen=True)
class JoinSourceSelection:
    """
    JoinSourceSelection class
    """
    attributes = describableAttrib(
        type=Optional[List[str]], description="Attributes selected from this source"
    )
    join = describableAttrib(
        type=JoinSpec,
        converter=lambda l: dict_to_attr_class(l, JoinSpec),
        description="Join Specification",
    )
    name = describableAttrib(type=str, description="Name of the Joined Data Source")
    profileGroup = describableAttrib(
        type=Optional[str], description="Group of this source"
    )
    timestamp = describableAttrib(
        type=Optional[TimestampSpec],
        converter=lambda l: dict_to_attr_class(l, TimestampSpec),
        description="Timestamp",
    )


@attrs(frozen=True)
class DataSourceSelection:
    """
    Represents the type of a value an attribute can hold
    """

    name = describableAttrib(
        type=str, description="Name of the Primary Source of Profile Schema"
    )
    attributes = describableAttrib(
        type=Optional[List[str]],
        description="Attributes selected from the Primary source",
    )
    profileKey = describableAttrib(
        type=str, description="profile key of the Primary Source(ProfileID)"
    )
    timestamp = describableAttrib(
        type=Optional[TimestampSpec],
        converter=lambda l: dict_to_attr_class(l, TimestampSpec),
        description="Timestamp",
    )
    profileGroup = describableAttrib(
        type=Optional[str], default=None, description="Group of this primary source"
    )


@attrs(frozen=True)
class ProfileNames:
    """
    Represents the type of a value an attribute can hold
    """

    categories = describableAttrib(
        type=Optional[List[str]], description="Categories of the Profile Schema"
    )
    singular = describableAttrib(
        type=str, description="Singular Name of the Profile Schema"
    )
    plural = describableAttrib(
        type=str, description="Plural Name of the Profile Schema"
    )
    title = describableAttrib(type=str, description="Title of the Profile Schema")


@attrs(frozen=True)
class GroupCount:
    """
    Represents the type of a value an attribute can hold
    """

    count = describableAttrib(
        type=int,
        default=None,
        description="Count of Profiles based on Specified Grouping",
    )
    key = describableAttrib(
        type=str, default=None, description="Key in a grouped Attribute"
    )


@attrs(frozen=True)
class ProfileCommit:
    """
    Represents the type of a value an attribute can hold
    """

    profileSchema = describableAttrib(
        type=str, default=None, description="Name of the Profile Schema"
    )
    project = describableAttrib(
        type=str, default=None, description="Project of the Profile Schema"
    )
    commitInfo = describableAttrib(
        type=CommitInfo,
        default=None,
        converter=lambda l: dict_to_attr_class(l, CommitInfo),
        description="Commit Info of the Profile Schema",
    )


@attrs(frozen=True)
class ProfileSchema:
    """
    Represents a group of attributes shared by a class of entities.
    """

    # ----
    name = describableAttrib(type=str, default=None, description=DESCRIPTIONS.NAME)
    title = describableAttrib(type=str, default=None, description=DESCRIPTIONS.TITLE)
    description = describableAttrib(
        type=str, default=None, description=DESCRIPTIONS.DESCRIPTION
    )
    names = describableAttrib(
        type=ProfileNames,
        default=None,
        converter=lambda l: dict_to_attr_class(l, ProfileNames),
        description="Names of the profile schema",
    )
    primarySource = describableAttrib(
        type=DataSourceSelection,
        default=None,
        converter=lambda l: dict_to_attr_class(l, DataSourceSelection),
        description="Primary Source the profile schema",
    )
    project = describableAttrib(
        type=str, default=None, description=DESCRIPTIONS.PROJECT
    )

    joins = describableAttrib(
        type=List[JoinSourceSelection],
        converter=lambda l: dicts_to_classes(l, JoinSourceSelection),
        description="How Schemas are Joined together?",
        default=None,
    )

    customAttributes = describableAttrib(
        type=List[CustomAttributeSpec],
        converter=lambda l: dicts_to_classes(l, CustomAttributeSpec),
        description="Custom Attributes in a profile schema",
        default=None,
    )
    bucketAttributes = describableAttrib(
        type=List[BucketAttributeSpec],
        converter=lambda l: dicts_to_classes(l, BucketAttributeSpec),
        description="Bucket Attributes in a profile schema",
        default=None,
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
class Profile:
    """
    Profile Representation...
    """

    profileID = describableAttrib(
        type=str, description="What is the id for this profile?"
    )
    profileSchema = describableAttrib(
        type=str, description="What is the id of the schema applied to this profile?"
    )
    attributes = describableAttrib(
        type=List[ProfileAttribute],
        converter=lambda l: dicts_to_classes(l, ProfileAttribute),
        description="What are the attributes of this profile?",
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
