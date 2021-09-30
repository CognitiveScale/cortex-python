"""
Copyright 2021 Cognitive Scale, Inc. All Rights Reserved.

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

import json
import unittest
import uuid
from test.unit import fixtures
from mocket.mockhttp import Entry
from mocket import mocketize

from cortex.session import SessionClient

PROJECTID = 'sesstest'

class TestSessionClient(unittest.TestCase):

    def setUp(self):
        self.client = SessionClient('http://localhost:8000', config=fixtures.mock_pat_config())
        self.session_id = str(uuid.uuid4())

    def register_entry(self, verb, uri, body):
        url = self.client._serviceconnector._construct_url(uri)
        Entry.single_register(verb,
                              url,
                              status=200,
                              body=json.dumps(body))

    ## Sessions ##

    @mocketize
    def test_start_sessions(self):
        uri = self.client.URIs['start'].format(projectId=PROJECTID)
        returns = { 'sessionId': self.session_id }
        self.register_entry(Entry.POST, uri, returns)

        r = self.client.start_session(100, 'test', PROJECTID)
        self.assertEqual(r, self.session_id)

    @mocketize
    def test_get_all(self):
        uri = self.client.URIs['get'].format(session_id=self.session_id, projectId=PROJECTID)
        returns = {'state': {'key1': 'value1'}}
        self.register_entry(Entry.GET, uri, returns)

        r = self.client.get_session_data(self.session_id, None, PROJECTID)
        self.assertEqual(r, returns['state'])

    @mocketize
    def test_get_by_key(self):
        uri = self.client.URIs['get'].format(session_id=self.session_id, projectId=PROJECTID) + '?key=key1'
        returns = {'state': {'key1': 'value1'}}
        self.register_entry(Entry.GET, uri, returns)

        r = self.client.get_session_data(self.session_id, 'key1', PROJECTID)
        self.assertEqual(r, returns['state'])

    @mocketize
    def test_put(self):
        uri = self.client.URIs['put'].format(session_id=self.session_id, projectId=PROJECTID)
        returns = {}
        self.register_entry(Entry.POST, uri, returns)

        r = self.client.put_session_data(self.session_id, {}, PROJECTID)
        self.assertEqual(r, returns)

    @mocketize
    def test_delete(self):
        uri = self.client.URIs['delete'].format(session_id=self.session_id, projectId=PROJECTID)
        returns = {}
        self.register_entry(Entry.DELETE, uri, returns)

        r = self.client.delete_session(self.session_id, PROJECTID)
        self.assertEqual(r, returns)
