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

import copy
import itertools
import uuid
from collections import defaultdict
from enum import Enum
from typing import (
    List,
    Optional,
    Any,
    Tuple,
    Callable,
    Union,
    Mapping,
    Iterable,
    Set,
    cast,
    TypeVar,
    Iterator,
)

import pandas as pd
import pydash

from cortex.utils import get_logger

log = get_logger(__name__)
# pylint: disable=line-too-long
# pylint: disable=invalid-name
# pylint: disable=unnecessary-comprehension
# pylint: disable=consider-using-generator
# pylint: disable=dangerous-default-value
# pylint: disable=cell-var-from-loop
# pylint: disable=unnecessary-lambda
# pylint: disable=logging-fstring-interpolation
# pylint: disable=no-self-argument

__all__ = [
    "unique_id",
    "head",
    "tail",
    "flatten_list_recursively",
    "flatmap",
    "append_to_list",
    "partition_list",
    "dervie_set_by_element_id",
    "filter_empty_records",
    "search_for_values_in_list",
    "nan_to_none",
    "tuples_with_nans_to_tuples_with_nones",
    "split_list_of_tuples",
    "merge_dicts",
    "assign_to_dict",
    "map_object",
    "map_dict_keys",
    "nest_values_under",
    "append_key_to_values_as",
    "drop_from_dict",
    "join_inner_arrays",
    "invert_dict_lookup",
    "pluck",
    "group_by_key",
    "group_objects_by",
    "reverse_index_dictionary",
    "map_key",
    "merge_unique_objects_on",
    "convert_to_string_dict",
    "negate_dict_of_numbers",
    "merge_enum_values",
    "EnumWithCamelCasedNamesAsDefaultValue",
    "EnumWithNamesAsDefaultValue",
    "rename",
    "unzip",
    "prune_and_log_nulls_in_list",
]


def unique_id() -> str:
    """
    Returns a unique id.
    """
    return str(uuid.uuid4())


# ------------------------------------------- List Utils ------------------------------------------------


def head(l: Optional[List[Any]]) -> Optional[Any]:
    """
    Gets the head of a list if its not empty.
    If its empty, None is returned ...
    :param l:
    :return:
    """
    if l is None:
        return None
    list_with_first_elem = l[0:1]
    return list_with_first_elem[0] if list_with_first_elem else None


def tail(l: List) -> List:
    """
    Returns every element except the first in a list ...
    :param l:
    :return:
    """
    return None if l is None else l[1:]


def flatten_list_recursively(l: Union[List[Any], Any], remove_empty_lists=False):
    """
    Recursively flattens a list of objects.
    :param l:
    :param remove_empty_lists:
    :return:
    """
    if l is None:
        return []
    if not isinstance(l, list):
        return [l]
    # THIS DOES WEIRD STUFF WITH TUPLES!
    return list(
        itertools.chain(
            *[flatten_list_recursively(x) for x in l if (not remove_empty_lists or x)]
        )
    )


def flatmap(listToItterate: List, inputToAppendTo: List, function: Callable) -> List:
    """
    flatmap impl
    :param listToItterate:
    :param inputToAppendTo:
    :param function:
    :return:
    """
    if not listToItterate:
        return []
    head_attr = listToItterate[0]
    tail_attr = listToItterate[1:]
    return flatmap(tail_attr, function(inputToAppendTo, head_attr), function)


def append_to_list(l: List, thing_to_append: Optional[object]) -> List:
    """
    Appends item to a list functionally
    :param l:
    :param thing_to_append:
    :return:
    """
    return l + [thing_to_append] if thing_to_append else l


def partition_list(l: List, n_partitions: int) -> List[List]:
    """
    Splits a list into X different lists
    :param l:
    :param n_partitions:
    :return:
    """
    assert n_partitions >= 1, "Partitions must be >= 1"
    size_of_each_partition = int(len(l) / n_partitions)
    partitions = cast(
        List[Tuple[Optional[int], ...]],
        zip(
            [x for x in range(0, n_partitions)],
            [x for x in range(1, n_partitions)] + [None],  # type: ignore
        ),
    )
    return [
        l[
            cast(int, start)
            * size_of_each_partition : cast(  # type: ignore
                Optional[int], (None if end is None else end * size_of_each_partition)
            )  # type: ignore
        ]
        for start, end in partitions  # type: ignore
    ]


def dervie_set_by_element_id(
    l: List[Any], identifier: Callable[[Any], str] = lambda x: x
) -> Set[Any]:
    """
    Makes a set out of a list, dropping dupplicates, based on a function to determine the id of each element
    :param l:
    :param identifier:
    :return:
    """
    # from itertools import combinations
    # combinations(l, 2)
    return set({identifier(x): x for x in l}.values())


def filter_empty_records(l: List) -> List:
    """
    Remove empty records from a list
    :param l:
    :return:
    """
    return [x for x in l if x]


def search_for_values_in_list(list_to_search: Iterable, search_query: Callable) -> List:
    """
    Returns a subset of the original list based on the elements that match the search function.
    :param list_to_search:
    :param search_query:
    :return:
    """
    return list(filter(search_query, list_to_search))


# ------------------------------------------- Tuple Utils ------------------------------------------------


def nan_to_none(value: Any) -> Optional[Any]:
    """
    Turns NaNs to Nones ...
    :return:
    """
    return None if isinstance(value, float) and pd.isna(value) else value


def tuples_with_nans_to_tuples_with_nones(
    iterator: List[Tuple[Any, ...]]
) -> List[Tuple[Optional[Any], ...]]:
    """
    Replaces NaNs within a tuple into Nones.

    # ... I only want to check for NaNs on primitives... and replace them with None ... not Lists ...
        # Unfortunately python has no way of saying "isPrimitive"
        # Luckily, NaNs are floats ...!

    :param iterator:
    :return:
    """
    return [tuple([nan_to_none(x) for x in tup]) for tup in iterator]


def split_list_of_tuples(l: List[Tuple[Any, ...]]) -> Optional[Tuple[List[Any], ...]]:
    """
    NOTE: No python way of specifying that the return type ... the number of List[Any] in it depends on the size of the tuple passed in ...
    :param l:
    :return:
    """
    if not l:
        return None
    lengths_of_each_tuple = list(map(lambda x: len(list(x)), l))
    # We know there is at least one item ...
    all_tuples_same_length = all(
        map(lambda x: x == lengths_of_each_tuple[0], lengths_of_each_tuple)
    )
    assert all_tuples_same_length, "All tuples must be of the same length: {}".format(
        lengths_of_each_tuple[0]
    )
    return tuple(*[[tupe[i] for tupe in l] for i in range(0, lengths_of_each_tuple[0])])


# ------------------------------------------- Object Utils ------------------------------------------------


def merge_dicts(a: dict, b: dict) -> dict:
    """
    Merges two dicts functionally
    :param a:
    :param b:
    :return:
    """
    c = copy.deepcopy(a)
    c.update(b)
    return c


def assign_to_dict(dictionary: dict, key: str, value: object) -> dict:
    """
    Assigns an additional k-v pair to a dict functionally
    :param dictionary:
    :param key:
    :param value:
    :return:
    """
    return merge_dicts(dictionary, {key: value})


def map_object(
    obj: Optional[Any], method: Callable[[Any], Any], default: Optional[Any] = None
) -> Any:
    """
    Maps an object to another object functionally ...
    :param obj:
    :param method:
    :param default:
    :return:
    """
    return method(obj) if obj is not None else default


def map_dict_keys(
    d: Mapping[str, Any], key_mappers: Optional[Mapping[str, Callable]] = None
) -> dict:
    """
    Remaps values in dicts based on a collection of mapping functions for the different keys in the dictionary
    :param d:
    :param key_mappers:
    :return:
    """
    key_mappers = key_mappers if key_mappers is not None else {}
    return {k: v if k not in key_mappers else key_mappers[k](v) for k, v in d.items()}


def nest_values_under(d: dict, under: str) -> dict:
    """
    Creates a new root key for the dictionary, nesting the passed dictionary under the passed key.
    :param d:
    :param under:
    :return:
    """
    return {k: {under: v} for k, v in d.items()}


def append_key_to_values_as(d: dict, key_title: str) -> List[dict]:
    """
    Appends an array of k-v pairs in a dictionaty as k-v pairs to the original dict ...
    :param d:
    :param key_title:
    :return:
    """
    return [pydash.merge(value, {key_title: key}) for key, value in d.items()]


def _drop_from_dict(d: dict, skip: List[object]) -> dict:
    """
    Internal method to help drop elements from a dict.
    :param d:
    :param skip:
    :return:
    """
    if d is None:
        d = None
    if isinstance(d, list):
        return [drop_from_dict(e, skip) for e in d]
    if isinstance(d, dict):
        return {k: drop_from_dict(v, skip) for k, v in d.items() if k not in skip}
    return d


def drop_from_dict(d: dict, skip: List[object]) -> dict:
    """
    Drop any specified elements from the dict recursively
    :param d:
    :param skip:
    :return:
    """
    return _drop_from_dict(d, skip)


def join_inner_arrays(_dict: dict, caster=lambda x: x) -> dict:
    """
    For any arrays in the dictionary, join its elements into a comma seperated string, optionally casting each element
    pre - join.
    :param _dict:
    :param caster:
    :return:
    """
    return {
        k: ",".join(map(caster, v)) if isinstance(v, list) else v
        for (k, v) in _dict.items()
    }


def invert_dict_lookup(d: dict) -> dict:
    """
    Flip the key-value pairs in a dict.
    :param d:
    :return:
    """
    return {v: k for k, v in d.items()}


def pluck(path, d, default={}):
    """
    Get a sepecific element from a dict.
    :param path:
    :param d:
    :param default:
    :return:
    """
    split_path = [x for x in path.split(".") if x]
    if len(split_path) > 0:
        return pluck(".".join(split_path[1:]), d.get(split_path[0], default))
    return d


def group_by_key(l: List[Any], key: Callable[[Any], str]) -> Mapping[str, List[Any]]:
    """
    Create groups of elements from a list, based on a grouping function.
    :param l:
    :param key:
    :return:
    """
    key_deriver = key if callable(key) else lambda x: x[key]
    returnVal: Mapping[str, List] = defaultdict(list)
    for x in l:
        returnVal[key_deriver(x)].append(x)
    return returnVal


def group_objects_by(
    l: List[Any], group_by: Callable[[Any], str]
) -> Mapping[str, List[Any]]:
    """
    Create groups of elements from a list, based on a grouping function.
    TODO whats the diff between this and group_by_key
    :param l:
    :param group_by:
    :return:
    """
    unique_groups = set(map(group_by, l))
    return {g: list(filter(lambda x: group_by(x) == g, l)) for g in unique_groups}


def reverse_index_dictionary(d: dict) -> dict:
    """
    Invert keys and values of a dictionary, hanging onto any duplicate values that occure pre-reversing
    :param d:
    :return:
    """
    new_keys = list(set(flatten_list_recursively(list(d.values()))))
    return {
        new_key: [old_key for old_key in list(d.keys()) if new_key in d[old_key]]
        for new_key in new_keys
    }


def map_key(o: dict, key: str, mapper: Callable) -> dict:
    """
    Map the value of a specific key in a dictionary.
    :param o:
    :param key:
    :param mapper:
    :return:
    """
    return pydash.set_(o, key, mapper(pydash.get(o, key)))


def merge_unique_objects_on(
    objects: List[Any], identifier: Callable, reducer: Callable = head
) -> List[Any]:
    """
    Reduce a list of objects that are in the same group (determined by a grouping function) based on the
    reduction function.
    :param objects:
    :param identifier:
    :param reducer:
    :return:
    """
    groups = group_by_key(objects, identifier)
    return list(
        {groupId: reducer(values) for groupId, values in groups.items()}.values()
    )


def convert_to_string_dict(d: dict) -> dict:
    """
    Cast keys and values in dict to strings.
    :param d:
    :return:
    """
    return {str(k): str(v) for k, v in d.items()}


def negate_dict_of_numbers(d: dict) -> dict:
    """
    For dicts with number values, invert the numbers.
    :param d:
    :return:
    """
    return {k: -1 * v for k, v in d.items()}


# ------------------------------------------ ENUM Utils ------------------------------------------


class EnumWithCamelCasedNamesAsDefaultValue(Enum):
    """
    Enum where auto values are CamelCased
    """

    def _generate_next_value_(name, start, count, last_values):
        return pydash.strings.camel_case(name)


class EnumWithNamesAsDefaultValue(Enum):
    """
    Enum where auto values are the raw name of the auto value.
    """

    def _generate_next_value_(name, start, count, last_values):
        return name


def merge_enum_values(
    values: List[Enum],
    merger: Callable[[list], object] = lambda values: ".".join(values),
) -> object:
    """
    Merges enum values
    :param values:
    :param merger:
    :return:
    """
    return merger(list(map(lambda x: x.value, values)))


def unzip(list_of_tuples: List) -> List[List]:
    """
    Turns a list of tuples into a list of lists ... where the first list groups all the first elements of the tuples ...

    Unzips a list of tuples into a list of the first elements, second elements, ...
    Tuples all have to be of equal length ...

    :param list_of_tuples:
    :return:
    """
    return list(map(list, zip(*list_of_tuples)))


def rename(d: dict, keys_to_rename: List[Tuple[str, str]]) -> dict:
    """
    Capable of renaming the same key into multiple new keys ...
    :param d:
    :param keys_to_rename:
    :return:
    """
    if not keys_to_rename:
        return d

    # keys_that_will_be_renamed = unzip(keys_to_rename)[0]
    keys_to_keep = pydash.omit(
        d, unzip(keys_to_rename)[0]
    )  # Omit all keys to be renamed ...
    renamed_keys = [
        pydash.rename_keys(pydash.pick(d, list(renamer.keys())[0]), renamer)
        for renamer in map(lambda pair: dict([pair]), keys_to_rename)
        if list(renamer.keys())[0]
        in d  # Omit all renaming for keys that dont exist in the dict to be renamed ...
    ]
    post_rename = pydash.merge({}, keys_to_keep, *renamed_keys)
    # print(f"keeping everything other than {keys_that_will_be_renamed} from {d} : {keys_to_keep}")
    # print(f"post_rename: {post_rename}")
    # print(f"renamed_keys: {renamed_keys}")
    return post_rename


ValidT = TypeVar("ValidT")


def prune_and_log_nulls_in_list(
    l: Iterable[Optional[ValidT]], iterable_label: str = "iterable"
) -> Iterator[ValidT]:
    """
    Logs and removes Nones from a list ...
    :param l:
    :param iterable_label:
    :return:
    """
    for i, item in enumerate(l):
        if item is None:
            log.warning(f"Pruned None value at index {i} within {iterable_label}.")
        else:
            yield item
