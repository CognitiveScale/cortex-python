"""
Copyright 2024 Tecnotree, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

----
Module to interact with the Sensa model registry
"""

import os
from typing import Optional, Dict, Any
from cortex.serviceconnector import _Client
try:
    import mlflow
except ImportError:
    mlflow = None


def check_installed():
    if mlflow is None:
        raise NotImplementedError(
            'Models SDK extra not installed, please run `pip install cortex-python[models_sdk]` to install')

class ModelClient(_Client):
    """
    Client for model registry, this class requires the `models_sdk` extras to be installed
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Setup model registry by default
        self._setup_model_client()

    def _setup_model_client(self):
        # Generate a JWT, this call stores the JWT in `_serviceconnector.jwt` ( meh )
        self._serviceconnector._construct_headers({}) # pylint: disable=protected-access

        mlflow.set_tracking_uri(self._serviceconnector.url)
        os.environ['MLFLOW_TRACKING_URI'] = self._serviceconnector.url
        os.environ['MLFLOW_TRACKING_TOKEN'] = self._serviceconnector.token
        #  detect cortex client setting to avoid invalid SSL cert errors
        # os.environ['MLFLOW_TRACKING_TOKEN']='true'
        # os.environ['MLFLOW_TRACKING_CLIENT_CERT_PATH']=
        # Need api to fetch serverside userid..
        # os.environ['MLFLOW_TRACKING_USERNAME']=_Client.???

    def login(self):
        """
        Configure connection settings for model registry.
        This also setup by `Cortex.client()`
        """
        check_installed()
        self._setup_model_client()
        print("Configuring connection for model registry")

    def create_experiment(self,
                          name: str,
                          tags: Optional[Dict[str, Any]] = None,
                          ) -> str:
        """
        Create an MLFlow experiment with default tags
        :param name: experiment name, must be unique
        :param tags: optional experiment tags
        """
        check_installed()
        if tags is None:
            tags = {}
        # default to client project if project tag isn't specified
        if tags.get('project') is None:
            tags['project'] = self._project()
        return mlflow.create_experiment(name, tags=tags)
