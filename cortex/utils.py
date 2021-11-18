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

import json
import base64
import hashlib
import logging
import python_jwt as py_jwt, jwcrypto.jwk as jwkLib
from requests.exceptions import HTTPError
from pathlib import Path
import datetime
from collections import namedtuple
from .exceptions import BadTokenException


def md5sum(file_name, blocksize=65536):
    """
    Computes md5sum on a fileself.

    :param file_name: The name of the file on which to compute the md5sum.
    :param blocksize: Blocksize used to compute md5 sum (default: 65536)
    :return: Hexdigest of md5sum for file.
    """
    md5 = hashlib.md5()
    with open(file_name, "rb") as f:
        for block in iter(lambda: f.read(blocksize), b""):
            md5.update(block)
    return md5.hexdigest()


def is_notebook() -> bool:
    """
    Checks if the shell is in a notebook.

    :return: `True` if the shell is for a notebook, `False` otherwise
    """
    try:
        from IPython import get_ipython
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True  # Jupyter notebook or console
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except (NameError, ImportError):
        return False


def log_message(msg: str, log: logging.Logger, level=logging.INFO, *args, **kwargs):
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


def b64encode(b: bytes) -> str:
    """
    Returns a string from an iterable collection of bytes.
    """
    encoded = base64.b64encode(b)
    return encoded.decode('utf-8')


def b64decode(s: str) -> bytes:
    """
    Returns an iterable collection of bytes representing a base-64 encoding of a given string.
    """
    return base64.decodebytes(s.encode('utf-8'))


def named_dict(obj):
    """
    Returns a named tuple for the given object if it's a dictionary or list;
    otherwise it returns the object itself.
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = named_dict(value)
        return namedtuple('NamedDict', obj.keys())(**obj)
    elif isinstance(obj, list):
        return [named_dict(item) for item in obj]
    else:
        return obj


def decode_JWT(*args):
    """
    thin wrapper around jwt.decode. This function exists for better error handling of the
    jwt exceptions.
    """
    invalidTokenMsg = 'Your Cortex Token is invalid: '
    try:
        (header, payload) = decodedJWT = py_jwt.process_jwt(*args)
        # there are places in the sdk where we try to decode 'any ol token' before sending the token to kong to get verified
        # therefore, here we have some reasonable checks to make sure that this is a cortex token by checking the JWT keys exist
        if not payload.get('aud') or not payload.get('sub') or not payload.get('exp'):
            raise BadTokenException(invalidTokenMsg)
        return decodedJWT
    except py_jwt._JWTError as err:
        raise BadTokenException(invalidTokenMsg.format(err))


def verify_JWT(token, config = None):
    """
    thin wrapper around jwt.decode. This function exists for better error handling of the
    jwt exceptions.
    """
    try:
        decode_JWT(token)
        return token
    except py_jwt._JWTError:
        return generate_token(config)


def generate_token(config, validity=2):
    """
    Use the Personal Access Token (JWK) obtained from Cortex's console to generate JWTs to access cortex services..
    """
    try:
        key = jwkLib.JWK.from_json(json.dumps(config.get('jwk')))
        token_payload = {
            "iss": config.get('issuer'),
            "aud": config.get('audience'),
            "sub": config.get('username'),
        }
        token = py_jwt.generate_jwt(claims=token_payload,
                                    priv_key=key,
                                    algorithm='EdDSA',
                                    lifetime=datetime.timedelta(minutes=validity),
                                    other_headers={"kid": key.thumbprint()})
        return token
    except Exception as err:
        genTokenmsg = "Unable to generate a JWT token, check PAT config or cortex profile:".format(err)
        raise BadTokenException(genTokenmsg)


def get_cortex_profile(profile_name=None):
    """
    Gets the current cortex profile or the profile that matches the optionaly given name.
    """

    cortex_config_path = Path.home() / '.cortex/config'

    if cortex_config_path.exists():
        with cortex_config_path.open() as f:
            cortex_config = json.load(f)

        if profile_name is None:
            profile_name = cortex_config.get('currentProfile')

        return cortex_config.get('profiles', {}).get(profile_name, {})
    return {}


def get_logger(name):
    """
    Gets a logger with the given name.
    """
    log = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s/%(module)s: %(message)s')
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
    return json.loads(base64.urlsafe_b64decode(base64encoded_jsonstring).decode('utf-8'))


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
            log_message(msg=resp.text, log=get_logger('http_status'), level=logging.ERROR)
        except Exception as e:
            pass  # resp.json() failed
        finally:
            raise http_exception
    if resp.status_code == 302:
        raise Exception(f'Authentication error: {resp.headers.get("X-Auth-Error")}')