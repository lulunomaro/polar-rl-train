"""UNUSED CPU-only NPZ serialization candidate; never imported by production.

Retains field order, dtype, shape and every array byte. Atomic rename, producer
SHA publication, paired retention, failure preservation, disk guards and lifecycle
remain the caller's unchanged responsibilities. There is no asynchronous writer.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import BinaryIO, Mapping, Sequence
import zipfile

import numpy as np


def _keys(arrays: Mapping[str, np.ndarray]) -> list[str]:
    keys = list(arrays)
    if not keys or any(not isinstance(k, str) or not k or '/' in k or '\\' in k for k in keys):
        raise ValueError('Expected nonempty simple NPZ field names')
    if any(np.asarray(arrays[k]).dtype.hasobject for k in keys):
        raise ValueError('Object arrays are outside the actual trace schema')
    return keys


def write_arrays_npz(file: BinaryIO, arrays: Mapping[str, np.ndarray], *, compresslevel: int) -> None:
    """Public NPY/ZIP APIs, explicit DEFLATE level; no dtype conversion."""
    keys = _keys(arrays)
    if compresslevel not in range(1, 10):
        raise ValueError('Use an explicit DEFLATE level between 1 and 9')
    with zipfile.ZipFile(file, mode='w', compression=zipfile.ZIP_DEFLATED,
                         compresslevel=compresslevel, allowZip64=True) as archive:
        for key in keys:
            with archive.open(key + '.npy', mode='w', force_zip64=True) as member:
                np.lib.format.write_array(member, np.asanyarray(arrays[key]), allow_pickle=False)


def write_trace_rows_npz(file: BinaryIO, rows: Sequence[Mapping[str, np.ndarray]], *, compresslevel: int) -> None:
    """Stack one field at a time; keep original rows alive until caller commits."""
    if not rows:
        raise ValueError('No trace rows')
    keys = _keys(rows[0])
    for row in rows:
        if list(row) != keys:
            raise ValueError('Trace row field order/schema mismatch')
        _keys(row)
    if compresslevel not in range(1, 10):
        raise ValueError('Use an explicit DEFLATE level between 1 and 9')
    with zipfile.ZipFile(file, mode='w', compression=zipfile.ZIP_DEFLATED,
                         compresslevel=compresslevel, allowZip64=True) as archive:
        for key in keys:
            value = np.stack([row[key] for row in rows])
            with archive.open(key + '.npy', mode='w', force_zip64=True) as member:
                np.lib.format.write_array(member, value, allow_pickle=False)
            del value


def sha256_file(path: str | Path, *, block_bytes: int = 8 * 1024**2) -> str:
    """Same final file SHA, bounded read buffer; retains the full read pass."""
    if block_bytes <= 0:
        raise ValueError('block_bytes must be positive')
    digest = hashlib.sha256()
    with Path(path).open('rb') as file:
        for block in iter(lambda: file.read(block_bytes), b''):
            digest.update(block)
    return digest.hexdigest()
