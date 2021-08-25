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
from cortex.utils import decode_JWT
from .fixtures import mock_pat_config
class TestAuthenticationClient(unittest.TestCase):

    def setUp(self):
        self.ac = AuthenticationClient('http://localhost:8000', 4)

    @mocketize
    def test_fetch_auth_token(self):
        # setup
        # uri = self.ac.URIs['authenticate'].format(projectId='cogscale')
        # url = self.ac._serviceconnector._construct_url(uri)
        body=mock_pat_config()
        # Entry.single_register(Entry.POST,
        #                       url,
        #                       status = 200,
        #                       body = json.dumps(body))
        # execute
        # todo mock this call?..
        token = self.ac.fetch_auth_token(body)
        # test
        decodedBody = decode_JWT(token, verify=False)
        self.assertEqual(body["issuer"], decodedBody["iss"])

