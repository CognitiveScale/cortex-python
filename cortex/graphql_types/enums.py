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
from enum import Enum


class AttributeDataType(str, Enum):
    """
    The `AttributeDataType` class is a subclass of the `str` class, and is an
    enumeration of the possible data types for an attribute
    """

    BOOLEAN = "BOOLEAN"
    DOUBLE = "DOUBLE"
    INTEGER = "INTEGER"
    LONG = "LONG"
    STRING = "STRING"


class CampaignLifecycleState(str, Enum):
    """`CampaignLifecycleState` is a string enum that
    represents the possible states of a campaign"""  # pylint: disable=line-too-long

    DEPLOYED = "DEPLOYED"
    IN_PROGRESS = "IN_PROGRESS"


class ConnectionType(str, Enum):
    """`ConnectionType` is a subclass of `str` that can only
    be one of the values in the `Enum` class"""  # pylint: disable=line-too-long

    FILE = "file"
    GCS = "gcs"
    GCSFILESTREAM = "gcsFileStream"
    HIVE = "hive"
    JDBC = "jdbc"
    JDBC_CDATA = "jdbc_cdata"
    JDBC_GENERIC = "jdbc_generic"
    MONGO = "mongo"
    S3 = "s3"
    S3FILESTREAM = "s3FileStream"


class ContentType(str, Enum):
    """`ContentType` is a subclass of `str` that can only
    be one of the values in the `Enum` class"""  # pylint: disable=line-too-long

    CSV = "csv"
    JSON = "json"
    PARQUET = "parquet"


class ExplorationType(str, Enum):
    """`ExplorationType` is a class that inherits from `str` and
    `Enum` and has a single attribute `value` that is a string"""  # pylint: disable=line-too-long

    EPSILON_GREEDY = "EPSILON_GREEDY"
    RND = "RND"
    SOFTMAX = "SOFTMAX"
    SQUARE_CB = "SQUARE_CB"


class JobStatus(str, Enum):
    """`JobStatus` is a subclass of `str` that has a fixed set of values"""

    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"
    QUEUED = "QUEUED"
    SUBMITTED = "SUBMITTED"


class MeasureFrequency(str, Enum):
    """`MeasureFrequency` is a subclass of `str` that has a fixed set of values"""

    DAILY = "DAILY"
    MONTHLY = "MONTHLY"
    WEEKLY = "WEEKLY"
    YEARLY = "YEARLY"


class MissionLifecycleState(str, Enum):
    """This class is a string that can only be one of the following
    values: `'UNKNOWN'`, `'CREATED'`, `'ACTIVE'`, `'COMPLETED'`, `'CANCELLED'`, `'FAILED'`,
    `'PENDING'`, `'INACTIVE'`, `'DELETED'`"""  # pylint: disable=line-too-long

    ARCHIVED = "ARCHIVED"
    DEPLOYED = "DEPLOYED"
    EDITING = "EDITING"
    READY_FOR_DEPLOYMENT = "READY_FOR_DEPLOYMENT"
    REVIEWING = "REVIEWING"
    SIMULATING = "SIMULATING"


class PolicyEvaluation(str, Enum):
    """The `PolicyEvaluation` class is a subclass of the `str` class and
    the `Enum` class"""  # pylint: disable=line-too-long

    DM = "DM"
    DR = "DR"
    IPS = "IPS"
    MTR = "MTR"


class ResourceType(str, Enum):
    """`ResourceType` is a subclass of `str` that can only be
    one of the values in the `Enum` class"""  # pylint: disable=line-too-long

    DATA_SOURCE = "DATA_SOURCE"
    PROFILE_SCHEMA = "PROFILE_SCHEMA"


class ScriptLanguage(str, Enum):
    """The `ScriptLanguage` class is a subclass of the `str`
    class and the `Enum` class"""  # pylint: disable=line-too-long

    JAVASCRIPT = "Javascript"
    PYTHON = "Python"
    ROBOTFRAMEWORK = "RobotFramework"


class SimulationStatus(str, Enum):
    """The `SimulationStatus` class is a subclass of the
    `str` class and the `Enum` class"""  # pylint: disable=line-too-long

    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"
    INITIALIZING = "INITIALIZING"
    PLANNING = "PLANNING"
    REFINING = "REFINING"
    RUNNING = "RUNNING"
    TRAINING = "TRAINING"
    UNKNOWN = "UNKNOWN"


class SinkKind(str, Enum):
    """It's a string that can only be one of a few values"""

    BATCH = "BATCH"
    STREAMING = "STREAMING"


class SourceKind(str, Enum):
    """It's a string that can only be one of the values in the list"""

    BATCH = "batch"
    STREAMING = "streaming"


class StreamStatus(str, Enum):
    """The `StreamStatus` class is a subclass of `str` that has a fixed set of values"""

    AWAITING = "AWAITING"
    PROCESSING = "PROCESSING"


class TimeoutUnit(str, Enum):
    """It's a string that can only be one of the following values:

    - `'seconds'`
    - `'minutes'`
    - `'hours'`
    - `'days'`

    The `Enum` class is a base class for enumerations, which means it defines some
    functionality that's common to all
    enumerations
    `UserQueryDialectSpec` is a subclass of `str`
    that is also an `Enum`"""  # pylint: disable=line-too-long

    DAY = "DAY"
    HOUR = "HOUR"
    MINUTE = "MINUTE"
    MONTH = "MONTH"
    SECOND = "SECOND"
    WEEK = "WEEK"
    YEAR = "YEAR"


class UserQueryDialectSpec(str, Enum):
    """`UserQueryDialectSpec` is a subclass of `str` that is also an `Enum`"""

    NATIVE = "NATIVE"
    SPARK_SQL = "SPARK_SQL"


class ValueDirection(str, Enum):
    """`ValueDirection` is a subclass of `str` that can only be
    one of the values in the `Enum` `ValueDirection`"""  # pylint: disable=line-too-long

    DOWN = "DOWN"
    NONE = "NONE"
    UP = "UP"


class WriteMode(str, Enum):
    """`WriteMode` is a subclass of `str` that has a fixed set of values"""

    APPEND = "APPEND"
    ERROR = "ERROR"
    OVERWRITE = "OVERWRITE"
