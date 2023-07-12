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

import unittest
import json
import os

import requests_mock

from cortex.client import Cortex
from cortex.experiment import ExperimentClient, Experiment

from .fixtures import mock_api_endpoint, mock_project
from .fixtures import john_doe_token

import dill

TOKEN=''
with requests_mock.Mocker() as m:
    TOKEN = john_doe_token(m)
projectId = mock_project()
url = mock_api_endpoint()
params = {"token": TOKEN, "projectId": projectId, "apiEndpoint": url}


@requests_mock.Mocker()
class TestExperiment(unittest.TestCase):
    """
    Test experiment checks experiment functionality
    """

    # values for testing experiments
    EXP_NAME = "unittest-exp"

    def setUp(self):
        self.cortex = Cortex.from_message(params)
        self.expc = ExperimentClient(self.cortex)
        self.local = Cortex.local()
        self.local_tmp = Cortex.local("/tmp/cortex")

    def test_get_remote_experiment(self, m):
        uri = self.cortex.experiments.URIs["experiment"].format(
            experimentName=self.EXP_NAME, projectId=projectId
        )
        local_url = self.cortex.experiments._serviceconnector._construct_url(uri)
        returns = {"name": self.EXP_NAME}
        m.get(local_url, status_code=200, json=returns)

        exp = self.cortex.experiments.get_experiment(self.EXP_NAME)
        self.assertNotEqual(exp, None)

    def test_list_remote_experiments(self, m):
        uri = self.cortex.experiments.URIs["experiments"].format(projectId=projectId)
        local_url = self.cortex.experiments._serviceconnector._construct_url(uri)
        returns = {"experiments": [{"name": self.EXP_NAME}]}
        m.get(local_url, status_code=200, json=returns)
        exps = self.cortex.experiments.list_experiments()

        self.assertNotEqual(exps, None)
        self.assertIsInstance(exps, list)

    def test_make_remote_experiment(self, m):
        uri = self.cortex.experiments.URIs["experiments"].format(projectId=projectId)
        local_url = self.cortex.experiments._serviceconnector._construct_url(uri)
        returns = {"name": self.EXP_NAME}
        m.post(local_url, status_code=200, json=returns)
        exp = Experiment(
            document=self.cortex.experiments.save_experiment(self.EXP_NAME),
            client=self.cortex.experiments,
        )
        self.assertNotEqual(exp, None)
        self.assertIsInstance(exp, Experiment)

    def test_make_local_experiment(self, m):
        uri = ExperimentClient.URIs["experiment"].format(
            experimentName=self.EXP_NAME, projectId=projectId
        )
        returns = {"name": self.EXP_NAME}
        m.get(uri, status_code=200, json=returns)
        exp = self.local.experiment(self.EXP_NAME)
        self.assertNotEqual(exp, None)

    def test_make_local_experiment_custom_basedir(self, m):
        exp = self.local_tmp.experiment(self.EXP_NAME)
        self.assertNotEqual(exp, None)
        self.assertTrue(os.path.isdir(f"/tmp/cortex/local/experiments/{self.EXP_NAME}"))

    def test_remote_load_artifact(self, m):
        uri = self.cortex.experiments.URIs["experiments"].format(projectId=projectId)
        local_url = self.expc._serviceconnector._construct_url(uri)
        returns = {"name": self.EXP_NAME}
        m.post(local_url, status_code=200, json=returns)

        exp = Experiment(
            document=self.cortex.experiments.save_experiment(
                experiment_name=self.EXP_NAME
            ),
            client=self.cortex.experiments,
        )
        # add a run & artifact

        # register mock for creating a run
        uri = ExperimentClient.URIs["runs"].format(
            projectId=projectId, experimentName=self.EXP_NAME
        )
        local_url = self.expc._serviceconnector._construct_url(uri)
        run_id = "000001"
        returns = {"runId": run_id}
        m.post(local_url, status_code=200, json=returns)
        run = exp.start_run()
        # make an artifact
        my_dictionary = {"a_thing": 1, "another_thing": 2}

        # get the artifact & test if it is what is expected
        # register mock for loading an artifact
        uri = ExperimentClient.URIs["artifact"].format(
            experimentName=self.EXP_NAME,
            runId=run_id,
            artifactId="my_dictionary",
            projectId=projectId,
        )
        local_url = self.expc._serviceconnector._construct_url(uri)
        m.get(local_url, status_code=200, content=dill.dumps(my_dictionary))

        result = exp.load_artifact(run, "my_dictionary")
        self.assertEqual(result, my_dictionary)

    def test_save_multiple_local_experiments(self, m):
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

    def test_reset_works_in_context(self, m):
        exp = self.local.experiment(self.EXP_NAME)
        exp.reset()
        exp.set_meta("style", "supervised")
        exp.set_meta("function", "regression")
        test_artifact = {"model": {}}
        with exp.start_run() as run:
            run.log_artifact("test", test_artifact)

        self.assertTrue(len(exp.runs()) == 1)
        self.assertEqual(run.get_artifact("test"), test_artifact)

    def make_run(self, exp):
        run = exp.start_run()
        run.set_meta("meta", "meta_val")
        run.log_params({"param": "param_val"})
        run.start()
        run.stop()
        run.log_metric(name="metric_1", metric=85)
        exp.save_run(run)
        return run
