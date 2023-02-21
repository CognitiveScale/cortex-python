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

import cuid
from ..timer import Timer
from ..exceptions import ConfigurationException


class Run:
    # pylint: disable=too-many-instance-attributes,too-many-public-methods
    """
    Captures the elapsed time of a run of an experiment and
    saves the metrics and parameters for the run.
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
            raise ValueError("Attempt to start a Run that is already started")

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
    def id(self):  # pylint: disable=invalid-name
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
        doc = {
            "id": self.id,
            "startTime": self.start_time,
            "endTime": self.end_time,
            "took": self.took,
            "params": self.params,
            "metrics": self.metrics,
            "meta": self.meta,
            "artifacts": list(self.artifacts),
        }
        return doc

    @staticmethod
    def from_json(json: dict, experiment):
        # pylint: disable=protected-access,duplicate-code
        """
        Creates a run from a json representation.

        :param json: The json representation of the run.
        :type json: dict
        :param experiment: The experiment to associate with the run.
        :type experiment: :class:`cortex.experiment.Experiment`
        :return: A run that has the values in the given json object with the given experiment.
        :rtype: :class:`cortex.experiment.model.Run`
        """
        run = Run(experiment)
        run._id = json["id"]
        run._start = json.get("startTime", json.get("start"))
        run._end = json.get("endTime", json.get("end"))
        run._interval = json.get("took")
        run._params = json.get("params", {})
        run._metrics = json.get("metrics", {})
        run._meta = json.get("meta", {})

        artifacts = json.get("artifacts", [])
        for name in artifacts:
            run._artifacts[name] = experiment.load_artifact(run, name)

        return run

    def log_param(self, name: str, param):
        """
        Logs for a given parameter.
        """
        if hasattr(param, "tolist"):
            _val = param.tolist()
        else:
            _val = self._to_scaler(param)

        self._params[name] = _val

    def log_params(self, params):
        """
        Logs a group of parameters.
        """
        for k, val in params.items():
            self.log_param(k, val)

    def log_metric(self, name: str, metric):
        """
        Logs a given metric.
        """
        if hasattr(metric, "tolist"):
            _val = metric.tolist()
        else:
            _val = self._to_scaler(metric)

        self._metrics[name] = _val

    def set_meta(self, name: str, val):
        """
        Sets metadata for the run.
        """
        if hasattr(val, "tolist"):
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
        self._artifacts[name] = {"ref": ref}

    @staticmethod
    def _is_numpy_dtype(arr):
        return hasattr(arr, "dtype")

    @staticmethod
    def _to_scaler(arr):
        if hasattr(arr, "dtype"):
            import numpy as np  # pylint: disable=import-outside-toplevel,import-error

            return np.asscalar(arr)
        return arr


def _to_html(exp):
    # pylint: disable=import-outside-toplevel
    try:
        import maya
        from jinja2 import Template
    except (ImportError, NameError) as exc:
        raise ConfigurationException(
            "The jupyter extras are required to use this,"
            'please install using "pip install cortex-python[viz]"'
        ) from exc

    runs = exp.runs()

    template = """
                    <style>
                        #table1 {
                          border: solid thin;
                          border-collapse: collapse;
                        }
                        #table1 caption {
                          padding-bottom: 0.5em;
                        }
                        #table1 th,
                        #table1 td {
                          border: solid thin;
                          padding: 0.5rem 2rem;
                        }
                        #table1 td {
                          white-space: nowrap;
                        }
                        #table1 td {
                          border-style: none solid;
                          vertical-align: top;
                        }
                        #table1 th {
                          padding: 0.2em;
                          vertical-align: middle;
                          text-align: center;
                        }
                        #table1 tbody td:first-child::after {
                          content: leader(". "); '
                        }
                    </style>
                    <table id="table1">
                        <caption><b>Experiment:</b> {{name}}</caption>
                        <thead>
                        <tr>
                            <th rowspan="2">ID</th>
                            <th rowspan="2">Date</th>
                            <th rowspan="2">Took</th>
                            <th colspan="{{num_params}}" scope="colgroup">Params</th>
                            <th colspan="{{num_metrics}}" scope="colgroup">Metrics</th>
                        </tr>
                        <tr>
                            {% for param in param_names %}
                            <th>{{param}}</th>
                            {% endfor %}
                            {% for metric in metric_names %}
                            <th>{{metric}}</th>
                            {% endfor %}
                        </tr>
                        </thead>
                        <tbody>
                            {% for run in runs %}
                            <tr>
                            <td>{{run.id}}</td>
                            <td>{{maya(run.start_time)}}</td>
                            <td>{{'%.2f' % run.took}} s</td>
                            {% for param in param_names %}
                            <td>{{run.params.get(param, "&#x2011;")}}</td>
                            {% endfor %}
                            {% for metric in metric_names %}
                            <td>{{'%.6f' % run.metrics.get(metric, 0.0)}}</td>
                            {% endfor %}
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>"""

    num_params = 0
    num_metrics = 0
    param_names = set()
    metric_names = set()
    if len(runs) > 0:
        for one_run in runs:
            param_names.update(one_run.params.keys())
            num_params = len(param_names)
            metric_names.update(one_run.metrics.keys())
            num_metrics = len(metric_names)

    tmpl = Template(template)
    return tmpl.render(
        name=exp.name,
        runs=runs,
        maya=maya.MayaDT,
        num_params=num_params,
        param_names=sorted(list(param_names)),
        num_metrics=num_metrics,
        metric_names=sorted(list(metric_names)),
    )
