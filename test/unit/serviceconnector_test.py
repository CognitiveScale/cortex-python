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
from mocket.mockhttp import Entry
from test.unit import fixtures
from mocket import mocketize
import pkg_resources
import requests
from cortex import __version__
from cortex.serviceconnector import ServiceConnector

URL = "http://1.2.3.4:80"
VERSION = 4

def test__init__():
    s = ServiceConnector(URL, VERSION, config=fixtures.mock_pat_config())

    assert s.url == URL
    assert s.version == VERSION


def test__construct_url():
    sc = ServiceConnector(URL, VERSION, config=fixtures.mock_pat_config())
    r = sc._construct_url('abc')
    expect = 'http://1.2.3.4:80/fabric/v4/{}'.format('abc')
    assert r == expect

@mocketize
def test_request():
    sc = ServiceConnector(URL, VERSION, config=fixtures.mock_pat_config())
    path = 'models/events'
    url = sc._construct_url(path)
    body={"handle": 123}
    userAgentFragment = f'cortex-python/{__version__}'
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
    assert userAgentFragment in r.request.headers['user-agent']
