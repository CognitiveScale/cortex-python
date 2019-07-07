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

import unittest

from cortex import Cortex
from cortex.message import Message

from .fixtures import john_doe_subject, john_doe_token


class Test_Cortex(unittest.TestCase):
    
    def test_client(self):
        api_endpoint = 'https://api.test.cortex'
        api_version = 1
        account = 'unittest'
        username = 'unittest'
        password = 'unittest'
        token = john_doe_token()

        cortex = Cortex.client(
                api_endpoint=api_endpoint,
                api_version=api_version,
                account=account,
                username=username,
                password=password,
                token=token
                )
        assert cortex._url == api_endpoint
        assert cortex._token._account == account
        assert cortex._token._username == username
        assert cortex._token._password == password
        assert cortex._token._token == token
        assert cortex._token._jwt['sub'] == john_doe_subject()

    def test_message_constructor(self):
        cortex = Cortex.client(
            api_endpoint = 'https://api.test.cortex',
            api_version = 1,
            account = 'unittest',
            username = 'unittest',
            password = 'unittest',
            token = john_doe_token()
            )
        message = cortex.message({'foo': 'bar'})
        assert isinstance(message, Message)
        assert message.apiEndpoint == cortex._url
        assert message.token == cortex._token.token
        assert message.token == john_doe_token()


