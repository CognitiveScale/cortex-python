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

import pickle
import json
from typing import Dict
from pathlib import Path
from datetime import datetime
from abc import ABC, abstractmethod
from .utils import get_logger
from .exceptions import ConfigurationException
from .camel import CamelResource
from .pipeline import Pipeline
from .pipeline_loader import PipelineLoader
from .properties import PropertyManager
from .serviceconnector import _Client
from .utils import raise_for_status_with_detail

log = get_logger(__name__)


class DatasetsClient(_Client):
    """
    A client used to manage datasets.
    """
    URIs = {'datasets': 'datasets',
            'content':  'content'}

    def list_datasets(self):
        """
        Get a list of all datasets.
        """
        # TODO: Use pagination?
        uri = self.URIs['datasets']
        r = self._serviceconnector.request('GET', uri)
        raise_for_status_with_detail(r)
        return r.json().get('datasets', [])

    def save_dataset(self, dataset: Dict[str, object]):
        """
        Saves a dataset.

        :param dataset: A Cortex dataset as dict.
        """
        uri = self.URIs['datasets']
        body_s = json.dumps(dataset)
        headers = {'Content-Type': 'application/json'}
        r = self._serviceconnector.request('POST', uri, body_s, headers)
        raise_for_status_with_detail(r)
        return r.json()

    def get_dataframe(self, dataset_name: str):
        """
        Gets data from a dataset as a dataframe.

        :param dataset_name: The name of the dataset to pull data.
        :return: A dataframe dictionary
        """
        uri = '/'.join([self.URIs['datasets'], dataset_name, 'dataframe'])
        r = self._serviceconnector.request('GET', uri)
        raise_for_status_with_detail(r)
        return r.json()

    def get_stream(self, stream_name: str):
        """
        Gets a dataset as a stream.
        """
        uri = '/'.join([self.URIs['datasets'], stream_name, 'stream'])
        r = self._serviceconnector.request('GET', uri, stream=True)
        raise_for_status_with_detail(r)
        return r.raw

    def post_stream(self, stream_name, data):
        uri = '/'.join([self.URIs['datasets'], stream_name, 'stream'])
        headers = {"Content-Type": "application/json-lines"}
        r = self._serviceconnector.request('POST', uri, data, headers)
        print(r.text)
        raise_for_status_with_detail(r)
        return r.json()

    def get_pipeline(self, dataset_name: str, pipeline_name: str):
        uri = '/'.join([self.URIs['datasets'], dataset_name, 'pipelines', pipeline_name])
        r = self._serviceconnector.request('GET', uri)
        raise_for_status_with_detail(r)
        return r.json()


class _DatasetPipelineLoader(PipelineLoader):

    def __init__(self, ds):
        super().__init__()
        self.ds = ds

    def add_pipeline(self, name, pipeline):
        super().add_pipeline(name, pipeline)
        self.ds._add_pipeline(name, pipeline)

    def get_pipeline(self, name):
        try:
            p = self.ds._client.get_pipeline(self.ds.name, name)
            pipeline = Pipeline.load(p, self)
            self.add_pipeline(name, pipeline)
            return pipeline
        except:
            return super().get_pipeline(name)

    def remove_pipeline(self, name):
        super().remove_pipeline(name)
        self.ds._remove_pipeline(name)


class AbstractDataset(ABC):
    """
    Abstract base class for datasets.
    """
    @abstractmethod
    def get_dataframe(self):
        raise NotImplementedError()

    @abstractmethod
    def get_stream(self):
        raise NotImplementedError()

    @abstractmethod
    def as_pandas(self):
        raise NotImplementedError()

    def visuals(self, df=None, figsize=(18, 9)):
        if df is None:
            df = self.as_pandas()
        try:
            from .viz import Viz
            return Viz(df, figsize)
        except ImportError:
            raise ConfigurationException('Please install the "viz" extras to use this method')

    @abstractmethod
    def save(self):
        raise NotImplementedError()

    @abstractmethod
    def to_camel(self):
        raise NotImplementedError()

    @abstractmethod
    def pipeline(self, name, clear_cache=False, depends=None):
        raise NotImplementedError()


class Dataset(AbstractDataset, CamelResource):

    """
    Defines the data and query parameters for accessing inputs to
    a managed content file or database connection.
    """

    def __init__(self, ds, client: DatasetsClient):
        super().__init__(ds, read_only=False)
        self._client = client
        self._work_dir = Path.cwd() / 'datasets' / self.name
        self._pipeline_loader = _DatasetPipelineLoader(self)

        # Cache all configured pipelines into our Pipeline loader
        if self.pipelines:
            for name in self.pipelines.keys():
                self._pipeline_loader.get_pipeline(name)
        else:
            self.pipelines = {}

    @staticmethod
    def get_dataset(name, client: DatasetsClient):
        """
        Gets a dataset.

        :param name: The name of the dataset to retrieve.
        :param client: The client instance to use.
        :return: A dataset object.
        """
        uri = '/'.join(['datasets', name])
        log.debug('Getting dataset using URI: %s' % uri)
        r = client._serviceconnector.request('GET', uri)
        raise_for_status_with_detail(r)

        return Dataset(r.json(), client)

    def get_dataframe(self):
        """
        Gets the dataframe for the dataset.
        """
        return self._client.get_dataframe('{}:{}'.format(self.name, self.version))

    def get_stream(self):
        """
        Streams the data coming from the dataset.
        """
        return self._client.get_stream('{}:{}'.format(self.name, self.version))

    def as_pandas(self):
        """
        Gets a pandas dataframe for the dataset.
        """
        df = self.get_dataframe()
        columns = df.get('columns')
        values = df.get('values')

        try:
            import pandas as pd
            return pd.DataFrame(values, columns=columns)
        except ImportError:
            log.warn('Pandas is not installed, please run `pip install pandas` or equivalent in your environment')
            return {'columns': columns, 'values': values}

    def save(self):
        try:
            from cortex_builders import DatasetBuilder
            b = DatasetBuilder(self.name, self._client, self.camel)
            return b.from_dataset(self).build()
        except ImportError:
            raise ConfigurationException('The cortex-python-builders library is required to save Datasets')

    def to_camel(self, camel='1.0.0'):
        ds = {
            'camel': camel,
            'name': self.name,
            'title': self.title,
            'description': self.description,
            'parameters': self.parameters,
            'pipelines': {key: pipeline.to_camel(camel) for key, pipeline in self.pipelines.items()}
        }

        if camel == '1.0.0':
            ds['connectionName'] = self.connectionName
            ds['connectionQuery'] = self.connectionQuery
        else:
            ds['connections'] = self.connections

        return ds

    def _add_pipeline(self, name, pipeline):
        self.pipelines[name] = pipeline

    def _remove_pipeline(self, name):
        if name in self.pipelines:
            del self.pipelines[name]

    def pipeline(self, name, clear_cache=False, depends=None):
        """
        Gets a pipeline for the dataset.

        :param name: name of the pipeline
        :param clear_cache: a flag to indicate whether previous results for the pipeline should be cleared
        :param depends: a list of pipeline names upon which this pipeline depends
        """
        p = self._pipeline_loader.get_pipeline(name)
        if clear_cache:
            # TODO clear any caches - e.g. for local mode
            pass

        if depends is not None:
            for d in depends:
                p.add_dependency(self._pipeline_loader.get_pipeline(d))

        return p


class LocalDataset(AbstractDataset):
    """
    References datasets that are external to Cortex.
    """

    config_file = 'config.yml'
    root_key = 'dataset'
    dir_cortex = '.cortex'
    dir_local = 'local'
    dir_data = 'data'
    dir_datasets = 'datasets'
    camel = '1.0.0'
    environment_id = 'cortex/local'

    def __init__(self, name, basedir=None):
        if basedir:
            self._basedir = Path(basedir)
        else:
            self._basedir = Path.home() / self.dir_cortex

        self._work_dir = self._basedir / self.dir_local / self.dir_datasets / name
        self._work_dir.mkdir(parents=True, exist_ok=True)
        self._data_dir = Path(self._work_dir / self.dir_data)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._pipeline_loader = PipelineLoader()

        # Initialize config
        pm = PropertyManager()
        try:
            # Load local dataset configuration
            pm.load(str(self._work_dir / self.config_file))

            # Cache all configured pipelines into our Pipeline loader
            pipelines = pm.get('pipelines') or {}
            for p_name, p_doc in pipelines.items():
                Pipeline.load(p_doc, self._pipeline_loader)
        except FileNotFoundError:
            # Set initial configuration state
            pm.set('name', name)
            pm.set('camel', self.camel)
            pm.set('_environmentId', self.environment_id)
            pm.set('createdAt', str(datetime.now()))
            pm.set('_version', 0)

        self._config = pm

    @property
    def name(self):
        return self._config.get('name')

    @name.setter
    def name(self, title):
        self._config.set('name', title)

    @property
    def version(self):
        return self._config.get('_version')

    @property
    def title(self):
        return self._config.get('title')

    @title.setter
    def title(self, title):
        self._config.set('title', title)

    @property
    def description(self):
        return self._config.get('description')

    @description.setter
    def description(self, description):
        self._config.set('description', description)

    @property
    def parameters(self):
        return self._config.get('parameters') or []

    @parameters.setter
    def parameters(self, params):
        self._config.set('parameters', params)

    def save(self):
        # Save pipelines from the loader
        pipelines = self._pipeline_loader.dump(self.camel)
        for k, v in pipelines.items():
            self._config.set(self._config.join('pipelines', k), v)

        self._config.set('_version', self.version + 1)
        self._config.save(self._work_dir / self.config_file)

        return self

    def as_pandas(self):
        return self.get_dataframe()

    @property
    def data_dir(self):
        return self._data_dir

    @property
    def content_key(self):
        return self._config.get('content_key')

    @content_key.setter
    def content_key(self, content_key: str):
        if not content_key:
            return
        ext = content_key.split('.')[-1]
        self._config.set('content_key', content_key)
        self._config.set('content_type', ext)

    @property
    def content_type(self):
        return self._config.get('content_type')

    def get_dataframe(self):
        try:
            import pandas as pd

            data_file = str(self._data_dir / self.content_key)

            if self.content_type == 'csv':
                return pd.read_csv(data_file)
            elif self.content_type == 'json':
                return pd.read_json(data_file, orient='records', lines=True)
            else:
                with self.get_stream() as s:
                    return pickle.load(s)
        except ImportError:
            raise ImportError('Pandas is not installed, please run `pip install pandas` or equivalent in your environment')

    def get_stream(self):
        data_file = str(self._data_dir / self.content_key)
        return open(data_file, 'rb')

    def to_camel(self):
        pipelines = self._config.get('pipelines') or {}
        ds = {
            'camel': self.camel,
            'name': self.name,
            '_version': self.version,
            'title': self.title,
            'description': self.description,
            'parameters': self.parameters,
            'pipelines':  pipelines
        }

        return ds

    def pipeline(self, name, clear_cache=False, depends=None):
        pipelines = self._config.get('pipelines') or {}
        p_doc = pipelines.get(name)
        if p_doc:
            return Pipeline.load(p_doc, self._pipeline_loader)

        p = Pipeline(name, depends, self._pipeline_loader)
        # pipelines[name] = p.to_camel(self.camel)
        # self._config.set('pipelines', pipelines)
        self.save()

        return p
