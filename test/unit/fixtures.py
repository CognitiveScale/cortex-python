'''
functions for mocking connection to cortex for testing 
'''


import json

from mocket.mockhttp import Entry

def john_doe_token():
    '''token with user name John Doe, this is a
        slight modification to the default at
        https://jwt.io/ debugger, with this json
        payload:
            {
            "sub": "mliu",
            "tenant": "mliu",
            "name": "John Doe",
            "iat": 1516239022,
            "exp": 12312411251
            }
    '''
    return 'eyJhbGciOiJIUzM4NCIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtbGl1IiwidGVuYW50IjoibWxpdSIsIm5hbWUiOiJKb2huIERvZSIsImlhdCI6MTUxNjIzOTAyMiwiZXhwIjoxMjMxMjQxMTI1MX0.lUathguAHKBxAlrN23ApExCB1b5OLf37EfX1gjI_plsPYYMyE0jHPUguByqrwKxT'

def john_doe_subject():
    '''
    The subject part of the jwt token
    '''
    return 'mliu'


def build_mock_url(uri, version=3):
    '''
    build a mock url for testing
    '''
    return "{api_endpoint}/v{version}/{uri}".format(api_endpoint=mock_api_endpoint(), version=version, uri=uri)


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
