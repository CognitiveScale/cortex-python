
"""
Copyright 2021 Cognitive Scale, Inc. All Rights Reserved.

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

import os
import glob

from requests_toolbelt.multipart.encoder import MultipartEncoder
from requests.exceptions import HTTPError
import tenacity
import time

from .serviceconnector import _Client
from .utils import raise_for_status_with_detail


class ManagedContentClient(_Client):
    """
    A client used to access the Cortex managed content service (blob store).
    """
    URIs = {'content':  'projects/{projectId}/content'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._serviceconnector.version = 4

    def upload(self, *args, **kwargs):
        """Store `stream` file in S3.

        :param key: The path where the file will be stored.
        :param project: The project to upload
        :param stream_name: The name under which to save the `stream`.
        :param stream: The file object.
        :param content_type: the type of the file to store (e.g., `text/csv`).
        :param retries: Number of times to retry a failed request from a retryable response.
        :return: a dict with the response to request upload.

        .. NOTE: This method uses a multi-part form request; to upload very large files, use `uploadStreaming` instead.
        .. seealso: uploadStreaming()
        """
        key = kwargs.get('key')
        project = kwargs.get('project', self._serviceconnector.project)
        stream_name = kwargs.get('stream_name')
        stream = kwargs.get('stream')
        content_type = kwargs.get('content_type')
        retries = kwargs.get('retries', 1)
        if len(args) > 0:
            if len(args) == 6:
                retries = args[5]
                content_type = args[4]
                stream = args[3]
                stream_name = args[2]
                project = args[1]
            if len(args) == 5:  # Assuming no retries
                # (key, 'foo', content, 'application/octet-stream', 5)
                if type(args[4]) == int:
                    retries = args[4]
                    content_type = args[3]
                    stream = args[2]
                    stream_name = args[1]
                else:
                    content_type = args[4]
                    stream = args[3]
                    stream_name = args[2]
                    project = args[1]
            if not key:
                key = args[0]
            if len(args) == 4:
                if not stream:
                    stream = args[2]
                if not stream_name:
                    stream_name = args[1]
                if not content_type:
                    content_type = args[3]

        r = tenacity.Retrying(
                stop = tenacity.stop_after_attempt(retries + 1),
                retry = tenacity.retry_if_exception(ManagedContentClient._http_request_retry_predicate)
                )
        return r.wraps(self._upload)(key, project, stream_name, stream, content_type)

    def _upload(self, key: str, project: str, stream_name: str, stream: object, content_type: str):
        uri = self.URIs['content'].format(projectId=project)
        fields = {'key': key, 'content': (stream_name, stream, content_type)}
        # Still using multi-part ???
        data = MultipartEncoder(fields=fields)
        headers = {'Content-Type': data.content_type}
        r = self._serviceconnector.request('POST', uri, data, headers)
        raise_for_status_with_detail(r)
        return r.json()

    @staticmethod
    def _get_source_files(source):
        source_regex = os.path.join(source, '**/*')
        for path in glob.iglob(source_regex, recursive=True):
            if os.path.isfile(path):
                yield {
                    'canonical': path,
                    'relative': path[len(source):]
                }

    def upload_directory(self, *args, **kwargs):
        """Walk source directory and store in S3

        :param source: The path to the local directory.
        :param destination: Prefix to add to resulting saved directory
        :param project: The project to store the content within.
        :param retries: Number of times to retry a failed request from a retryable response.
        :return: A dict with the response to request upload.
        """
        source = kwargs.get('source')
        destination = kwargs.get('destination')
        project = kwargs.get('project', self._serviceconnector.project)
        retries = kwargs.get('retries', 1)
        if len(args) > 0:
            if len(args) == 4:
                retries = args[3]
            if len(args) == 3:
                project = args[2]
            if len(args) == 2:
                if not source:
                    source = args[0]
                if not destination:
                    destination = args[1]
        source_path = source
        if not source.endswith('/'):
            source_path = source_path + '/'
        generated_paths = ManagedContentClient._get_source_files(source_path)
        responses = []
        for path_dict in generated_paths:
            key = os.path.join(destination, path_dict.get('relative'))
            with open(path_dict.get('canonical'), 'rb') as stream:
                responses.append(self.upload_streaming(key, project, stream, 'application/octet-stream', retries))

        return responses

    def upload_streaming(self, *args, ** kwargs): # key: str, project: str, stream: object, content_type: str, retries: int = 1):
        """Store `stream` file in S3.

        :param key: The path where the file will be stored.
        :param project: The project to store the content within.
        :param stream: The file object.
        :param content_type: The type of the file to store (e.g., `text/csv`)
        :param retries: Number of times to retry a failed request from a retryable response.
        :return: A dict with the response to request upload.
        """
        key = kwargs.get('key')
        project = kwargs.get('project', self._serviceconnector.project)
        stream = kwargs.get('stream')
        content_type = kwargs.get('content_type')
        retries = kwargs.get('retries', 1)
        if len(args) > 0:
            if len(args) == 5:
                retries = args[4]
            if len(args) == 4:
                project = args[1]
            if len(args) == 3:
                if not key:
                    key = args[0]
                if not stream:
                    stream = args[1]
                if not content_type:
                    content_type = args[2]
        r = tenacity.Retrying(
            stop = tenacity.stop_after_attempt(retries + 1),
            retry = tenacity.retry_if_exception(ManagedContentClient._http_request_retry_predicate)
            )
        return r.wraps(self._upload_streaming)(key, project, stream, content_type)

    def _upload_streaming(self, key: str, project: str, stream: object, content_type: str):
        uri = self._make_content_uri(key, project)
        headers = {'Content-Type': content_type}
        r = self._serviceconnector.request('POST', uri, stream, headers)
        raise_for_status_with_detail(r)
        return r.json()

    def download(self, *args, **kwargs):
        """Download a file from managed content (S3).

        :param key: The path of the file to retrieve.
        :param project: The project to which to get file from.
        :param retries: Number of times to retry a failed request from a response.
        :returns: A Generator.
        """
        key = kwargs.get('key')
        project = kwargs.get('project', self._serviceconnector.project)
        retries = kwargs.get('retries', 1)
        if len(args) > 0:
            if len(args) == 3:
                retries = args[2]
            if len(args) == 2:
                project = args[1]
            if not key:
                key = args[0]
        r = tenacity.Retrying(
            stop = tenacity.stop_after_attempt(retries + 1),
            retry = tenacity.retry_if_exception(ManagedContentClient._http_request_retry_predicate)
            )
        return r.wraps(self._download)(key, project)

    def _download(self, key: str, project):
        uri = self._make_content_uri(key, project)
        r = self._serviceconnector.request('GET', uri, stream=True)
        raise_for_status_with_detail(r)
        return r.raw

    def exists(self, *args, **kwargs) -> bool:
        """Check that a file from managed content (S3) exists.

        :param key: The path of the file to check.
        :param project: The project to check.
        :returns: A boolean indicating wether the file exists or not.
        """
        key = kwargs.get('key')
        project = kwargs.get('project', self._serviceconnector.project)
        if len(args) > 0:
            if len(args) == 2:
                project = args[1]
            if not key:
                key = args[0]
        uri = self._make_content_uri(key, project)
        r = self._serviceconnector.request('HEAD', uri)
        return r.status_code == 200

    ## Private ##

    @staticmethod
    def _http_request_retry_predicate(exception: Exception) -> bool:
        if isinstance(exception, HTTPError):
            retry_after = exception.response.headers.get('Retry-After')
            if retry_after:
                ## NOTE: sleep in predicate, ugly, but how to extract this?
                time.sleep(retry_after)
                return True
        return False

    def _make_content_uri(self, key: str, project: str):
        return self.URIs['content'].format(projectId=project) + '/' + key.lstrip('/')
