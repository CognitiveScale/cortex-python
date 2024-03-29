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

from typing import Dict
from .utils import get_logger, parse_string
from .serviceconnector import _Client

log = get_logger(__name__)


class SessionClient(_Client):
    """
    A client for the Cortex Sessions API.
    """

    URIs = {
        "start": "projects/{projectId}/sessions",
        "get": "projects/{projectId}/sessions/{sessionId}",
        "put": "projects/{projectId}/sessions/{sessionId}",
        "delete": "projects/{projectId}/sessions/{sessionId}",
    }

    def start_session(self, ttl=None, description="No description given") -> str:
        """
        Starts a new session.

        :param ttl: Resets sessions expiration; default is 15 minutes.
        :param description: An optional human-readable description for this sessions instance
        :return: The ID of the new Session.
        """
        uri = self.URIs["start"].format(projectId=self._project())
        params = {}
        if ttl:
            params["ttl"] = ttl

        params["description"] = description

        result = self._post_json(uri, params)
        return result.get("sessionId")

    def get_session_data(self, session_id, key=None) -> Dict[str, object]:
        """
        Gets data for a specific session.

        :param session_id: The ID of the session to query.
        :param key: An optional key in the session memory; the entire session memory is returned if a key is not specified.
        :return: A dict containing the requested session data
        """  # pylint: disable=line-too-long
        uri = self.URIs["get"].format(
            sessionId=parse_string(session_id), projectId=self._project()
        )
        if key:
            uri += "?key={key}".format(key=key)

        result = self._get_json(uri) or {}
        return result.get("state", {})

    def put_session_data(self, session_id, data: Dict):
        """
        Adds data to an existing session.

        :param session_id: The ID of the session to modify.
        :param data: Dict containing the new session keys to set.
        :return: status
        """
        uri = self.URIs["put"].format(
            sessionId=parse_string(session_id), projectId=self._project()
        )
        return self._post_json(uri, {"state": data})

    def delete_session(self, session_id):
        """
        Deletes a session.

        :param session_id: The ID of the session to delete.
        :return: status
        """
        uri = self.URIs["delete"].format(
            sessionId=parse_string(session_id), projectId=self._project()
        )
        return self._request_json(uri, method="DELETE")


class Session:
    """
    Session Represents a state for a client interaction with Cortex.
    """

    def __init__(self, session_id, client: SessionClient):
        self._session_id = session_id
        self._client = client
        self._project = client._project

    def get(self, key=None) -> object:
        """
        Gets the session data corresponding to the given key.

        :param key: the key to retrieve
        :return: session data corresponding to the given key
        """
        return self._client.get_session_data(self._session_id, key)

    def put(self, value: Dict):
        """
        Gets the session data corresponding to the given key.

        :param value: the value of the data to be put in the session
        :return: a json representation of the data put in the session
        """
        return self._client.put_session_data(self._session_id, value)

    def get_all(self) -> Dict:
        """
        Gets all the data associated with the session.
        :return: Session data
        """
        return self._client.get_session_data(self._session_id)

    def delete(self):
        """
        Deletes the session from the client.
        :return: status
        """
        return self._client.delete_session(self._session_id)
