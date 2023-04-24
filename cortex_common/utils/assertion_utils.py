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

from typing import List, Callable, Any

import pandas as pd

__all__ = [
    "is_not_none_or_nan",
    "all_values_in_list_are_not_nones_or_nans",
    "all_values_in_list_pass",
    "first_arg_is_type_wrapper",
    "key_has_value_in_dict",
]


# pylint: disable=invalid-name
# pylint: disable=simplifiable-if-expression
def is_not_none_or_nan(v: object) -> bool:
    """
    Asserting an object (usually an element in a df) is not NaN or None
    :param v:
    :return:
    """
    return (
        (True if v else False)
        if not isinstance(v, float)
        else (not pd.isna(v) if v else False)
    )


def all_values_in_list_are_not_nones_or_nans(l: List) -> bool:
    """
    Asserts that all vals in a list are set
    :param l:
    :return:
    """
    return all_values_in_list_pass(l, is_not_none_or_nan)


def all_values_in_list_pass(l: List, validity_filter: Callable) -> bool:
    """
    Assert all times in list pass the validity check function.
    :param l:
    :param validity_filter:
    :return:
    """
    return all(map(validity_filter, l))


def first_arg_is_type_wrapper(_callable, tuple_of_types) -> Callable[[Any], bool]:
    """
    ???
    :param _callable:
    :param tuple_of_types:
    :return:
    """
    return lambda x: x if not isinstance(x, tuple_of_types) else _callable(x)


def key_has_value_in_dict(d: dict, key: str, value: object):
    """
    Check if a dictionary has a specific key with a specific value within it.

    :param d:
    :param key:
    :param value:
    :return:
    """
    return isinstance(d, dict) and d.get(key) == value
