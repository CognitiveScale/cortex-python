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

import json
from typing import Dict

from .camel import CamelResource
from .serviceconnector import _Client
from .utils import raise_for_status_with_detail, parse_string


class ModelClient(_Client):

    """
    A client for the Cortex model management API. While the :mod:`cortex.experiment` module deals with the initial lifecycle aspects of model ideation, and design, the :class:`cortex.model.ModelClient` exists to save metadata about a known well-working model configuration produced after multiple iterations of Experiment runs and training configurations.

    Models can have a lifecycle, are able to store metadata about their types, and more. Refer to the `official API reference <https://cognitivescale.github.io/cortex-fabric/swagger/index.html#operation/PostModel>`_ to understand all the model metadata that can be saved when models are created or updated.
    """  # pylint: disable=line-too-long

    URIs = {
        "models": "projects/{projectId}/models",
        "model": "projects/{projectId}/models/{modelName}",
    }

    def list_models(self):
        """
        List Models
        :return: list of models
        """
        res = self._serviceconnector.request(
            method="GET", uri=self.URIs["models"].format(projectId=self._project())
        )
        raise_for_status_with_detail(res)
        res = res.json()

        return res.get("models", [])

    def save_model(self, model_obj):
        """
        Save or update model object
        :param model_obj: Model object to be saved or updated
        :return: status
        """
        body = json.dumps(model_obj)
        headers = {"Content-Type": "application/json"}
        uri = self.URIs["models"].format(projectId=self._project())
        res = self._serviceconnector.request(
            method="POST", uri=uri, body=body, headers=headers
        )
        raise_for_status_with_detail(res)
        return res.json()

    def get_model(self, model_name):
        """
        Get model by model name
        :param model_name: Model name
        :return: model json
        """
        uri = self.URIs["model"].format(
            projectId=self._project(), modelName=parse_string(model_name)
        )
        res = self._serviceconnector.request(method="GET", uri=uri)
        raise_for_status_with_detail(res)

        return res.json()

    def delete_model(self, model_name):
        """
        Delete model by name
        :param model_name: Model name
        :return: status
        """
        uri = self.URIs["model"].format(
            projectId=self._project(), modelName=parse_string(model_name)
        )
        res = self._serviceconnector.request(method="DELETE", uri=uri)
        raise_for_status_with_detail(res)
        res_json = res.json()

        return res_json.get("success", False)


class Model(CamelResource):
    """
    Tracks associated parameters of models.
    """

    def __init__(self, document: Dict, client: ModelClient):
        super().__init__(document, False)
        self._client = client
        self._project = client._project

    def to_camel(self, camel="1.0.0") -> dict:
        # pylint: disable=duplicate-code
        """Converts this instance of Model to a CAMEL JSON representation

        :param camel: Version of the CAMEL spec to convert to, defaults to "1.0.0"
        :type camel: str, optional
        :return: A python dict representing a JSON CAMEL specification of the model
        :rtype: dict
        """
        return {
            "camel": camel,
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "type": self.type,
            "tags": self.tags or [],
            "properties": self.properties or [],
        }
