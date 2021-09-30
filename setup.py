"""
Copyright 2021 Cognitive Scale, Inc. All Rights Reserved.

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

from setuptools import setup
from setuptools import find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
about = {}
with open(os.path.join(here, 'cortex', '__version__.py'), 'r') as f:
    exec(f.read(), about)

with open('README.md') as f:
    long_description = f.read()

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    license=about['__license__'],
    package_data={'': ['LICENSE', 'CHANGELOG.md']},
    project_urls={
        'Documentation': 'https://cognitivescale.github.io/cortex-python/master/',
        'Source': 'https://github.com/CognitiveScale/cortex-python',
    },
    platforms=['any'],
    packages=find_packages(),
    include_package_data=True,
  install_requires=[
      'requests>=2.12.4,<3',
      'requests-toolbelt>=0.8.0',
      'python-jwt>=3.3.0,<4.0',
      'pyyaml>=5.3.1,<6',
      'cuid>=0.3,<1',
      'tenacity>=8.0,<9.0',
      'dill>=0.2.8.2'
  ],
  extras_require={
      'viz': [
          'matplotlib>=2.2.2,<3',
          'seaborn>=0.9.0,<0.10',
          'pandas'
      ],
      'jupyter': [
          'ipython>=6.4.0,<7',
          'maya>=0.5.0',
          'jinja2'
      ],
  },
  tests_require=[
      'mocket>=3.9.0,<4.0',
      'pytest>=3.2.5,<4'
  ],
  classifiers=[
      'Operating System :: MacOS :: MacOS X',
      'Operating System :: POSIX',
      'Programming Language :: Python :: 3.6',
  ])
