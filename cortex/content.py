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

import os
import glob
import time
from io import BytesIO, StringIO, FileIO
from typing import Union, List
from urllib3.response import HTTPResponse


from requests_toolbelt.multipart.encoder import MultipartEncoder
from requests.exceptions import HTTPError

from .serviceconnector import _Client
from .utils import (
    raise_for_status_with_detail,
    get_logger,
)

log = get_logger(__name__)


class ManagedContentClient(_Client):
    """
    A client used to access the `Cortex managed content service (blob store) <https://cognitivescale.github.io/cortex-fabric/docs/manage-data/managed-content>`_. You can find a pre-created instance of this class on every :py:class:`cortex.client.Client` instance via the :py:attr:`Client.content` attribute.

    >>> from cortex.client import Cortex; client = Cortex.client();
    >>> client.content.list() # list content from the default project configured for the user

    """  # pylint: disable=line-too-long

    URIs = {"content": "projects/{projectId}/content"}

    def upload(
        self,
        key: str,
        stream_name: str,
        stream: Union[BytesIO, StringIO, FileIO],
        content_type: str,
        retries: int = 1,
    ) -> dict:
        """Store `stream` file in Managed Content (S3).

        :param key: The path where the file will be stored in managed content
        :type key: str
        :param stream_name:  The name under which to save the `stream`.
        :type stream_name: str
        :param stream: The file object.
        :type stream: Union[BytesIO, StringIO, FileIO]
        :param content_type: the type of the file to store (e.g., `text/csv`).
        :type content_type: str
        :param retries: Number of times to retry a failed request from a retryable response, defaults to 1
        :type retries: int, optional
        :return: a dict with the response to request upload.
        :rtype: dict

        .. NOTE: This method uses a multi-part form request; to upload very large files, use `uploadStreaming` instead.
        .. seealso: uploadStreaming()
        """  # pylint: disable=line-too-long
        return self._upload(key, stream_name, stream, content_type, retries)

    def _upload(
        self,
        key: str,
        stream_name: str,
        stream: object,
        content_type: str,
        retries: int = 1,
    ):
        uri = self.URIs["content"].format(projectId=self._project())
        fields = {"key": key, "content": (stream_name, stream, content_type)}
        data = MultipartEncoder(fields=fields)
        headers = {"Content-Type": data.content_type}
        res = self._serviceconnector.request_with_retry(
            "POST", uri=uri, body=data, headers=headers, retries=retries
        )
        raise_for_status_with_detail(res)
        return res.json()

    @staticmethod
    def _get_source_files(source):
        source_regex = os.path.join(source, "**/*")
        for path in glob.iglob(source_regex, recursive=True):
            if os.path.isfile(path):
                yield {"canonical": path, "relative": path[len(source) :]}

    def upload_directory(self, source: str, destination: str, retries: int = 1) -> dict:
        """Walk source directory and store in Managed Content

        :param source: The path to the local directory.
        :type source: str
        :param destination: Prefix to add to resulting saved directory.
        :type destination: str
        :param retries: Number of times to retry a failed request from a retryable response, defaults to 1
        :type retries: int, optional
        :return: A dict with the response to request upload.
        :rtype: dict
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
    ) -> dict:
        """Store `stream` file in Managed Content. Use this method to upload large files to Managed Content

        :param key: The path where the file will be stored.
        :type key: str
        :param stream: The file object.
        :type stream: object
        :param content_type: The type of the file to store (e.g., `text/csv`), defaults to "application/octet-stream"
        :type content_type: str, optional
        :param retries: Number of times to retry a failed request from a retryable response., defaults to 1
        :type retries: int, optional
        :return: A dict with the response to request upload.
        :rtype: dict
        """  # pylint: disable=line-too-long
        return self._upload_streaming(key, stream, content_type, retries)

    def _upload_streaming(
        self, key: str, stream: object, content_type: str, retries: int = 1
    ):
        uri = self._make_content_uri(key)
        headers = {"Content-Type": content_type}
        res = self._serviceconnector.request_with_retry(
            "POST", uri=uri, body=stream, headers=headers, retries=retries
        )
        raise_for_status_with_detail(res)
        return res.json()

    def download(self, key: str, retries: int = 1) -> HTTPResponse:
        """Download a file from managed content (S3 like blob store).

        :param key: The path of the file to retrieve.
        :type key: str
        :param retries: Number of times to retry a failed request from a response., defaults to 1
        :type retries: int, optional
        :return: A HTTPResponse object
        :rtype: :py:class:`urllib3.response.HTTPResponse`
        """
        return self._download(key, retries)

    def _download(self, key: str, retries: int = 1):
        uri = self._make_content_uri(key)
        res = self._serviceconnector.request_with_retry(
            "GET", uri=uri, stream=True, retries=retries
        )
        raise_for_status_with_detail(res)
        return res.raw

    def exists(self, key: str) -> bool:
        """Check that a file from managed content (S3) exists.

        :param key: The path of the file to check.
        :type key: str
        :return: A boolean indicating whether the file exists or not.
        :rtype: bool
        """
        uri = self._make_content_uri(key)
        res = self._serviceconnector.request("HEAD", uri=uri)
        return res.status_code == 200

    def delete(self, key: str) -> dict:
        """Delete a file from managed content (S3)

        :param key: The path of the file to delete
        :type key: str
        :return: A boolean indicating whether the file exists or not.
        :rtype: dict
        """
        uri = self._make_content_uri(key)
        res = self._serviceconnector.request_with_retry("DELETE", uri=uri, retries=1)
        raise_for_status_with_detail(res)
        return res.json()

    def list(self, prefix: str = None, limit: int = -1, skip: int = -1) -> List[dict]:
        """List objects in a project's managed content store

        :param prefix:  The key prefix to filter objects with, defaults to None
        :type prefix: str, optional
        :param limit: Limit the number of results returned, defaults to -1
        :type limit: int, optional
        :param skip: Skip number of records. Use along with limit to paginate results, defaults to -1
        :type skip: int, optional
        :return: List of dictionaries with each dictionary holding metadata about individual files in the project's managed content store
        :rtype: List[dict]
        """  # pylint: disable=line-too-long
        uri = self.URIs["content"].format(projectId=self._project())
        query = {}
        if prefix is not None:
            query["filter"] = prefix
        if limit > 0:
            query["limit"] = limit
        if skip > 0:
            query["skip"] = skip
        res = self._serviceconnector.request_with_retry(
            "GET", uri=uri, params=query, retries=1
        )
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
