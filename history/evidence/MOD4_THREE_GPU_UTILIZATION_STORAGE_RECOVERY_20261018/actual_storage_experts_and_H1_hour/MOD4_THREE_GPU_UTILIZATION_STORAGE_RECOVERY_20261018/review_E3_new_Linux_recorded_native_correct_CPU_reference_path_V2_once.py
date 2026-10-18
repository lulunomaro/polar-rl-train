"""Resolve the existing CPU geometry reference's actual runtime path; do not rerun E2 or GPU."""
from pathlib import Path
import importlib.util,json,time,traceback,hashlib
B=Path(__file__).resolve().parent;R=B/'reports';p=B/'review_new_Linux_native_recorded_physics_reward_frames_CPU_once.py';sp=importlib.util.spec_from_file_location('native_CPU_functions_only_not_old_main',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);original=m.load_module
def resolved(name,p):
 p=Path(p)
 if not p.is_file() and p.name=='h1_authored_full_collider_plane_reference_v1.py':
  actual=p.parent/'frozen_shared/runtime/isaac/mod4'/p.name;assert actual.is_file();return original(name,actual)
 return original(name,p)
if __name__=='__main__':
 try:
  m.load_module=resolved;rng=m.torch.get_rng_state().clone();v=m.audit('E3');assert m.torch.equal(rng,m.torch.get_rng_state()) and not m.torch.cuda.is_initialized();v['old_CPU_reference_root_lookup_miss_retained_runtime_alias_only_fixed']=True
  with (R/'E3_LINUX_NATIVE120_RECORDED_PHYSICS_REWARD_CPU_V2_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
  print(json.dumps({k:v[k] for k in ('expert','passed_recorded_native_data_source_physics_CPU','actor_CPU_reference_maxabs','geometry_dual64_reference_maxabs','source_phase_available_fields_error','missing_original_internal_phase_fields','legacy_active_presence')}),flush=True)
 except BaseException:
  with (R/('E3_NEW_LINUX_NATIVE_CPU_V2_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay_or_threshold_change=True),f,indent=2)
  raise
