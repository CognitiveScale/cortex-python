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

import time


class Timer:
    """
    Used with the run class to time actions.
    """
    def __init__(self):
        self.start_time = None
        self._start_clock = None
        self.end_time = None
        self._end_clock = None
        self.interval = None

    def start(self):
        """
        Starts the timer.
        """
        self._start_clock = time.perf_counter()
        self.start_time = time.time()

    def stop(self):
        """
        Stops the timer.
        """
        self._end_clock = time.perf_counter()
        self.end_time = time.time()
        self.interval = self._end_clock - self._start_clock

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
