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
class ProfileFeatures(BaseModel):
    profile_features: List["ProfileFeaturesProfileFeatures"] = Field(
        alias="profileFeatures"
    )


# pylint: disable=duplicate-code
class ProfileFeaturesProfileFeatures(BaseModel):
    data_type: Optional[str] = Field(alias="dataType")
    feature_name: str = Field(alias="featureName")
    feature_type: Optional[str] = Field(alias="featureType")
    max_value: Optional[float] = Field(alias="maxValue")
    mean_value: Optional[float] = Field(alias="meanValue")
    min_value: Optional[float] = Field(alias="minValue")
    pct_dom: Optional[float] = Field(alias="pctDom")
    pct_null: Optional[float] = Field(alias="pctNull")
    profile_group: str = Field(alias="profileGroup")
    observations: Optional[str]
    source_name: str = Field(alias="sourceName")
    std_dev: Optional[float] = Field(alias="stdDev")
    unique_count: Optional[Any] = Field(alias="uniqueCount")


ProfileFeatures.update_forward_refs()
ProfileFeaturesProfileFeatures.update_forward_refs()
# pylint: enable=missing-class-docstring
