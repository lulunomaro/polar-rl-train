"""One exact selected source byte-open/decode; explicit local caller reuse.

No Path.open/builtins.open redirection. Only runner.load temporarily routes
torch.load for this exact source. New own artifacts use the original loader.
"""
from contextlib import contextmanager
from pathlib import Path
import copy, hashlib, io, os

ACTIVE = None


class PinnedSource213:
    def __init__(self, torch, path, expected_SHA, expected_bytes):
        self.torch = torch; self.path = Path(path).resolve()
        self.original_load = torch.load
        self.physical_byte_opens = 0; self.decodes = 0
        self.logical_cache_loads = 0; self.logical_cached_hashes = 0
        self.own_or_other_artifact_loads = []
        before = self.path.stat()
        with self.path.open('rb') as stream:
            self.raw = stream.read(); self.physical_byte_opens += 1
        self.SHA = hashlib.sha256(self.raw).hexdigest()
        if len(self.raw) != expected_bytes or self.SHA != expected_SHA:
            raise ValueError('Selected source actual bytes/SHA mismatch')
        if self.path.stat().st_mtime_ns != before.st_mtime_ns:
            raise ValueError('Selected source changed during the one physical read')
        self.state = self.original_load(io.BytesIO(self.raw), map_location='cpu', weights_only=False)
        self.decodes += 1

    def owns(self, value):
        return isinstance(value, (str, os.PathLike)) and Path(value).resolve() == self.path

    def load(self, value, *args, **kwargs):
        if self.owns(value):
            self.logical_cache_loads += 1
            # Independent CPU tensor copies retain the immutable decoded source
            # when a resume helper copies state onto its own live CUDA buffers.
            return copy.deepcopy(self.state)
        self.own_or_other_artifact_loads.append(str(value) if isinstance(value, (str, os.PathLike)) else '<file-like>')
        return self.original_load(value, *args, **kwargs)

    def H(self, value):
        if self.owns(value):
            self.logical_cached_hashes += 1
            return self.SHA
        with Path(value).open('rb') as stream:
            return hashlib.file_digest(stream, 'sha256').hexdigest()

    def receipt(self):
        return dict(selected_source_path=str(self.path), source_SHA=self.SHA,
            source_physical_byte_opens=self.physical_byte_opens, source_bytes=len(self.raw),
            source_decodes=self.decodes, logical_source_state_cache_loads=self.logical_cache_loads,
            logical_source_cached_hashes=self.logical_cached_hashes,
            own_or_other_new_artifact_loads=list(self.own_or_other_artifact_loads),
            no_Path_or_builtin_open_redirect=True, exact_selected_path_only=True)


@contextmanager
def selected_source(cache):
    global ACTIVE
    if ACTIVE is not None:
        raise RuntimeError('One selected source owner per worker process')
    ACTIVE = cache
    try:
        yield cache
    finally:
        ACTIVE = None


def cached_load(value, *args, **kwargs):
    if ACTIVE is None:
        raise RuntimeError('No worker-owned selected source cache')
    return ACTIVE.load(value, *args, **kwargs)


def cached_H(value):
    if ACTIVE is None:
        raise RuntimeError('No worker-owned selected source cache')
    return ACTIVE.H(value)


def cached_source_owns(value):
    return ACTIVE is not None and ACTIVE.owns(value)


@contextmanager
def runner_source_load_scope():
    if ACTIVE is None:
        raise RuntimeError('Runner source load needs selected cache')
    module = ACTIVE.torch; original = module.load
    def selected_only(value, *args, **kwargs):
        if ACTIVE is not None and ACTIVE.owns(value):
            return ACTIVE.load(value, *args, **kwargs)
        return original(value, *args, **kwargs)
    module.load = selected_only
    try:
        yield
    finally:
        module.load = original
