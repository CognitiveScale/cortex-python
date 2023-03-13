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
from typing import List

from pydantic import Field

from .base_model import BaseModel


# pylint: disable=missing-class-docstring


class DeleteBucketAttribute(BaseModel):
    delete_bucket_attribute: "DeleteBucketAttributeDeleteBucketAttribute" = Field(
        alias="deleteBucketAttribute"
    )


class DeleteBucketAttributeDeleteBucketAttribute(BaseModel):
    name: str
    bucket_attributes: List[
        "DeleteBucketAttributeDeleteBucketAttributeBucketAttributes"
    ] = Field(alias="bucketAttributes")


class DeleteBucketAttributeDeleteBucketAttributeBucketAttributes(BaseModel):
    name: str
    buckets: List["DeleteBucketAttributeDeleteBucketAttributeBucketAttributesBuckets"]


class DeleteBucketAttributeDeleteBucketAttributeBucketAttributesBuckets(BaseModel):
    filter: str


DeleteBucketAttribute.update_forward_refs()
DeleteBucketAttributeDeleteBucketAttribute.update_forward_refs()
DeleteBucketAttributeDeleteBucketAttributeBucketAttributes.update_forward_refs()
DeleteBucketAttributeDeleteBucketAttributeBucketAttributesBuckets.update_forward_refs()
# pylint: enable=missing-class-docstring
