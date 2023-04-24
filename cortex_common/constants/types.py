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


__all__ = [
    "VERSION",
    "CAMEL",
    "DESCRIPTIONS",
]


VERSION = "0.0.1"
CAMEL = "2.0.0"


# pylint: disable=too-few-public-methods

class DESCRIPTIONS(AttrsAsDict):
    """
    An "Enum" like class capturing the descriptions of common fields used in classes.
    """

    ID = "How can this piece of data be uniquely identified?"
    CONTEXT = "What is the type of this piece of data?"
    VERSION = "What version of the CAMEL spec is this piece of data based on?"
    ATTRIBUTE_SUMMARY = "How can the value of this attribute be concisely expressed?"
    ATTRIBUTE_KEY = "What is the unqiue key for the attribute that distinguishes it from the rest of the attributes captured w.r.t the profile?"  # pylint: disable=line-too-long
    CREATED_AT = "When was this piece of data created?"
    UPDATED_AT = "When was this piece of data created?"
    CAMEL = "What CAMEL spec does this piece of data adhere to?"
    NAME = "What is a unqiue name for this piece of data?"
    LABEL = "What is a UI friendly short name for this piece of data?"
    TITLE = "What is a UI friendly short name for this piece of data?"
    DESCRIPTION = (
        "What is the detailed explanation of the purpose of this piece of data?"
    )
    TAGS = "What tags are applicable to this CAMEL resource?"
    WEIGHT = "How relevant is this piece of information?"
    PROJECT = "what is the project name?"
