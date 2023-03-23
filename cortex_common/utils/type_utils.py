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

import typing
from typing import TypeVar, Callable, Any, Tuple, Union, Optional, List

import numpy as np

NoneType = type(None)
T = TypeVar("T")

# pylint: disable=invalid-name
__all__ = [
    "is_typing_type",
    "get_types_of_union",
    "is_optional_type",
    "is_union_type",
    "pass_through_converter",
    "fold_list",
    "numpy_type_to_python_type",
    "is_primitive",
]


def is_typing_type(t: Any) -> bool:
    """
    Is a type from the typing library ...
    Confirmed true for the following typing types:
        - typing.Mapping
        - typing.Tuple
        - typing.Callable
        - typing.Type
        - typing.List
        - typing.Dict
        - typing.DefaultDict
        - typing.Set
        - typing.FrozenSet
        - typing.Counter
        - typing.Deque
    :param t:
    :return:
    """
    return hasattr(t, "__origin__") and t.__origin__ in [typing.Union, typing.Generic]


def get_types_of_union(union: Any) -> Tuple:
    """
    Gets all of the types associated with the union type ...
    :param union:
    :return:
    """
    return tuple(union.__args__) if hasattr(union, "__args__") else tuple()


def is_optional_type(t: Any) -> bool:
    """
    Determines if a type is an Option Type ...
    :param t:
    :return:
    """
    # return is_typing_type(t) and len(t.__args__) == 2 and type(None) in t.__args__
    # return t.__origin__ in [typing.Optional]
    return repr(t).startswith("typing.Optional")


def is_union_type(t: type) -> bool:
    """
    Determines if a type is a Union Type ...
    :param t:
    :return:
    """
    # return t.__origin__ in [typing.Union]
    return repr(t).startswith("typing.Union")


def pass_through_converter(
    types_that_need_conversion: Tuple[Any, ...], converter_method: Callable
) -> Callable[[Any], Any]:
    """
    Returns a method that when invoked with the values, determines whether or not the value should be converted.
    Items that don't need conversion are passed through as is ...

    :param types_that_need_conversion:
    :param converter_method:
    :return:
    """  # pylint: disable=line-too-long
    return (
        lambda x: converter_method(x)
        if isinstance(x, types_that_need_conversion)
        else x
    )


# pylint: disable=line-too-long
# Union feels like a hack ... you can't really treat it as a type ... you almost have to explicitly fill in the union types every time ...
# def union_type_from_tuples(tup:Tuple[Any,...]) -> Union:
#     return Union[tup]

OptionalList = Union[
    Optional[List[Optional[Any]]],
    Optional[List[Any]],
    List[Any],
    List[Optional[Any]],
]


def fold_list(l: OptionalList) -> List[Any]:
    """
    Folds a list that can optionally contain items by removing Null items ...
    :param l:
    :return:
    """
    if l is None:
        return []
    return [x for x in l if x]


def numpy_type_to_python_type(value):
    """
    Turns numpy types into python types ...
    :param value:
    :return:
    """
    return (
        int(value)
        if isinstance(value, (int, np.integer))
        else (float(value) if isinstance(value, (float, np.floating)) else value)
    )


def is_primitive(value: Union[int, float, str, bool, None, Any]) -> bool:
    """
    Tests if a value is primitive
    :param value:
    :return:
    """
    if isinstance(value, (float, int)):
        return True
    if isinstance(value, str):
        return True
    if isinstance(value, bool):
        return True
    return False
