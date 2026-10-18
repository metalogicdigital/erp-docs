import shutil
import sys
from pathlib import Path

#=== General configuration ===#

project = 'MetaLogic ERP Docs'
copyright = 'MetaLogic Digital'
author = 'MetaLogic Digital'

# The Odoo version the case studies are built on.
version = release = '17.0'

master_doc = 'index'
source_suffix = '.rst'
language = None
exclude_patterns = ['README.*', '_build']

# `foo` behaves like ``foo`` (same default as the Odoo documentation).
default_role = 'literal'

html_scaled_image_link = False

#=== Extensions ===#

# The theme and directives come from the Odoo documentation project (CC BY-SA 4.0).
# See extensions/README.md for what was taken and what was changed.
sys.path.insert(0, str(Path('extensions').absolute()))

extensions = [
    'odoo_theme',
    'custom_admonitions',
    'cards',
    'spoilers',
    'sphinx_tabs.tabs',
    'sphinx.ext.graphviz' if shutil.which('dot') else 'graphviz_placeholder',
]

sphinx_tabs_disable_tab_closing = True
sphinx_tabs_disable_css_loading = True

graphviz_output_format = 'svg'
graphviz_dot_args = [
    '-Gfontname=Inter', '-Nfontname=Inter', '-Efontname=Inter',
    '-Gbgcolor=transparent', '-Nfontsize=11', '-Efontsize=10',
]

# Our own templates override the theme's Odoo-branded header, footer and homepage.
templates_path = ['_templates']

#=== HTML output ===#

html_theme = 'odoo_theme'
html_theme_path = ['extensions']
pygments_style = 'odoo'
html_static_path = ['static']
html_favicon = 'static/img/favicon.svg'
html_css_files = ['css/metalogic.css']
html_permalinks = True
html_title = 'MetaLogic ERP Docs'


def _set_switcher_context(app, pagename, templatename, context, doctree):
    """ The theme's layout expects the alternate URL keys that Odoo's conf.py computes. This site
    has a single version and language, so the switchers stay empty. """
    context.setdefault('canonical', '')
    context['version_display_name'] = f'Odoo {version.split(".")[0]}'
    context['alternate_versions'] = []
    context['language_code'] = 'en'
    context['alternate_languages'] = []


def setup(app):
    app.connect('html-page-context', _set_switcher_context)
