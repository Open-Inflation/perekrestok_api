from __future__ import annotations

import inspect
import importlib.util
import types
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
SNAPSHOT_DIR = BASE / 'tests/endpoints/__snapshots__'
ENDPOINTS_DIR = BASE / 'perekrestok_api/endpoints'
DOCS_ROOT = Path(__file__).resolve().parents[1]
REF_DIR = DOCS_ROOT / 'reference'


def generate() -> None:
    REF_DIR.mkdir(exist_ok=True)

    # copy README as index with reference to generated pages
    readme = (BASE / 'README.md').read_text()
    index = DOCS_ROOT / 'index.md'
    index.write_text(readme + '\n\n```{toctree}\n:maxdepth: 1\n\nreference/index\n```\n')

    pages = []

    if 'perekrestok_api.endpoints' not in sys.modules:
        sys.modules['perekrestok_api.endpoints'] = types.ModuleType('perekrestok_api.endpoints')

    for py_file in ENDPOINTS_DIR.glob('*.py'):
        module_name = f'perekrestok_api.endpoints.{py_file.stem}'
        spec = importlib.util.spec_from_file_location(module_name, py_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules[module_name] = module
        for name, obj in inspect.getmembers(module, inspect.isclass):
            for method_name, method in inspect.getmembers(obj, inspect.isfunction):
                snap = SNAPSHOT_DIR / f'{method_name}.schema.json'
                if not snap.exists():
                    continue
                rst_path = REF_DIR / f'{method_name}.rst'
                title = f'{method_name}{inspect.signature(method)}'
                lines = [title, '=' * len(title), '']
                doc = inspect.getdoc(method)
                if doc:
                    lines.append(doc)
                    lines.append('')
                lines.extend(['Response schema', '--------------', '', '.. code-block:: json', ''])
                for line in snap.read_text().splitlines():
                    lines.append(f'   {line}')
                rst_path.write_text('\n'.join(lines))
                pages.append(f'   reference/{method_name}')

    (REF_DIR / 'index.rst').write_text(
        'Endpoint reference\n===================\n\n.. toctree::\n   :maxdepth: 1\n\n' + '\n'.join(pages) + '\n'
    )


if __name__ == '__main__':
    generate()
