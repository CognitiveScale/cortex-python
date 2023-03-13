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
from typing import Any, Dict, List, Optional


# pylint: disable=missing-class-docstring


class GraphQLClientError(Exception):
    """Base exception."""


class GraphQLClientHttpError(GraphQLClientError):
    def __init__(self, status_code: int, response) -> None:
        self.status_code = status_code
        self.response = response

    def __str__(self) -> str:
        return f"HTTP status code: {self.status_code}"


class GraphQlClientInvalidResponseError(GraphQLClientError):
    def __init__(self, response) -> None:
        self.response = response

    def __str__(self) -> str:
        return "Invalid response format."


class GraphQLClientGraphQLError(GraphQLClientError):
    def __init__(
        self,
        message: str,
        locations: Optional[List[Dict[str, int]]] = None,
        path: Optional[List[str]] = None,
        extensions: Optional[Dict[str, object]] = None,
        orginal: Optional[Dict[str, object]] = None,
    ):
        self.message = message
        self.locations = locations
        self.path = path
        self.extensions = extensions
        self.orginal = orginal

    def __str__(self) -> str:
        return self.message

    @classmethod
    def from_dict(cls, error: dict[str, Any]) -> "GraphQLClientGraphQLError":
        """
        It takes a dictionary and returns a GraphQLClientGraphQLError object

        :param cls: The class that is being instantiated
        :param error: dict[str, Any]
        :type error: dict[str, Any]
        :return: A GraphQLClientGraphQLError object
        """
        return cls(
            message=error["message"],
            locations=error.get("locations"),
            path=error.get("path"),
            extensions=error.get("extensions"),
            orginal=error,
        )


class GraphQLClientGraphQLMultiError(GraphQLClientError):
    def __init__(self, errors: List[GraphQLClientGraphQLError], data: dict[str, Any]):
        """
        This function takes in a list of GraphQLClientGraphQLError objects and a dictionary of data and
        returns a GraphQLClientResponse object.

        :param errors: A list of GraphQLClientGraphQLError objects
        :type errors: List[GraphQLClientGraphQLError]
        :param data: The data returned from the GraphQL API
        :type data: dict[str, Any]
        """  # pylint: disable=line-too-long
        self.errors = errors
        self.data = data

    def __str__(self) -> str:
        """
        It returns a string that is the result of joining the string representation of each error in the
        list of errors, separated by a semicolon and a space
        :return: A string of the errors
        """  # pylint: disable=line-too-long
        return "; ".join(str(e) for e in self.errors)

    @classmethod
    def from_errors_dicts(
        cls, errors_dicts: List[dict[str, Any]], data: dict[str, Any]
    ) -> "GraphQLClientGraphQLMultiError":
        """
        It takes a list of error dictionaries and a data dictionary and returns a
        GraphQLClientGraphQLMultiError object

        :param cls: The class that is being instantiated
        :param errors_dicts: List[dict[str, Any]]
        :type errors_dicts: List[dict[str, Any]]
        :param data: The data returned from the GraphQL server
        :type data: dict[str, Any]
        :return: A GraphQLClientGraphQLMultiError object
        """
        return cls(
            errors=[GraphQLClientGraphQLError.from_dict(e) for e in errors_dicts],
            data=data,
        )


# pylint: enable=missing-class-docstring
