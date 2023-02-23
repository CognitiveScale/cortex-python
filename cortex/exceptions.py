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


class CortexException(Exception):
    """
    Base exception type.
    """


class AuthenticationException(CortexException):
    """
    Cortex authentication exception.
    """


class InvalidMessageTypeException(CortexException):
    """This exception is thrown when the :class:`cortex.message.Message` instance is invalid

    :type Exception: Exception
    """


class IncompleteMessageKeysException(CortexException):
    """This exception is raised when the message passed to a Skill has missing fields

    :type Exception: Exception
    """


class SendMessageException(CortexException):
    """This exception is raised when a message send to Skill doesn't result in a successful HTTP status code"""  # pylint: disable=line-too-long


class BadTokenException(CortexException):
    """
    Cortex token invalid exception.
    """


class ConfigurationException(CortexException):
    """
    Cortex configuration exception.
    """


class APIException(CortexException):
    """
    Cortex API exception.
    """


class ProjectException(CortexException):
    """
    Cortex Project exception.
    """


class VisualisationException(CortexException):
    """Indicates missing dependent packages when using the cortex-python package inside a jupyter notebook"""  # pylint: disable=line-too-long


class UpdateRunException(CortexException):
    """Raised when the :meth:`cortex.experiment.ExperimentClient.update_run` method fails"""


class DeleteRunException(CortexException):
    """Raised when the :meth:`cortex.experiment.ExperimentClient.delete_run` method fails"""


class AuthenticationHeaderError(Exception):
    """This error is raised when a request to the Fabric API results in a 302 redirect status code along with the header `X-Auth-Error` containing additional context about the failure. This usually occurs due to an expired JWT."""  # pylint: disable=line-too-long
