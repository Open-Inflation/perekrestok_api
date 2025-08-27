
project = 'Perekrestok API'
author = 'Miskler'
copyright = '2025, Miskler'
from perekrestok_api import __version__
release   = __version__


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',  # если есть Google/Numpy-стиль докстрингов
    "enum_tools.autoenum",
    'jsoncrack_for_sphinx',  # для визуализации JSON-схем
]
toc_object_entries = True                 # заставляем Sphinx добавлять объекты в локальный TOC
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
# ──────────────────────────────────────────────────────────────────────────────
# Theme / HTML
# ──────────────────────────────────────────────────────────────────────────────
html_theme       = "furo"
html_static_path = ["_static"]
html_theme_options = {
    "light_logo": "logo-day.svg",
    "dark_logo":  "logo-night.svg",
    "sidebar_hide_name": True,

    "source_repository": "https://github.com/Open-Inflation/perekrestok_api",
    "source_branch": "main",
    "source_directory": "docs/",

    "globaltoc_collapse": False,
    "dark_css_variables": {},
}
templates_path   = ["_templates"]


# ──────────────────────────────────────────────────────────────────────────────
# Навигация и compact-style
# ──────────────────────────────────────────────────────────────────────────────
add_module_names                     = False        # compare() → Config
toc_object_entries_show_parents      = "hide"       # короче TOC
python_use_unqualified_type_names    = True         # Config, а не jsonschema_diff.core.Config
multi_line_parameter_list            = True         # каждый аргумент с новой строки
python_maximum_signature_line_length = 60           # длина, после которой рвём строку

# ──────────────────────────────────────────────────────────────────────────────
# Type-hints
# ──────────────────────────────────────────────────────────────────────────────
autodoc_typehints = "signature"      # str / Dict[...] остаются в сигнатуре
typehints_fqcn    = False            # короткие имена в хинтах


# ──────────────────────────────────────────────────────────────────────────────
# Intersphinx – ссылки на stdlib / typing
# ──────────────────────────────────────────────────────────────────────────────
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}



# Configure the schema directory for examples
import os
json_schema_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'endpoints', '__snapshots__')

from jsoncrack_for_sphinx.config import RenderMode, Directions, Theme, ContainerConfig, RenderConfig, SearchPolicy, PathSeparator

jsoncrack_default_options = {
    'render': RenderConfig(
        mode=RenderMode.OnClick()
    ),
    'container': ContainerConfig(
        direction=Directions.DOWN,
        height='500',
        width='100%'
    ),
    'theme': Theme.AUTO,
    'search_policy': SearchPolicy(custom_patterns=['{class_name}.{method_name}.main.json']),
    'autodoc_ignore': [
        'perekrestok_api.abstraction',
        'perekrestok_api.PerekrestokAPI',
    ]
}


from sphinx.roles import XRefRole
def setup(app):
    app.add_role("pyclass", XRefRole("class"))
    app.add_role("pyfunc", XRefRole("func"))
    #app.add_css_file("tighten.css")
