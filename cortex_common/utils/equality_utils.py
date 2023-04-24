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

from typing import List, Mapping

from cortex_common.utils.object_utils import head, tail

# pylint: disable=line-too-long
# pylint: disable=invalid-name
# pylint: disable=use-a-generator
# pylint: disable=unnecessary-lambda

__all__ = [
    "equal",
    "lists_are_equal",
    "dicts_are_equal",
    "merge_hashes",
    "hasher",
    "list_hasher",
    "dict_hasher",
]


def equal(x, y, equality_function=lambda a, b: a == b):
    """
    Determines if two things are equal
    :param x:
    :param y:
    :param equality_function:
    :return:
    """
    if isinstance(x, list):
        return lists_are_equal(x, y)
    if isinstance(x, dict):
        return dicts_are_equal(x, y)
    return equality_function(x, y)


def lists_are_equal(l1: List, l2: List):
    """
    Determines if two lists are equal
    :param l1:
    :param l2:
    :return:
    """
    return (
        isinstance(l1, list)
        and isinstance(l2, list)
        and (len(l1) == len(l2))
        and (all([t1 == t2 for t1, t2 in zip(map(type, l1), map(type, l2))]))
        and (all([equal(x, y) for x, y in zip(l1, l2)]))
    )


def dicts_are_equal(d1, d2):
    """
    Determines if two dicts are equal
    :param d1:
    :param d2:
    :return:
    """
    return (
        isinstance(d1, dict)
        and isinstance(d2, dict)
        and lists_are_equal(sorted(d1.keys()), sorted(d2.keys()))
        and all([equal(d1[x], d2[x]) for x in d1.keys()])
    )


def merge_hashes(*hn):
    """
    For combining hashes: https://stackoverflow.com/questions/29435556/how-to-combine-hash-codes-in-in-python3
    :return:
    """  # pylint: disable=line-too-long
    only_1_hash = head(tail(hn)) is None
    h1 = head(hn)
    h2 = head(tail(hn))
    return (
        hash(None)
        if not hn
        else (h1 if only_1_hash else merge_hashes(h1 ^ h2, *tail(tail(hn))))
    )


def hasher(x, hash_function=lambda a: hash(a)):
    """
    Hashes things in unison with their equality function.
    :param x:
    :param hash_function:
    :return:
    """
    if isinstance(x, list):
        return list_hasher(x)
    if isinstance(x, dict):
        return dict_hasher(x)
    return hash_function(x)


def list_hasher(l1: List):
    """
    Hashes a list in unison with its equality function.
    :param l1:
    :return:
    """
    return merge_hashes(*[hasher(x) for x in l1])


def dict_hasher(d1: Mapping):
    """
    Hashes a dict in unison with its equality function.
    :param d1:
    :return:
    """
    return merge_hashes(
        list_hasher(sorted(d1.keys())), list_hasher([d1[k] for k in sorted(d1.keys())])
    )
