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

from setuptools import setup
from setuptools import find_packages

with open('README.md') as f:
    long_description = f.read()

setup(name='cortex-python',
      description="Python module for the CognitiveScale Cortex Cognitive Platform",
      long_description=long_description,
      long_description_content_type='text/markdown',
      version='1.4.0',
      author='CognitiveScale',
      author_email='info@cognitivescale.com',
      url='https://github.com/CognitiveScale/cortex-python',
      license='Apache License Version 2.0',
      platforms=['linux', 'osx'],
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
          'requests>=2.12.4,<3',
          'requests-toolbelt==0.8.0',
          'pyjwt>=1.6.1,<2',
          'pyyaml>=5.3.1,<6',
          'cuid>=0.3,<1',
          'tenacity>=5.0.2',
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
          'builders': [
              'cortex-python-builders>=1.0.0,<2'
          ]
      },
      tests_require=[
          'mocket>=2.5.0,<3',
          'mock>=2,<3',
          'pytest>=3.2.5,<4',
          'pipdeptree'
      ],
      classifiers=[
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 3.6',
      ])
