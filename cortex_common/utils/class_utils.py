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

from typing import Callable, Any
from functools import wraps
from cortex_common.utils.attr_utils import attr_class_to_dict

# pylint: disable=too-few-public-methods
__all__ = [
    "state_modifier",
    "BaseAttrClass",
]


def state_modifier(result_factory: Callable, state_updater: Callable[[Any, Any], Any]):
    """
    Decorator on class methods that modify the state of the class (self) with the output of the class method
    based on the provided state_updater function
    :param result_factory:
    :param state_updater:
    :return:
    """  # pylint: disable=line-too-long

    def inner_decorator(f_to_wrap: Callable):
        @wraps(result_factory)
        def f_that_gets_called(*args, **kwargs):
            state_updater(args[0], result_factory(*args[1:], **kwargs))
            return f_to_wrap(args[0])

        return f_that_gets_called

    return inner_decorator


class BaseAttrClass:
    """
    Base class for attr oriented models.
    """

    def __iter__(self):
        # Skipping nulls ... so that the JS defaults kick into place ...
        return iter(
            attr_class_to_dict(
                self, hide_internal_attributes=True, skip_nulls=True
            ).items()
        )
