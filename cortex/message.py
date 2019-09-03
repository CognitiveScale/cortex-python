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

from typing import Dict

from .utils import get_logger
from .camel import Document
from .env import CortexEnv

log = get_logger(__name__)


class Message(Document):
    """
    Wraps a set of parameters or a payload when invoking an action, skill, or agent.

    params:
    instanceId: The ID of the agent instance that produced the message.
    typeName: The resource name of the type/schema contained in the payload of this message.
    token: The JWT token to be used for making authenticated requests to APIs needed to process this message.
    sessionId: The ID of the session associated with this message
    channelId: The ID of the channel (wire) this message was sent on
    apiEndpoint: The URI of the API server to use when making requests to platform services in processing of this message.
    properties: An object whose keys represent metadata properties set for the message.
    payload: The body of the message in one of three supported payload formats (see the CAMEL spec for details).
    """

    def __init__(self, params:Dict = None):
        if params is None:
            params = {}

        super().__init__(params, False)
        self._params = params

    def to_params(self) -> Dict:
        """
        Gets the parameters in the message.
        """
        return self._params

    def __setattr__(self, key, value):
        super().__setattr__(key, value)

        if not key.startswith('_'):
            self._params[key] = value

    def as_pandas(self, client=None):
        """
        Returns the message's payload as a pandas dataframe
        """
        if not hasattr(self, 'payload') or self.payload is None:
            raise AttributeError('Message is missing payload attribute')

        columns = []
        values = []

        ds_ref = self.payload.get('$ref')
        if ds_ref:
            if client is None:
                from .client import Cortex
                client = Cortex.from_message(self)

            ds = client.dataset(ds_ref)
            df = ds.get_dataframe()
            columns = df.get('columns')
            values = df.get('values')

        elif 'records' in self.payload:
            records = self.payload.get('records')
            if len(records) > 0:
                columns = records[0].keys()
                for obj in records:
                    values.append([obj[key] for key in columns])

        else:
            values = self.payload.get('values')
            if not values:
                raise ValueError('Invalid DataFrame: values missing from payload')

            columns = self.payload.get('columns')
            if not columns:
                raise ValueError('Invalid DataFrame: columns missing from payload')

        try:
            import pandas as pd
            return pd.DataFrame(values, columns=columns)
        except ImportError:
            log.warn('Pandas is not installed, please run `pip install pandas` or equivalent in your environment')
            return {'columns': columns, 'values': values}

    def get_dataset(self):
        """
        Returns the message's payload as a dataset.
        """
        if not hasattr(self, 'payload') or self.payload is None:
            raise AttributeError('Message is missing payload attribute')

        ds_ref = self.payload.get('$ref')
        if ds_ref:
            from .client import Cortex
            client = Cortex.from_message(self)
            return client.dataset(ds_ref)

        raise AttributeError('Message payload does not contain a dataset reference')

    @staticmethod
    def from_env(**kwargs):
        env = CortexEnv(**kwargs)

        params = {}
        if env.api_endpoint:
            params['apiEndpoint'] = env.api_endpoint
        if env.token:
            params['token'] = env.token

        return Message(params)
