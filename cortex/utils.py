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
import base64
import hashlib
import logging
import urllib.parse
from collections import namedtuple
from datetime import datetime, timedelta, timezone
from pathlib import Path

import python_jwt as py_jwt
import jwcrypto.jwk as jwkLib
from requests.exceptions import HTTPError
from requests import request
from .exceptions import BadTokenException, AuthenticationHeaderError


def md5sum(file_name, blocksize=65536):
    """
    Computes md5sum on a fileself.

    :param file_name: The name of the file on which to compute the md5sum.
    :param blocksize: Blocksize used to compute md5 sum (default: 65536)
    :return: Hexdigest of md5sum for file.
    """
    md5 = hashlib.md5()
    with open(file_name, "rb") as filed:
        for block in iter(lambda: filed.read(blocksize), b""):
            md5.update(block)
    return md5.hexdigest()


def is_notebook() -> bool:
    """
    Checks if the shell is in a notebook.

    :return: `True` if the shell is for a notebook, `False` otherwise
    """
    try:
        from IPython import get_ipython  # pylint: disable=import-outside-toplevel

        shell = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell":
            return True  # Jupyter notebook or console
        if shell == "TerminalInteractiveShell":
            return False  # Terminal running IPython
        return False  # Other type (?)
    except (NameError, ImportError):
        return False


def log_message(msg: str, log: logging.Logger, *args, level=logging.INFO, **kwargs):
    """
    Logs a message.

    :param msg: Message to log
    :param log: logger where message should be logged
    :param level: optional log level, defaults to INFO
    :param args: a tuple of arguments passed to the logger
    :param kwargs: a dictionary of keyword arguments passed to the logger
    """
    if is_notebook():
        log.debug(msg, *args, **kwargs)
    else:
        log.log(level, msg, *args, **kwargs)


def b64encode(byts: bytes) -> str:
    """
    Returns a string from an iterable collection of bytes.
    """
    encoded = base64.b64encode(byts)
    return encoded.decode("utf-8")


def b64decode(string: str) -> bytes:
    """
    Returns an iterable collection of bytes representing a base-64 encoding of a given string.
    """
    return base64.decodebytes(string.encode("utf-8"))


def named_dict(obj):
    """
    Returns a named tuple for the given object if it's a dictionary or list;
    otherwise it returns the object itself.
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = named_dict(value)
        return namedtuple("NamedDict", obj.keys())(**obj)
    if isinstance(obj, list):
        return [named_dict(item) for item in obj]
    return obj


def decode_JWT(*args) -> tuple:
    # pylint: disable=invalid-name
    """
    thin wrapper around jwt.decode. This function exists for better error handling of the
    jwt exceptions.
    """
    invalid_token_msg = "Your Cortex Token is invalid: "
    try:
        (_, payload) = decodedJWT = py_jwt.process_jwt(*args)
        # there are places in the sdk where we try to decode 'any ol token' before sending the token
        # to auth to get verified therefore, here we have some reasonable checks to make sure that
        # this is a cortex token by checking the JWT keys exist
        if not payload.get("aud") or not payload.get("sub") or not payload.get("exp"):
            raise BadTokenException(invalid_token_msg)
        return decodedJWT
    except py_jwt._JWTError as err:  # pylint: disable=protected-access
        raise BadTokenException(invalid_token_msg.format(err)) from err


def verify_JWT(token, config=None):
    # pylint: disable=invalid-name
    """
    thin wrapper around jwt.decode. This function exists for better error handling of the
    jwt exceptions.
    """
    try:
        decode_JWT(token)
        return token
    except py_jwt._JWTError:  # pylint: disable=protected-access
        return generate_token(config)


def _get_fabric_info(config: dict):
    uri = config.get("url") + "/fabric/v4/info"
    headers = {"Content-Type": "application/json"}
    return request("GET", uri, headers=headers).json()


def _get_fabric_server_ts(config: dict):
    return _get_fabric_info(config).get("serverTs")


def generate_token(config, validity=2):
    """
    Use the Personal Access Token (JWK) obtained from Cortex's console
    to generate JWTs to access cortex services..
    """
    try:
        server_ts = int(
            _get_fabric_server_ts(config) / 1000
        )  # fabric info returns serverTs in milliseconds
        key = jwkLib.JWK.from_json(json.dumps(config.get("jwk")))
        token_payload = {
            "iss": config.get("issuer"),
            "aud": config.get("audience"),
            "sub": config.get("username"),
            "iat": server_ts / 1000,
        }

        server_ts_dt = datetime.fromtimestamp(server_ts, tz=timezone.utc)

        expiry = server_ts_dt + timedelta(minutes=validity)

        token = py_jwt.generate_jwt(
            claims=token_payload,
            priv_key=key,
            algorithm="EdDSA",
            expires=expiry,
            other_headers={
                "kid": key.thumbprint(),
            },
        )
        return token
    except Exception as err:
        gen_token_msg = (
            "Unable to generate a JWT token, " "check PAT config or cortex profile: {}"
        ).format(err)
        raise BadTokenException(gen_token_msg) from err


def get_cortex_profile(profile_name=None):
    """
    Gets the current cortex profile or the profile that matches the optional given name.
    """

    cortex_config_path = Path.home() / ".cortex" / "config"

    if cortex_config_path.exists():
        with cortex_config_path.open() as filed:
            cortex_config = json.load(filed)

        if profile_name is None:
            profile_name = cortex_config.get("currentProfile")

        return cortex_config.get("profiles", {}).get(profile_name, {})
    return {}


def get_logger(name):
    """
    Gets a logger with the given name.
    """
    log = logging.getLogger(name)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s/%(module)s: %(message)s"
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(logging.INFO)
    return log


def json_str(val):
    """
    Get the string representation of a json object.
    """
    try:
        return json.dumps(val)
    except TypeError:
        return str(val)


def base64decode_jsonstring(base64encoded_jsonstring: str):
    """
    Loads a json from a base64 encoded json string.
    :param base64encoded_jsonstring:
    :return:
    """
    return json.loads(
        base64.urlsafe_b64decode(base64encoded_jsonstring).decode("utf-8")
    )


def raise_for_status_with_detail(resp):
    """
    wrap raise_for_status and attempt give detailed reason for api failure
    re-raise HTTPError for normal flow
    :param resp: python request resp
    :return:
    """
    try:
        resp.raise_for_status()
    except HTTPError as http_exception:
        try:
            log_message(
                msg=resp.text, log=get_logger("http_status"), level=logging.ERROR
            )
        finally:
            raise http_exception
    if resp.status_code == 302:
        raise AuthenticationHeaderError(
            f'Authentication error: {resp.headers.get("X-Auth-Error")}'
        )


def parse_string(string: str):
    """
    parse a given string and apply common encoding/substitution rules
    :param string: the string to parse
    :return:
    """
    # Replaces special characters like / with %2F (URL encoding)
    return urllib.parse.quote(string, safe="")
