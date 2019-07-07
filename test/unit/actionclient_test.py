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
import unittest

from mocket.mockhttp import Entry
from mocket import mocketize

from cortex.action import ActionClient


class TestActionClient(unittest.TestCase):

    def setUp(self):
        self.client = ActionClient('http://localhost:8000', 3, 'token')

    def register_entry(self, verb, uri, body):
        url = self.client._serviceconnector._construct_url(uri)
        Entry.single_register(verb,
                              url,
                              status=200,
                              body=json.dumps(body))

    ## Actions ##

    @mocketize
    def test_invoke_action(self):
        uri = self.client.URIs['invoke'].format(action_name='unittest')
        returns = {"payload": {"text": "Hello World"}}
        self.register_entry(Entry.POST, uri, returns)

        r = self.client.invoke_action("unittest", {})
        self.assertEqual(r, returns)

    @mocketize
    def test_get_logs(self):
        uri = self.client.URIs['logs'].format(action_name='unittest')
        returns = {"logs": []}
        self.register_entry(Entry.GET, uri, returns)

        r = self.client.get_logs("unittest")
        self.assertEqual(r, returns)

    @mocketize
    def test_get_tasks(self):
        uri = self.client.URIs['tasks'].format(action_name='unittest')
        returns = {
            "success": True,
            "data": [
                {
                    "status": "SUCCEEDED",
                    "createdAt": "2018-10-03T15:53:46.294Z",
                    "taskId": "foo1"
                },
            ]
        }
        self.register_entry(Entry.GET, uri, returns)

        r = self.client.get_tasks("unittest")
        self.assertEqual(r, returns)

    @mocketize
    def test_delete_task(self):
        uri = self.client.URIs['task_delete'].format(action_name='unittest', task_id='123')
        returns = {"success": True, "status": "CANCELLED"}
        self.register_entry(Entry.DELETE, uri, returns)

        r = self.client.delete_task('unittest', '123')
        self.assertEqual(r, returns)

    @mocketize
    def test_task_stats(self):
        uri = self.client.URIs['job_stats'].format(action_name='unittest')
        returns = {
            "success": True,
            "stats": {
                "CANCELLED": 1,
                "FAILED": 1,
                "SUCCEEDED": 2
            }
        }
        self.register_entry(Entry.GET, uri, returns)

        r = self.client.get_job_stats('unittest')
        self.assertEqual(r, returns)