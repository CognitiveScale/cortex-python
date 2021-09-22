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
import urllib.parse
from typing import Optional, Dict
from .serviceconnector import _Client
from .camel import CamelResource
from .utils import get_logger
from .utils import raise_for_status_with_detail

log = get_logger(__name__)


class SkillClient(_Client):
    """
    A client used to interact with skills.
    """
    URIs = {
        'deploy': 'projects/{projectId}/skills/{skillName}/deploy',
        'invoke': '/fabric/v4/projects/{project}/skillinvoke/{skill_name}/inputs/{input}',
        'logs': 'projects/{projectId}/skills/{skillName}/action/{actionName}/logs',
        'send_message': '{url}/internal/messages/{activation}/{channel}/{output_name}',
        'skill': 'projects/{projectId}/skills/{skillName}',
        'skills': 'projects/{projectId}/skills',
        'undeploy': 'projects/{projectId}/skills/{skillName}/undeploy',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._serviceconnector.version = 4
        if len(args) > 0:
            self._project = args[0]._project
        else:
            self._project = None

    def list_skills(self):
        r = self._serviceconnector.request(method='GET', uri=self.URIs['skills'].format(projectId=self._project))
        raise_for_status_with_detail(r)
        rs = r.json()

        return rs.get('skills', [])

    def save_skill(self, skill_obj):
        body = json.dumps(skill_obj)
        headers = {'Content-Type': 'application/json'}
        uri = self.URIs['skills'].format(projectId=self._project)
        r = self._serviceconnector.request(method='POST', uri=uri, body=body, headers=headers)
        raise_for_status_with_detail(r)
        return r.json()

    def get_skill(self, skill_name):
        uri = self.URIs['skill'].format(projectId=self._project, skillName=self.parse_string(skill_name))
        r = self._serviceconnector.request(method='GET', uri=uri)
        raise_for_status_with_detail(r)

        return r.json()

    def delete_skill(self, skill_name):
        uri = self.URIs['skill'].format(projectId=self._project, skillName=self.parse_string(skill_name))
        r = self._serviceconnector.request(method='DELETE', uri=uri)
        raise_for_status_with_detail(r)
        rs = r.json()

        return rs.get('success', False)

    def get_logs(self, skill_name, action_name):
        uri = self.URIs['logs'].format(projectId=self._project, skillName=self.parse_string(skill_name),
                                       actionName=self.parse_string(action_name))
        r = self._serviceconnector.request(method='GET', uri=uri)
        raise_for_status_with_detail(r)

        return r.json()

    def deploy(self, skill_name):
        uri = self.URIs['deploy'].format(projectId=self._project, skillName=self.parse_string(skill_name))
        r = self._serviceconnector.request(method='GET', uri=uri)
        raise_for_status_with_detail(r)

        return r.json()

    def undeploy(self, skill_name):
        uri = self.URIs['undeploy'].format(projectId=self._project, skillName=self.parse_string(skill_name))
        r = self._serviceconnector.request(method='GET', uri=uri)
        raise_for_status_with_detail(r)
        return r.json()

    def parse_string(self, string):
        # Replaces special characters like / with %2F
        return urllib.parse.quote(string, safe='')

    def send_message(self, activation: str, channel: str, output_name: str, message: object):
        """
        Send a payload to a specific output, this can be called more than one and will replace the stdout/stderr as payload for jobs
        :param activation: ActivationId provided in resources
        :param channel: ChannelId provided in the parameters
        :param output_name: Output name provided in the parameters or another skill output connected from this skill
        :param message: dict - payload to be send to the agent
        :return: success or failure message
        """
        uri = self.URIs['send_message'].format(url=self._serviceconnector.url, activation=activation, channel=channel, output_name=output_name)
        data = json.dumps(message)
        headers = {'Content-Type': 'application/json'}
        r = self._serviceconnector.request(method='POST', uri=uri, body=data, headers=headers, debug=False, is_internal_url=True)
        if r.status_code != 200:
            raise Exception(f'Send message failed {r.status_code}: {r.text}')
        return r.json()


    def invoke(self, project: str, skill_name: str, input: str, payload: object, properties: object):
        """
        """
        uri = self.URIs['invoke'].format(project=project, skill_name=skill_name, input=input)
        data = json.dumps({ payload: payload, properties: properties})
        headers = {'Content-Type': 'application/json'}
        r = self._serviceconnector.request('POST', uri, data, headers)
        raise_for_status_with_detail(r)
        return r.json()

class Skill(CamelResource):
    """
     Computational components of an agent; executes an
     atomic unit of work and can be triggered by one or more inputs to produce
     one or more outputs.
    """
    def __init__(self, skill, project: str, client: SkillClient):
        super().__init__(skill, True)
        self._client = client
        self._project = project

class SkillRequest():
    '''
    Skill request: parameters passed in during skill invoke
    '''
    activationId: str
    agentName: Optional[str] = None
    apiEndpoint: str
    channelId: Optional[str] = None
    outputName: Optional[str] = None
    payload: Dict
    properties: Dict
    sessionId: Optional[str] = None
    skillName: Optional[str] = None
    token: Optional[str] = None

class SkillResponse():
    '''
    Skill response: skill output
    '''
    outputName: Optional[str] = None
    payload: Dict
