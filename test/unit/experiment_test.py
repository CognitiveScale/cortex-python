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
import os

from cortex import Cortex
from cortex.experiment import ExperimentClient

from mocket.mockhttp import Entry
from mocket import mocketize
from .fixtures import john_doe_token, build_mock_url, mock_api_endpoint
import dill


class TestExperiment(unittest.TestCase):
    '''
    Test experiment checks experiment functionality
    '''    
    # values for testing experiments
    EXP_NAME = 'unittest/exp'

    def setUp(self):
        self.local = Cortex.local()
        self.local_tmp = Cortex.local('/tmp/cortex')
        self.cortex = Cortex.client(api_endpoint=mock_api_endpoint(), api_version=3, token=john_doe_token())

        # register mock for getting an expeiment from the client
        uri = ExperimentClient.URIs['experiment'].format(experiment_name=self.EXP_NAME)
        returns = {"name": self.EXP_NAME}
        Entry.single_register(Entry.GET, build_mock_url(uri), status=200, body=json.dumps(returns))

    @mocketize
    def test_make_remote_experiment(self):       
        exp = self.cortex.experiment(self.EXP_NAME, version='3')
        self.assertNotEqual(exp, None)

    def test_make_local_experiment(self):
        exp = self.local.experiment(self.EXP_NAME)
        self.assertNotEqual(exp, None)

    def test_make_local_experiment_custom_basedir(self):
        exp = self.local_tmp.experiment(self.EXP_NAME)
        self.assertNotEqual(exp, None)
        self.assertTrue(os.path.isdir(f'/tmp/cortex/local/experiments/{self.EXP_NAME}'))

    @mocketize
    def test_remote_load_artifact(self):
        exp = self.cortex.experiment(self.EXP_NAME, version='3')
        # add a run & artifact

        ## register mock for creating a run
        uri = ExperimentClient.URIs['runs'].format(experiment_name=self.EXP_NAME)
        run_id = '000001'
        returns = {"runId": run_id}
        Entry.single_register(Entry.POST, build_mock_url(uri), status=200, body=json.dumps(returns))

        run = exp.start_run()
        ## make an artifact
        my_dictionary = {'a_thing': 1, 'another_thing': 2}

        # get the artifact & test if it is what is expected
        ## register mock for loading an artifact
        uri = ExperimentClient.URIs['artifact'].format(experiment_name=self.EXP_NAME, run_id=run_id, artifact='my_dictionary')
        Entry.single_register(Entry.GET, build_mock_url(uri), status=200, body=dill.dumps(my_dictionary))

        result = exp.load_artifact(run, 'my_dictionary')
        self.assertEqual(result, my_dictionary)

    def test_save_multiple_local_experiments(self):
        exp = self.local.experiment(self.EXP_NAME)
        exp.reset()
        run_a = self.make_run(exp)
        run_b = self.make_run(exp)

        self.assertTrue(len(exp.runs()) == 2)

        # does exp have runs?
        self.assertFalse(exp.get_run(run_a.id) == None)
        self.assertFalse(exp.get_run(run_b.id) == None)

        # Are runs gone after reset and retrival?
        exp.reset()

        exp = self.local.experiment(self.EXP_NAME)
        self.assertTrue(len(exp.runs()) == 0)

    def test_reset_works_in_context(self):
        exp = self.local.experiment(self.EXP_NAME)
        exp.reset()
        exp.set_meta('style', 'supervised')
        exp.set_meta('function', 'regression')
        test_artifact = {'model': {}}
        with exp.start_run() as run:
            run.log_artifact('test', test_artifact)

        self.assertTrue(len(exp.runs()) == 1)
        self.assertEqual(run.get_artifact('test'), test_artifact)

    def make_run(self, exp):
        run = exp.start_run()
        run.set_meta('meta','meta_val')
        run.log_params({'param':'param_val'})
        run.start()
        run.stop()
        run.log_metric(name='metric_1',metric=85)
        exp.save_run(run)
        return run
