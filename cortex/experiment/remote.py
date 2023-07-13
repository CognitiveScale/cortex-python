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

import io
import json
import os
from typing import Dict, List

import tempfile
import dill


from .model import Run, _to_html
from ..camel import CamelResource
from ..exceptions import (
    APIException,
    ConfigurationException,
    UpdateRunException,
    DeleteRunException,
)
from ..serviceconnector import _Client
from ..utils import raise_for_status_with_detail, get_logger, parse_string

log = get_logger(__name__)


class ExperimentClient(_Client):
    """
    A client for the `Cortex experiment and model management API <https://cognitivescale.github.io/cortex-fabric/docs/models/experiments>`_. You can find a pre-created instance of this class on every :class:`cortex.client.Client` instance via the :attr:`Client.experiments` attribute.

    >>> from cortex.client import Cortex; client = Cortex.client();
    >>> client.experiments.list_experiments() # list experiments from the default project configured for the user
    """  # pylint: disable=line-too-long

    headers = {"Content-Type": "application/json"}

    URIs = {
        "experiments": "projects/{projectId}/experiments",
        "experiment": "projects/{projectId}/experiments/{experimentName}",
        "runs": "projects/{projectId}/experiments/{experimentName}/runs",
        "run": "projects/{projectId}/experiments/{experimentName}/runs/{runId}",
        "artifact": (
            "projects/{projectId}/experiments/"
            "{experimentName}/runs/{runId}/artifacts/{artifactId}"
        ),
        "meta": "projects/{projectId}/experiments/{experimentName}/runs/{runId}/meta/{metaId}",
        "param": "projects/{projectId}/experiments/{experimentName}/runs/{runId}/params/{paramId}",
        "metric": (
            "projects/{projectId}/experiments/"
            "{experimentName}/runs/{runId}/metrics/{metricId}"
        ),
    }

    def list_experiments(self) -> List[Dict]:
        """Returns a list of experiments available on the project configured for the experiment client.

        >>> from cortex.client import Cortex; cc=Cortex.client()
        >>> cc.experiments.list_experiments()
        [{'_version': 2, 'name': 'op-gc_dtree_exp', 'title': 'Decision Tree model', 'description': 'Decision Tree model', 'meta': None, 'tags': [], 'modelId': 'op-german-credit', 'updatedAt': '2023-01-24T10:21:01.347Z', 'createdAt': '2023-01-24T10:11:16.445Z'}]

        :return: A list containing multiple dictionaries, each corresponding to an experiment and all associated metadata
        :rtype: List[Dict]
        """
        res = self._serviceconnector.request(
            method="GET", uri=self.URIs["experiments"].format(projectId=self._project())
        )
        raise_for_status_with_detail(res)
        res_json = res.json()

        return res_json.get("experiments", [])

    def save_experiment(self, experiment_name: str, model_id=None, **kwargs) -> Dict:
        """Save an experiment with the provided `experiment_name`, and `modelId`. All the fields specified in the `API reference for Cortex Experiments <https://cognitivescale.github.io/cortex-fabric/swagger/index.html#operation/CreateExperiment>`_ (except name and modelId) can be passed in as keyword args to this method

        >>> from cortex.client import Cortex; cc=Cortex.client()
        >>> cc.experiments.save_experiment('exp-name', 'juhf')
        {'_version': 1, 'name': 'exp-name', 'tags': [], '_projectId': 'exp-test', 'modelId': 'juhf'}

        :param experiment_name: Name to use for the new experiment which is to be saved
        :type experiment_name: str
        :param model_id: _description_, defaults to None
        :type model_id: str, optional
        :return: A dictionary with metadata about the saved experiment
        :rtype: Dict
        """
        if model_id:
            body_obj = {"name": experiment_name, "modelId": model_id}
        else:
            body_obj = {"name": experiment_name}

        if kwargs:
            body_obj.update(kwargs)

        body = json.dumps(body_obj)
        headers = {"Content-Type": "application/json"}
        uri = self.URIs["experiments"].format(projectId=self._project())
        res = self._serviceconnector.request(
            method="POST", uri=uri, body=body, headers=headers
        )
        raise_for_status_with_detail(res)
        return res.json()

    def delete_experiment(self, experiment_name: str) -> bool:
        """Delete an experiment specified by `experiment_name`

        >>> from cortex.client import Cortex; cc=Cortex.client(project='test')
        >>> cc.experiments.delete_experiment('another')
        True

        :param experiment_name: Name of the experiment to be deleted
        :type experiment_name: str
        :return: A boolean value indicating the status of the delete operation
        :rtype: bool
        """
        uri = self.URIs["experiment"].format(
            projectId=self._project(), experimentName=parse_string(experiment_name)
        )
        res = self._serviceconnector.request(method="DELETE", uri=uri)
        raise_for_status_with_detail(res)
        res_json = res.json()

        return res_json.get("success", False)

    def get_experiment(self, experiment_name: str) -> Dict:
        """Retrieve all data for the experiment with name `experiment_name`

        >>> from cortex.client import Cortex; cc=Cortex.client()
        >>> cc.experiments.get_experiment('ddgc_dtree_exp')
        {'_version': 1, 'name': 'ddgc_dtree_exp', 'title': 'Decision Tree model', 'description': 'Decision Tree model', 'tags': [], '_projectId': 'test', 'modelId': 'german-credit-model'}

        :param experiment_name: Name of the experiment to retrieve data from
        :type experiment_name: str
        :return: A dictionary with all metadata about the experiment
        :rtype: Dict
        """
        uri = self.URIs["experiment"].format(
            projectId=self._project(), experimentName=parse_string(experiment_name)
        )
        res = self._serviceconnector.request(method="GET", uri=uri)
        raise_for_status_with_detail(res)

        return res.json()

    def list_runs(self, experiment_name: str) -> List[Dict]:
        """`List all the runs <https://cognitivescale.github.io/cortex-fabric/swagger/index.html#operation/ListRuns>`_ that belong to the specified `experiment_name`

        >>> from cortex.client import Cortex; cc=Cortex.client()
        >>> cc.experiments.list_runs('op-gc_dtree_exp')
        [{'_id': '63cfb10ffe65fb07bf8a94b9', '_projectId': 'test', 'runId': 'run_01', 'experimentName': 'op-gc_dtree_exp', 'params': {'category': 'Decision Tree', 'version': 1, 'SourceData': 'Upstream Server Data'}, 'metrics': {'accuracy': 0.68}, 'meta': {'algo': 'DecisionTreeClassifier'}, '_createdAt': '2023-01-24T10:21:03.120Z', '_updatedAt': '2023-01-24T10:21:04.497Z', 'artifacts': {'model': 'experiments/op-gc_dtree_exp/run_01/artifacts/model'}}]

        :param experiment_name: Experiment name whose runs are to be listed
        :type experiment_name: str
        :return: A List of dictionaries that contain the information available for each run of that experiment
        :rtype: List[Dict]
        """
        uri = self.URIs["runs"].format(
            projectId=self._project(), experimentName=parse_string(experiment_name)
        )
        res = self._serviceconnector.request(method="GET", uri=uri)
        raise_for_status_with_detail(res)
        res_json = res.json()

        return res_json.get("runs", [])

    def find_runs(
        self, experiment_name: str, filter_obj: Dict, sort: dict = None, limit=25
    ) -> List[Dict]:
        """Similar to :meth:`cortex.experiment.ExperimentClient.list_runs`, but also allows you to filter with a mongo-style query dictionary passed in through `filter_obj`, along with `sort` and `limit` options

        >>> from cortex.client import Cortex; cc=Cortex.client()
        >>> cc.experiments.find_runs('op-gc_dtree_exp', filter_obj={"runId": "run_01"})
        [{'_id': '63cfb10ffe65fb07bf8a94b9', '_projectId': 'test', 'runId': 'run_01', 'experimentName': 'op-gc_dtree_exp', 'params': {'category': 'Decision Tree', 'version': 1, 'SourceData': 'Upstream Server Data'}, 'metrics': {'accuracy': 0.68}, 'meta': {'algo': 'DecisionTreeClassifier'}, '_createdAt': '2023-01-24T10:21:03.120Z', '_updatedAt': '2023-01-24T10:21:04.497Z', 'artifacts': {'model': 'experiments/op-gc_dtree_exp/run_01/artifacts/model'}}]

        :param experiment_name: Name of the experiment whose runs are to be filtered
        :type experiment_name: str
        :param filter_obj: A mongo style query object. For example. `{"runId": "run_01"}`. Allowed fields which can be set as keys in this dictionary include [runId, _createdAt, startTime, endTime, took, experimentName]
        :type filter_obj: Dict
        :param sort: A mongo style sort object, defaults to None on the client. Server side default is `{"_updatedAt": -1}`
        :type sort: Dict, optional
        :param limit: Limit the number of results to this number, defaults to 25
        :type limit: int, optional
        :return: A list of JSON objects (dictionaries), with each dictionary encoding the information available for a run that matches the provided filter criteria
        :rtype: List[Dict]
        """
        uri = self.URIs["runs"].format(
            projectId=self._project(), experimentName=parse_string(experiment_name)
        )

        # filter and limit are required query params
        params = {"filter": json.dumps(filter_obj), "limit": limit}

        # Add sorting
        if sort:
            params["sort"] = json.dumps(sort)

        res = self._serviceconnector.request(method="GET", uri=uri, params=params)
        raise_for_status_with_detail(res)
        res_json = res.json()

        return res_json.get("runs", [])

    def delete_runs(
        self,
        experiment_name,
        filter_obj: Dict = None,
    ) -> str:
        """Delete runs belonging to the specified `experiment_name` that match the optional `filter_obj` conditions

        >>> from cortex.client import Cortex; cc=Cortex.client(project='test')
        >>> cc.experiments.delete_runs('op-gc_dtree_exp')
        'Runs deleted'

        :param experiment_name: Name of the experiment whose runs are to be deleted
        :type experiment_name: str
        :param filter_obj: A mongo style query object. For example. `{"runId": "run_01"}`. Allowed fields which can be set as keys in this dictionary include [runId, _createdAt, startTime, endTime, took, experimentName]
        :type filter_obj: Dict
        :raises: :exc:`requests.exceptions.HTTPError`
        :return: A message indicating that runs were deleted
        :rtype: _type_
        """
        uri = self.URIs["runs"].format(
            projectId=self._project(), experimentName=parse_string(experiment_name)
        )

        params = {}

        # Add query filter
        if filter_obj:
            params["filter"] = json.dumps(filter_obj)

        res = self._serviceconnector.request(method="DELETE", uri=uri, params=params)
        raise_for_status_with_detail(res)
        res_json = res.json()

        return res_json.get("message")

    def create_run(self, experiment_name: str, **kwargs) -> Dict:
        """Creates a run for the specified `experiment_name`. Refer to the `official CreateRun docs <https://cognitivescale.github.io/cortex-fabric/swagger/index.html#operation/CreateRun>`_ for information on other possible `kwargs` this method can accept

        >>> from cortex.client import Cortex; cc=Cortex.client(project='test')
        >>> cc.experiments.create_run('op-gc_dtree_exp')
        {'_projectId': 'test', 'runId': 'ox00gu0', 'experimentName': 'op-gc_dtree_exp', '_id': '63f0f9e809c5267ccb9110ca', '_createdAt': '2023-02-18T16:16:40.405Z', '_updatedAt': '2023-02-18T16:16:40.405Z'}

        :raises: :exc:`requests.exceptions.HTTPError`
        :param experiment_name: The experiment to associate with this run.
        :type experiment_name: str
        :return: A dictionary providing a JSON representation of the created run
        :rtype: Dict
        """
        body_obj = {}

        if kwargs:
            body_obj.update(kwargs)

        body = json.dumps(body_obj)
        headers = {"Content-Type": "application/json"}
        uri = self.URIs["runs"].format(
            projectId=self._project(), experimentName=parse_string(experiment_name)
        )
        res = self._serviceconnector.request(
            method="POST", uri=uri, body=body, headers=headers
        )
        raise_for_status_with_detail(res)
        return res.json()

    def get_run(self, experiment_name: str, run_id: str) -> Dict:
        """Get all details available for a `run_id` belonging to an `experiment_name`

        >>> from cortex.client import Cortex; cc=Cortex.client(project='test')
        >>> cc.experiments.get_run('op-gc_dtree_exp', 'ox00gu0')
        {'_id': '63f0f9e809c5267ccb9110ca', '_projectId': 'test', 'runId': 'ox00gu0', 'experimentName': 'op-gc_dtree_exp', '_createdAt': '2023-02-18T16:16:40.405Z', '_updatedAt': '2023-02-18T16:16:40.405Z'}

        :raises: :exc:`requests.exceptions.HTTPError`
        :param experiment_name: Name of the experiment whose run is to be retrieved
        :type experiment_name: str
        :param run_id: ID of the Run to be retrieved
        :type run_id: str
        :return: A dictionary providing a JSON representation of the specified run
        :rtype: Dict
        """
        uri = self.URIs["run"].format(
            projectId=self._project(),
            experimentName=parse_string(experiment_name),
            runId=run_id,
        )
        res = self._serviceconnector.request(method="GET", uri=uri)
        raise_for_status_with_detail(res)

        return res.json()

    def update_run(self, experiment_name: str, run_id: str, **kwargs) -> bool:
        """Updates a run and returns the boolean status of the operation. Refer to the `official UpdateRun docs <https://cognitivescale.github.io/cortex-fabric/swagger/index.html#operation/UpdateRun>`_ for information on other possible `kwargs` this method can accept

        :param experiment_name: Name of the experiment whose run is to be updated
        :type experiment_name: str
        :param run_id: ID of the run to be updated
        :type run_id: str
        :raises: :exc:`cortex.exceptions.UpdateRunException`
        :return: Boolean indicating the status of the operation
        :rtype: bool
        """
        body_obj = {}

        if kwargs:
            body_obj.update(kwargs)

        body = json.dumps(body_obj)
        headers = {"Content-Type": "application/json"}
        uri = self.URIs["run"].format(
            projectId=self._project(),
            experimentName=parse_string(experiment_name),
            runId=run_id,
        )
        res = self._serviceconnector.request(
            method="PUT", uri=uri, body=body, headers=headers
        )
        raise_for_status_with_detail(res)
        res_json = res.json()

        success = res_json.get("success", False)
        if not success:
            raise UpdateRunException(
                "Error updating run {}: {}".format(run_id, res_json.get("error"))
            )
        return success

    def delete_run(self, experiment_name: str, run_id: str) -> bool:
        """Deletes a run with identifier `run_id` from the experiment with name `experiment_name`

        :param experiment_name: Name of the experiment to which this run belongs
        :type experiment_name: str
        :param run_id: Identifier of the run to be deleted
        :type run_id: str
        :raises: :exc:`cortex.exceptions.DeleteRunException`
        :return: A boolean indicating the status of the delete operation
        :rtype: bool
        """
        uri = self.URIs["run"].format(
            projectId=self._project(),
            experimentName=parse_string(experiment_name),
            runId=run_id,
        )
        res = self._serviceconnector.request(method="DELETE", uri=uri)
        raise_for_status_with_detail(res)
        res_json = res.json()

        success = res_json.get("success", False)
        if not success:
            raise DeleteRunException(
                "Error deleting run {}: {}".format(run_id, res_json.get("error"))
            )
        return success

    def update_meta(
        self, experiment_name: str, run_id: str, meta: str, val: any
    ) -> bool:
        """Update the value of a meta attribute of an experiment's run. The value `val` needs to be serializable to json. The meta attributes should be used to store metadata about a particular run of an experiment. It can contain information about the class of model being trained, usecases, problem specification and more.

        :param experiment_name: Experiment name
        :type experiment_name: str
        :param run_id: Identifier of the run whose meta attribute is to be updated
        :type run_id: str
        :param meta: Identifier of the meta attribute
        :type meta: str
        :param val: Value to be updated for the provided `meta` attribute
        :type val: any
        :raises: :exc:`cortex.exceptions.UpdateRunException`
        :return: A boolean indicating the status of the update operation
        :rtype: bool
        """
        uri = self.URIs["meta"].format(
            projectId=self._project(),
            experimentName=parse_string(experiment_name),
            runId=run_id,
            metaId=meta,
        )
        headers = {"Content-Type": "application/json"}
        res = self._serviceconnector.request(
            method="PUT", uri=uri, body=json.dumps({"value": val}), headers=headers
        )
        raise_for_status_with_detail(res)
        res_json = res.json()

        success = res_json.get("success", False)
        if not success:
            raise UpdateRunException(
                "Error updating run {} meta property {}: {}".format(
                    run_id, meta, res_json.get("error")
                )
            )
        return success

    def update_param(
        self, experiment_name: str, run_id: str, param: str, val: any
    ) -> bool:
        """Update the value of a param attribute of an experiment's run. The value `val` needs to be serializable to json. Params should be used to store information about a model's runtime or train-time characteristics. For example, hyper-parameters of a models should be stored in this object

        :param experiment_name: Experiment name
        :type experiment_name: str
        :param run_id: Identifier of the run whose param attribute is to be updated
        :type run_id: str
        :param param: Identifier of the param attribute
        :type param: str
        :param val: Value to be updated for the provided `param` attribute
        :type val: any
        :raises: :exc:`cortex.exceptions.UpdateRunException`
        :return: A boolean indicating the status of the update operation
        :rtype: bool
        """
        uri = self.URIs["param"].format(
            projectId=self._project(),
            experimentName=parse_string(experiment_name),
            runId=run_id,
            paramId=param,
        )
        headers = {"Content-Type": "application/json"}
        res = self._serviceconnector.request(
            method="PUT", uri=uri, body=json.dumps({"value": val}), headers=headers
        )
        raise_for_status_with_detail(res)
        res_json = res.json()

        success = res_json.get("success", False)
        if not success:
            raise UpdateRunException(
                "Error updating run {} param {}: {}".format(
                    run_id, param, res_json.get("error")
                )
            )
        return success

    def update_metric(self, experiment_name: str, run_id: str, metric: str, val: any):
        """Update the value of a metric attribute of an experiment's run. The value `val` needs to be serializable to json. Metrics should be used to store data pertaining to a run's performance, and other dimensions

        :param experiment_name: Experiment name
        :type experiment_name: str
        :param run_id: Identifier of the run whose param attribute is to be updated
        :type run_id: str
        :param metric: Identifier of the param attribute
        :type metric: str
        :param val: Value to be updated for the provided `metric` attribute
        :type val: any
        :raises: :exc:`cortex.exceptions.UpdateRunException`
        :return: A boolean indicating the status of the update operation
        :rtype: bool
        """

        uri = self.URIs["metric"].format(
            projectId=self._project(),
            experimentName=parse_string(experiment_name),
            runId=run_id,
            metricId=metric,
        )
        headers = {"Content-Type": "application/json"}
        res = self._serviceconnector.request(
            method="PUT", uri=uri, body=json.dumps({"value": val}), headers=headers
        )
        raise_for_status_with_detail(res)
        res_json = res.json()

        success = res_json.get("success", False)
        if not success:
            raise UpdateRunException(
                "Error updating run {} metric {}: {}".format(
                    run_id, metric, res_json.get("error")
                )
            )
        return success

    def update_artifact(self, experiment_name: str, run_id: str, artifact: str, stream):
        """Update the bytes or file content corresponding to experiment's run artifact with name provided in the `artifact` param. `stream` should be a valid Python I/O stream. Use this field to store trained models, large model weights and training data corresponding to an experiment run.

        :param experiment_name: Experiment name
        :type experiment_name: str
        :param run_id: Identifier of the run whose param attribute is to be updated
        :type run_id: str
        :param artifact: Name or Key of the artifact to be stored. This will be used to store the `stream` data in Managed Content
        :type artifact: str
        :param stream: A Python I/O stream which will be written to managed content with filename provided in the `artifact` param
        :type stream: Python I/O stream
        :raises: :exc:`cortex.exceptions.UpdateRunException`
        :return: A boolean indicating the status of the update operation
        :rtype: bool
        """
        uri = self.URIs["artifact"].format(
            projectId=self._project(),
            experimentName=parse_string(experiment_name),
            runId=run_id,
            artifactId=artifact,
        )
        res = self._serviceconnector.request(method="PUT", uri=uri, body=stream)
        raise_for_status_with_detail(res)
        res_json = res.json()

        success = res_json.get("success", False)
        if not success:
            raise UpdateRunException(
                "Error updating run {} artifact {}: {}".format(
                    run_id, artifact, res_json.get("error")
                )
            )
        return success

    def get_artifact(self, experiment_name: str, run_id: str, artifact: str) -> bytes:
        """Retrieve the artifact with key `artifact` from run `run_id` belonging to experiment `experiment_name`

        :param experiment_name: Experiment name
        :type experiment_name: str
        :param run_id: Identifier of the run whose param attribute is to be updated
        :type run_id: str
        :param artifact: Name or Key of the artifact to be stored. This will be used to store the `stream` data in Managed Content
        :type artifact: str
        :return: A Python bytes object containing the data corresponding to the `artifact` key in managed content
        :rtype: bytes
        """
        uri = self.URIs["artifact"].format(
            projectId=self._project(),
            experimentName=parse_string(experiment_name),
            runId=run_id,
            artifactId=artifact,
        )
        res = self._serviceconnector.request(method="GET", uri=uri, stream=True)
        raise_for_status_with_detail(res)

        return res.content


class Experiment(CamelResource):
    """
    Tracks runs, associated parameters, metrics, and artifacts of experiments.
    """  # pylint: disable=line-too-long

    def __init__(self, document: Dict, client: ExperimentClient):
        super().__init__(document, False)
        self._project = client._project
        self._client = client
        self.meta = {}

    def start_run(self) -> Run:
        """Starts a run for the experiment

        :return: A :class:`cortex.experiment.Run` instance
        :rtype: Run
        """
        return RemoteRun.create(self, self._client)

    def save_run(self, run: Run) -> None:
        """Alias to :class:`cortex.experiment.ExperimentClient.update_run`

        :param run: An instance of :class:`cortex.experiment.Run`
        :type run: Run
        """
        self._client.update_run(
            self.name,
            run.id,
            took=run.took,
            startTime=run.start_time,
            endTime=run.end_time,
        )

    def reset(self, filter_obj: dict = None) -> None:
        """Deletes all runs associated with this Experiment with filter conditions applied via the optional `filter_obj` param.

        :param filter_obj: A mongo style query object. For example. `{"runId": "run_01"}`. Allowed fields which can be set as keys in this dictionary include [runId, _createdAt, startTime, endTime, took, experimentName], is optional
        :type filter_obj: Dict
        """
        self._client.delete_runs(self.name, filter_obj)

    def set_meta(self, prop: str, value: any):
        """Sets a meta property along with value on an experiment

        :param prop: The key of the meta attribute
        :type prop: str
        :param value: The value of the meta attribute. Needs to be serialisable to json
        :type value: any
        """
        self.meta[prop] = value
        self._client.save_experiment(self.name, **self.to_camel())

    def runs(self) -> List[Run]:
        """Alias to :meth:`cortex.experiment.ExperimentClient.list_runs`

        :return: A list of RemoteRun instances that belong this experiment
        :rtype: List[Run]
        """
        runs = self._client.list_runs(self.name)
        return [RemoteRun.from_json(r, self) for r in runs]

    def get_run(self, run_id: str) -> Run:
        """Alias to :meth:`cortex.experiment.ExperimentClient.get_run`

        :param run_id: The identifier for the run.
        :type run_id: str
        :return: An instance of :class:`cortex.experiment.Run`
        :rtype: Run
        """
        run = self._client.get_run(self.name, run_id)
        return RemoteRun.from_json(run, self)

    def last_run(self) -> Run:
        """Returns the most recent Run available on this Experiment. Recency is computed using the `endTime` attribute of a Run

        :raises: :exc:`cortex.exceptions.APIException`
        :return: _description_
        :rtype: Run
        """
        sort = {"endTime": -1}
        runs = self._client.find_runs(self.name, {}, sort=sort, limit=1)
        if len(runs) == 1:
            log.debug(self)
            return RemoteRun.from_json(runs[0], self)
        raise APIException("Last run for experiment {} not found".format(self.name))

    def find_runs(
        self, filter_obj: dict = None, sort: dict = None, limit: int = None
    ) -> List[Run]:
        """Alias to :meth:`cortex.experiment.ExperimentClient.find_runs`

        :param filter_obj: A mongo style query object. For example. `{"runId": "run_01"}`. Allowed fields which can be set as keys in this dictionary include [runId, _createdAt, startTime, endTime, took, experimentName]
        :type filter_obj: Dict
        :param sort: A mongo style sort object, defaults to None on the client. Server side default is `{"_updatedAt": -1}`
        :type sort: Dict, optional
        :param limit: Limit the number of results to this number, defaults to 25
        :type limit: int, optional
        :return: A list of :class:`cortex.experiment.Run` instances that match the provided filter, sort and limit criteria
        :rtype: List[Run]
        """
        runs = self._client.find_runs(
            self.name, filter_obj or {}, sort=sort, limit=limit
        )
        return [RemoteRun.from_json(r, self) for r in runs]

    def load_artifact(self, run: Run, name: str) -> any:
        """Downloads the given artifact with name `name` for the Run `run` using :meth:`cortex.experiment.ExperimentClient.get_artifact` loads it using :func:`dill.loads`

        :param run: The run for which artifact is to be loaded from
        :type run: Run
        :param name: Name/key of the artifact belonging to this run
        :type name: str
        :return: Unpickled object loaded into memory by dill
        :rtype: any
        """
        return dill.loads(self._client.get_artifact(self.name, run.id, name))

    def to_camel(self, camel: str = "1.0.0") -> Dict:
        # pylint: disable=duplicate-code
        """Converts the instance of this class to a valid CAMEL specification

        :param camel: Version of the CAMEL specification to use, defaults to "1.0.0"
        :type camel: str, optional
        :return: A python dictionary containing the valid CAMEL specification of this :class:`cortex.experiment.Experiment` instance
        :rtype: Dict
        """
        return {
            "camel": camel,
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "tags": self.tags or [],
            "meta": self.meta or {},
        }

    def _repr_html_(self):
        return _to_html(self)

    def display(self):
        # pylint: disable=import-outside-toplevel, import-error
        """_summary_"""
        # Only available within a jupyter notebook
        from IPython.display import (
            display,
            HTML,
        )

        display(HTML(self._repr_html_()))


class RemoteRun(Run):
    # pylint: disable=too-many-instance-attributes, line-too-long
    """
    A run that is executed remotely, through a client.
    """

    def __init__(self, experiment, client: ExperimentClient):
        super().__init__(experiment)
        self._client = client

    @staticmethod
    def create(experiment: Experiment, experiment_client: ExperimentClient) -> Run:
        # pylint: disable=protected-access
        """
        Creates a remote run.
        :param experiment: The experiment to associate with this run.
        :type experiment: Experiment
        :param experiment_client: The client for the run.
        :type experiment_client: ExperimentClient
        :return: A run.
        :rtype: :class:`cortex.experiment.RemoteRun`
        """
        run_json = experiment_client.create_run(experiment.name)
        run = RemoteRun(experiment, experiment_client)
        run._id = run_json["runId"]

        return run

    @staticmethod
    def get(
        experiment: Experiment, run_id: str, experiment_client: ExperimentClient
    ) -> Run:
        """
        Gets a run.

        :param experiment: The parent experiment of the run.
        :type experiment: Experiment
        :param run_id: The identifier for the run.
        :type run_id: str
        :param experiment_client: The client for the run.
        :type experiment_client: ExperimentClient
        :return: A RemoteRun instance.
        :rtype: :class:`cortex.experiment.RemoteRun`
        """
        run_json = experiment_client.get_run(experiment.name, run_id)
        return RemoteRun.from_json(run_json, experiment)

    @staticmethod
    def from_json(json: dict, experiment: Experiment):
        # pylint: disable=protected-access,redefined-outer-name,duplicate-code
        """
        Builds a run from the given json.
        :param run_json: json that specifies the run; acceptable values are runId, startTime, endTime, took, a list of params, metrics, metadata, and artifacts
        :type run_json: Dict
        :param experiment: the parent experiment of the run
        :type experiment: :class:`cortex.experiment.Experiment`
        :return: a run
        :rtype: :class:`cortex.experiment.RemoteRun`
        """
        run = RemoteRun(experiment, experiment._client)
        run._id = json["runId"]
        run._start = json.get("startTime", json.get("start"))
        run._end = json.get("endTime", json.get("end"))
        run._interval = json.get("took")
        run._params = json.get("params", {})
        run._metrics = json.get("metrics", {})
        run._meta = json.get("meta", {})
        run._artifacts = json.get("artifacts", {})

        return run

    def log_param(self, name: str, param: any) -> None:
        """Updates the params for the run.

        :param name: Name of the parameter to log and update
        :type name: str
        :param param: Value of the parameter to log and update. This value needs to be JSON serializable
        :type param: any
        """
        super().log_param(name, param)
        self._client.update_param(self._experiment.name, self.id, name, param)

    def log_metric(self, name: str, metric: any):
        """Updates the metric for the run.

        :param name: Name of the metric to log and update
        :type name: str
        :param metric: Value of the metric to log and update. This value needs to be JSON serializable
        :type metric: any
        """
        super().log_metric(name, metric)
        self._client.update_metric(self._experiment.name, self.id, name, metric)

    def set_meta(self, name: str, val: any):
        """Sets the metadata for the run.

        :param name: Name of the meta attribute to set
        :type name: str
        :param val: Value of the meta attribute to set. Needs to be JSON serializable
        :type val: any
        """
        super().set_meta(name, val)
        self._client.update_meta(self._experiment.name, self.id, name, val)

    def log_artifact(self, name: str, artifact):
        """
        Updates the artifacts for the run.
        """
        super().log_artifact(name, artifact)
        if hasattr(artifact, "ref"):
            with open(artifact["ref"], "rb") as stream:
                self.log_artifact_stream(name, stream)
        else:
            stream = io.BytesIO()
            dill.dump(artifact, stream)
            stream.seek(0)
            self.log_artifact_stream(name, stream)

    def log_artifact_file(self, name: str, file_path):
        """
        Logs the artifact to the file given in the filepath.
        """
        super().log_artifact(name, file_path)
        with open(file_path, "rb") as file_d:
            self.log_artifact_stream(name, file_d)

    def log_artifact_stream(self, name: str, stream):
        """
        Updates the artifact with the given stream.
        """
        self._client.update_artifact(self._experiment.name, self.id, name, stream)

    def log_keras_model(self, model, artifact_name="model"):
        """
        Logs a keras model as an artifact.
        """
        with tempfile.NamedTemporaryFile(mode="w+b") as temp:
            model.save(filepath=temp.name)
            self.log_artifact_file(artifact_name, temp.name)

    def get_artifact(self, name: str, deserializer=dill.loads) -> bytes:
        """Gets an artifact with the given name.  Deserializes the artifact stream using dill by default.  Deserialization can be disabled entirely or the deserializer function can be overridden.

        :param name: Name of the artifact to be fetched
        :type name: str
        :param deserializer: Function to be used as the deserializer, defaults to dill.loads
        :type deserializer: function, optional
        :return: Bytes in memory containing the artifact's file contents
        :rtype: bytes
        """
        artifact_bytes = self._client.get_artifact(
            experiment_name=self._experiment.name, run_id=self.id, artifact=name
        )
        if deserializer:
            return deserializer(artifact_bytes)
        return artifact_bytes

    def get_keras_model(self, artifact_name="model"):
        # pylint: disable=import-outside-toplevel, import-error
        """
        Gets the keras model.
        """
        try:
            from keras.models import (
                load_model,
            )
        except ImportError as exc:
            raise ConfigurationException(
                "Keras needs to be installed in order to use get_keras_model"
            ) from exc

        with tempfile.NamedTemporaryFile(delete=False) as file_d:
            file_d.write(self.get_artifact(artifact_name, deserializer=lambda x: x))
            model_file = file_d.name
        try:
            model = load_model(model_file)
        finally:
            os.remove(model_file)

        return model
