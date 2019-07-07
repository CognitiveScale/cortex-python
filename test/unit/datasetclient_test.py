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

from cortex.dataset import DatasetsClient

import json
import unittest
from mocket.mockhttp import Entry
from mocket import mocketize

from .fixtures import john_doe_token, mock_api_endpoint, build_mock_url, register_entry


class DatasetTestClient(unittest.TestCase):
    """
    Tests for the datasetclient.
    """

    def setUp(self):
        self.ds_client = DatasetsClient(mock_api_endpoint(), 3, john_doe_token())

    @mocketize
    def test_list_datasets(self):
        # mocks
        get_datasets_uri = DatasetsClient.URIs['datasets']
        get_datasets_returns = {'datasets': [{'_environmentId': 'cortex/default',
                                              '_id': '000000000000000000000000',
                                              'connectionQuery': [{'_id': '000000000000000000000000',
                                                                   'value': 'CSV',
                                                                   'name': 'contentType'},
                                                                  {'_id': '000000000000000000000000', 'value': ',', 'name': 'csv/delimiter'},
                                                                  {'_id': '000000000000000000000000',
                                                                   'value': 'true',
                                                                   'name': 'csv/headerRow'},
                                                                  {'_id': '000000000000000000000000',
                                                                   'value': '/cortex/datasets/dataset.csv/000000000000000000000000.csv',
                                                                   'name': 'key'}],
                                              'description': '',
                                              'connectionName': 'cortex/content',
                                              'parameters': [
                                                  {'format': 'int64', 'type': 'integer', 'name': 'value'},
                                                  {'type': 'string', 'name': 'value2'}
                                              ],
                                              'camel': '1.0.0',
                                              'title': 'TestDataset',
                                              'name': 'dataset.csv',
                                              'tags': [],
                                              'connectionWrite': [],
                                              '_tenantId': 'tenant',
                                              'createdAt': '2019-04-19T10:10:10.000',
                                              'updatedAt': '2019-04-19T10:10:10.000Z',
                                              '_version': 1}
                                             ]
                                }
        register_entry(Entry.GET, build_mock_url(get_datasets_uri), get_datasets_returns)
        list_datasets_expected = get_datasets_returns["datasets"]
        list_datasets_got = self.ds_client.list_datasets()
        self.assertEqual(len(list_datasets_got), 1)
        self.assertEqual(json.dumps(list_datasets_got, sort_keys=True),
                         json.dumps(list_datasets_expected, sort_keys=True))
