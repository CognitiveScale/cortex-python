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

import dill
import os
import json
import urllib.parse

from pathlib import Path
from .run import Run, RemoteRun
from .properties import PropertyManager
from contextlib import closing
from datetime import datetime
from .camel import CamelResource
from typing import Dict, List
from requests.exceptions import HTTPError
from .exceptions import APIException, ConfigurationException
from .serviceconnector import _Client
from .utils import raise_for_status_with_detail


class ExperimentClient(_Client):

    """
    A client for the Cortex experiment and model management API.
    """
    headers = {'Content-Type': 'application/json'}

    URIs = {
        'experiments': 'projects/{projectId}/experiments',
        'experiment': 'projects/{projectId}/experiments/{experimentName}',
        'runs': 'projects/{projectId}/experiments/{experimentName}/runs',
        'run': 'projects/{projectId}/experiments/{experimentName}/runs/{runId}',
        'artifact': 'projects/{projectId}/experiments/{experimentName}/runs/{runId}/artifacts/{artifactId}',
        'meta': 'projects/{projectId}/experiments/{experimentName}/runs/{runId}/meta/{metaId}',
        'param': 'projects/{projectId}/experiments/{experimentName}/runs/{runId}/params/{paramId}',
        'metric': 'projects/{projectId}/experiments/{experimentName}/runs/{runId}/metrics/{metricId}'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._serviceconnector.version = 4

    def list_experiments(self, project: str = None):
        """
        List all experiments in the specified projectN
        :param project: Project name (default: Connection's project)
        :return: list of experiments
        :raise HTTPError: Non 2xx response
        """
        if project is None: project = self._serviceconnector.project
        # TODO add limit/skip/...
        r = self._serviceconnector.request(method='GET', uri=self.URIs['experiments'].format(projectId=project))
        raise_for_status_with_detail(r)
        rs = r.json()

        return rs.get('experiments', [])

    def save_experiment(self, experiment_name: str, project: str = None, model_id: str = None, **kwargs):
        """
        Create or update an experiment
        :param experiment_name: Experiment name/id
        :param project: Project name (default: Connection's project)
        :param model_id: Model to associate this experiment to (default: None)
        :param kwargs:
        :return: response JSON
        :raise HTTPError: Non 2xx response
        """
        if project is None: project = self._serviceconnector.project
        if model_id is None: model_id = ""
        
        body_obj = {'name': experiment_name, 'modelId': model_id}

        if kwargs:
            body_obj.update(kwargs)

        body = json.dumps(body_obj)
        headers = {'Content-Type': 'application/json'}
        uri = self.URIs['experiments'].format(projectId=project)
        r = self._serviceconnector.request(method='POST', uri=uri, body=body, headers=headers)
        raise_for_status_with_detail(r)
        return r.json()

    def delete_experiment(self, experiment_name: str, project: str = None):
        """
        Delete experiment
        :param experiment_name: Experiment name/id
        :param project: Project name (default: Connection's project)
        :return: boolean - success
        :raise HTTPError: Non 2xx response
        """
        if project is None: project = self._serviceconnector.project
        uri = self.URIs['experiment'].format(projectId=project, experimentName=self.parse_string(experiment_name))
        r = self._serviceconnector.request(method='DELETE', uri=uri)
        raise_for_status_with_detail(r)
        rs = r.json()

        return rs.get('success', False)

    def get_experiment(self, experiment_name: str, project = None):
        """
        Fetch experiment by name
        :param experiment_name: Experiment name/id
        :param project: Project name (default: Connection's project)
        :return: experiment JSON
        :raise HTTPError: Non 2xx response
        """
        if project is None: project = self._serviceconnector.project
        uri = self.URIs['experiment'].format(projectId=project, experimentName=self.parse_string(experiment_name))
        r = self._serviceconnector.request(method='GET', uri=uri)
        raise_for_status_with_detail(r)

        return r.json()

    def list_runs(self, experiment_name: str, project: str = None):
        """
        List runs for experiment
        :param experiment_name: Experiment name/id
        :param project: Project name (default: Connection's project)
        :return: list of runs
        :raise HTTPError: Non 2xx response
        """
        if project is None: project = self._serviceconnector.project
        uri = self.URIs['runs'].format(projectId=project, experimentName=self.parse_string(experiment_name))
        r = self._serviceconnector.request(method='GET', uri=uri)
        raise_for_status_with_detail(r)
        rs = r.json()

        return rs.get('runs', [])

    def find_runs(self, experiment_name: str, project: str = None, filter: str = None, sort: str =None, limit: int =25):
        """
        Find runs within an experiments
        :param experiment_name: Experiment name/id
        :param project: Project name (default: Connection's project)
        :param filter: key/value of attribute and values to filter by ex. '{"name" : "somename" }'
        :param sort: key/value of attributes and sort order ascending 1, descending 0 ex. '{ "name": 1 }'
        :param limit: limit number of results (default: 25)
        :return: list of runs
        :raise HTTPError: Non 2xx response
        """
        if project is None: project = self._serviceconnector.project
        uri = self.URIs['runs'].format(projectId=project, experimentName=self.parse_string(experiment_name))

        # filter and limit are required query params
        params = {
            'filter': json.dumps(filter),
            'limit': limit
        }

        # Add sorting
        if sort:
            params['sort'] = json.dumps(sort)

        r = self._serviceconnector.request(method='GET', uri=uri, params=params)
        raise_for_status_with_detail(r)
        rs = r.json()

        return rs.get('runs', [])

    def delete_runs(self, experiment_name: str, project: str = None, filter: str = None, sort: str = None, limit: int = None):
        """
        Delete runs from an experiment
        :param experiment_name: Experiment name/id
        :param project: Project name (default: Connection's project)
        :param filter: key/value of attribute and values to filter by ex. '{"name" : "somename" }'
        :param sort: key/value of attributes and sort order ascending 1, descending 0 ex. '{ "name": 1 }'
        :param limit: limit number of results (default: 25)
        :return: response message
        :raise HTTPError: Non 2xx response
        """
        if project is None: project = self._serviceconnector.project
        uri = self.URIs['runs'].format(projectId=project, experimentName=self.parse_string(experiment_name))

        params = {}

        # Add query filter
        if filter:
            params['filter'] = json.dumps(filter)

        # Add sorting
        if sort:
            params['sort'] = json.dumps(sort)

        # Add limit
        if limit:
            params['limit'] = limit

        r = self._serviceconnector.request(method='DELETE', uri=uri, params=params)
        raise_for_status_with_detail(r)
        rs = r.json()

        return rs.get('message')

    def create_run(self, experiment_name: str, project: str = None, **kwargs):
        """
        Add a run to an experiment
        :param experiment_name: Experiment name/id
        :param project: Project name (default: Connection's project)
        :param kwargs: Properties to set on the run ex. '{"runId": "run1"}'
        :return: dict - response message
        :raise HTTPError: Non 2xx response
        """
        body_obj = {}
        if project is None: project = self._serviceconnector.project

        if kwargs:
            body_obj.update(kwargs)

        body = json.dumps(body_obj)
        headers = {'Content-Type': 'application/json'}
        uri = self.URIs['runs'].format(projectId=project, experimentName=self.parse_string(experiment_name))
        r = self._serviceconnector.request(method='POST', uri=uri, body=body, headers=headers)
        raise_for_status_with_detail(r)
        return r.json()

    def get_run(self, experiment_name: str, run_id: str, project: str = None):
        """
        Fetch a run from an experiment
        :param experiment_name: Experiment name/id
        :param run_id: Run id to fetch
        :param project: Project name (default: Connection's project)
        :return: dict - run object
        :raise HTTPError: Non 2xx response, 404 not found
        """
        if project is None: project = self._serviceconnector.project
        uri = self.URIs['run'].format(projectId=project, experimentName=self.parse_string(experiment_name), runId=run_id)
        r = self._serviceconnector.request(method='GET', uri=uri)
        raise_for_status_with_detail(r)

        return r.json()

    def update_run(self, experiment_name: str, run_id: str, project: str = None, **kwargs):
        """
        Update an existing run
        :param experiment_name: Experiment name/id
        :param run_id: Run id to fetch
        :param project: Project name (default: Connection's project)
        :param kwargs: Properties to set on the run ex. '{"att1": "vall1"}'
        :return: response message
        :raise HTTPError: Non 2xx response, 404 not found
        """
        body_obj = {}
        if project is None: project = self._serviceconnector.project

        if kwargs:
            body_obj.update(kwargs)

        body = json.dumps(body_obj)
        headers = {'Content-Type': 'application/json'}
        uri = self.URIs['run'].format(projectId=project, experimentName=self.parse_string(experiment_name), runId=run_id)
        r = self._serviceconnector.request(method='PUT', uri=uri, body=body, headers=headers)
        raise_for_status_with_detail(r)
        rs = r.json()

        success = rs.get('success', False)
        if not success:
            raise Exception('Error updating run {}: {}'.format(run_id, rs.get('error')))
        return success

    def delete_run(self, experiment_name: str, run_id: str, project: str = None):
        """
        Delete the specified run from the experiment
        :param experiment_name: Experiment name/id
        :param run_id: Run id to fetch
        :param project: Project name (default: Connection's project)
        :return: response message
        :raise HTTPError: Non 2xx response, 404 not found
        """
        if project is None: project = self._serviceconnector.project
        uri = self.URIs['run'].format(projectId=project, experimentName=self.parse_string(experiment_name), runId=run_id)
        r = self._serviceconnector.request(method='DELETE', uri=uri)
        raise_for_status_with_detail(r)
        rs = r.json()

        success = rs.get('success', False)
        if not success:
            raise Exception('Error deleting run {}: {}'.format(run_id, rs.get('error')))
        return success

    def update_meta(self, experiment_name: str, run_id: str, meta, val, project: str = None):
        """
        Update metadata key/value on a experiment's run
        :param experiment_name: Experiment name/id
        :param run_id: Run id to fetch
        :param meta: Metadata name
        :param val: Metadata value
        :param project: Project name (default: Connection's project)
        :return: dict - response message
        :raise HTTPError: Non 2xx response
        """
        if project is None: project = self._serviceconnector.project
        uri = self.URIs['meta'].format(projectId=project, experimentName=self.parse_string(experiment_name), runId=run_id, metaId=meta)
        headers = {'Content-Type': 'application/json'}
        r = self._serviceconnector.request(method='PUT', uri=uri, body=json.dumps({'value': val}), headers=headers)
        raise_for_status_with_detail(r)
        rs = r.json()

        success = rs.get('success', False)
        if not success:
            raise Exception('Error updating run {} meta property {}: {}'.format(run_id, meta, rs.get('error')))
        return success

    def update_param(self, experiment_name: str, run_id: str, param, val, project: str = None):
        """
        Update param key/value on a experiment's run
        :param experiment_name: Experiment name/id
        :param run_id: Run id to fetch
        :param param: Metadata name
        :param val: Metadata value
        :param project: Project name (default: Connection's project)
        :return: dict - response message
        :raise HTTPError: Non 2xx response
        """
        if project is None: project = self._serviceconnector.project
        uri = self.URIs['param'].format(projectId=project, experimentName=self.parse_string(experiment_name), runId=run_id, paramId=param)
        headers = {'Content-Type': 'application/json'}
        r = self._serviceconnector.request(method='PUT', uri=uri, body=json.dumps({'value': val}), headers=headers)
        raise_for_status_with_detail(r)
        rs = r.json()

        success = rs.get('success', False)
        if not success:
            raise Exception('Error updating run {} param {}: {}'.format(run_id, param, rs.get('error')))
        return success

    def update_metric(self, experiment_name: str, run_id: str, metric: str, val, project: str = None):
        """
        Update metric key/value on a experiment's run
        :param experiment_name: Experiment name/id
        :param run_id: Run id to fetch
        :param metric: Metadata name
        :param val: Metadata value
        :param project: Project name (default: Connection's project)
        :return: dict - response message
        :raise HTTPError: Non 2xx response
        """
        if project is None: project = self._serviceconnector.project
        uri = self.URIs['metric'].format(projectId=project, experimentName=self.parse_string(experiment_name), runId=run_id, metricId=metric)
        headers = {'Content-Type': 'application/json'}
        r = self._serviceconnector.request(method='PUT', uri=uri, body=json.dumps({'value': val}), headers=headers)
        raise_for_status_with_detail(r)
        rs = r.json()

        success = rs.get('success', False)
        if not success:
            raise Exception('Error updating run {} metric {}: {}'.format(run_id, metric, rs.get('error')))
        return success

    def update_artifact(self, experiment_name: str, run_id: str, artifact: str, stream, project: str = None):
        """
        Add/Update an artifact on a run
        :param experiment_name: Experiment name/id
        :param run_id: Run id to fetch
        :param artifact: str - Artifact key
        :param stream: Dictionary, list of tuples, bytes, or file-like object
        :param project: Project name (default: Connection's project)
        :return: dict - response message
        :raise HTTPError: Non 2xx response
        """
        if project is None: project = self._serviceconnector.project
        uri = self.URIs['artifact'].format(projectId=project, experimentName=self.parse_string(experiment_name), runId=run_id, artifactId=artifact)
        r = self._serviceconnector.request(method='PUT', uri=uri, body=stream)
        raise_for_status_with_detail(r)
        rs = r.json()

        success = rs.get('success', False)
        if not success:
            raise Exception('Error updating run {} artifact {}: {}'.format(run_id, artifact, rs.get('error')))
        return success

    def get_artifact(self, experiment_name: str, run_id: str, artifact: str, project: str = None):
        """
        Fetch an artifact from a run
        :param experiment_name: Experiment name/id
        :param run_id: Run id to fetch
        :param artifact: str - Artifact key
        :param project: Project name (default: Connection's project)
        :return: bytes - artifact content
        :raise HTTPError: Non 2xx response
        """
        if project is None: project = self._serviceconnector.project
        uri = self.URIs['artifact'].format(projectId=project, experimentName=self.parse_string(experiment_name), runId=run_id, artifactId=artifact)
        r = self._serviceconnector.request(method='GET', uri=uri, stream=True)
        raise_for_status_with_detail(r)
        return r.content

    def parse_string(self, string):
        # Replaces special characters like / with %2F
        return urllib.parse.quote(string, safe='')

def _to_html(exp):
    try:
        import maya
        from jinja2 import Template
    except (ImportError, NameError):
        raise ConfigurationException(
            'The jupyter extras are required to use this, please install using "pip install cortex-python[jupyter]"')

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

    t = Template(template)
    return t.render(
            name=exp.name, 
            runs=runs, 
            maya=maya.MayaDT, 
            num_params=num_params, 
            param_names=sorted(list(param_names)), 
            num_metrics=num_metrics, 
            metric_names=sorted(list(metric_names))
            )

class Experiment(CamelResource):
    """
    Tracks runs, associated parameters, metrics, and artifacts of experiments.
    """

    def __init__(self, document: Dict, project: str, client: ExperimentClient):
        super().__init__(document, False)
        self._project = project
        self._client = client
        if not self.meta:
            self.meta = {}

    @staticmethod
    def get_experiment(name, project, client: ExperimentClient, model_id=None, **kwargs):
        """
        Fetches or creates an experiment to work with.

        :param name: The name of the experiment to retrieve.
        :param project: The project from which the experiment is to be retrieved.
        :param client: The client instance to use.
        :param model_id: The model reference(optional).
        :return: An experiment object.
        """
        try:
            exp = client.get_experiment(name, project)
        except HTTPError:
            # Likely a 404, try to create a new experiment
            exp = client.save_experiment(name, project, model_id, **kwargs)

        return Experiment(exp, project, client)

    def start_run(self) -> Run:
        return RemoteRun.create(self, self._project, self._client)

    def save_run(self, run: Run):
        self._client.update_run(self.name, self._project, run.id, took=run.took, startTime=run.start_time, endTime=run.end_time)

    def reset(self, filter=None, sort=None, limit=None):
        self._client.delete_runs(self.name, self._project, filter, sort, limit)

    def set_meta(self, prop, value):
        self.meta[prop] = value
        self._client.save_experiment(self.name, self._project, **self.to_camel())

    def runs(self) -> List[Run]:
        runs = self._client.list_runs(self.name, self._project)
        return [RemoteRun.from_json(r, self._project, self) for r in runs]

    def get_run(self, run_id) -> Run:
        run = self._client.get_run(self.name, self._project, run_id)
        return RemoteRun.from_json(run, self._project, self)

    def last_run(self) -> Run:
        sort = {'endTime': -1}
        runs = self._client.find_runs(self.name, self._project, {}, sort=sort, limit=1)
        if len(runs) == 1:
            print(self)
            return RemoteRun.from_json(runs[0], self._project, self)
        raise APIException('Last run for experiment {} not found'.format(self.name))

    def find_runs(self, filter, sort, limit: int) -> List[Run]:
        runs = self._client.find_runs(self.name, self._project, filter or {}, sort=sort, limit=limit)
        return [RemoteRun.from_json(r, self._project, self) for r in runs]

    def load_artifact(self, run: Run, name: str):
        return dill.loads(self._client.get_artifact(experiment_name=self.name, project=self._project,run_id= run.id, artifact=name))

    def to_camel(self, camel='1.0.0'):
        return {
            'camel': camel,
            'name': self.name,
            'title': self.title,
            'description': self.description,
            'tags': self.tags or [],
            'meta': self.meta or {}
        }

    def _repr_html_(self):
        return _to_html(self)

    def display(self):
        from IPython.display import (display, HTML)
        display(HTML(self._repr_html_()))


class LocalExperiment:
    """
    Runs experiment locally, not using Cortex services.
    """
    config_file = 'config.yml'
    root_key = 'experiment'
    dir_cortex = '.cortex'
    dir_local = 'local'
    dir_artifacts = 'artifacts'
    dir_experiments = 'experiments'
    runs_key = 'runs'

    def __init__(self, name, basedir=None):
        self._name = name

        if basedir:
            self._basedir = Path(basedir)
        else:
            self._basedir = Path.home() / self.dir_cortex

        self._work_dir = self._basedir / self.dir_local / self.dir_experiments / self.name
        self._work_dir.mkdir(parents=True, exist_ok=True)
        Path(self._work_dir / self.dir_artifacts).mkdir(parents=True, exist_ok=True)

        # Initialize config
        pm = PropertyManager()
        try:
            pm.load(str(self._work_dir / self.config_file))
        except FileNotFoundError:
            pm.set('meta', {'created': str(datetime.now())})

        self._config = pm

    @property
    def name(self):
        """
        Name of the experiment.
        """
        return self._name

    def start_run(self) -> Run:
        """
        Creates a run for the experiment.
        """
        return Run(self)

    def save_run(self, run: Run):
        """
        Saves a run.

        :param run: The run you want to save.
        """
        updated_runs = []
        runs = self._config.get(self._config.join(self.root_key, self.runs_key)) or []
        replaced = False
        if len(runs) > 0:
            for r in runs:
                if r['id'] == run.id:
                    updated_runs.append(run.to_json())
                    replaced = True
                else:
                    updated_runs.append(r)

        if not replaced:
            updated_runs.append(run.to_json())

        self._config.set(self._config.join(self.root_key, self.runs_key), updated_runs)
        self._save_config()

        for name, artifact in run.artifacts.items():
            with closing(open(self.get_artifact_path(run, name), 'wb')) as f:
                dill.dump(artifact, f)

    def reset(self):
        """
        Resets the experiement, removing all associated configuration and runs.
        """
        self._config.remove_all()
        self.clean_dir(self._work_dir)
        self.clean_dir(Path(self._work_dir / self.dir_artifacts))

    def clean_dir(self, dir_to_clean):
        """
        Removes only the files from the given directory
        """
        for f in os.listdir(dir_to_clean):
             if os.path.isfile(os.path.join(dir_to_clean, f)):
                 os.remove(os.path.join(dir_to_clean, f))

    def set_meta(self, prop, value):
        """
        Associates metadata properties with the experiment.

        :param prop: The name of the metadata property to associate with the experiment.
        :param value: The value of the metadata property to associate with the experiment.
        """
        meta = self._config.get('meta')
        meta[prop] = value
        self._config.set('meta', meta)
        self._save_config()

    def runs(self) -> List[Run]:
        """
        Returns the runs associated with the experiment.
        """
        props = self._config
        runs = props.get(props.join(self.root_key, self.runs_key)) or []
        return [Run.from_json(r, self) for r in runs]

    def get_run(self, run_id: str) -> Run:
        """
        Gets a particular run from the runs in this experiment.
        """
        for r in self.runs():
            if r.id == run_id:
                return r
        return None

    def last_run(self) -> Run:
        runs = self.runs()
        if len(runs) > 0:
            return runs[-1]
        return None

    def find_runs(self, filter, sort, limit: int) -> List[Run]:
        raise NotImplementedError('find_runs is not supported in local mode')

    def _save_config(self):
        self._config.save(self._work_dir / self.config_file)

    def load_artifact(self, run: Run, name: str, extension: str = 'pk'):
        """
        Returns a particualr artifact created by the given run of the experiement.

        :param run: The run that generated the artifact requested.
        :param name: The name of the artifact.
        :param extension: An optional extension (defaults to 'pk').
        """
        artifact_file = self.get_artifact_path(run, name, extension)
        with closing(open(artifact_file, 'rb')) as f:
            return dill.load(f)

    def get_artifact_path(self, run: Run, name: str, extension: str = 'pk'):
        """
        Returns the fully qualified path to a particular artifact.

        :param run: The run that generated the artifact requested.
        :param name: The name of the artifact.
        :param extension: An optional extension (defaults to 'pk').
        """
        return self._work_dir / self.dir_artifacts / "{}_{}.{}".format(name, run.id, extension)

    def _repr_html_(self):
        return _to_html(self)

    def display(self):
        """
        Provides html output of the experiment.
        """
        try:
            from IPython.display import (display, HTML)
            display(HTML(self._repr_html_()))
        except ImportError:
            raise ConfigurationException(
                'The ipython package is required, please install it using pip install cortex-python[jupyter]')
