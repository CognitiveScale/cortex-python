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

import json
import pkg_resources
import platform
import requests
import sys
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Dict, Any, List, Union, Optional, Type, TypeVar
from .utils import get_logger, get_cortex_profile
from .utils import raise_for_status_with_detail
log = get_logger(__name__)

JSONType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
T = TypeVar('T', bound="_Client")

userAgent = f'cortex-python/{pkg_resources.get_distribution("cortex-python").version} ({sys.platform}; {platform.architecture()[0]}; {platform.release()})'

class ServiceConnector:
    """
    Defines the settings and security credentials required to access a service.
    """
    def __init__(self, url, version=3, token=None, verify_ssl_cert=True):
        self.url = url
        self.version = version
        self.token = token
        self.verify_ssl_cert = verify_ssl_cert

    ## properties ##

    @property
    def base_url(self):
        return u'{0}/v{1}'.format(self.url, self.version)

    ## methods ##

    def post_file(self, uri, files, data, headers=None):
        """
        Posts to a service, extending the path with the specified URI.

        :param uri: Path to extend the service URL.
        :param files: Files to send to the service.
        :param data: Data to send as the post body to the service.
        :param headers: HTTP headers for the post.
        """
        headersToSend = self._construct_headers(headers)
        url = self._construct_url(uri)
        return requests.post(url, files=files, data=data, headers=headersToSend,
                             verify=self.verify_ssl_cert)

    def request_with_retry(self, method, uri, body=None, headers=None, debug=False, **kwargs):
        """
        Sends a request to the specified URI. Auto retry with backoff on 50x errors

        :param method: HTTP method to send to the service.
        :param uri: Path to extend service URL.
        :param data: Data to send as the post body to the service.
        :param headers: HTTP headers for this post.
        :param kwargs: Additional key-value pairs to pass to the request method.
        :return: :class:`Response <Response>` object
        """
        headersToSend = self._construct_headers(headers)
        url = self._construct_url(uri)
        if debug:
            log.debug("START {} {}".format('GET', uri))
        r = ServiceConnector.requests_retry_session().request(
            method,
            url,
            data=body,
            headers=headersToSend,
            verify=self.verify_ssl_cert,
            **kwargs
        )
        if debug:
            log.debug("  END {} {}".format('GET', uri))
        return r

    def request(self, method, uri, body=None, headers=None, debug=False, **kwargs):
        """
        Sends a request to the specified URI.

        :param method: HTTP method to send to the service.
        :param uri: Path to extend service URL.
        :param data: Data to send as the post body to the service.
        :param headers: HTTP headers for this post.
        :param kwargs: Additional key-value pairs to pass to the request method.
        :return: :class:`Response <Response>` object
        """
        headersToSend = self._construct_headers(headers)
        url = self._construct_url(uri)
        if debug:
            log.debug("START {} {}".format('GET', uri))
        r = requests.request(
            method,
            url,
            data=body,
            headers=headersToSend,
            verify=self.verify_ssl_cert,
            **kwargs
        )
        if debug:
            log.debug("  END {} {}".format('GET', uri))
        return r

    @staticmethod
    def requests_retry_session(
            retries=5,
            backoff_factor=0.5,
            status_forcelist=(500, 502, 503, 504),
            session=None,
    ):
        session = session or requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    @staticmethod
    def urljoin(pieces):
        """
        Joins together the pieces of a URL.

        :parma pieces: Strings representing the pieces of a URL.
        :return: A string representing the joined pieces of the URL.
        """
        pieces = [_f for _f in [s.rstrip('/') for s in pieces] if _f]
        return '/'.join(pieces)

    ## private ##

    def _construct_url(self, uri):
        return self.urljoin([self.base_url, uri])

    def _construct_headers(self, headers):
        headersToSend = { 'User-Agent': userAgent }

        if self.token:
            auth = 'Bearer {}'.format(self.token)
            headersToSend[u'Authorization'] = auth

        if headers is not None:
            headersToSend.update(headers)
        return headersToSend


class _Client:
    """
    A client.
    """

    # type: Dict[str, str]
    URIs = {}

    def __init__(self,  *args, **kwargs):
        url = kwargs.get("url")
        version = kwargs.get("version")
        token = kwargs.get("token")
        verify_ssl_cert = kwargs.get("verify_ssl_cert")
        # If all kwargs or first arg is a string create a Connector
        if len(args) == 0 or (len(args) > 0 and type(args[0]) == str):
            if len(args) > 0:
                url = args[0]
            if len(args) > 1:
                version = args[1]
            if len(args) > 2:
                token = args[2]
            if len(args) > 3:
                verify_ssl_cert = args[3]
            self._serviceconnector = ServiceConnector(url, version, token, verify_ssl_cert)
        # if first arg not string assume Client object was passed
        else:
            self._serviceconnector = args[0].to_connector()
            self._serviceconnector.version = version

    def _post_json(self, uri, obj: JSONType):
        body_s = json.dumps(obj)
        headers = {'Content-Type': 'application/json'}
        r = self._serviceconnector.request('POST', uri, body_s, headers)
        if r.status_code not in [requests.codes.ok, requests.codes.created]:
            log.info("Status: {}, Message: {}".format(r.status_code, r.text))
        raise_for_status_with_detail(r)
        return r.json()

    def _post_json_with_retry(self, uri, obj: JSONType):
        body_s = json.dumps(obj)
        headers = {'Content-Type': 'application/json'}
        r = self._serviceconnector.request_with_retry('POST', uri, body_s, headers)
        if r.status_code not in [requests.codes.ok, requests.codes.created]:
            log.info("Status: {}, Message: {}".format(r.status_code, r.text))
        raise_for_status_with_detail(r)
        return r.json()

    def _get(self, uri, debug=False, **kwargs):
        return self._serviceconnector.request('GET', uri, debug=debug, **kwargs)

    def _delete(self, uri, debug=False):
        r = self._serviceconnector.request('DELETE', uri, debug=debug)
        return r

    def _get_json(self, uri, debug=False) -> Optional[dict]:
        r = self._serviceconnector.request('GET', uri, debug=debug)
        # If the resource is not found, return None ...
        if r.status_code == requests.codes.not_found:
            return None
        raise_for_status_with_detail(r)
        return r.json()

    def _request_json(self, uri, method='GET'):
        r = self._serviceconnector.request(method, uri)
        raise_for_status_with_detail(r)
        return r.json()

    @classmethod
    def from_current_cli_profile(cls: Type[T], version: str = '3', **kwargs) -> T:
        cli_cfg = get_cortex_profile()
        url, token = cli_cfg["url"], cli_cfg["token"]
        return cls(url, version, token, **kwargs)   # type: ignore # ignore until mypy properyly supports attr ...

    @classmethod
    def from_cortex_message(cls, message, version:str="3", **kwargs):
        return cls(message["apiEndpoint"], version, message["token"], **kwargs)