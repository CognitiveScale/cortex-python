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

import sys
import yaml
import json
import dill
import copy
from collections import OrderedDict
from .utils import log_message, b64encode, b64decode, get_logger
from .pipeline_loader import PipelineLoader

log = get_logger(__name__)

# Configure dill to 'recurse' dependencies when dumping objects
dill.settings['recurse'] = True


class _FunctionStep:

    def __init__(self, name, function_name, function_type, serialized_code):
        self.name = name
        self.function_name = function_name
        self.function_type = function_type
        self.serialized_code = serialized_code

    def run(self, pipeline, data, code_deserializer):
        if self.function_type == 'inline':
            fn = code_deserializer(self.serialized_code)
            log_message('> %s ' % self.function_name, log)
            result = fn(pipeline, data)
            if result is not None:
                data = result
            return data

    def to_camel(self, camel='1.0.0'):
        return {'name': self.name, 'function': {'name': self.function_name, 'code': b64encode(self.serialized_code), 'type': self.function_type}}

    @staticmethod
    def load(doc):
        name = doc.get('name')
        f = doc.get('function', {})
        function_name = f.get('name')
        function_type = f.get('type')
        code = f.get('code')

        return _FunctionStep(name, function_name, function_type, b64decode(code))


class _TransformStep:

    def __init__(self, name, module_name, class_name):
        self.class_name = class_name
        self.module_name = module_name
        self.full_name = '.'.join([module_name, class_name])
        self.name = name or self.full_name
        self._validate_transform(module_name, class_name)

    def run(self, pipeline, data, code_deserializer):
        t = self._get_instance(self.module_name, self.class_name)
        log_message('> %s ' % self.name, log)
        result = t.transform(pipeline, data)
        if result is not None:
            data = result
        return data

    def to_camel(self, camel='1.0.0'):
        return {'name': self.name, 'transform': {'class_name': self.class_name, 'module_name': self.module_name}}

    @staticmethod
    def load(doc):
        name = doc.get('name')
        t = doc.get('transform', {})
        class_name = t.get('class_name')
        module_name = t.get('module_name')

        return _TransformStep(name, module_name, class_name)

    @staticmethod
    def _get_instance(module_name, class_name):
        try:
            # Attempt to import module
            return getattr(__import__(module_name, globals(), locals(), [class_name], 0), class_name)()
        except ValueError:
            # Attempt to locate class in globals
            return globals()[class_name]()

    @staticmethod
    def _validate_transform(module_name, class_name):
        full_name = '.'.join([module_name, class_name])

        # Transform validation
        # 1. Make sure we can instantiate the step
        t = _TransformStep._get_instance(module_name, class_name)

        # 2. Make sure the class has a 'transform' attribute that is callable
        try:
            t_func = getattr(t, 'transform')
            if not callable(t_func):
                raise ValueError('"transform" attribute of class ' + full_name + ' is not callable')
        except AttributeError:
            raise AttributeError('Provided class ' + full_name + ' does not have a "transform" method')


class Pipeline:

    """
    Provides a pipeline abstraction used to transform or enrich data; steps either Python functions
    or classes with a transform method; a pipeline step accepts a dataframe as an argument and is expected to transform
    or enrich the dataframe in sequential order.

    To create a pipeline to remove an unused column:

        >>> from cortex import Cortex
        >>> train_ds = cortex.dataset(' <path to your data set> ')
        >>> pipeline = train_ds.pipeline(' <pipeline name> ', clear_cache=True)
        >>> pipeline.reset()
        >>> def drop_unused(pipeline, df):
        ...     df.drop(columns=['Id'], axis=1, inplace=True) # this pipeline will drop the field ID
        ...
        >>> pipeline.add_step(drop_unused)

    """

    def __init__(self, name: str, depends=None, loader=PipelineLoader.default_loader()):
        self._name = name
        self._dependencies = OrderedDict({})
        self._steps = []
        self._context = {}
        self._loader = loader

        if depends is not None and len(depends) > 0:
            for d in depends:
                self.add_dependency(loader.get_pipeline(d))

        loader.add_pipeline(name, self)

    @property
    def name(self):
        """
        Gets the name of the pipeline.
        """
        return self._name

    @property
    def steps(self):
        """
        Gets a list of steps in the pipeline.
        """
        return self._steps

    @property
    def dependencies(self):
        """
        Gets a list of dependencies for the pipeline.
        """
        return self._dependencies.values()

    def get_context(self, key: str, default_value=None, deserializer=dill.loads):
        """
        Gets the context for the pipeline.

        :param key: The key for the context.
        :param default_value: (Optional) A default value to return if the context for the given key is not found
        :return: The context for the given key, if it exists. If it does not exist, the default value or `none`.
        """
        if deserializer is None:
            def _identity(o): return o
            deserializer = _identity

        val = self._context.get(key)
        if val:
            return deserializer(val)
        else:
            depends = self.dependencies
            if len(depends) > 0:
                for dep in depends:
                    if self._name == dep._name:
                        raise Exception('Circular dependency detected in pipeline dependency graph')
                    val = dep.get_context(key, deserializer=None)
                    if val:
                        return deserializer(val)

        return default_value

    def set_context(self, key: str, obj, serializer=dill.dumps):
        """
        Sets the context for the pipeline.

        :param key: The key for the context to set.
        :param obj: The value for the context to set.
        """
        if serializer is None:
            def _identity(o): return o
            serializer = _identity

        self._context[key] = serializer(obj)

    def add_step(self, step, name=None, serializer=dill.dumps):
        """
        Adds a transformation function to the pipeline.

        :param fn: The function to add.
        :param name: An optional name for the function to add.
        """
        if isinstance(step, type):
            return self._add_transform_step(step, name)
        return self._add_inline_step(step, name, serializer)

    def _add_inline_step(self, fn, name=None, serializer=dill.dumps):
        fn_name = fn.__name__
        if name is None:
            name = fn_name

        code = serializer(fn)
        self._steps.append(_FunctionStep(name, fn_name, 'inline', code))

        return self

    def _add_transform_step(self, kls, name=None):
        class_name = kls.__name__
        module_name = kls.__module__
        self._steps.append(_TransformStep(name, module_name, class_name))

        return self

    def get_step(self, name, deserializer=dill.loads):
        """
        Gets a pipeline step by name.

        :param name: Name of the function to get.

        :return: The code for the step.
        """
        for step in self._steps:
            if step.name == name:
                if isinstance(step, _FunctionStep):
                    return deserializer(step.serialized_code)
                elif isinstance(step, _TransformStep):
                    return step._get_instance(step.module_name, step.class_name)
                else:
                    raise ValueError('Invalid step: must be either a function or a transform class')
        return None

    def remove_step(self, name):
        """
        Removes a step by name.

        :param name: Name of the function to remove.
        """
        new_steps = []
        for step in self._steps:
            if step.name != name:
                new_steps.append(step)

        self._steps = new_steps

        return self

    def add_dependency(self, pipeline):
        """
        Adds a dependency on another pipeline.

        :param pipeline: the pipeline on which this pipeline depends.
        """
        self._dependencies[pipeline.name] = pipeline
        return self

    def reset(self, reset_deps=False, reset_context=False):
        """
        Removes all steps from the pipeline, but leaves context and dependencies in place. Context and
        dependencies can also be reset using the optional flags for each.

        :param reset_deps: If `True`, removes all dependencies.  Default: `False`.
        :param reset_context: If `True`, resets context. Default: `False`
        :return: The pipeline instance.
        """
        self._steps = []
        if reset_deps:
            self._dependencies = OrderedDict({})
        if reset_context:
            self._context = {}

        return self

    def from_pipeline(self, pipeline):
        """
        Copies a pipeline from the given pipeline.

        :param pipeline: The pipeline from which to copy this pipeline.
        """
        self._steps = copy.deepcopy(pipeline.steps)
        self._dependencies = copy.deepcopy(pipeline._dependencies)
        self._context = copy.deepcopy(pipeline._context)
        return self

    def _run_dependencies(self, data):
        depends = self.dependencies
        if len(depends) > 0:
            for dep in depends:
                if self._name == dep._name:
                    raise Exception('Circular dependency detected in pipeline dependency graph')

                data = dep.run(data)

        return data

    def run(self, data, code_deserializer=dill.loads):
        """
        Runs the steps on the pipeline.

        :param data: Data to pass to dependencies.
        :return: The dataframe as transformed by the dependencies and steps.
        """
        # run dependencies
        df = self._run_dependencies(data)

        log_message('running pipeline [%s]:' % self._name, log)

        for step in self._steps:
            df = step.run(self, df, code_deserializer)

        return df

    def to_camel(self, camel='1.0.0'):
        pipeline = {
            'name': self._name,
            'steps': [step.to_camel(camel) for step in self._steps],
            'dependencies': [dep.name for dep in self.dependencies],
            'context': {k: b64encode(v) for k, v in self._context.items()}
        }
        return pipeline

    def dumps(self, stream=None, notebook=False, camel='1.0.0', yaml_format=False):
        """
        Dumps the steps, dependencies, and context for the pipeline.

        :param stream: Optional stream on which to dump the pipeline.
        :param notebook: Optional notebook where the dump should be displayed.
        """
        if stream is None and notebook:
            stream = sys.stdout

        doc = self.to_camel(camel)
        print(doc)

        if yaml_format:
            s = yaml.dump(doc, stream=stream, indent=2)
            if stream is None:
                return s
        else:
            if stream is None:
                return json.dumps(doc)
            else:
                json.dump(doc, stream)

    @staticmethod
    def load(doc, loader=PipelineLoader.default_loader()):
        p = Pipeline(name=doc.get('name'), loader=loader)
        steps = doc.get('steps', [])
        context = doc.get('context', {})
        deps = doc.get('dependencies', [])

        for step in steps:
            if step.get('function'):
                p._steps.append(_FunctionStep.load(step))
            elif step.get('transform'):
                p._steps.append(_TransformStep.load(step))

        for key in context.keys():
            p._context[key] = b64decode(context[key])

        for d in deps:
            p._dependencies[d] = loader.get_pipeline(d)

        return p
