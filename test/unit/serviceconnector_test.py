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

import json
from mocket.mockhttp import Entry
from mocket import mocketize
import requests
from cortex import __version__
from cortex.serviceconnector import ServiceConnector

from .fixtures import mock_api_endpoint, john_doe_token

URL = mock_api_endpoint()
VERSION = 4
TOKEN = john_doe_token()


def test__init__():
    s = ServiceConnector(URL, VERSION, token=TOKEN)

    assert s.url == URL
    assert s.version == VERSION


def test__construct_url():
    sc = ServiceConnector(URL, VERSION, token=TOKEN)
    r = sc._construct_url("abc")
    expect = "http://127.0.0.1:8000/fabric/v4/{}".format("abc")
    assert r == expect


@mocketize
def test_request():
    sc = ServiceConnector(URL, VERSION, token=TOKEN)
    path = "models/events"
    url = sc._construct_url(path)
    body = {"handle": 123}
    useragentfragment = f"cortex-python/{__version__}"
    Entry.single_register(Entry.POST, url, status=200, body=json.dumps(body))
    r = sc.request("POST", path, body)

    assert isinstance(r, requests.Response)
    assert r.status_code == 200
    assert r.json() == body
    assert useragentfragment in r.request.headers["user-agent"]
