"""Future worker-owned selected71db cache. This module does no I/O on import.

No PT operation is performed by the source-only generator. At a future separately
admitted run, ONE physical byte-read, ONE SHA calculation and ONE CPU decode serve
RSL and every original H1/D0-D7 helper. New own disk-roundtrip artifacts retain
real original I/O. No global Path/open patch, stream reconstruction or slicing.
"""
from contextlib import contextmanager
from pathlib import Path
import copy,hashlib,io,os

ACTIVE=None

class PinnedSourceH1:
    def __init__(self,torch,path,expected_SHA,expected_bytes):
        self.torch=torch;self.path=Path(path).resolve();self.original_load=torch.load
        self.physical_byte_reads=0;self.source_SHA_calculations=0;self.source_decodes=0
        self.logical_purposes=[];self.own_or_other_artifact_loads=[]
        with self.path.open('rb') as stream:
            self.raw=stream.read();self.physical_byte_reads+=1
        self.SHA=hashlib.sha256(self.raw).hexdigest();self.source_SHA_calculations+=1
        if len(self.raw)!=expected_bytes or self.SHA!=expected_SHA:
            raise ValueError('Selected71db source actual bytes/SHA mismatch')
        self.state=self.original_load(io.BytesIO(self.raw),map_location='cpu',weights_only=False)
        self.source_decodes+=1

    def owns(self,path):
        return isinstance(path,(str,os.PathLike)) and Path(path).resolve()==self.path

    def load(self,path,*args,purpose,**kwargs):
        if self.owns(path):
            self.logical_purposes.append(dict(operation='cached_state',purpose=purpose))
            return copy.deepcopy(self.state)
        self.own_or_other_artifact_loads.append(dict(path=str(path),purpose=purpose))
        return self.original_load(path,*args,**kwargs)

    def H(self,path,*,purpose):
        if self.owns(path):
            self.logical_purposes.append(dict(operation='cached_SHA',purpose=purpose))
            return self.SHA
        with Path(path).open('rb') as stream:
            return hashlib.file_digest(stream,'sha256').hexdigest()

    def receipt(self):
        return dict(source_path=str(self.path),source_SHA=self.SHA,source_bytes=len(self.raw),
            selected_source_physical_byte_reads=self.physical_byte_reads,
            selected_source_SHA_calculations=self.source_SHA_calculations,
            selected_source_decodes=self.source_decodes,logical_purposes=list(self.logical_purposes),
            new_own_artifact_real_loads=list(self.own_or_other_artifact_loads),
            immutable_original_CPU_pytree=True,no_slice_or_queue_reconstruction=True,
            no_Path_or_builtin_open_redirection=True)

@contextmanager
def selected_source(cache):
    global ACTIVE
    if ACTIVE is not None:raise RuntimeError('One worker-owned H1 source cache')
    ACTIVE=cache
    try:yield cache
    finally:ACTIVE=None

def cached_load(path,*args,purpose,**kwargs):
    if ACTIVE is None:raise RuntimeError('H1 selected cache is not active')
    return ACTIVE.load(path,*args,purpose=purpose,**kwargs)

def cached_H(path,*,purpose):
    if ACTIVE is None:raise RuntimeError('H1 selected cache is not active')
    return ACTIVE.H(path,purpose=purpose)

def cached_source_owns(path):
    return ACTIVE is not None and ACTIVE.owns(path)

@contextmanager
def runner_source_load_scope():
    if ACTIVE is None:raise RuntimeError('Runner needs worker-owned H1 source cache')
    module=ACTIVE.torch;original=module.load
    def selected_only(path,*args,**kwargs):
        if ACTIVE is not None and ACTIVE.owns(path):
            return ACTIVE.load(path,*args,purpose='RSL.runner.load.actor_critic_STD17Adam_iter',**kwargs)
        return original(path,*args,**kwargs)
    module.load=selected_only
    try:yield
    finally:module.load=original
