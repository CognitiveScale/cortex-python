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
import platform
import sys
from typing import Dict, Any, List, Union, Optional, Type, TypeVar
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .constant import VERSION
from .__version__ import __version__, __title__

from .utils import get_logger, get_cortex_profile, verify_JWT, generate_token
from .utils import raise_for_status_with_detail

log = get_logger(__name__)

JSONType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
T = TypeVar("T", bound="_Client")

userAgent = (
    f"{__title__}/{__version__} ({sys.platform};"
    f"{platform.architecture()[0]}; {platform.release()})"
)


class ServiceConnector:
    """
    Defines the settings and security credentials required to access a service.
    """

    def __init__(
        self, url, version=4, token=None, config=None, verify_ssl_cert=True, project=""
    ):
        self.url = url
        self.version = version
        self.token = token
        self._config = config
        self.verify_ssl_cert = verify_ssl_cert
        self.project = project

    ## properties ##

    @property
    def base_url(self) -> str:
        """_summary_

        :return: _description_
        :rtype: str
        """
        return f"{self.url}/fabric/v{self.version}"

    ## methods ##

    def post_file(self, uri, files, data, headers=None):
        """
        Posts to a service, extending the path with the specified URI.

        :param uri: Path to extend the service URL.
        :param files: Files to send to the service.
        :param data: Data to send as the post body to the service.
        :param headers: HTTP headers for the post.
        """
        headers_to_send = self._construct_headers(headers)
        url = self._construct_url(uri)
        return requests.post(
            url,
            files=files,
            body=data,
            headers=headers_to_send,
            allow_redirects=False,
            verify=self.verify_ssl_cert,
        )

    def request_with_retry(
        self, method, uri, body=None, headers=None, debug=False, retries=2, **kwargs
    ):
        """
        Sends a request to the specified URI. Auto retry with backoff on 50x errors

        :param method: HTTP method to send to the service.
        :param uri: Path to extend service URL.
        :param body: Data to send as the post body to the service.
        :param headers: HTTP headers for this post.
        :param debug: Enable debug True|False (default: False)
        :param retries: defaults to 2
        :param kwargs: Additional key-value pairs to pass to the request method.
        :return: :class:`Response <Response>` object
        """
        headers_to_send = self._construct_headers(headers)
        url = self._construct_url(uri)
        if debug:
            log.debug("START {} {}".format("GET", uri))
        res = ServiceConnector.requests_retry_session(retries=retries).request(
            method,
            url,
            data=body,
            allow_redirects=False,
            headers=headers_to_send,
            verify=self.verify_ssl_cert,
            **kwargs,
        )
        if debug:
            log.debug("  END {} {}".format("GET", uri))
        return res

    def request(
        self,
        method: str,
        uri: str,
        body: object = None,
        headers: object = None,
        debug: bool = False,
        is_internal_url: bool = False,
        **kwargs: dict,
    ):
        """
        Sends a request to the specified URI.

        :param method: HTTP method to send to the service.
        :param uri: Path to extend service URL.
        :param body: Data to send as the post body to the service.
        :param headers: HTTP headers for this post.
        :param debug: Enable debug True|False (default: False)
        :param is_internal_url: Url is internal fabric URL (default: false)
        :param kwargs: Additional key-value pairs to pass to the request method.
        :return: :class:`Response <Response>` object
        """
        headers_to_send = self._construct_headers(headers)
        url = uri if is_internal_url else self._construct_url(uri)
        if debug:
            log.debug("START {} {}".format(method, uri))
        res = requests.request(
            method,
            url,
            data=body,
            allow_redirects=False,
            headers=headers_to_send,
            verify=self.verify_ssl_cert,
            **kwargs,
        )
        if debug:
            log.debug("  END {} {}".format(method, uri))
        return res

    @staticmethod
    def requests_retry_session(
        retries=5,
        backoff_factor=0.5,
        status_forcelist=(500, 502, 503, 504),
        session=None,
    ):
        """_summary_

        :param retries: _description_, defaults to 5
        :type retries: int, optional
        :param backoff_factor: _description_, defaults to 0.5
        :type backoff_factor: float, optional
        :param status_forcelist: _description_, defaults to (500, 502, 503, 504)
        :type status_forcelist: tuple, optional
        :param session: _description_, defaults to None
        :type session: _type_, optional
        :return: _description_
        :rtype: _type_
        """
        session = session or requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    @staticmethod
    def urljoin(pieces):
        """
        Joins together the pieces of a URL.

        :parma pieces: Strings representing the pieces of a URL.
        :return: A string representing the joined pieces of the URL.
        """
        pieces = [_f for _f in [s.rstrip("/") for s in pieces] if _f]
        return "/".join(pieces)

    ## private ##

    def _construct_url(self, uri):
        return self.urljoin([self.base_url, uri])

    def _construct_headers(self, headers):
        headers_to_send = {"User-Agent": userAgent}

        if hasattr(self, "token") and self.token:
            self.token = verify_JWT(self.token, self._config)
            auth = "Bearer {}".format(self.token)
            headers_to_send["Authorization"] = auth
        else:
            self.token = generate_token(self._config)
            auth = "Bearer {}".format(self.token)
            headers_to_send["Authorization"] = auth

        if headers is not None:
            headers_to_send.update(headers)
        return headers_to_send


class _Client:
    """
    An internal client for accessing the Fabric API
    """

    URIs = {}

    def __init__(self, *args, **kwargs):
        # See kubernetes client for better handling of this ..
        # patch_namespaced_custom_object_with_http_info()  using locals() and
        # checks..
        url = kwargs.get("url")
        version = kwargs.get("version", VERSION)
        token = kwargs.get("token")
        config = kwargs.get("config")
        verify_ssl_cert = kwargs.get("verify_ssl_cert")
        project = kwargs.get("project")
        # If all kwargs or first arg is a string create a Connector
        if len(args) == 0 or (len(args) > 0 and isinstance(args[0], str)):
            if len(args) > 0:
                url = args[0]
            if len(args) > 1:
                version = args[1]
            if len(args) > 2:
                token = args[2]
            if len(args) > 3:
                config = args[3]
            if len(args) > 4:
                verify_ssl_cert = args[4]
            self._serviceconnector = ServiceConnector(
                url=url,
                version=version,
                token=token,
                config=config,
                verify_ssl_cert=verify_ssl_cert,
                project=project,
            )
        # if first arg not string assume Client object was passed
        else:
            self._serviceconnector = args[0].to_connector()
            if project:
                self._serviceconnector.project = project
            self._serviceconnector.version = version

    def _post_json(self, uri, obj: JSONType):
        # pylint: disable=no-member
        body_s = json.dumps(obj)
        headers = {"Content-Type": "application/json"}
        res = self._serviceconnector.request("POST", uri, body_s, headers)
        if res.status_code not in [requests.codes.ok, requests.codes.created]:
            log.info("Status: {}, Message: {}".format(res.status_code, res.text))
        raise_for_status_with_detail(res)
        return res.json()

    def _post_json_with_retry(self, uri, obj: JSONType):
        # pylint: disable=no-member
        body_s = json.dumps(obj)
        headers = {"Content-Type": "application/json"}
        res = self._serviceconnector.request_with_retry("POST", uri, body_s, headers)
        if res.status_code not in [requests.codes.ok, requests.codes.created]:
            log.info("Status: {}, Message: {}".format(res.status_code, res.text))
        raise_for_status_with_detail(res)
        return res.json()

    def _get(self, uri, debug=False, **kwargs):
        return self._serviceconnector.request("GET", uri, debug=debug, **kwargs)

    def _delete(self, uri, debug=False):
        res = self._serviceconnector.request("DELETE", uri, debug=debug)
        return res

    def _project(self):
        return self._serviceconnector.project

    def _get_json(self, uri, debug=False) -> Optional[dict]:
        # pylint: disable=no-member
        res = self._serviceconnector.request("GET", uri=uri, debug=debug)
        # If the resource is not found, return None ...
        if res.status_code == requests.codes.not_found:
            return None
        raise_for_status_with_detail(res)
        return res.json()

    def _request_json(self, uri, method="GET"):
        res = self._serviceconnector.request(method, uri=uri)
        raise_for_status_with_detail(res)
        return res.json()

    @classmethod
    def from_current_cli_profile(cls: Type[T], version: str = "3", **kwargs) -> T:
        """_summary_

        :param cls: _description_
        :type cls: Type[T]
        :param version: _description_, defaults to "3"
        :type version: str, optional
        :return: _description_
        :rtype: T
        """
        cli_cfg = get_cortex_profile()
        url, token = cli_cfg["url"], cli_cfg["token"]
        # type: ignore # ignore until mypy properyly supports attr ...
        return cls(url, version, token, **kwargs)

    @classmethod
    def from_cortex_message(cls, message, version: str = "3", **kwargs):
        """_summary_

        :param message: _description_
        :type message: _type_
        :param version: _description_, defaults to "3"
        :type version: str, optional
        :return: _description_
        :rtype: _type_
        """
        return cls(message["apiEndpoint"], version, message["token"], **kwargs)
