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
    A client for the Cortex experiment and model management API.
    """

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

    def list_experiments(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        res = self._serviceconnector.request(
            method="GET", uri=self.URIs["experiments"].format(projectId=self._project())
        )
        raise_for_status_with_detail(res)
        res_json = res.json()

        return res_json.get("experiments", [])

    def save_experiment(self, experiment_name, model_id=None, **kwargs):
        """_summary_

        Args:
            experiment_name (_type_): _description_
            model_id (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
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

    def delete_experiment(self, experiment_name):
        """_summary_

        Args:
            experiment_name (_type_): _description_

        Returns:
            _type_: _description_
        """
        uri = self.URIs["experiment"].format(
            projectId=self._project(), experimentName=parse_string(experiment_name)
        )
        res = self._serviceconnector.request(method="DELETE", uri=uri)
        raise_for_status_with_detail(res)
        res_json = res.json()

        return res_json.get("success", False)

    def get_experiment(self, experiment_name):
        """_summary_

        Args:
            experiment_name (_type_): _description_

        Returns:
            _type_: _description_
        """
        uri = self.URIs["experiment"].format(
            projectId=self._project(), experimentName=parse_string(experiment_name)
        )
        res = self._serviceconnector.request(method="GET", uri=uri)
        raise_for_status_with_detail(res)

        return res.json()

    def list_runs(self, experiment_name) -> List[Dict]:
        """_summary_

        Args:
            experiment_name (_type_): _description_

        Returns:
            List[Dict]: _description_
        """
        uri = self.URIs["runs"].format(
            projectId=self._project(), experimentName=parse_string(experiment_name)
        )
        res = self._serviceconnector.request(method="GET", uri=uri)
        raise_for_status_with_detail(res)
        res_json = res.json()

        return res_json.get("runs", [])

    def find_runs(
        self, experiment_name: str, filter_obj: Dict, sort=None, limit=25
    ) -> List[Dict]:
        """_summary_

        Args:
            experiment_name (str): _description_
            filter_obj (Dict): _description_
            sort (_type_, optional): _description_. Defaults to None.
            limit (int, optional): _description_. Defaults to 25.

        Returns:
            _type_: _description_
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

    def delete_runs(self, experiment_name, filter_obj=None, sort=None, limit=None):
        """_summary_

        Args:
            experiment_name (_type_): _description_
            filter_obj (_type_, optional): _description_. Defaults to None.
            sort (_type_, optional): _description_. Defaults to None.
            limit (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """ """_summary_

        Args:
            experiment_name (_type_): _description_
            filter_obj (_type_, optional): _description_. Defaults to None.
            sort (_type_, optional): _description_. Defaults to None.
            limit (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """ """_summary_

        Args:
            experiment_name (_type_): _description_
            filter (_type_, optional): _description_. Defaults to None.
            sort (_type_, optional): _description_. Defaults to None.
            limit (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        uri = self.URIs["runs"].format(
            projectId=self._project(), experimentName=parse_string(experiment_name)
        )

        params = {}

        # Add query filter
        if filter_obj:
            params["filter"] = json.dumps(filter_obj)

        # Add sorting
        if sort:
            params["sort"] = json.dumps(sort)

        # Add limit
        if limit:
            params["limit"] = limit

        res = self._serviceconnector.request(method="DELETE", uri=uri, params=params)
        raise_for_status_with_detail(res)
        res_json = res.json()

        return res_json.get("message")

    def create_run(self, experiment_name, **kwargs):
        """
        Creates a run.
        :param experiment_name: The experiment to associate with this run.
        :return: A run.
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

    def get_run(self, experiment_name, run_id):
        """
        Gets a run.

        :param experiment_name: The parent experiment of the run.
        :param run_id: The identifier for the run.
        :return: A run.
        """
        uri = self.URIs["run"].format(
            projectId=self._project(),
            experimentName=parse_string(experiment_name),
            runId=run_id,
        )
        res = self._serviceconnector.request(method="GET", uri=uri)
        raise_for_status_with_detail(res)

        return res.json()

    def update_run(self, experiment_name, run_id, **kwargs):
        """
        Updates a run.
        :param experiment_name: The experiment to associate with this run.
        :param run_id: The identifier for the run.
        :return: A run.
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

    def delete_run(self, experiment_name, run_id):
        """
        Deletes a run.

        :param experiment_name: The parent experiment of the run.
        :param run_id: The identifier for the run.
        :return: status
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

    def update_meta(self, experiment_name, run_id, meta, val):
        """_summary_

        Args:
            experiment_name (_type_): _description_
            run_id (_type_): _description_
            meta (_type_): _description_
            val (_type_): _description_

        Raises:
            Exception: _description_

        Returns:
            _type_: _description_
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

    def update_param(self, experiment_name, run_id, param, val):
        """_summary_

        Args:
            experiment_name (_type_): _description_
            run_id (_type_): _description_
            param (_type_): _description_
            val (_type_): _description_

        Raises:
            Exception: _description_

        Returns:
            _type_: _description_
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

    def update_metric(self, experiment_name, run_id, metric, val):
        """_summary_

        Args:
            experiment_name (_type_): _description_
            run_id (_type_): _description_
            metric (_type_): _description_
            val (_type_): _description_

        Raises:
            Exception: _description_

        Returns:
            _type_: _description_
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

    def update_artifact(self, experiment_name, run_id, artifact, stream):
        """_summary_

        Args:
            experiment_name (_type_): _description_
            run_id (_type_): _description_
            artifact (_type_): _description_
            stream (_type_): _description_

        Raises:
            Exception: _description_

        Returns:
            _type_: _description_
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

    def get_artifact(self, experiment_name, run_id, artifact):
        """_summary_

        Args:
            experiment_name (_type_): _description_
            run_id (_type_): _description_
            artifact (_type_): _description_

        Returns:
            _type_: _description_
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
    """

    def __init__(self, document: Dict, client: ExperimentClient):
        super().__init__(document, False)
        self._project = client._project
        self._client = client
        self.meta = {}

    def start_run(self) -> Run:
        """_summary_

        Returns:
            Run: _description_
        """
        return RemoteRun.create(self, self._client)

    def save_run(self, run: Run):
        """_summary_

        Args:
            run (Run): _description_
        """
        self._client.update_run(
            self.name,
            run.id,
            took=run.took,
            startTime=run.start_time,
            endTime=run.end_time,
        )

    def reset(self, filter_obj=None, sort=None, limit=None):
        """_summary_

        Args:
            filter_obj (_type_, optional): _description_. Defaults to None.
            sort (_type_, optional): _description_. Defaults to None.
            limit (_type_, optional): _description_. Defaults to None.
        """
        self._client.delete_runs(self.name, filter_obj, sort, limit)

    def set_meta(self, prop, value):
        """_summary_

        Args:
            prop (_type_): _description_
            value (_type_): _description_
        """
        self.meta[prop] = value
        self._client.save_experiment(self.name, **self.to_camel())

    def runs(self) -> List[Run]:
        """_summary_

        Returns:
            List[Run]: _description_
        """
        runs = self._client.list_runs(self.name)
        return [RemoteRun.from_json(r, self) for r in runs]

    def get_run(self, run_id) -> Run:
        """_summary_

        Args:
            run_id (_type_): _description_

        Returns:
            Run: _description_
        """
        run = self._client.get_run(self.name, run_id)
        return RemoteRun.from_json(run, self)

    def last_run(self) -> Run:
        """_summary_

        Raises:
            APIException: _description_

        Returns:
            Run: _description_
        """
        sort = {"endTime": -1}
        runs = self._client.find_runs(self.name, {}, sort=sort, limit=1)
        if len(runs) == 1:
            log.debug(self)
            return RemoteRun.from_json(runs[0], self)
        raise APIException("Last run for experiment {} not found".format(self.name))

    def find_runs(self, filter_obj, sort, limit: int) -> List[Run]:
        """_summary_

        Args:
            filter_obj (_type_): _description_
            sort (_type_): _description_
            limit (int): _description_

        Returns:
            List[Run]: _description_
        """
        runs = self._client.find_runs(
            self.name, filter_obj or {}, sort=sort, limit=limit
        )
        return [RemoteRun.from_json(r, self) for r in runs]

    def load_artifact(self, run: Run, name: str):
        """_summary_

        Args:
            run (Run): _description_
            name (str): _description_

        Returns:
            _type_: _description_
        """
        return dill.loads(self._client.get_artifact(self.name, run.id, name))

    def to_camel(self, camel="1.0.0"):
        # pylint: disable=duplicate-code
        """_summary_

        Args:
            camel (str, optional): _description_. Defaults to "1.0.0".

        Returns:
            _type_: _description_
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
    # pylint: disable=too-many-instance-attributes
    """
    A run that is executed remotely, through a client.
    """

    def __init__(self, experiment, client: ExperimentClient):
        super().__init__(experiment)
        self._client = client

    @staticmethod
    def create(experiment, experiment_client):
        # pylint: disable=protected-access
        """
        Creates a remote run.
        :param experiment: The experiment to associate with this run.
        :param experiment_client: The client for the run.
        :return: A run.
        """
        run_json = experiment_client.create_run(experiment.name)
        run = RemoteRun(experiment, experiment_client)
        run._id = run_json["runId"]

        return run

    @staticmethod
    def get(experiment, run_id, experiment_client):
        """
        Gets a run.

        :param experiment: The parent experiment of the run.
        :param run_id: The identifier for the run.
        :param experiment_client: The client for the run.
        :return: A run.
        """
        run_json = experiment_client.get_run(experiment.name, run_id)
        return RemoteRun.from_json(run_json, experiment)

    @staticmethod
    def from_json(json, experiment):
        # pylint: disable=protected-access,redefined-outer-name,duplicate-code
        """
        Builds a run from the given json.
        :param run_json: json that specifies the run; acceptable values are runId,
        startTime, endTime, took, a list of params, metrics, metadata, and artifacts
        :param experiment: the parent experiment of the run
        :return: a run
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

    def log_param(self, name: str, param):
        """
        Updates the params for the run.
        """
        super().log_param(name, param)
        self._client.update_param(self._experiment.name, self.id, name, param)

    def log_metric(self, name: str, metric):
        """
        Updates the metrics for the run.
        """
        super().log_metric(name, metric)
        self._client.update_metric(self._experiment.name, self.id, name, metric)

    def set_meta(self, name: str, val):
        """
        Sets the metadata for the run.
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

    def get_artifact(self, name: str, deserializer=dill.loads):
        """
        Gets an artifact with the given name.  Deserializes the artifact stream
        using dill by default.  Deserialization can be disabled entirely or the
        deserializer function can be overridden.
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
