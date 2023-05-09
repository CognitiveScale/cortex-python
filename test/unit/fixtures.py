"""
functions for mocking connection to cortex for testing 
"""

import json

from cortex.utils import generate_token
from datetime import datetime
import calendar


def john_doe_token(mock):
    register_mock_fabric_info(mock)
    return generate_token(mock_pat_config())


def register_mock_fabric_info(mock, base_url=None):
    """_summary_

    :param url: _description_, defaults to None
    :type url: _type_, optional
    """
    url = None
    if base_url is None:
        url = build_mock_url("info")
    else:
        url = f"{base_url}/fabric/v4/info"
    mock.get(url, status_code=200, json=fabric_info_resp())


def fabric_info_resp() -> dict:
    """Mock Fabric info response

    :return: dict with fabric info response
    :rtype: dict
    """
    return {
        "version": "6.4.0-1462-dev",
        "healths": [
            {
                "health": {
                    "redis": {"ok": True, "message": "Connected to redis on db# 0"}
                },
                "version": "6.15.26-g46c7d25-ubi8",
                "name": "accounts",
                "healthy": True,
            },
        ],
        "endpoints": '{ "registry": { "url": "https://private-registry.dci-dev.dev-eks.insights.ai", "description": "Cortex Configured Registry" }, "chartDocs": { "url": "https://cognitivescale.github.io/cortex-charts", "description": "Helm Chart Docs" }, "fabricDocs": { "url": "https://cognitivescale.github.io/cortex-fabric", "description": "Fabric Usage" } }',  # pylint: disable=line-too-long
        # this mess is so we can get a timestamp in utc..
        # because the generate_token method works with utc
        "serverTs": calendar.timegm(datetime.utcnow().utctimetuple())
        * 1000,  # pylint: disable=line-too-long
        "deployType": "ENTERPRISE",
    }


def john_doe_subject():
    """
    The subject part of the jwt token
    """
    return "71a8faac-9dfb-428d-a90c-0b53481b8665"


def build_mock_url(uri, version=4):
    """
    build a mock url for testing
    """
    return "{api_endpoint}/fabric/v{version}/{uri}".format(
        api_endpoint=mock_api_endpoint(), version=version, uri=uri
    )


def mock_api_endpoint():
    """
    the url endpoint for mocking
    """
    return "http://127.0.0.1:8000"


def mock_project():
    """
    the project for mocking
    """
    return "cogscale"


def mock_pat_config():
    """
    Return a PAt config to allow test and create new JWTs
    :return: PAT config
    """
    return {
        "jwk": {
            "crv": "Ed25519",
            "x": "fPxYvREALYwHVpZtCmYxtc2EW6asDTpqyhqgfco6kWQ",
            "d": "B9vmiGHtwG9GuFZNso3JDm5_O9bcUbtQyGgp6VrAfL4",
            "kty": "OKP",
            "kid": "HpW-ya7FSU7yV-alzyewPPDwPeFgrki0VQPKbh4J4Pw",
        },
        "issuer": "cognitivescale.com",
        "audience": "cortex",
        "username": "71a8faac-9dfb-428d-a90c-0b53481b8665",
        "url": mock_api_endpoint()
    }
