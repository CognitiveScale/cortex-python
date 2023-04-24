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

from typing import List
from attr import attrs, attrib


@attrs(repr=False, slots=True, hash=True)
class ListItemsAreInstanceOf:
    """
    Checks if items of a list are the right value ...
    """

    type = attrib()
    nullable = attrib(type=bool, default=False)  # Is the list itself nullable?

    def __call__(self, inst, attr, value: List):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        if value is None:
            if self.nullable:
                pass
            else:
                raise TypeError("'{name}' can not be None.".format(name=attr.name))
        for item in value:
            self.check_if_item_is_instance(attr, item)

    def check_if_item_is_instance(self, attr, value):
        """
        check_if_item_is_instance
        :param attr:
        :type attr:
        :param value:
        :type value:
        :return:
        :rtype:
        """  # pylint: disable=line-too-long
        if not isinstance(value, self.type):
            raise TypeError(
                "All instances of '{name}' must be {type!r} (got {value!r} that is actually a {actual!r}).".format(
                    name=attr.name,
                    type=self.type,
                    actual=value.__class__,
                    value=value,
                )
            )

    def __repr__(self):
        return "<instance_of validator for type {type!r}>".format(type=self.type)
