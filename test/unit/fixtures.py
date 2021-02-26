'''
functions for mocking connection to cortex for testing 
'''

import json
from cortex.utils import generate_token
from mocket.mockhttp import Entry

def john_doe_token():
    return generate_token(mock_pat_config())

def john_doe_subject():
    '''
    The subject part of the jwt token
    '''
    return '71a8faac-9dfb-428d-a90c-0b53481b8665'


def build_mock_url(uri, version=4):
    '''
    build a mock url for testing
    '''
    return "{api_endpoint}/fabric/v{version}/{uri}".format(api_endpoint=mock_api_endpoint(), version=version, uri=uri)


def mock_api_endpoint():
    '''
    the url endppoint for mocking
    '''
    return 'http://1.2.3.4:8000'


def register_entry(verb, url, body:dict):
    print('Registering mock for', verb, url)
    Entry.single_register(verb, url, status=200, body=json.dumps(body))


def register_entry_from_path(verb, url, path:str):
    with open(path) as fh:
        register_entry(verb, url, json.load(fh))

def mock_pat_config():
    '''
    Return a PAt config to allow test t ocreate new JWTs
    :return: PAT config
    '''
    return {
        "jwk":{
            "crv":"Ed25519",
            "x":"fPxYvREALYwHVpZtCmYxtc2EW6asDTpqyhqgfco6kWQ",
            "d":"B9vmiGHtwG9GuFZNso3JDm5_O9bcUbtQyGgp6VrAfL4",
            "kty":"OKP","kid":"HpW-ya7FSU7yV-alzyewPPDwPeFgrki0VQPKbh4J4Pw"
        },
        "issuer":"cognitivescale.com",
        "audience":"cortex",
        "username":"71a8faac-9dfb-428d-a90c-0b53481b8665",
        "url":"https://192.168.39.27:31326"
    }
