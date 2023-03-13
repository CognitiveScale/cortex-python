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
from typing import Any, Dict

# pylint: disable=no-name-in-module
from pydantic import BaseModel as PydanticBaseModel
from pydantic.class_validators import validator
from pydantic.fields import ModelField

# pylint: enable=no-name-in-module
from .scalars import SCALARS_PARSE_FUNCTIONS, SCALARS_SERIALIZE_FUNCTIONS


# pylint: disable=too-few-public-methods
class BaseModel(PydanticBaseModel):
    """`BaseModel` is a class that inherits from `PydanticBaseModel` and is used as a base
    class for all models"""

    class Config:
        """Config class"""

        allow_population_by_field_name = True
        validate_assignment = True
        arbitrary_types_allowed = True

    # pylint: disable=no-self-argument
    @validator("*", pre=True)
    def decode_custom_scalars(cls, value: Any, field: ModelField) -> Any:
        """
        If the field type is a custom scalar, then use the appropriate function to parse the value

        :param cls: The model class
        :param value: The value to be decoded
        :type value: Any
        :param field: The field object that is being decoded
        :type field: ModelField
        :return: The value of the field.
        """
        decode = SCALARS_PARSE_FUNCTIONS.get(field.type_)
        if decode and callable(decode):
            return decode(value)
        return value

    def dict(self, **kwargs: Any) -> Dict[str, Any]:
        """
        It takes a dictionary and returns a dictionary with all the values serialized

        :param : `SCALARS_SERIALIZE_FUNCTIONS` is a dictionary of functions that will be used to
        serialize the scalar values
        :type : Any
        :return: A dictionary with the keys and values of the object.
        """
        dict_ = super().dict(**kwargs)
        for key, value in dict_.items():
            serialize = SCALARS_SERIALIZE_FUNCTIONS.get(type(value))
            if serialize and callable(serialize):
                dict_[key] = serialize(value)
        return dict_
