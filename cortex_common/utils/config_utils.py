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

import base64

# pylint: disable=line-too-long
# pylint: disable=no-value-for-parameter
# pylint: disable=bad-mcs-method-argument
# pylint: disable=unnecessary-pass
# pylint: disable=too-few-public-methods

__all__ = [
    "AttrsAsDict",
    "base64encode_string",
    "base64decode_string",
]


class _AttrsAsDictMeta(type):
    """
    Meta class to help transform any python class that extends this type into a dict where the keys are the attributes
    of the class and the values are the respected attribute values.

    This class is useful in place of enums, where we want an IDE to auto fill in attributes, but we want to treat the
    class like a dict as well.
    """

    def __iter__(self):
        """
        __iter__
        :return:
        :rtype:
        """
        return zip(self.keys(), self.values())

    def __getitem__(self, arg):
        """
        __getitem__
        :param arg:
        :type arg:
        :return:
        :rtype:
        """
        return dict(list(self)).get(arg)

    def keys(cls):
        """
        keys
        :return:
        :rtype:
        """
        return list(filter(lambda x: x[0] != "_", cls.__dict__.keys()))

    def values(cls):
        """
        values
        :return:
        :rtype:
        """
        return [getattr(cls, k) for k in cls.keys()]

    def items(cls):
        """
        items
        :return:
        :rtype:
        """
        return dict(list(cls)).items()


class AttrsAsDict(metaclass=_AttrsAsDictMeta):
    """
    Any class that extends this will have its attributes be transformable into a dict.
    """

    pass


def base64encode_string(string_to_base64encode: str, encoding: str = "utf-8") -> str:
    """
    Encodes a string into a base64 encoded string
    :param base64encoded_jsonstring:
    :return:
    """
    return base64.urlsafe_b64encode(string_to_base64encode.encode(encoding)).decode(
        encoding
    )


def base64decode_string(base64encoded_string: str, encoding="utf-8") -> str:
    """
    Decodes a base64 encoded string back into the original string.
    :param base64encoded_jsonstring:
    :return:
    """
    return base64.urlsafe_b64decode(base64encoded_string).decode(encoding)
