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
from typing import Optional, Dict, AnyStr
from .serviceconnector import _Client
from .camel import CamelResource
from .utils import get_logger, raise_for_status_with_detail, parse_string
from .exceptions import SendMessageException

log = get_logger(__name__)


class SkillClient(_Client):
    """
    A client used to interact with skills.
    """

    URIs = {
        "deploy": "projects/{projectId}/skills/{skillName}/deploy",
        "invoke": "projects/{project}/skillinvoke/{skill_name}/inputs/{input}",
        "logs": "projects/{projectId}/skills/{skillName}/action/{actionName}/logs",
        "send_message": "{url}/internal/messages/{activation}/{channel}/{output_name}",
        "skill": "projects/{projectId}/skills/{skillName}",
        "skills": "projects/{projectId}/skills",
        "undeploy": "projects/{projectId}/skills/{skillName}/undeploy",
    }

    def list_skills(self):
        """
        Retrieve List of skills for specified project
        :return: list of skills
        """
        res = self._serviceconnector.request(
            method="GET", uri=self.URIs["skills"].format(projectId=self._project())
        )
        raise_for_status_with_detail(res)
        rs_json = res.json()

        return rs_json.get("skills", [])

    def save_skill(self, skill_obj):
        """
        Create or Update skill
        :param skill_obj: Skill object to save
        :return: response json
        """
        body = json.dumps(skill_obj)
        headers = {"Content-Type": "application/json"}
        uri = self.URIs["skills"].format(projectId=self._project())
        res = self._serviceconnector.request(
            method="POST", uri=uri, body=body, headers=headers
        )
        raise_for_status_with_detail(res)
        return res.json()

    def get_skill(self, skill_name):
        """
        Get a skill by name
        :param skill_name: Skill name
        :return: skill json
        """
        uri = self.URIs["skill"].format(
            projectId=self._project(), skillName=parse_string(skill_name)
        )
        res = self._serviceconnector.request(method="GET", uri=uri)
        raise_for_status_with_detail(res)

        return res.json()

    def delete_skill(self, skill_name):
        """
        Delete a skill by name
        :param skill_name: Skill name
        :return: status
        """
        uri = self.URIs["skill"].format(
            projectId=self._project(), skillName=parse_string(skill_name)
        )
        res = self._serviceconnector.request(method="DELETE", uri=uri)
        raise_for_status_with_detail(res)
        rs_json = res.json()

        return rs_json.get("success", False)

    def get_logs(self, skill_name, action_name):
        """
        Get logs by skill name and action name
        :param skill_name: Skill name
        :param action_name: Action name
        :return: Logs
        """
        uri = self.URIs["logs"].format(
            projectId=self._project(),
            skillName=parse_string(skill_name),
            actionName=parse_string(action_name),
        )
        res = self._serviceconnector.request(method="GET", uri=uri)
        raise_for_status_with_detail(res)

        return res.json()

    def deploy(self, skill_name):
        """
        Deploy a skill
        :param skill_name: Skill name
        :return: status
        """
        uri = self.URIs["deploy"].format(
            projectId=self._project(), skillName=parse_string(skill_name)
        )
        res = self._serviceconnector.request(method="GET", uri=uri)
        raise_for_status_with_detail(res)

        return res.json()

    def undeploy(self, skill_name):
        """
        Undeploy a skill
        :param skill_name: Skill name
        :return: status
        """
        uri = self.URIs["undeploy"].format(
            projectId=self._project(), skillName=parse_string(skill_name)
        )
        res = self._serviceconnector.request(method="GET", uri=uri)
        raise_for_status_with_detail(res)
        return res.json()

    def send_message(
        self, activation: str, channel: str, output_name: str, message: object
    ):
        """
        Send a payload to a specific output, this can be called more than one
        and will replace the stdout/stderr
        as payload for jobs
        :param activation: ActivationId provided in resources
        :param channel: ChannelId provided in the parameters
        :param output_name: Output name provided in the parameters or another
        skill output connected from this skill
        :param message: dict - payload to be sent to the agent
        :return: success or failure message
        """
        uri = self.URIs["send_message"].format(
            url=self._serviceconnector.url,
            activation=activation,
            channel=channel,
            output_name=output_name,
        )
        data = json.dumps(message)
        headers = {"Content-Type": "application/json"}
        res = self._serviceconnector.request(
            method="POST",
            uri=uri,
            body=data,
            headers=headers,
            debug=False,
            is_internal_url=True,
        )
        if res.status_code != 200:
            raise SendMessageException(
                f"Send message failed {res.status_code}: {res.text}"
            )
        return res.json()

    def invoke(
        self,
        skill_name: str,
        input_name: str,
        payload: object,
        properties: object,
        sync: bool = False,
    ) -> dict:
        """Invoke a skill on a specified `input_name` with the specified `payload` and `properties`. Use `sync=True` if you want to access the Skill invocation results without polling.

        :param skill_name: Skill name
        :type skill_name: str
        :param input_name: Input name of the Skill
        :type input_name: str
        :param payload: Skill payload
        :type payload: object
        :param properties: Skill properties
        :type properties: object
        :param sync: Set this to True if you want synchronous skill invokes
        :type sync: bool,
        :return: The activation details of the invocation if `sync=False`, and the full Skill response if `sync=True`
        :rtype: dict
        """  # pylint: disable=line-too-long
        uri = self.URIs["invoke"].format(
            project=self._project(), skill_name=skill_name, input=input_name
        )
        data = json.dumps({"payload": payload, "properties": properties})
        params = {"sync": "true" if sync is True else "false"}
        headers = {"Content-Type": "application/json"}
        res = self._serviceconnector.request("POST", uri, data, headers, params=params)
        raise_for_status_with_detail(res)
        return res.json()

    @property
    def project(self) -> AnyStr:
        """_summary_

        Returns:
            _type_: _description_
        """
        return self._project


class Skill(CamelResource):
    """
    Computational components of an agent; executes an
    atomic unit of work and can be triggered by one or more inputs to produce
    one or more outputs.
    """

    def __init__(self, skill, client: SkillClient):
        super().__init__(skill, True)
        self._client = client
        self._project = client._project


class SkillRequest:
    # pylint: disable=too-few-public-methods
    """
    Skill request: parameters passed in during skill invoke
    """
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


class SkillResponse:
    # pylint: disable=too-few-public-methods
    """
    Skill response: skill output
    """
    outputName: Optional[str] = None
    payload: Dict
