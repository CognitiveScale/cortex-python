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

import unittest
from cortex.pipeline import Pipeline


class T1:
    def transform(self, pipeline, data):
        pipeline.set_context('T1', {'name': 'T1'})
        data['foo'] = data.get('foo', 0) + 1


def T5(pipeline, data):
    pipeline.set_context('T5', {'name': 'T5'})
    data['foo'] = data.get('foo', 0) + 1


def T3(pipeline, data):
    pipeline.set_context('T3', {'name': 'T3'})
    data['bar'] = data.get('bar', 0) + 2


class PipelineTest(unittest.TestCase):

    def test_transforms(self):
        p = Pipeline('test_transforms')
        p.add_step(T1)

        class T2:
            def transform(self, pipeline, data):
                return data

        try:
            # Nested classes are not supported, expecting AttributeError
            p.add_step(T2)
            assert False # Fail
        except AttributeError:
            pass

        def T4(pipeline, data):
            return data

        # Nested function should be serialized properly
        p.add_step(T4)

        data = {}
        p.run(data)
        assert 'foo' in data
        assert 1 == data['foo']

    def test_mixed_steps(self):
        p = Pipeline('test_mixed_steps')
        p.add_step(T1)
        p.add_step(T3)

        data = {}
        p.run(data)

        assert 'foo' in data
        assert 1 == data['foo']

        assert 'bar' in data
        assert 2 == data['bar']

    def test_dumps(self):
        p = Pipeline('test_dumps')
        p.add_step(T1)
        p.add_step(T3)

        data = {}
        p.run(data)

        print(p.dumps())

    def test_load(self):
        p = Pipeline('test_load')
        p.add_step(T1)
        p.add_step(T3)

        p_obj = p.to_camel()
        p = Pipeline.load(p_obj)

        data = {}
        p.run(data)

        assert 'foo' in data
        assert 1 == data['foo']

        assert 'bar' in data
        assert 2 == data['bar']

    def test_dependencies(self):
        p1 = Pipeline('p1')
        p1.add_step(T1)

        p3 = Pipeline('p3')
        p3.add_step(T5)

        p2 = Pipeline('p2')
        p2.add_step(T3)
        p2.add_dependency(p1)
        p2.add_dependency(p3)
        p2.add_dependency(p3)   # Intentional - make sure p3 only runs once

        data = {}
        p2.run(data)

        assert 'foo' in data
        assert 2 == data['foo']

        assert 'bar' in data
        assert 2 == data['bar']

        assert p2.get_context('T1') is not None

        p2_obj = p2.to_camel()
        p2 = Pipeline.load(p2_obj)

        data = {}
        p2.run(data)

        assert 'foo' in data
        assert 2 == data['foo']

        assert 'bar' in data
        assert 2 == data['bar']

        assert p2.get_context('T1') is not None
