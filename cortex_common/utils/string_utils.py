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

import itertools
import re
from typing import List, cast

from cortex_common.utils.object_utils import head, tail

# pylint: disable=line-too-long
# pylint: disable=invalid-name
# pylint: disable=no-else-return

__all__ = [
    "split_camel_case",
    "split_string_into_parts",
]


def split_camel_case(string: str) -> List[str]:
    """
    Turns "CLevelChangeInsights" into ['C', 'Level', 'Change ', 'Insights']
    :param string:
    :return:
    """
    l = [x for x in re.split(r"([A-Z])", string) if x]
    if not l:
        return l
    if not tail(l):
        return l

    upper_case_chrs = list(map(chr, range(ord("A"), ord("Z") + 1)))
    lower_case_chrs = list(map(chr, range(ord("a"), ord("z") + 1)))
    if head(l) in upper_case_chrs and head(head(tail(l))) in upper_case_chrs:
        return cast(List[str], [head(l)]) + split_camel_case("".join(tail(l)))
    elif head(l) in upper_case_chrs and head(head(tail(l))) in lower_case_chrs:
        return cast(
            List[str], ["{}{}".format(head(l), head(tail(l)))]
        ) + split_camel_case("".join(tail(tail(l))))
    else:
        return cast(List[str], [head(l), head(tail(l))]) + split_camel_case(
            "".join(tail(tail(l)))
        )


def split_string_into_parts(string: str, num_of_parts: int) -> List:
    """
    Split up a string ...
    :param string:
    :param num_of_parts:
    :return:
    """
    l = len(string)
    splittings = list(
        zip(
            [0]
            + list(map(lambda x: int(x * l / num_of_parts), range(1, num_of_parts))),
            list(map(lambda x: int(x * l / num_of_parts), range(1, num_of_parts))) + [None],  # type: ignore
        )
    )
    return ["".join(list(itertools.islice(string, x, y))) for x, y in splittings]
