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

import copy
import datetime
import traceback
from typing import Union, Optional, List, TypeVar, Type, Any, Callable, Mapping, cast

import arrow
import attr
import pandas as pd
import pydash

from cortex.utils import get_logger
from cortex_common.utils.type_utils import is_union_type, get_types_of_union

log = get_logger(__name__)

# pylint: disable=line-too-long
# pylint: disable=logging-fstring-interpolation
# pylint: disable=broad-exception-raised
# pylint: disable=broad-exception-caught
# pylint: disable=invalid-name
# pylint: disable=unnecessary-lambda
# pylint: disable=no-else-return
# pylint: disable=too-many-return-statements
# pylint: disable=unnecessary-lambda-assignment
# pylint: disable=inconsistent-return-statements
# pylint: disable=useless-return


__all__ = [
    "construct_attr_class_from_dict",
    "dict_to_attr_class",
    "dicts_to_classes",
    "attr_class_to_dict",
    "describableAttrib",
    "describableStrAttrib",
    "str_or_context",
    "union_type_validator",
    "converter_for_union_type",
    "time_converter",
    "attr_fields_except",
    "keep_fields_for_attr_value",
    "modify_attr_class",
    "field_names_of_attr_class",
    "not_none_validator",
    "datetime_to_iso_converter",
]

NoneType = type(None)
T = TypeVar("T")


def construct_attr_class_from_dict(cls: Type[T], data: dict) -> Optional[T]:
    """
    Deals with internal variable renaming ...
    :param cls:
    :param data:
    :return:
    """
    try:
        # Map attributes with underscores ...
        # only do this if things are not a union type ... the dict_constructor is required if
        # union ...
        attr_fields = list(attr.fields_dict(cls).keys())
        private_var_mappings = {
            attr_field: attr_field.replace("_", "", 1)
            for attr_field in attr_fields
            if attr_field.startswith("_")
        }
        data_fields = pydash.rename_keys(
            {
                k: v for k, v in data.items() if k in attr_fields
            },  # Ignore fields not in schema ...
            private_var_mappings,
        )
        return_val = cls(**data_fields)  # type: ignore #
    except Exception as ex:
        log.error(traceback.format_exc())
        log.error(f"Could not construct an instance of {cls} from {data}")
        raise ex
    return return_val


def dict_to_attr_class(
    data: Union[dict, T],
    desired_attr_type: Type[T],
    dict_constructor: Optional[Callable] = None,
) -> Optional[T]:
    """
    Convert a attribute into an attr class ...
    Previously known as `converter_for_classes`
    :param data:
    :param desired_attr_type:
    :param dict_constructor:
    :return:
    """

    if is_union_type(desired_attr_type) and dict_constructor is None:
        raise Exception(
            "Cannot construct union type {}, dict_constructor required.".format(
                desired_attr_type
            )
        )

    valid_types = (
        tuple([desired_attr_type])
        if not is_union_type(desired_attr_type)
        else get_types_of_union(desired_attr_type)
    )

    if data is None:
        return None

    if not isinstance(data, valid_types + tuple([dict])):
        raise Exception("Invalid type {} of data.".format(type(data)))

    # Don't construct already valid types ... and consider union types ...
    # What happens if one of the union types is a dict???
    if isinstance(data, valid_types) and not isinstance(data, dict):
        return data

    # Do we allow data to be "dict" like items?
    return (
        construct_attr_class_from_dict(desired_attr_type, cast(dict, data))
        if dict_constructor is None
        else dict_constructor(data)
    )


def dicts_to_classes(
    l: List[Union[dict, T]], cls: Type[T], dict_constructor: Optional[Callable] = None
) -> Optional[List[Optional[T]]]:
    """
    Turns a List of Dicts into a List of Class Instances ...
    In the case that there are invalid items in the input list, None is returned ..
    Previously known as: converter_for_list_of_classes, list_converter


    :param l:
    :param cls:
    :return:
    """

    if l is None:
        return None

    if not l:
        return cast(List[Optional[T]], l)

    # Check to see if there invalid types to be converted in the list ...
    valid_types = tuple([cls]) if not is_union_type(cls) else get_types_of_union(cls)
    invalid_types_in_list = list(
        map(
            lambda x: type(x),
            filter(lambda x: not isinstance(x, valid_types + tuple([dict])), l),
        )
    )
    if invalid_types_in_list:
        e = Exception("Invalid type(s) {} in list".format(invalid_types_in_list))
        log.error(e)
        return None

    return [
        dict_to_attr_class(elem, cls, dict_constructor=dict_constructor) for elem in l
    ]


def attr_class_to_dict(
    attr_class: Any,
    skip_when_serializing: bool = True,
    skip_nulls: bool = False,
    hide_internal_attributes: bool = False,
) -> dict:
    """
    Turns an attr oriented class into a dict, recursively ignoring any fields that have been marked as `skip_when_serializing`
    Previously known as attr_instance_to_dict

    :param attr_class:
    :return:
    """
    # If filter evaluates to true for an attribute ... its kept ...
    return attr.asdict(
        attr_class,
        filter=lambda a, v: (
            (
                not a.metadata.get("skip_when_serializing", False)
                if skip_when_serializing
                else True
            )
            and (
                not a.metadata.get("internal", False)
                if hide_internal_attributes
                else True
            )
            and (v is not None if skip_nulls else True)
        ),
    )


def describableAttrib(
    description: str = None,
    skip_when_serializing: Optional[bool] = None,
    internal: Optional[bool] = None,
    **kwargs,
) -> dict:
    """
    An attr.ib helper to create fields on attr classes with more structured metadata.
    :param description:
    :param skip_when_serializing:
    :param internal:
    :param kwargs:
    :return:
    """
    attrib_args = copy.deepcopy(kwargs)
    if description:
        attrib_args["metadata"] = pydash.merge(
            attrib_args.get("metadata", {}),
            {"description": description},
            {"internal": internal} if internal is not None else {},
            {"skip_when_serializing": skip_when_serializing}
            if skip_when_serializing is not None
            else {},
        )
    if internal:
        attrib_args["repr"] = False
    return attr.attrib(**attrib_args)


def describableStrAttrib(*args, **kwargs):
    """
    Helper to make an string based attr attribute.
    :param args:
    :param kwargs:
    :return:
    """
    return describableAttrib(
        *args, type=str, validator=attr.validators.instance_of(str), **kwargs
    )


def str_or_context(ip: Union[str, type]) -> Optional[str]:
    """
    Given a string ... it keeps it as is ...
    Given a type ... it assumes the type is an attr class and attempts to get the default value of the context for the
      attr class
    :param ip:
    :return:
    """
    if isinstance(ip, str):
        return ip
    try:
        context = attr.fields(ip).context.default
        return context if isinstance(context, str) else None
    except Exception as e:
        e = TypeError(f"Could not find context for input: {ip}")
        log.error(e)
        return None


def union_type_validator(union_type: type) -> Callable[[Any, Any, Any], bool]:
    """
    Returns an attr validator that ensures that the given value is one of the union types
    :param union_type:
    :return:
    """

    def validator(value) -> bool:
        return type(value) in get_types_of_union(union_type)

    return validator


def converter_for_union_type(
    handlers: Mapping[type, Union[Type[Any], Callable[[Any], Any]]],
) -> Callable[[Any], Optional[T]]:
    """
    Returns an attr oriented converter that is capable of converting a value into the appropriate type for a union type
    :param handlers:
    :return:
    """

    def invalid_input_handler(data: Any) -> NoneType:
        error_message = "Can not convert data of type {} into Union[{}], no valid handlers found.".format(
            type(data), ",".join(map(str, handlers.keys()))
        )
        log.error(error_message)
        return None

    def converter(data: Any):
        # Previous Bug ... don't assert that the type of the input is in union.__args__
        #   ... since union.__args__ types eats up any types that are subclasses
        #   of each other ... such as int and bool.
        assert (
            type(data) in handlers.keys()
        ), "Value of unexpected type ({}) encountered. Expecting: {}".format(
            type(data), list(handlers.keys())
        )
        return handlers.get(type(data), invalid_input_handler)(data)

    return converter


def time_converter(time: Union[str, arrow.arrow.Arrow]) -> Optional[int]:
    """
    Converts a time into an epoch with millisecond resolution.
    :param time:
    :return:
    """
    # Assumption that its a utc timestamp ...
    if isinstance(time, (str)):
        return arrow.get(time).timestamp * 1000
    elif isinstance(time, (arrow.arrow.Arrow)):
        return time.timestamp * 1000
    elif isinstance(time, pd.Timestamp):
        return time.timestamp() * 1000
    elif isinstance(time, int):
        if len(str(time)) == 13:
            return time
        elif len(str(time)) == 9:
            return time * 1000
        else:
            log.error(f"Could not convert int time provided {time}")
            return None
    else:
        log.error(f"Type not yet supported for time_converter: {type(time)}")
        return None
    return None


def attr_fields_except(
    cls: type, fields_to_ignore: List[attr.Attribute]
) -> List[attr.Attribute]:
    """
    List fields of an attr class except for ...
    :param cls:
    :param fields_to_ignore:
    :return:
    """
    return [
        attribute for attribute in attr.fields(cls) if attribute not in fields_to_ignore
    ]


def keep_fields_for_attr_value(
    value: type, fields_to_keep: List[attr.Attribute]
) -> Mapping[str, Any]:
    """
    Serialize an attr intance into a dict, keeping only specific fields
    :param value:
    :param fields_to_keep:
    :return:
    """
    return attr.asdict(value, recurse=False, filter=lambda a, v: a in fields_to_keep)


def modify_attr_class(attrClass: type, modifications: dict):
    """
    Modify an attr instance, functionally ...
    :param attrClass:
    :param modifications:
    :return:
    """
    return attr.evolve(attrClass, **modifications)


def field_names_of_attr_class(attr_class: type) -> List[str]:
    """
    List all the fields of an attr class
    :param attr_class:
    :return:
    """
    return list(map(lambda x: x.name, attr.fields(attr_class)))


not_none_validator = lambda self, a, v: v is not None


def datetime_to_iso_converter(d: Union[str, datetime.datetime]) -> str:
    """
    Convert a datetime into an iso timestamp ...
    :param d:
    :return:
    """
    if isinstance(d, str):
        # Doing this to turn strings like "2019/01/01 into an iso datetime ..."
        return str(arrow.get(d))
    if isinstance(d, arrow.arrow.Arrow):
        return str(d)
    if isinstance(d, datetime.datetime):
        return str(arrow.get(d))


if __name__ == "__main__":
    # Testing Profile Schema _version conversion ...
    from cortex_common.types.schemas import ProfileSchema

    attr.asdict(ProfileSchema(name="1", title="1", description="1", version=1))
