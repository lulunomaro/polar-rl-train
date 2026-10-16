"""Strict frozen-eval checks and lossless failed-prefix persistence; no action setters."""
from pathlib import Path
import os,json,time,hashlib
import numpy as np
def finite_arrays(arrays):
 for name,value in arrays.items():
  a=np.asarray(value)
  if a.dtype.kind in 'fc':assert np.isfinite(a).all(),('nonfinite',name)
def check_physics(h):
 finite_arrays(h['arrays']);assert np.isfinite(h['COM_frame_error_m']) and float(h['COM_frame_error_m'])<=1e-5
def check_control(row):
 finite_arrays(row);assert float(np.max(row['mimic']))<=.01 and float(np.max(row['post_reset_mimic']))<=.01
def declared_config(cfg):
 assert float(cfg.terminations.closure.params['threshold'])==.002
 old=float(cfg.terminations.mimic.params['threshold']);assert old>=.01
 cfg.terminations.mimic.params={**cfg.terminations.mimic.params,'threshold':.01}
 return dict(original_base_mimic_threshold=old,declared_eval_mimic_threshold=.01,closure_ordinary_selected_reset_threshold=.002,no_reward_physics_setter_or_actor_change=True)
def check_reasons(names):
 assert names and set(names)<=set(('time_out','bad_orientation','base_contact','closure','mimic','low_base','tunnel_roof_hit')),names
def save_failed_prefix(context,output,save):
 e=context.get('env');w=getattr(e,'_retention_native_witness',None) if e is not None else None
 if w is None:return dict(actual_witness_not_constructed_no_prefix_claim=True)
 arrays={};lengths={}
 for label,rows in (('control',w.rows),('physical',w.sub)):
  lengths[label]=len(rows)
  if not rows:continue
  shared=set.intersection(*(set(r) for r in rows))
  for key in sorted(shared):arrays[label+'_'+key]=np.stack([np.asarray(r[key]) for r in rows])
 p=Path(output)/'FAILED_VALID_PREFIX_ORIGINAL_ARRAYS.npz';assert not p.exists();tmp=p.with_suffix('.npz.partial')
 with tmp.open('xb') as f:np.savez_compressed(f,**arrays);f.flush();os.fsync(f.fileno())
 tmp.replace(p);v=dict(epoch=time.time(),raw=dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()),actual_control_rows=lengths['control'],actual_physics_rows=lengths['physical'],requested_controls=w.args.steps,not_full_requested_scope_pass=True,nonfinite_if_present_preserved_not_repaired=True,callback_coverage_not_inferred_from_requested_steps=True,phase_and_hardware_fields=[str(k) for k in arrays]);save('FAILED_VALID_PREFIX_ACTUAL.json',v);return v
