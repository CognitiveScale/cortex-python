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

from typing import Any, Dict, Optional, TypeVar, cast

from pydantic import BaseModel  # pylint: disable=no-name-in-module
from cortex.graphql_types.exceptions import (
    GraphQLClientGraphQLMultiError,
    GraphQLClientHttpError,
    GraphQlClientInvalidResponseError,
)
from .serviceconnector import _Client
from .utils import raise_for_status_with_detail

Self = TypeVar("Self", bound="BaseClient")


class BaseClient(_Client):
    """Base client used to manage graphql api requests.

    :param _Client: _description_
    :type _Client: _type_
    :return: An instance of a BaseClient
    """

    URIs = {"graphql": "graphql"}

    def __enter__(self: Self) -> Self:
        return self

    def execute(self, query: str, variables: Optional[Dict[str, Any]] = None):
        """
        It takes a GraphQL query and variables, and returns the result of the query.

        :param query: The GraphQL query to execute
        :type query: str
        :param variables: A dictionary of variables to pass to the GraphQL query
        :type variables: Optional[Dict[str, Any]]
        :return: A JSON object
        """
        payload: Dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = self._convert_dict_to_json_serializable(variables)
        uri = self.URIs["graphql"].format(projectId=self._project())
        headers = {"Content-Type": "application/json"}
        res = self._serviceconnector.request("POST", uri, payload, headers)
        raise_for_status_with_detail(res)
        return res.json()

    def get_data(self, response) -> dict[str, Any]:
        """
        If the response is not successful, raise an error.
        If the response is successful, return the data

        :param response: The response object returned by the requests library
        :return: A dictionary of the data returned from the GraphQL query.
        """  # pylint: disable=line-too-long
        if not response.is_success:
            raise GraphQLClientHttpError(
                status_code=response.status_code, response=response
            )

        try:
            response_json = response.json()
        except ValueError as exc:
            raise GraphQlClientInvalidResponseError(response=response) from exc

        if (not isinstance(response_json, dict)) or ("data" not in response_json):
            raise GraphQlClientInvalidResponseError(response=response)

        data = response_json["data"]
        errors = response_json.get("errors")

        if errors:
            raise GraphQLClientGraphQLMultiError.from_errors_dicts(
                errors_dicts=errors, data=data
            )

        return cast(dict[str, Any], data)

    def _convert_dict_to_json_serializable(
        self, dict_: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        > It takes a dictionary of keys and values, and if any of the values are instances of `BaseModel`,
        it converts them to dictionaries using `BaseModel.dict()`

        :param dict_: The dictionary to convert
        :type dict_: Dict[str, Any]
        :return: A dictionary with the keys and values of the original dictionary, but with the values converted to JSON
        serializable objects.
        """  # pylint: disable=line-too-long
        return {
            key: value
            if not isinstance(value, BaseModel)
            else value.dict(by_alias=True)
            for key, value in dict_.items()
        }
