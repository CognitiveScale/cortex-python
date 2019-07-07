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
import json

import dill
from mocket.mockhttp import Entry
from mocket import mocketize
from sklearn.linear_model import LinearRegression

from cortex import Cortex
from cortex.experiment import ExperimentClient
from cortex.run import RemoteRun
from .fixtures import john_doe_token, build_mock_url, mock_api_endpoint


class TestRun(unittest.TestCase):
    '''
    Test experiment checks experiment functionality
    '''
    RUN_EXP_NAME = 'unittest/exp'
    RUN_ID = '000001'

    def setUp(self):
        self.local = Cortex.local()
        self.cortex = Cortex.client(api_endpoint=mock_api_endpoint(), api_version=3, token=john_doe_token())

        # register mock for getting an expeiment from the client
        uri = ExperimentClient.URIs['experiment'].format(experiment_name=self.RUN_EXP_NAME)
        returns = {"name": self.RUN_EXP_NAME}
        Entry.single_register(Entry.GET, build_mock_url(uri), status=200, body=json.dumps(returns))

        # register mock for creating a run
        uri = ExperimentClient.URIs['runs'].format(experiment_name=self.RUN_EXP_NAME)

        returns = {"runId": self.RUN_ID}
        Entry.single_register(Entry.POST, build_mock_url(uri), status=200, body=json.dumps(returns))

    @mocketize
    def test_make_remote_run(self): 
        exp = self.cortex.experiment(self.RUN_EXP_NAME, version='3')
        r = exp.start_run()

        self.assertIsInstance(r, RemoteRun)

    @mocketize
    def test_run_get_artifact(self):
        exp = self.cortex.experiment(self.RUN_EXP_NAME, version='3')
        r = exp.start_run()

        test_artifact = {'a': 0.7071, 'b': 1.4142, 'c': 2.718}

        # get the artifact & test if it is what is expected
        ## register mock for loading an artifact
        uri = ExperimentClient.URIs['artifact'].format(
                experiment_name=self.RUN_EXP_NAME, 
                run_id=self.RUN_ID, 
                artifact='artifact'
                )
        Entry.single_register(Entry.GET, build_mock_url(uri), status=200, body=dill.dumps(test_artifact))
        result = r.get_artifact('artifact')

        self.assertEqual(test_artifact, result)
