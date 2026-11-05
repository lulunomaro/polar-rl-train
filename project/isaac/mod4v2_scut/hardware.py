"""Bind the released portable v2 geometry/action adapter in a new process."""
import importlib.util
from pathlib import Path
import sys
from . import BINDINGS


def adapter():
    key = '_mod4v2_selected_hardware_adapter'
    if key not in sys.modules:
        path = Path(BINDINGS['hardware_package']) / 'runtime_adapter_v2.py'
        spec = importlib.util.spec_from_file_location(key, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[key] = module
        spec.loader.exec_module(module)
    return sys.modules[key]
