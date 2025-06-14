# -- Path setup --------------------------------------------------------------
from os.path import abspath, dirname
here = abspath(dirname(__file__))
# -- Project information -----------------------------------------------------
project = 'Downwind API'
copyright = '2025, Guto Maia'
author = 'Guto Maia'
from dw_api import __version__
release = __version__
# -- General configuration ---------------------------------------------------
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx_autodoc_typehints',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.imgmath',
    'sphinx.ext.ifconfig',
    'sphinxcontrib.plantuml',
    'sphinx_multiversion',
    'sphinx.ext.autosummary',
]
plantuml = f'java -jar {here}/plantuml.jar'
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'pydantic': ('https://docs.pydantic.dev', None),
}

# Autosummary settings
autosummary_generate = True
autosummary_imported_members = True

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

# -- Versioning --------------------------------------------------------------
smv_tag_whitelist = r'^v\d+\.\d+.\d+.*$'
smv_branch_whitelist = r'^(\d+\.\d+\.x)|(feat/.*)|(fix/.*)$'
smv_remote_whitelist = None
smv_released_pattern = r'^tags/.*$'
smv_outputdir_format = '{ref.name}'
smv_prefer_remote_refs = False
smv_latest_version = f'v{release}'
