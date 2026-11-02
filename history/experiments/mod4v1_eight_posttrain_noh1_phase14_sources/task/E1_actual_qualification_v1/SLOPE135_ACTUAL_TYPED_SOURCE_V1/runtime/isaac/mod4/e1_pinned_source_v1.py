"""Future E1 worker-owned COMPLETE source cache, NO I/O on module import.
One actual source byte read/SHA/CPUdecode. Four-leaf in-memory migration only;
original untyped dict remains intact. No PT writing/stat, slicing or RNG draws.
Every original RSL/D0-D7/E1 helper gets a deep copy of the SAME typed complete
state. Own new roundtrip artifacts retain real loads, not a source-cache alias.
"""
from contextlib import contextmanager
from pathlib import Path
import copy,hashlib,io,os
from e1_four_leaf_migration_v1 import migrate_complete_source
ACTIVE=None

class PinnedSourceE1:
 def __init__(self,torch,path,expected_SHA,expected_bytes,*,role,original_source_SHA,CPU_receipt_SHA):
  self.torch=torch;self.path=Path(path).resolve();self.original_load=torch.load;self.role=role;self.original_source_SHA=original_source_SHA;self.CPU_receipt_SHA=CPU_receipt_SHA
  self.physical_byte_reads=0;self.source_SHA_calculations=0;self.source_decodes=0;self.logical_purposes=[];self.own_or_other_artifact_loads=[]
  with self.path.open('rb') as stream:self.raw=stream.read();self.physical_byte_reads+=1
  self.SHA=hashlib.sha256(self.raw).hexdigest();self.source_SHA_calculations+=1
  if self.SHA!=expected_SHA or (expected_bytes is not None and len(self.raw)!=expected_bytes):raise ValueError('Exact selected originalE1 source bytes/SHA mismatch')
  self.state=self.original_load(io.BytesIO(self.raw),map_location='cpu',weights_only=False);self.source_decodes+=1
  from e1_four_leaf_migration_v1 import FOUR_PATHS,NEW_VALUES,leaf
  if not all(leaf(self.state,p)==v for p,v in zip(FOUR_PATHS,NEW_VALUES)):raise ValueError('Alreadytyped40050 completeinput required; no retyping')
  if self.state['independent_terrain_expert']!=role or self.state['spring_pressure_state']['n']!=20000 or self.state['feedback_delay_recipe']['control_period_us']!=10000:raise ValueError('ExacttypedE1role/20k/100Hzfeedback required')
  self.migration_receipt=dict(kind='ALREADY_TYPED_COMPLETE_NO_RETYPE',original_source_SHA=original_source_SHA,actual_CPU_receipt_SHA=CPU_receipt_SHA,typed_source_SHA=self.SHA,original_four_leaf_inverse_actual_proof_is_external=True,migration_calls_in_SDK=0,checkpoint_metadata_keys_added=0)
 def owns(self,path):return isinstance(path,(str,os.PathLike)) and Path(path).resolve()==self.path
 def load(self,path,*args,purpose,**kwargs):
  if self.owns(path):self.logical_purposes.append(dict(operation='cached_complete_typed_state',purpose=purpose));return copy.deepcopy(self.state)
  self.own_or_other_artifact_loads.append(dict(path=str(path),purpose=purpose));return self.original_load(path,*args,**kwargs)
 def H(self,path,*,purpose):
  if self.owns(path):self.logical_purposes.append(dict(operation='cached_original_source_SHA',purpose=purpose));return self.SHA
  with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
 def receipt(self):
  return dict(source_path=str(self.path),original_source_SHA=self.original_source_SHA,source_SHA=self.SHA,source_bytes=len(self.raw),selected_source_physical_byte_reads=self.physical_byte_reads,selected_source_SHA_calculations=self.source_SHA_calculations,selected_source_decodes=self.source_decodes,logical_purposes=list(self.logical_purposes),new_own_artifact_real_loads=list(self.own_or_other_artifact_loads),four_leaf_migration=self.migration_receipt,selected_typed_complete_pytree_unmodified=True,typed_pytree_only_four_leaves_differ=True,PT_writes=0,no_slicing_or_history_timestamp_rescaling=True,no_Path_or_builtin_open_redirection=True)

@contextmanager
def selected_source(cache):
 global ACTIVE
 if ACTIVE is not None:raise RuntimeError('One worker-owned E1 selected cache')
 ACTIVE=cache
 try:yield cache
 finally:ACTIVE=None

def cached_load(path,*args,purpose,**kwargs):
 if ACTIVE is None:raise RuntimeError('E1 selected source cache not active')
 return ACTIVE.load(path,*args,purpose=purpose,**kwargs)

def cached_H(path,*,purpose):
 if ACTIVE is None:raise RuntimeError('E1 selected source cache not active')
 return ACTIVE.H(path,purpose=purpose)

def cached_source_owns(path):return ACTIVE is not None and ACTIVE.owns(path)

@contextmanager
def runner_source_load_scope():
 if ACTIVE is None:raise RuntimeError('RSL requires shared E1 source cache')
 module=ACTIVE.torch;original=module.load
 def selected_only(path,*args,**kwargs):
  if ACTIVE is not None and ACTIVE.owns(path):return ACTIVE.load(path,*args,purpose='RSL.runner.load.complete_actor_STD17Adam_actual_LR_iter',**kwargs)
  return original(path,*args,**kwargs)
 module.load=selected_only
 try:yield
 finally:module.load=original
