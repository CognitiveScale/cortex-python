"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

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
# -*- coding: utf-8 -*-
#
# CORTEX Python SDK documentation build configuration file, created by
# sphinx-quickstart on Thu Jun  8 15:19:41 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('..'))
import sphinx_rtd_theme
from git import Repo


# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
#extensions = ['sphinx.ext.autodoc', 'sphinxcontrib.restbuilder']
extensions = ['sphinx.ext.autodoc',
              "sphinx_rtd_theme",
              'sphinx.ext.githubpages'
              ]

extensions.append('sphinxcontrib.versioning.sphinx_')

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'CORTEX Python SDK'
copyright = u'2017, Cognitive Scale'
author = u'Cognitive Scale'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = u'5.0.11'
# The full version, including alpha/beta/rc tags.
release = version 

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'basic'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}
# html_theme_options = {
#     'display_version': True,
#     'prev_next_buttons_location': 'bottom',
#     'style_nav_header_background': 'white',
#     # Toc options
#     'collapse_navigation': True,
#     'sticky_navigation': True,
#     'navigation_depth': 4,
#     'includehidden': True,
#     'titles_only': False
# }

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'CORTEXPythonSDKdoc'


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'CORTEXPythonSDK.tex', u'CORTEX Python SDK Documentation',
     u'Cognitive Scale', 'manual'),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'cortexpythonclient', u'CORTEX Python SDK Documentation',
     [author], 1)
]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'CORTEXPythonSDK', u'CORTEX Python SDK Documentation',
     author, 'CORTEXPythonSDK', 'One line description of project.',
     'Miscellaneous'),
]

# https://sphinx-versions.readthedocs.io/en/latest/settings.html#cmdoption
# scv_priority = 'branches'
# TODO look into https://sphinx-versions.readthedocs.io/en/latest/settings.html#cmdoption-w
html_theme = 'sphinx_rtd_theme'
scv_overflow = ("-A", "html_theme=sphinx_rtd_theme")

# Copied from https://stackoverflow.com/questions/49331914/enable-versions-in-sidebar-in-sphinx-read-the-docs-theme
############################
# SETUP THE RTD LOWER-LEFT #
############################
try:
    html_context
except NameError:
    html_context = dict()
html_context['display_lower_left'] = True

templates_path = ['_templates']



# SET CURRENT_LANGUAGE
if 'current_language' in os.environ:
    # get the current_language env var set by buildDocs.sh
    current_language = os.environ['current_language']
else:
    # the user is probably doing `make html`
    # set this build's current language to english
    current_language = 'en'

# SET CURRENT_VERSION
# repo = Repo( search_parent_directories=True )

if 'current_version' in os.environ:
    # get the current_version env var set by buildDocs.sh
    current_version = os.environ['current_version']
else:
    # the user is probably doing `make html`
    # set this build's current version by looking at the branch
    # current_version = repo.active_branch.name
    current_version = 'sphinxVersion'

# tell the theme which version we're currently on ('current_version' affects
# the lower-left rtd menu and 'version' affects the logo-area version)
html_context['current_version'] = current_version
html_context['version'] = current_version

# POPULATE LINKS TO OTHER LANGUAGES
html_context['languages'] = [ ]

# languages = [lang.name for lang in os.scandir('locales') if lang.is_dir()]
# for lang in languages:
#     html_context['languages'].append( (lang, '/' +REPO_NAME+ '/' +lang+ '/' +current_version+ '/') )

if 'REPO_NAME' in os.environ:
    REPO_NAME = os.environ['REPO_NAME']
else:
    REPO_NAME = 'cortex-python'
    # REPO_NAME = repo.remotes.origin.url.split('.git')[0].split('/')[-1]

# POPULATE LINKS TO OTHER VERSIONS
html_context['versions'] = list()

versions = []
# versions = [branch.name for branch in repo.branches]
for version in versions:
    html_context['versions'].append( (version, '/' +REPO_NAME+ '/' +version+ '/') )

# # POPULATE LINKS TO OTHER FORMATS/DOWNLOADS
#
# # settings for creating PDF with rinoh
# rinoh_documents = [(
#     master_doc,
#     'target',
#     project+ ' Documentation',
#     '© ' +copyright,
# )]
# today_fmt = "%B %d, %Y"
#
# # settings for EPUB
# epub_basename = 'target'
#
html_context['downloads'] = list()
# html_context['downloads'].append( ('pdf', '/' +REPO_NAME+ '/' +current_language+ '/' +current_version+ '/' +project+ '-docs_' +current_language+ '_' +current_version+ '.pdf') )
#
# html_context['downloads'].append( ('epub', '/' +REPO_NAME+ '/' +current_language+ '/' +current_version+ '/' +project+ '-docs_' +current_language+ '_' +current_version+ '.epub') )

##########################
# "EDIT ON GITHUB" LINKS #
##########################

html_context['display_github'] = True
html_context['github_user'] = 'cognitivescale'
html_context['github_repo'] = REPO_NAME
html_context['github_version'] = 'master/docs/'

print('HTML_CONTEXT')
print(html_context)
