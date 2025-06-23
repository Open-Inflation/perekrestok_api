import sys, pathlib, types
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
if "perekrestok_api.endpoints" not in sys.modules:
    sys.modules["perekrestok_api.endpoints"] = types.ModuleType("perekrestok_api.endpoints")
import inspect
import importlib.util
from pathlib import Path
import mkdocs_gen_files

SNAPSHOT_DIR = Path("tests/endpoints/__snapshots__")
ENDPOINTS_DIR = Path("perekrestok_api/endpoints")
nav_lines = []

readme = Path("README.md").read_text()
with mkdocs_gen_files.open("index.md", "w") as f:
    f.write(readme)

for py_file in ENDPOINTS_DIR.glob("*.py"):
    module_name = f"perekrestok_api.endpoints.{py_file.stem}"
    spec = importlib.util.spec_from_file_location(module_name, py_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules[module_name] = module
    for name, obj in inspect.getmembers(module, inspect.isclass):
        for method_name, method in inspect.getmembers(obj, inspect.isfunction):
            snap = SNAPSHOT_DIR / f"{method_name}.schema.json"
            if not snap.exists():
                continue
            path = Path("reference", f"{method_name}.md")
            nav_lines.append(f"* [{method_name}]({path.as_posix()})")
            with mkdocs_gen_files.open(path, "w") as f:
                sig = str(inspect.signature(method))
                doc = inspect.getdoc(method) or ""
                f.write(f"## `{method_name}{sig}`\n\n{doc}\n\n### Response schema\n")
                f.write("```json\n")
                f.write(snap.read_text())
                f.write("\n```)\n")

with mkdocs_gen_files.open("SUMMARY.md", "w") as f:
    f.write("* [Home](index.md)\n")
    f.write("* Reference\n")
    for line in nav_lines:
        f.write(f"    {line}\n")
