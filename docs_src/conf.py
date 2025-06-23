import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR.parent))

project = 'Perekrestok API'
extensions = ['myst_parser', 'autoapi.extension']
autoapi_type = 'python'
autoapi_dirs = [str(BASE_DIR.parent / 'perekrestok_api')]

templates_path = ['_templates']
exclude_patterns = []
html_theme = 'alabaster'


def run_gen_ref(app):
    from scripts.gen_ref import generate
    generate()


def setup(app):
    app.connect('builder-inited', run_gen_ref)
