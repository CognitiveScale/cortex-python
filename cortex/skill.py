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
import urllib.parse

from .utils import get_logger
from .serviceconnector import _Client
from .camel import CamelResource
from .utils import raise_for_status_with_detail

log = get_logger(__name__)


class SkillClient(_Client):
    """
    A client for the Cortex Skill management API.
    """

    URIs = {
        'skills': 'projects/{projectId}/skills',
        'skill': 'projects/{projectId}/skills/{skillName}',
        'logs': 'projects/{projectId}/skills/{skillName}/action/{actionName}/logs',
        'deploy': 'projects/{projectId}/skills/{skillName}/deploy',
        'undeploy': 'projects/{projectId}/skills/{skillName}/undeploy'

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
