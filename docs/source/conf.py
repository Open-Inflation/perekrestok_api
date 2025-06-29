# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Perekrestok API'
copyright = '2025, miskler'
author = 'miskler'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',  # если есть Google/Numpy-стиль докстрингов
    "enum_tools.autoenum",
    'myst_parser',
]
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}
toc_object_entries = True                 # заставляем Sphinx добавлять объекты в локальный TOC
toc_object_entries_show_parents = "hide"  # короткие имена (без module.Class.) :contentReference[oaicite:0]{index=0}
autosummary_generate = True
autosummary_imported_members = True
autodoc_default_options = {          # чтобы не писать :members: в каждом файле
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    "member-order": "bysource",
}

autodoc_attr_value_repr      = "repr"   # использовать repr(), а не сокращённое имя класса
autodoc_attr_value_cutoff    = 80       # не обрезать repr короче 80 симв.


nitpicky = True

toc_object_entries = True                # выводим классы/функции в локальный TOC
toc_object_entries_show_parents = "hide" # не писать module.Class.method() :contentReference[oaicite:0]{index=0}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


python_maximum_signature_line_length = 30


autodoc_typehints = "signature"   # типы (и | None) → в сигнатуру
autodoc_preserve_defaults = True  # показывает реальные default, а не …
typehints_defaults = None      # в field-list останется пометка “, optional”
typehints_use_rtype = False       # return-type остаётся в сигнатуре, не дублируется
napoleon_use_rtype = False



#extensions.append("sphinx_wagtail_theme")
#html_theme = 'sphinx_wagtail_theme'
html_theme = 'sphinx_nefertiti'

html_theme_options = {
    "style": "green",
    "style_header_neutral": True,
    "logo": "logo.svg",
    "logo_alt": "Перекрёсток",
    "logo_width": 40,
    "logo_height": 40,
    "repository_url": "https://github.com/Open-Inflation/perekrestok_api",
    "repository_name": "GitHub"
}
html_static_path = ['_static']

from perekrestok_api.abstraction import CatalogFeedFilter

def inject_filter_info(app, what, name, obj, options, lines):
    from perekrestok_api.abstraction import CatalogFeedFilter
    if isinstance(obj, CatalogFeedFilter.Filter):
        # если в докстринге уже есть текст — добавляем пустую строку
        if lines and lines[-1].strip():
            lines.append("")
        lines.extend([
            f":type: {obj.__class__.__name__}",
            f":value: {obj!r}",
        ])

def setup(app):
    #app.add_css_file("tighten.css")
    app.connect("autodoc-process-docstring", inject_filter_info)
