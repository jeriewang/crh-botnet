import os
import sys

sys.path.insert(0, os.path.abspath('../'))
from crh_botnet import __version__

# -- Project information -----------------------------------------------------

project = 'CRH BotNet'
copyright = '2019, Jerie Wang'
author = 'Jerie Wang'
release = __version__

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx_sitemap'
]

autodoc_member_order = 'bysource'
# autoclass_content='both'

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

html_theme = 'alabaster'
html_theme_options = {
    'show_powered_by': False,
    'canonical_url'  : 'docs.jerie.wang/crh-botnet/',
    'analytics_id'   : 'UA-115911413-2',
    'github_user'    : 'jeriewang',
    'github_repo'    : 'crh-botnet',
    'github_button'  : 'true',
    'github_type'    : 'star',
    'github_count'   : 'false'
}
html_baseurl = 'https://docs.jerie.wang/crh-botnet/'
html_static_path = ['_static', '_static/custom.css']

intersphinx_mapping = {
    'python'  : ('https://docs.python.org/3', None),
    'gpiozero': ('https://gpiozero.readthedocs.io/en/stable/', None)
}


def setup(app):
    app.add_stylesheet('custom.css')
