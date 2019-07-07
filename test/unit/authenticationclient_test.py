"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

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
import json
import unittest

from mocket.mockhttp import Entry
from mocket import mocketize

from cortex.auth import AuthenticationClient

class TestAuthenticationClient(unittest.TestCase):

    def setUp(self):
        self.ac = AuthenticationClient('http://localhost:8000', 2)

    @mocketize
    def test_fetch_auth_token(self):
        # setup
        uri = self.ac.URIs['authenticate'].format('cogscale')
        url = self.ac._serviceconnector._construct_url(uri)
        body={"jwt": "123"}
        Entry.single_register(Entry.POST,
                              url,
                              status = 200,
                              body = json.dumps(body))
        # execute
        token = self.ac.fetch_auth_token('cogscale', 'marcus', 'secret')
        # test
        self.assertEqual(token, '123')

