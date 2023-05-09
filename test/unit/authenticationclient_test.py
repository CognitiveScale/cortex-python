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
import requests_mock

from cortex.auth import AuthenticationClient
from cortex.utils import decode_JWT, verify_JWT
from .fixtures import mock_pat_config, mock_api_endpoint, register_mock_fabric_info


@requests_mock.Mocker()
class TestAuthenticationClient(unittest.TestCase):
    def setUp(self):
        pass

    def test_contructor_with_args(self, m):
        # This client doesn't need parameters, but allow them for backward compat
        register_mock_fabric_info(m)
        ac = AuthenticationClient(mock_api_endpoint(), 4)
        jwt = ac.fetch_auth_token(mock_pat_config())

    def test_fetch_auth_token(self, m):
        register_mock_fabric_info(m)
        self.ac = AuthenticationClient()
        # setup
        # uri = self.ac.URIs['authenticate'].format(projectId='cogscale')
        # url = self.ac._serviceconnector._construct_url(uri)
        body = mock_pat_config()
        # Entry.single_register(Entry.POST,
        #                       url,
        #                       status = 200,
        #                       body = json.dumps(body))
        # execute
        # todo mock this call?..
        token = self.ac.fetch_auth_token(body)
        # test
        decodedbody = decode_JWT(token)
        self.assertEqual(body["issuer"], decodedbody[1]["iss"])

    def test_expired_token(self, m):
        # Shouldn't fail to validate expired token WITHIN the python lib, this is responsibiltiy of auth proxy...
        exp_token = "eyJhbGciOiJFZERTQSIsImtpZCI6IkhwVy15YTdGU1U3eVYtYWx6eWV3UFBEd1BlRmdya2kwVlFQS2JoNEo0UHciLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJjb3J0ZXgiLCJleHAiOjE2MzAzNDgxOTYsImlhdCI6MTYzMDM0ODE2NiwiaXNzIjoiY29nbml0aXZlc2NhbGUuY29tIiwianRpIjoiU0dkRjVidG1fUXlYcjZhMVRrOU9oZyIsIm5iZiI6MTYzMDM0ODE2Niwic3ViIjoiNzFhOGZhYWMtOWRmYi00MjhkLWE5MGMtMGI1MzQ4MWI4NjY1In0.pB7hvEcIMV1Qt6GTGPGcKbS1zhidPMJ-luV-KBOaHrwgCh2jDOQdve2Sv5RqmNa6Jkk-Bxh-1g4XG8CxGGSqAQ"
        verify_JWT(exp_token)
