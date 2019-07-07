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

import cuid
import io
import os
import dill
import tempfile
from .timer import Timer
from .exceptions import ConfigurationException


class Run:
    """
    Captures the elapsed time of a run of an experiment and saves the metrics and parameters for the run.
    """
    def __init__(self, experiment):
        self._id = cuid.slug()
        self._experiment = experiment
        self._timer = None
        self._start = None
        self._end = None
        self._interval = None
        self._params = {}
        self._metrics = {}
        self._artifacts = {}
        self._meta = {}

    def start(self):
        """
        Starts the timer.
        """
        if self._timer is not None:
            raise ValueError('Attempt to start a Run that is already started')

        self._timer = Timer()
        self._timer.start()
        self._start = self._timer.start_time
        self._experiment.save_run(self)

    def stop(self):
        """
        Stops the time and captures data about the run.
        """
        self._timer.stop()
        self._end = self._timer.end_time
        self._interval = self._timer.interval
        self._experiment.save_run(self)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    @property
    def id(self):
        """
        The id for the run.
        """
        return self._id

    @property
    def start_time(self):
        """
        The start time for the run.
        """
        if self._start:
            return int(self._start)
        return None

    @property
    def end_time(self):
        """
        The end time for the run.
        """
        if self._end:
            return int(self._end)
        return None

    @property
    def took(self):
        """
        The interval between the start and end of the run.
        """
        return self._interval

    @property
    def params(self):
        """
        Params of the run.
        """
        return self._params

    def get_param(self, param):
        """
        Gets a particular parameter of the run.

        :param param: Parameter to get.
        """
        return self._params.get(param)

    @property
    def metrics(self):
        """
        The metrics for the run.
        """
        return self._metrics

    def get_metric(self, metric):
        """
        Gets a particular metric for the run.

        :param metric: metric to get
        """
        return self._metrics.get(metric)

    @property
    def meta(self):
        """
        Metadata for the run.
        """
        return self._meta

    def get_meta(self, meta):
        """
        Gets metadata for the run.
        """
        return self.meta.get(meta)

    @property
    def artifacts(self):
        """
        The artifacts stored in this run.

        :return: The artifact object.
        """
        return self._artifacts

    def get_artifact(self, name):
        """
        Gets an artifact object by name.

        :param name: The key of the artifact.
        :return: The artifact object.
        """
        return self.artifacts.get(name)

    def to_json(self):
        """
        A json representation of the run.
        """
        doc = {'id': self.id, 'startTime': self.start_time, 'endTime': self.end_time, 'took': self.took,
               'params': self.params, 'metrics': self.metrics, 'meta': self.meta,
               'artifacts': [name for name in self.artifacts.keys()]}
        return doc

    @staticmethod
    def from_json(json, experiment):
        """
        Creates a run from a json representation.

        :param json: The json representation of the run.
        :param experiment: The experiment to associate with the run.
        :return: A run that has the values in the given json object with
        the given experiment.
        """
        run = Run(experiment)
        run._id = json['id']
        run._start = json.get('startTime', json.get('start'))
        run._end = json.get('endTime', json.get('end'))
        run._interval = json.get('took')
        run._params = json.get('params', {})
        run._metrics = json.get('metrics', {})
        run._meta = json.get('meta', {})

        artifacts = json.get('artifacts', [])
        for name in artifacts:
            run._artifacts[name] = experiment.load_artifact(run, name)

        return run

    def log_param(self, name: str, param):
        """
        Logs for a given parameter.
        """
        if hasattr(param, 'tolist'):
            _val = param.tolist()
        else:
            _val = self._to_scaler(param)

        self._params[name] = _val

    def log_params(self, params):
        """
        Logs a group of parameters.
        """
        for k, v in params.items():
            self.log_param(k, v)

    def log_metric(self, name: str, metric):
        """
        Logs a given metric.
        """
        if hasattr(metric, 'tolist'):
            _val = metric.tolist()
        else:
            _val = self._to_scaler(metric)

        self._metrics[name] = _val

    def set_meta(self, name: str, val):
        """
        Sets metadata for the run.
        """
        if hasattr(val, 'tolist'):
            _val = val.tolist()
        else:
            _val = self._to_scaler(val)

        self._meta[name] = _val

    def log_artifact(self, name: str, artifact):
        """
        Logs a given artifact.
        """
        self._artifacts[name] = artifact

    def log_artifact_ref(self, name: str, ref):
        """
        Logs a given artifact reference.
        """
        self._artifacts[name] = {'ref': ref}

    @staticmethod
    def _is_numpy_dtype(x):
        return hasattr(x, 'dtype')

    @staticmethod
    def _to_scaler(x):
        if hasattr(x, 'dtype'):
            import numpy as np
            return np.asscalar(x)
        return x


class RemoteRun(Run):
    """
    A run that is executed remotely, through a client.
    """

    def __init__(self, experiment, experiment_client):
        super().__init__(experiment)
        self._client = experiment_client

    @staticmethod
    def create(experiment, experiment_client):
        """
        Creates a remote run.

        :param experiment: The experiment to associate with this run.
        :param experiment_client: The client for the run.
        :return: A run.
        """
        r = experiment_client.create_run(experiment.name)
        run = RemoteRun(experiment, experiment_client)
        run._id = r['runId']

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
        r = experiment_client.get_run(experiment.name, run_id)
        return RemoteRun.from_json(r, experiment)

    @staticmethod
    def from_json(json, experiment):
        """
        Builds a run from the given json.

        :param jsom: json that specifies the run; acceptable values are runId,
        startTime, endTime, took, a list of params, metrics, metadata, and artifacts
        :param experiment: the parent experiment of the run
        :return: a run
        """
        run = RemoteRun(experiment, experiment._client)
        run._id = json['runId']
        run._start = json.get('startTime', json.get('start'))
        run._end = json.get('endTime', json.get('end'))
        run._interval = json.get('took')
        run._params = json.get('params', {})
        run._metrics = json.get('metrics', {})
        run._meta = json.get('meta', {})
        run._artifacts = json.get('artifacts', {})

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
        if hasattr(artifact, 'ref'):
            with open(artifact['ref'], 'rb') as stream:
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
        with open(file_path, 'rb') as f:
            self.log_artifact_stream(name, f)

    def log_artifact_stream(self, name: str, stream):
        """
        Updates the artifact with the given stream.
        """
        self._client.update_artifact(self._experiment.name, self.id, name, stream)

    def log_keras_model(self, model, artifact_name='model'):
        """
        Logs a keras model as an artifact.
        """
        with tempfile.NamedTemporaryFile(mode='w+b') as temp:
            model.save(filepath=temp.name)
            self.log_artifact_file(artifact_name, temp.name)

    def get_artifact(self, name: str, deserializer=dill.loads):
        """
        Gets an artifact with the given name.  Deserializes the artifact stream using dill by default.  Deserialization
        can be disabled entirely or the deserializer function can be overridden.
        """
        artifact_bytes = self._client.get_artifact(self._experiment.name, self.id, name)
        if deserializer:
            return deserializer(artifact_bytes)
        return artifact_bytes

    def get_keras_model(self, artifact_name='model'):
        """
        Gets the keras model.
        """
        try:
            from keras.models import load_model
        except ImportError:
            raise ConfigurationException('Keras needs to be installed in order to use get_keras_model')

        f = tempfile.NamedTemporaryFile(delete=False)
        f.write(self.get_artifact(artifact_name, deserializer=lambda x: x))
        model_file = f.name
        f.close()
        try:
            model = load_model(model_file)
        finally:
            os.remove(model_file)

        return model
