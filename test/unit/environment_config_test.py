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

import unittest

from unittest.mock import Mock

from cortex.env import CortexEnv
from cortex.exceptions import BadTokenException


class TestCortexConfiguration(unittest.TestCase):

    def setUp(self):
        self.getCortexTokenOriginal = CortexEnv.get_cortex_token
        self.getCortexProfileOriginal = CortexEnv.get_cortex_profile

    def test_get_cortex_token(self):
        token = 'some_token'
        CortexEnv.get_cortex_token = Mock(return_value=token)
        self.assertEqual(CortexEnv.get_cortex_token(), token)

    def test_get_cortex_profile(self):
        profile = { "A" : 1, "B": 2 } 
        CortexEnv.get_cortex_profile = Mock(return_value=profile)
        self.assertEqual(CortexEnv.get_cortex_profile(), profile)
    
    def test_get_token_with_token_and_profile(self):
        token = 'some_token'
        profile =  {
            "url": "https://api.cortex-dev.insights.ai",
            "username": "adminTenant-666",
            "account": "testtenant-666",
            "token": "123c3MiOiJjb2duaXRpdmVzY2FsZS5jb20iLCJhdWQiOiJjb3J0ZXgiLCJzdWIiOiJhZG1pblRlbmFudC02NjYiLCJ0ZW5hbnQiOiJ0ZXN0dGVuYW50LTY2NiIsImJlYXJlciI6InB1YmxpYyIsImtleSI6Im5nM2NTa2Y0R2FlSmticU9wN1BIbVRNVHFPekh5eEc2IiwiZXhwIjoxNTU4MzY3ODEyLCJhY2wiOnsiLioiOlsiUkVBRCIsIlJVTiIsIldSSVRFIiwiREVMRVRFIl19LCJpYXQiOjE1NTcxNTgyMTJ9.VQPxm6j2i2QzqFGQGw-dMSSU8TkxQwkx_e9WN1tdHcU"
        }
        CortexEnv.get_cortex_token = Mock(return_value=token)
        CortexEnv.get_cortex_profile = Mock(return_value=profile)
        self.assertEqual(CortexEnv.get_token(), token)

    def test_get_token_with_token_and_empty_profile(self):
        token = 'some_token'
        profile = {}
        CortexEnv.get_cortex_token = Mock(return_value=token)
        CortexEnv.get_cortex_profile = Mock(return_value=profile)
        self.assertEqual(CortexEnv.get_token(), token)
    
    def test_get_token_with_no_token_and_profile(self):
        profile_token = '123c3MiOiJjb2duaXRpdmVzY2FsZS5jb20iLCJhdWQiOiJjb3J0ZXgiLCJzdWIiOiJhZG1pblRlbmFudC02NjYiLCJ0ZW5hbnQiOiJ0ZXN0dGVuYW50LTY2NiIsImJlYXJlciI6InB1YmxpYyIsImtleSI6Im5nM2NTa2Y0R2FlSmticU9wN1BIbVRNVHFPekh5eEc2IiwiZXhwIjoxNTU4MzY3ODEyLCJhY2wiOnsiLioiOlsiUkVBRCIsIlJVTiIsIldSSVRFIiwiREVMRVRFIl19LCJpYXQiOjE1NTcxNTgyMTJ9.VQPxm6j2i2QzqFGQGw-dMSSU8TkxQwkx_e9WN1tdHcU'
        profile =  {
            "url": "https://api.cortex-dev.insights.ai",
            "username": "adminTenant-666",
            "account": "testtenant-666",
            "token": profile_token
        }
        CortexEnv.get_cortex_token = Mock(return_value=None) # notice this is None (not the profile_token)
        CortexEnv.get_cortex_profile = Mock(return_value=profile)
        self.assertEqual(CortexEnv.get_token(), profile_token)

    def test_get_token_with_no_token_no_profile(self):
        profile_token = ''
        profile =  {}
        CortexEnv.get_cortex_token = Mock(return_value=profile_token)
        CortexEnv.get_cortex_profile = Mock(return_value=profile)
        self.assertEqual(CortexEnv.get_token(), None)

    def test_get_token_with_token_and_profile2(self):
        token = '123c3MiOiJjb2duaXRpdmVzY2FsZS5jb20iLCJhdWQiOiJjb3J0ZXgiLCJzdWIiOiJhZG1pblRlbmFudC02NjYiLCJ0ZW5hbnQiOiJ0ZXN0dGVuYW50LTY2NiIsImJlYXJlciI6InB1YmxpYyIsImtleSI6Im5nM2NTa2Y0R2FlSmticU9wN1BIbVRNVHFPekh5eEc2IiwiZXhwIjoxNTU4MzY3ODEyLCJhY2wiOnsiLioiOlsiUkVBRCIsIlJVTiIsIldSSVRFIiwiREVMRVRFIl19LCJpYXQiOjE1NTcxNTgyMTJ9.VQPxm6j2i2QzqFGQGw-dMSSU8TkxQwkx_e9WN1tdHcU'
        profile =  {
            "url": "https://api.cortex-dev.insights.ai",
            "username": "adminTenant-666",
            "account": "testtenant-666",
            "token": 'mumjobotoken'
        }
        CortexEnv.get_cortex_token = Mock(return_value=token) # notice this is None
        CortexEnv.get_cortex_profile = Mock(return_value=profile)
        self.assertEqual(CortexEnv.get_token(), token)

    def test_constructor_no_profile_and_no_token(self):
        token = ''
        profile = {}
        CortexEnv.get_cortex_token = Mock(return_value=token)
        CortexEnv.get_cortex_profile = Mock(return_value=profile)
        self.assertRaises(BadTokenException, CortexEnv)

    # we don't want methods calls to CortexEnv to use the monkey patched methods
    # so we revert back to the original methods.
    def tearDown(self):
        CortexEnv.get_cortex_token = self.getCortexTokenOriginal
        CortexEnv.get_cortex_profile = self.getCortexProfileOriginal
