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

from .camel import CamelResource
from typing import Dict
from .serviceconnector import _Client
from .utils import raise_for_status_with_detail, parse_string


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

    def list_models(self):
        """
        List Models
        :return: list of models
        """
        r = self._serviceconnector.request(method='GET', uri=self.URIs['models'].format(projectId=self._project()))
        raise_for_status_with_detail(r)
        rs = r.json()

        return rs.get('models', [])

    def save_model(self, model_obj):
        """
        Save or update model object
        :param model_obj: Model object to be saved or updated
        :return: status
        """
        body = json.dumps(model_obj)
        headers = {'Content-Type': 'application/json'}
        uri = self.URIs['models'].format(projectId=self._project())
        r = self._serviceconnector.request(method='POST', uri=uri, body=body, headers=headers)
        raise_for_status_with_detail(r)
        return r.json()

    def get_model(self, model_name):
        """
        Get model by model name
        :param model_name: Model name
        :return: model json
        """
        uri = self.URIs['model'].format(projectId=self._project(), modelName=parse_string(model_name))
        r = self._serviceconnector.request(method='GET', uri=uri)
        raise_for_status_with_detail(r)

        return r.json()

    def delete_model(self, model_name):
        """
        Delete model by name
        :param model_name: Model name
        :return: status
        """
        uri = self.URIs['model'].format(projectId=self._project(), modelName=parse_string(model_name))
        r = self._serviceconnector.request(method='DELETE', uri=uri)
        raise_for_status_with_detail(r)
        rs = r.json()

        return rs.get('success', False)


class Model(CamelResource):
    """
    Tracks associated parameters of models.
    """

    def __init__(self, document: Dict, client: ModelClient):
        super().__init__(document, False)
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
