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

from io import BytesIO
import json
import unittest

from mocket.mockhttp import Entry
from mocket import mocketize

from cortex.connection import ConnectionClient
from cortex.content import ManagedContentClient
from cortex import Cortex

from .fixtures import john_doe_token

TOKEN = john_doe_token()
projectId = 'cogscale'
url = 'http://localhost:123'

# params similar to those passed from
params = {'token': TOKEN, 'projectId': projectId, 'apiEndpoint': url}


class TestConnectionClient(unittest.TestCase):

    def setUp(self):
        self.cc = ConnectionClient(url, token=TOKEN, project=projectId)
        self.mc = ManagedContentClient(url, token=TOKEN, project=projectId)
        self.client = Cortex.from_message(params)
        self.mcFromClient = ManagedContentClient(self.client)

    @mocketize
    def test_save_connection(self):
        uri = self.cc.URIs['connections'].format(projectId=projectId)
        url = self.cc._serviceconnector._construct_url(uri)
        connection = {'connectionType': 'ctype', 'name': 'cname'}
        Entry.single_register(Entry.POST,
                              url,
                              status=200,
                              body=json.dumps(connection))
        r = self.cc.save_connection(connection=connection, project=projectId)
        self.assertEqual(r, connection)

    @mocketize
    def test_upload(self):
        key = 'some-key'
        result = {'Key': key}
        uri = self.mc.URIs['content'].format(projectId=projectId)
        url = self.mc._serviceconnector._construct_url(uri)

        with BytesIO(b'arbitrary content') as content:
            Entry.single_register(Entry.POST,
                                  url,
                                  status=200,
                                  body=json.dumps(result))
            r = self.mc.upload(key=key, stream_name='foo', stream=content, content_type='application/octet-stream', project=projectId)
            self.assertEqual(r, result)

    @mocketize
    def test_uploadStreaming(self):
        key = 'some-key'
        result = { 'Key': key }
        uri = '{0}/{1}'.format(self.mc.URIs['content'].format(projectId=projectId), key)
        url = self.mc._serviceconnector._construct_url(uri)

        with BytesIO(b'arbitrary content') as content:
            Entry.single_register(Entry.POST,
                                  url,
                                  status = 200,
                                  body = json.dumps(result))
            r = self.mc.upload_streaming(key=key, stream=content, content_type='application/octet-stream', project=projectId)
            self.assertEqual(r, result)

    @mocketize
    def test_download(self):
        key = 'some-key'
        uri = '{0}/{1}'.format(self.mc.URIs['content'].format(projectId=projectId), key)
        url = self.mc._serviceconnector._construct_url(uri)
        buf = b'arbitrary content'
        with BytesIO(buf) as content:
            Entry.single_register(Entry.GET,
                                url,
                                status = 200,
                                body = content)
            r = self.mc.download(key=key, project=projectId)
            self.assertEqual(r.read(), buf)

    @mocketize
    def test_exists(self):
        key = 'some-key'
        result = { 'Key': key }
        uri = '{0}/{1}'.format(self.mc.URIs['content'].format(projectId=projectId), key)
        url = self.cc._serviceconnector._construct_url(uri)
        Entry.single_register(Entry.HEAD,
                              url,
                              status = 200,
                              body = json.dumps(result))
        
        r = self.mc.exists(key=key, project=projectId)
        self.assertTrue(r)
