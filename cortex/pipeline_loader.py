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
import threading


class PipelineLoader:
    """
    Manages a collection of pipelines.
    """

    _default_loader = None
    _default_loader_lock = threading.Lock()

    @classmethod
    def default_loader(cls):
        with cls._default_loader_lock:
            if cls._default_loader is None:
                cls._default_loader = cls()
            return cls._default_loader

    def __init__(self):
        self._pipelines = {}

    def add_pipeline(self, name, pipeline):
        self._pipelines[name] = pipeline

    def get_pipeline(self, name):
        p = self._pipelines.get(name)
        if not p:
            from .pipeline import Pipeline
            p = Pipeline(name=name, loader=self)
            self.add_pipeline(name, p)
        return p

    def remove_pipeline(self, name):
        if name in self._pipelines:
            del self._pipelines[name]

    def dump(self, camel='1.0.0'):
        return {k: v.to_camel(camel) for k, v in self._pipelines.items()}
