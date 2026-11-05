"""Load unchanged shared code by its frozen identity, without copying a tree."""
import hashlib
import importlib.util
from pathlib import Path
import sys
from . import BINDINGS


def load(name):
    key = __package__ + '._source_' + name
    if key in sys.modules:
        return sys.modules[key]
    path = Path(BINDINGS['shared_package']) / (name + '.py')
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != BINDINGS['shared_SHA'][name + '.py']:
        raise ValueError('Shared source changed: ' + str(path))
    spec = importlib.util.spec_from_file_location(key, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[key] = module
    spec.loader.exec_module(module)
    return module


def export(module, namespace):
    namespace.update({key: value for key, value in vars(module).items()
                      if not key.startswith('__')})
