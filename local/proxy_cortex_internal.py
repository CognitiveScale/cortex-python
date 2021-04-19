from mitmproxy import http
from cortex import Cortex
import json
import re
import os


# This script will intercept internal routes traffic, so this URL won't have public DNS name.
cortex_endpoint = os.getenv("CORTEX_URL")
if not cortex_endpoint:
    raise Exception("CORTEX_URL environment variable must be set to DCI URL")
else:
    cortex_endpoint = cortex_endpoint.strip("/")

'''
Secret file should be json like:
{
    "secret": "value"
}
'''
# Local secrets store json filepath
secrets_env_filepath = os.getenv("SECRETS_PATH")
if not secrets_env_filepath:
    raise Exception("SECRETS_PATH must be set to local JSON filepath with all secrets key: value")
secrets = json.load(open(secrets_env_filepath))


def request(flow: http.HTTPFlow) -> None:
    if 'cortex.svc.cluster.local' in flow.request.pretty_url:
        if '/internal' in flow.request.pretty_url:
            if '/connections' in flow.request.pretty_url:
                try:
                    cortex_token = flow.request.headers.get('Authorization').split("Bearer")[-1].strip()
                    cortex_project = re.search('/projects/(.*)/connections/', flow.request.pretty_url).group(1)
                    client = Cortex.client(api_endpoint=cortex_endpoint, project=cortex_project, token=cortex_token)
                    conn = client.get_connection(flow.request.pretty_url.split('/connections/')[-1])
                    # resolve secrets
                    missing_secrets = []
                    for param in conn['params']:
                        if param["value"].startswith("#SECURE"):
                            secret = secrets.get(param["value"].split("#SECURE.")[-1])
                            if secret:
                                param["value"] = secret
                            else:
                                missing_secrets.append(param["value"].split("#SECURE.")[-1])

                    params = dict(map(lambda kv: (kv["name"], kv["value"]), conn['params']))
                    conn['params'] = params

                    if missing_secrets:
                        flow.response = http.HTTPResponse.make(
                            400,
                            json.dumps({"error": f"Secrets {missing_secrets} missing in file {secrets_env_filepath}"}),
                            {"Content-Type": "application/json"}
                        )
                    else:
                        flow.response = http.HTTPResponse.make(
                            200,
                            json.dumps(conn),
                            {"Content-Type": "application/json"}
                        )
                except Exception as e:
                    flow.response = http.HTTPResponse.make(
                        400,
                        json.dumps({"error": str(e)}),
                        {"Content-Type": "application/json"}
                    )
        else:
            flow.request.pretty_url = flow.request.pretty_url.replace('http://cortex-internal.cortex.svc.cluster.local',
                                                                      cortex_endpoint)
