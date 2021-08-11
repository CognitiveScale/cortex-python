"""
Copyright 2019 Cognitive Scale, Inc. All Rights Reserved.

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

import json
import urllib.parse

from .camel import CamelResource
from typing import Dict
from .serviceconnector import _Client
from .utils import raise_for_status_with_detail


class ModelClient(_Client):

    """
    A client for the Cortex model management API.
    """

    URIs = {
        'models': 'projects/{projectId}/models',
        'model': 'projects/{projectId}/models/{modelName}'

    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._serviceconnector.version = 4
        # get project from connection b default
        if kwargs.get('project'):
            self._project = kwargs.get('project')
        else:
            self._project = self._serviceconnector.project

    def list_models(self):
        """
        List models in the current project
        :return: list - models objects
        """
        r = self._serviceconnector.request(method='GET', uri=self.URIs['models'].format(projectId=self._project))
        raise_for_status_with_detail(r)
        rs = r.json()

        return rs.get('models', [])

    def save_model(self, model_obj):
        """
        Create/Update a model in the current project
        :param model_obj: dict: Model object
        :return: Response message
        """
        body = json.dumps(model_obj)
        headers = {'Content-Type': 'application/json'}
        uri = self.URIs['models'].format(projectId=self._project)
        r = self._serviceconnector.request(method='POST', uri=uri, body=body, headers=headers)
        raise_for_status_with_detail(r)
        return r.json()

    def get_model(self, model_name: str):
        """
        Fetch a model from the current project
        :param model_name: Model name/id
        :return: dict - Response message
        """
        uri = self.URIs['model'].format(projectId=self._project, modelName=self.parse_string(model_name))
        r = self._serviceconnector.request(method='GET', uri=uri)
        raise_for_status_with_detail(r)
        return r.json()

    def delete_model(self, model_name: str):
        """
        Delete a model
        :param model_name:  Model name/id
        :return: dict - Response message
        """
        uri = self.URIs['model'].format(projectId=self._project, modelName=self.parse_string(model_name))
        r = self._serviceconnector.request(method='DELETE', uri=uri)
        raise_for_status_with_detail(r)
        rs = r.json()

        return rs.get('success', False)

    def parse_string(self, string: str):
        # Replaces special characters like / with %2F
        return urllib.parse.quote(string, safe='')


class Model(CamelResource):
    """
    Tracks associated parameters of models.
    """

    def __init__(self, document: Dict, project: str, client: ModelClient):
        super().__init__(document, False)
        self._project = project
        self._client = client

    def to_camel(self, camel='1.0.0'):
        return {
            'camel': camel,
            'name': self.name,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'type': self.type,
            'tags': self.tags or [],
            'properties': self.properties or [],
        }
