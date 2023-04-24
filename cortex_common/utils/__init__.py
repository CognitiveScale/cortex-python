"""
Copyright 2021 Cognitive Scale, Inc. All Rights Reserved.

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
import logging
import os


def get_logger(name, log_level=None):
    """
    Gets a logger with the given name.
    """
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        log_level = (
            os.environ.get("LOG_LEVEL", logging.getLogger().level)
            if log_level is None
            else log_level
        )
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s/%(module)s: %(message)s"
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(log_level)
    return logger


# The reason these packages were named all with a suffix of _util was so they don't get confused
# with any builtins ...   # pylint: disable=line-too-long
# pylint: disable=wrong-import-position
from .config_utils import *

from .assertion_utils import *
from .id_utils import *

from .type_utils import *
from .attr_utils import *
from .class_utils import *

from .object_utils import *
from .time_utils import *
from .equality_utils import *

from .string_utils import *
from .generator_utils import *

# These need to come after the rest ...
from .etl_utils import *
from .dataframe_utils import *
