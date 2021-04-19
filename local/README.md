### Setup proxy with script to intercept internal API calls

Follow [this](https://docs.mitmproxy.org/stable/overview-installation/#installation-from-the-python-package-index-pypi) to install mitmproxy using pipx to be able to run scripts with cortex-python library

Run mitmproxy with our [python script](proxy_cortex_internal.py) 

Create a file `secrets.json` for substituting secrets locally. The file will have all the secrets used in the cortex project. Example:
```json
{
  "secret1": "value1"
}
```

```bash
export CORTEX_URL=<DCI URL>
export SECRETS_PATH=<HSON File path with secrets>
mitmproxy -s proxy_cortex_internal.py
```

Configure proxy in python library (and cURL)
```bash
export HTTP_PROXY=localhost:8080
curl ...
OR
python ...
```
