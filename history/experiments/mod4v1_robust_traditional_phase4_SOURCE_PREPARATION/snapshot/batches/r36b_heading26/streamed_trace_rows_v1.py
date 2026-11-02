"""Persist each new physical row before keeping it in memory.
The producer hashes bytes as written; handles NumPy scalar types explicitly,
not arbitrary objects, and never converts nonfinite values to fake numbers.
"""
from pathlib import Path
import hashlib
import json
import numpy as np


def scalar_default(value):
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError('unsupported trace field ' + type(value).__name__)


class StreamedRows(list):
    def __init__(self, path):
        super().__init__()
        self.path = Path(path)
        self.path.open('xb').close()
        self.sha = hashlib.sha256()
        self.bytes = 0

    def append(self, row):
        encoded = (json.dumps(row, separators=(',', ':'), allow_nan=False,
                              default=scalar_default) + '\n').encode('utf-8')
        with self.path.open('ab') as stream:
            stream.write(encoded)
        self.sha.update(encoded)
        self.bytes += len(encoded)
        super().append(row)
