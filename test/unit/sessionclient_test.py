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

import unittest
import uuid
import requests_mock

from cortex.session import SessionClient
from cortex.client import Cortex

from .fixtures import john_doe_token, mock_api_endpoint, mock_project

projectId = mock_project()
url = mock_api_endpoint()

TOKEN=''
with requests_mock.Mocker() as m:
    TOKEN = john_doe_token(m)


@requests_mock.Mocker()
class TestSessionClient(unittest.TestCase):
    def setUp(self):
        params = {"token": TOKEN, "projectId": projectId, "apiEndpoint": url}
        self.client = SessionClient(Cortex.from_message(params))
        self.session_id = str(uuid.uuid4())

    def register_entry(self, m, verb, uri, body):
        url = self.client._serviceconnector._construct_url(uri)
        m.register_uri(verb, url, status_code=200, json=body)
    
    # Sessions #
    def test_start_sessions(self, m):
        uri = self.client.URIs["start"].format(projectId=projectId)
        returns = {"sessionId": self.session_id}
        self.register_entry(m, 'POST', uri, returns)
        r = self.client.start_session(100, "test")
        self.assertEqual(r, self.session_id)

    def test_get_all(self, m):
        uri = self.client.URIs["get"].format(
            sessionId=self.session_id, projectId=projectId
        )
        returns = {"state": {"key1": "value1"}}
        self.register_entry(m, 'GET', uri, returns)

        r = self.client.get_session_data(self.session_id, None)
        self.assertEqual(r, returns["state"])

    def test_get_by_key(self, m):
        uri = (
            self.client.URIs["get"].format(
                sessionId=self.session_id, projectId=projectId
            )
            + "?key=key1"
        )
        returns = {"state": {"key1": "value1"}}
        self.register_entry(m, 'GET', uri, returns)

        r = self.client.get_session_data(self.session_id, "key1")
        self.assertEqual(r, returns["state"])

    def test_put(self, m):
        uri = self.client.URIs["put"].format(
            sessionId=self.session_id, projectId=projectId
        )
        returns = {}
        self.register_entry(m, 'POST', uri, returns)

        r = self.client.put_session_data(self.session_id, {})
        self.assertEqual(r, returns)

    def test_delete(self, m):
        uri = self.client.URIs["delete"].format(
            sessionId=self.session_id, projectId=projectId
        )
        returns = {}
        self.register_entry(m, 'DELETE', uri, returns)

        r = self.client.delete_session(self.session_id)
        self.assertEqual(r, returns)
