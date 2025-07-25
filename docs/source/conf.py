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



html_theme = "furo"
html_logo = './static/logo-label.svg'


html_theme_options = {
    "globaltoc_collapse": False,
    "dark_css_variables": {},
}
html_static_path = ['static']

def setup(app):
    ...
    #app.add_css_file("tighten.css")
