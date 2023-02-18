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

import os
import glob
import time

from requests_toolbelt.multipart.encoder import MultipartEncoder
from requests.exceptions import HTTPError
import tenacity

from .serviceconnector import _Client
from .utils import raise_for_status_with_detail, get_logger

log = get_logger(__name__)


class ManagedContentClient(_Client):
    """
    A client used to access the Cortex managed content service (blob store).
    """

    URIs = {"content": "projects/{projectId}/content"}

    def upload(
        self,
        key: str,
        stream_name: str,
        stream: object,
        content_type: str,
        retries: int = 1,
    ):
        """Store `stream` file in S3.

        :param key: The path where the file will be stored.
        :param stream_name: The name under which to save the `stream`.
        :param stream: The file object.
        :param content_type: the type of the file to store (e.g., `text/csv`).
        :param retries: Number of times to retry a failed request from a retryable response.
        :return: a dict with the response to request upload.

        .. NOTE: This method uses a multi-part form request; to upload very large files,
        use `uploadStreaming` instead.
        .. seealso: uploadStreaming()
        """
        res = tenacity.Retrying(
            stop=tenacity.stop_after_attempt(retries + 1),
            retry=tenacity.retry_if_exception(
                ManagedContentClient._http_request_retry_predicate
            ),
        )
        return res.wraps(self._upload)(key, stream_name, stream, content_type)

    def _upload(self, key: str, stream_name: str, stream: object, content_type: str):
        uri = self.URIs["content"].format(projectId=self._project())
        fields = {"key": key, "content": (stream_name, stream, content_type)}
        data = MultipartEncoder(fields=fields)
        headers = {"Content-Type": data.content_type}
        res = self._serviceconnector.request(
            "POST", uri=uri, body=data, headers=headers
        )
        raise_for_status_with_detail(res)
        return res.json()

    @staticmethod
    def _get_source_files(source):
        source_regex = os.path.join(source, "**/*")
        for path in glob.iglob(source_regex, recursive=True):
            if os.path.isfile(path):
                yield {"canonical": path, "relative": path[len(source) :]}

    def upload_directory(self, source: str, destination: str, retries: int = 1):
        """Walk source directory and store in S3

        :param source: The path to the local directory.
        :param destination: Prefix to add to resulting saved directory.
        :param retries: Number of times to retry a failed request from a retryable response.
        :return: A dict with the response to request upload.
        """
        source_path = source
        if not source.endswith("/"):
            source_path = source_path + "/"

        generated_paths = ManagedContentClient._get_source_files(source_path)
        responses = []
        for path_dict in generated_paths:
            key = os.path.join(destination, path_dict.get("relative"))
            with open(path_dict.get("canonical"), "rb") as stream:
                responses.append(
                    self.upload_streaming(
                        key, stream, "application/octet-stream", retries
                    )
                )

        return responses

    def upload_streaming(
        self,
        key: str,
        stream: object,
        content_type: str = "application/octet-stream",
        retries: int = 1,
    ):
        """Store `stream` file in S3.

        :param key: The path where the file will be stored.
        :param stream: The file object.
        :param content_type: The type of the file to store (e.g., `text/csv`)
        :param retries: Number of times to retry a failed request from a retryable response.
        :return: A dict with the response to request upload.
        """
        res = tenacity.Retrying(
            stop=tenacity.stop_after_attempt(retries + 1),
            retry=tenacity.retry_if_exception(
                ManagedContentClient._http_request_retry_predicate
            ),
        )
        return res.wraps(self._upload_streaming)(key, stream, content_type)

    def _upload_streaming(self, key: str, stream: object, content_type: str):
        uri = self._make_content_uri(key)
        headers = {"Content-Type": content_type}
        res = self._serviceconnector.request(
            "POST", uri=uri, body=stream, headers=headers
        )
        raise_for_status_with_detail(res)
        return res.json()

    def download(self, key: str, retries: int = 1):
        """Download a file from managed content (S3).

        :param key: The path of the file to retrieve.
        :param retries: Number of times to retry a failed request from a response.
        :returns: A Generator.
        """
        res = tenacity.Retrying(
            stop=tenacity.stop_after_attempt(retries + 1),
            retry=tenacity.retry_if_exception(
                ManagedContentClient._http_request_retry_predicate
            ),
        )
        return res.wraps(self._download)(key)

    def _download(self, key: str):
        uri = self._make_content_uri(key)
        res = self._serviceconnector.request("GET", uri=uri, stream=True)
        raise_for_status_with_detail(res)
        return res.raw

    def exists(self, key: str) -> bool:
        """Check that a file from managed content (S3) exists.

        :param key: The path of the file to check.
        :returns: A boolean indicating wether the file exists or not.
        """
        uri = self._make_content_uri(key)
        res = self._serviceconnector.request("HEAD", uri=uri)
        return res.status_code == 200

    def delete(self, key: str):
        """Delete a file from managed content (S3) .

        :param key: The path of the file to check.
        :returns: A boolean indicating wether the file exists or not.
        """
        uri = self._make_content_uri(key)
        res = self._serviceconnector.request("DELETE", uri=uri)
        raise_for_status_with_detail(res)
        return res.json()

    def list(self, prefix: str = None, limit: int = -1, skip: int = -1):
        """List objects in a project

        :param prefix: The key prefix to filter objects
        :param limit: Limit the number of results returns
        :param skip: Skip number of records
        :returns: List of object keys
        """
        uri = self.URIs["content"].format(projectId=self._project())
        query = {}
        if prefix is not None:
            query["filter"] = prefix
        if limit > 0:
            query["limit"] = limit
        if skip > 0:
            query["skip"] = skip
        res = self._serviceconnector.request("GET", uri=uri, params=query)
        raise_for_status_with_detail(res)
        return res.json()

    ## Private ##

    @staticmethod
    def _http_request_retry_predicate(exception: Exception) -> bool:
        if isinstance(exception, HTTPError):
            retry_after = exception.response.headers.get("Retry-After")
            if retry_after:
                # NOTE: sleep in predicate, ugly, but how to extract this?
                time.sleep(retry_after)
                return True
        return False

    def _make_content_uri(self, key: str):
        return (
            self.URIs["content"].format(projectId=self._project())
            + "/"
            + key.lstrip("/")
        )
