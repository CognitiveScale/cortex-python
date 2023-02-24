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

import dill
from mocket.mockhttp import Entry
from mocket import mocketize

from pytest import raises
from requests.exceptions import HTTPError

from cortex import Cortex
from cortex.experiment import ExperimentClient, RemoteRun, Experiment
from .fixtures import build_mock_url, mock_api_endpoint, mock_project, john_doe_token

PROJECT = mock_project()
TOKEN = john_doe_token()
url = mock_api_endpoint()


class TestRun(unittest.TestCase):
    """
    Test experiment checks experiment functionality
    """

    RUN_EXP_NAME = "unittest-exp"
    RUN_ID = "000001"

    def setUp(self):
        params = {"token": TOKEN, "projectId": PROJECT, "apiEndpoint": url}
        self.local = Cortex.local()
        self.cortex = Cortex.from_message(params)

        # register mock for getting an experiment from the client
        uri = ExperimentClient.URIs["experiment"].format(
            experimentName=self.RUN_EXP_NAME, projectId=PROJECT
        )
        returns = {"name": self.RUN_EXP_NAME}
        Entry.single_register(
            Entry.GET, build_mock_url(uri), status=200, body=json.dumps(returns)
        )

        # register mock for creating a run
        uri = ExperimentClient.URIs["runs"].format(
            experimentName=self.RUN_EXP_NAME, projectId=PROJECT
        )

        returns = {"runId": self.RUN_ID}
        Entry.single_register(
            Entry.POST, build_mock_url(uri), status=200, body=json.dumps(returns)
        )

    @mocketize
    def test_make_remote_run(self):
        exp = Experiment(
            document=self.cortex.experiments.get_experiment(self.RUN_EXP_NAME),
            client=self.cortex.experiments,
        )
        r = exp.start_run()

        self.assertIsInstance(r, RemoteRun)

    @mocketize
    def test_get_run(self):
        exp = Experiment(
            document=self.cortex.experiments.get_experiment(self.RUN_EXP_NAME),
            client=self.cortex.experiments,
        )

        uri = self.cortex.experiments.URIs["run"].format(
            experimentName=self.RUN_EXP_NAME, projectId=PROJECT, runId=self.RUN_ID
        )
        returns = {
            "_id": "63cfb10ffe65fb07bf8a94b9",
            "_projectId": "prajna-test",
            "runId": "run_01",
            "experimentName": "praj-op-gc_dtree_exp",
            "params": {
                "category": "Decision Tree",
                "version": 1,
                "SourceData": "Upstream Server Data",
            },
            "metrics": {"accuracy": 0.68},
            "meta": {"algo": "DecisionTreeClassifier"},
            "_createdAt": "2023-01-24T10:21:03.120Z",
            "_updatedAt": "2023-01-24T10:21:04.497Z",
            "artifacts": {
                "model": "experiments/praj-op-gc_dtree_exp/run_01/artifacts/model"
            },
        }

        Entry.single_register(
            Entry.GET, build_mock_url(uri), status=200, body=json.dumps(returns)
        )

        ret = self.cortex.experiments.get_run(self.RUN_EXP_NAME, self.RUN_ID)
        self.assertEqual(returns, ret)

    @mocketize
    def test_get_run_failed(self):
        exp = Experiment(
            document=self.cortex.experiments.get_experiment(self.RUN_EXP_NAME),
            client=self.cortex.experiments,
        )

        uri = self.cortex.experiments.URIs["run"].format(
            experimentName=self.RUN_EXP_NAME, projectId=PROJECT, runId=self.RUN_ID
        )
        returns = "error"

        Entry.single_register(
            Entry.GET, build_mock_url(uri), status=404, body=json.dumps(returns)
        )
        with raises(HTTPError) as ex:
            ret = self.cortex.experiments.get_run(self.RUN_EXP_NAME, self.RUN_ID)

    @mocketize
    def test_run_get_artifact(self):
        exp = Experiment(
            document=self.cortex.experiments.get_experiment(self.RUN_EXP_NAME),
            client=self.cortex.experiments,
        )
        r = exp.start_run()

        test_artifact = {"a": 0.7071, "b": 1.4142, "c": 2.718}

        # get the artifact & test if it is what is expected
        # register mock for loading an artifact
        uri = ExperimentClient.URIs["artifact"].format(
            experimentName=self.RUN_EXP_NAME,
            runId=self.RUN_ID,
            artifactId="artifact",
            projectId=PROJECT,
        )
        Entry.single_register(
            Entry.GET, build_mock_url(uri), status=200, body=dill.dumps(test_artifact)
        )
        result = r.get_artifact("artifact")

        self.assertEqual(test_artifact, result)

    @mocketize
    def test_list_runs(self):
        uri = self.cortex.experiments.URIs["runs"].format(
            experimentName=self.RUN_EXP_NAME, projectId=PROJECT
        )
        local_url = self.cortex.experiments._serviceconnector._construct_url(uri)
        returns = {
            "runs": {
                "_id": "63cfb10ffe65fb07bf8a94b9",
                "_projectId": "prajna-test",
                "runId": "run_01",
                "experimentName": "praj-op-gc_dtree_exp",
                "params": {
                    "category": "Decision Tree",
                    "version": 1,
                    "SourceData": "Upstream Server Data",
                },
                "metrics": {"accuracy": 0.68},
                "meta": {"algo": "DecisionTreeClassifier"},
                "_createdAt": "2023-01-24T10:21:03.120Z",
                "_updatedAt": "2023-01-24T10:21:04.497Z",
                "artifacts": {
                    "model": "experiments/praj-op-gc_dtree_exp/run_01/artifacts/model"
                },
            }
        }

        Entry.single_register(
            Entry.GET, local_url, status=200, body=json.dumps(returns)
        )

        runs = self.cortex.experiments.list_runs(experiment_name=self.RUN_EXP_NAME)

        self.assertNotEqual(runs, None)

    @mocketize
    def test_update_run(self):
        uri = self.cortex.experiments.URIs["run"].format(
            experimentName=self.RUN_EXP_NAME, projectId=PROJECT, runId=self.RUN_ID
        )
        local_url = self.cortex.experiments._serviceconnector._construct_url(uri)

        body = {"success": True}
        Entry.single_register(Entry.PUT, local_url, status=200, body=json.dumps(body))

        ret = self.cortex.experiments.update_run(
            experiment_name=self.RUN_EXP_NAME, run_id=self.RUN_ID, meta={"blah": 1}
        )
        self.assertEqual(ret, True)

    @mocketize
    def test_update_run_failed(self):
        uri = self.cortex.experiments.URIs["run"].format(
            experimentName=self.RUN_EXP_NAME, projectId=PROJECT, runId=self.RUN_ID
        )
        local_url = self.cortex.experiments._serviceconnector._construct_url(uri)

        body = {"success": False}
        Entry.single_register(Entry.PUT, local_url, status=200, body=json.dumps(body))
        with raises(Exception) as ex:
            ret = self.cortex.experiments.update_run(
                experiment_name=self.RUN_EXP_NAME, run_id=self.RUN_ID, meta={"blah": 1}
            )

    @mocketize
    def test_delete_run(self):
        uri = self.cortex.experiments.URIs["run"].format(
            experimentName=self.RUN_EXP_NAME, projectId=PROJECT, runId=self.RUN_ID
        )
        local_url = self.cortex.experiments._serviceconnector._construct_url(uri)

        body = {"success": True}
        Entry.single_register(
            Entry.DELETE, local_url, status=200, body=json.dumps(body)
        )

        ret = self.cortex.experiments.delete_run(
            experiment_name=self.RUN_EXP_NAME, run_id=self.RUN_ID
        )
        self.assertTrue(ret)

    @mocketize
    def test_delete_run_failed(self):
        uri = self.cortex.experiments.URIs["run"].format(
            experimentName=self.RUN_EXP_NAME, projectId=PROJECT, runId=self.RUN_ID
        )
        local_url = self.cortex.experiments._serviceconnector._construct_url(uri)

        body = {"success": False}
        Entry.single_register(
            Entry.DELETE, local_url, status=200, body=json.dumps(body)
        )
        with raises(Exception) as ex:
            self.cortex.experiments.delete_run(
                experiment_name=self.RUN_EXP_NAME, run_id=self.RUN_ID
            )
