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

from io import BytesIO, StringIO
import unittest
import requests_mock

from cortex.connection import ConnectionClient
from cortex.content import ManagedContentClient
from cortex.client import Cortex

from .fixtures import john_doe_token, mock_api_endpoint, mock_project

projectId = mock_project()
url = mock_api_endpoint()
TOKEN=''
with requests_mock.Mocker() as m:
    TOKEN = john_doe_token(m)


@requests_mock.Mocker()
class TestConnectionClient(unittest.TestCase):
    def setUp(self):
        params = {"token": TOKEN, "projectId": projectId, "apiEndpoint": url}
        self.cc = ConnectionClient(url, token=TOKEN, project=projectId)
        self.mc = ManagedContentClient(url, token=TOKEN, project=projectId)
        self.client = Cortex.from_message(params)
        self.mcFromClient = ManagedContentClient(self.client)

    def test_save_connection(self, m):
        uri = self.cc.URIs["connections"].format(projectId=projectId)
        url = self.cc._serviceconnector._construct_url(uri)
        connection = {"connectionType": "ctype", "name": "cname"}
        m.post(url, status_code=200, json=connection)
        r = self.cc.save_connection(connection=connection)
        self.assertEqual(r, connection)

    def test_upload(self, m):
        key = "some-key"
        result = {"Key": key}
        uri = self.mc.URIs["content"].format(projectId=projectId)
        local_url = self.mc._serviceconnector._construct_url(uri)
        with BytesIO(b"arbitrary content") as content:
            m.post(local_url, status_code=200, json=result)
            res = self.mc.upload(
                key=key,
                stream_name="foo",
                stream=content,
                content_type="application/octet-stream",
            )
            self.assertEqual(res, result)

        with StringIO("arbitrary content") as content:
            m.post(local_url, status_code=200, json=result)
            res = self.mc.upload(
                key=key,
                stream_name="foo",
                stream=content,
                content_type="application/text",
            )
            self.assertEqual(res, result)

    def test_uploadStreaming(self, m):
        key = "some-key"
        result = {"Key": key}
        uri = "{0}/{1}".format(self.mc.URIs["content"].format(projectId=projectId), key)
        local_url = self.mc._serviceconnector._construct_url(uri)

        with BytesIO(b"arbitrary content") as content:
            m.post(local_url, status_code=200, json=result)
            r = self.mc.upload_streaming(
                key=key, stream=content, content_type="application/octet-stream"
            )
            self.assertEqual(r, result)

    def test_download(self, m):
        key = "some-key"
        uri = "{0}/{1}".format(self.mc.URIs["content"].format(projectId=projectId), key)
        local_url = self.mc._serviceconnector._construct_url(uri)
        buf = b"arbitrary content"
        with BytesIO(buf) as content:
            m.get(local_url, status_code=200, body=content)
            r = self.mc.download(key=key)
            self.assertEqual(r.read(), buf)

    def test_exists(self, m):
        key = "some-key"
        result = {"Key": key}
        uri = "{0}/{1}".format(self.mc.URIs["content"].format(projectId=projectId), key)
        url = self.cc._serviceconnector._construct_url(uri)
        m.head(url, status_code=200, json=result)
        r = self.mc.exists(key=key)
        self.assertTrue(r)
