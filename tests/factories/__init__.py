import importlib
import pathlib
import pkgutil

for _mod in pkgutil.iter_modules([str(pathlib.Path(__file__).parent)]):
    importlib.import_module(f"tests.factories.{_mod.name}")
