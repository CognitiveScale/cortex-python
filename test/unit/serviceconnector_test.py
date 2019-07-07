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

import json
from mocket.mockhttp import Entry
from mocket import mocketize
import requests


from cortex.serviceconnector import ServiceConnector

URL = "http://1.2.3.4:80"
VERSION = 3
TOKEN = "abc123"

def test__init__():
    s = ServiceConnector(URL, VERSION, TOKEN)

    assert s.token == TOKEN
    assert s.url == URL
    assert s.version == VERSION


def test__construct_url():
    sc = ServiceConnector(URL, VERSION, TOKEN)
    r = sc._construct_url('abc')
    expect = 'http://1.2.3.4:80/v3/{}'.format('abc')
    assert r == expect

@mocketize
def test_request():
    sc = ServiceConnector(URL, VERSION, TOKEN)
    path = 'models/events'
    url = sc._construct_url(path)
    body={"handle": 123}
    Entry.single_register(
        Entry.POST,
        url,
        status = 200,
        body = json.dumps(body)
    )
    r = sc.request('POST', path, body)

    assert isinstance(r, requests.Response)
    assert r.status_code == 200
    assert r.json() == body
