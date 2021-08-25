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

from typing import Dict


class Document:
    """
    Defines document (read-only) attributes.
    """
    def __init__(self, document: Dict, read_only=True):
        super().__setattr__('_document', document or {})
        super().__setattr__('_read_only', read_only)

    def __getattr__(self, name):
        if name.startswith('_'):
            return super().__getattribute__(name)

        doc = super().__getattribute__('_document')
        return doc.get(name)

    def __setattr__(self, name: str, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        elif super().__getattribute__('_read_only'):
            raise AttributeError(
                'Attempt to modify a read-only attribute: %s' % name)
        else:
            doc = super().__getattribute__('_document')
            doc[name] = value


class CamelResource(Document):
    """
    Contains CAMEL attributes for a Cortex object.
    """
    def __init__(self, document: Dict, read_only=True):
        super().__init__(document, read_only)

    @property
    def name(self):
        """
        The CAMEL resource name attribute.
        """
        return self._document.get('name')

    @property
    def version(self):
        """
        The CAMEL resource version (spelled _version) attribute.
        """
        return self._document.get('_version')

    @property
    def title(self):
        """
        The CAMEL resource title attribute.
        """
        return self._document.get('title')
