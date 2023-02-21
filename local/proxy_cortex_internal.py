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

from mitmproxy import http
from cortex import Cortex
import json
import re
import os

"""
This script is to intercept HTTP traffic through MITM proxy (https://docs.mitmproxy.org/stable/addons-scripting/)
Install MITM proxy and run with this script as described in `local/README.md`
"""


# This script will intercept internal routes traffic, so this URL won't have a public DNS name.
cortex_endpoint = os.getenv("CORTEX_URL")
if not cortex_endpoint:
    raise Exception("CORTEX_URL environment variable must be set to DCI URL")
else:
    cortex_endpoint = cortex_endpoint.strip("/")

"""
Secret file should be json like:
```json
{
    "secret": "value"
}
```
"""
# Local secrets store json filepath
secrets_env_filepath = os.getenv("SECRETS_PATH")
if not secrets_env_filepath:
    raise Exception(
        "SECRETS_PATH must be set to local JSON filepath with all secrets key: value"
    )
secrets = json.load(open(secrets_env_filepath))


def request(flow: http.HTTPFlow) -> None:
    if "cortex.svc.cluster.local" in flow.request.pretty_url:
        if "/internal" in flow.request.pretty_url:
            if "/connections" in flow.request.pretty_url:
                try:
                    cortex_token = (
                        flow.request.headers.get("Authorization")
                        .split("Bearer")[-1]
                        .strip()
                    )
                    cortex_project = re.search(
                        "/projects/(.*)/connections/", flow.request.pretty_url
                    ).group(1)
                    client = Cortex.client(
                        api_endpoint=cortex_endpoint,
                        project=cortex_project,
                        token=cortex_token,
                    )
                    conn = client.get_connection(
                        flow.request.pretty_url.split("/connections/")[-1]
                    )
                    # resolve secrets
                    missing_secrets = []
                    for param in conn["params"]:
                        if param["value"].startswith("#SECURE"):
                            secret = secrets.get(param["value"].split("#SECURE.")[-1])
                            if secret:
                                param["value"] = secret
                            else:
                                missing_secrets.append(
                                    param["value"].split("#SECURE.")[-1]
                                )

                    # params = dict(map(lambda kv: (kv["name"], kv["value"]), conn['params']))
                    # conn['params'] = params

                    if missing_secrets:
                        flow.response = http.HTTPResponse.make(
                            400,
                            json.dumps(
                                {
                                    "error": f"Secrets {missing_secrets} missing in file {secrets_env_filepath}"
                                }
                            ),
                            {"Content-Type": "application/json"},
                        )
                    else:
                        flow.response = http.HTTPResponse.make(
                            200, json.dumps(conn), {"Content-Type": "application/json"}
                        )
                except Exception as e:
                    flow.response = http.HTTPResponse.make(
                        400,
                        json.dumps({"error": str(e)}),
                        {"Content-Type": "application/json"},
                    )
            elif "/secrets/" in flow.request.pretty_url:
                secret_name = flow.request.pretty_url.split("/secrets/")[-1]
                secret_value = secrets[secret_name]
                if secret_value:
                    flow.response = http.HTTPResponse.make(
                        200,
                        json.dumps({"value": secret_value}),
                        {"Content-Type": "application/json"},
                    )
                else:
                    flow.response = http.HTTPResponse.make(
                        404,
                        json.dumps(
                            {
                                "error": f"{secret_name} not found in file {secrets_env_filepath}"
                            }
                        ),
                        {"Content-Type": "application/json"},
                    )
        else:
            flow.request.url = flow.request.pretty_url.replace(
                "http://cortex-internal.cortex.svc.cluster.local", cortex_endpoint
            )
