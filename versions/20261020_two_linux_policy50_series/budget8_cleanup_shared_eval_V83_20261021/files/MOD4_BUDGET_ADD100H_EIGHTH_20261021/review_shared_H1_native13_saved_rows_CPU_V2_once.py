from pathlib import Path
import json,time,numpy as np,torch
import torch.nn.functional as F
from frozen_actor_exact_cpu import FrozenActor
B=Path(__file__).resolve().parent;R=B/'reports';A=B/'shared_H1_native13_V3_actual'
receipt=json.loads((R/'SHARED_H1_NATIVE13_V3_FINITE_RETURNED_ACTUAL.json').read_bytes());f=receipt['final']
assert receipt['actual_child_waited'] and receipt['actual_returncode']==0 and receipt['own_eval_lock_released'] and not receipt['original_error_paths'] and f['passed_diagnostic_execution']
c=np.load(A/'out/CONTROL_ACTUAL.npz',allow_pickle=False);p=np.load(A/'out/PHYSICAL_CALLBACK_ACTUAL.npz',allow_pickle=False);initial=np.load(A/'out/INITIAL_ACTUAL.npz',allow_pickle=False)
for data,count in ((c,60),(p,480)):
 for k in data.files:
  x=data[k];assert x.shape[:2]==(count,13)
  if x.dtype.kind in 'fc':assert np.isfinite(x).all(),k
assert c['policy'].shape==(60,13,35) and c['raw_action'].shape==(60,13,6)
assert p['all31_force'].shape==(480,13,31,3) and p['witness_clear34'].shape==(480,13,34)
assert not c['policy'][:,:,:3].any() and np.array_equal(initial['recipe'],np.arange(13))
torch.set_num_threads(2);rng=torch.get_rng_state().clone()
src=B.parent/'MOD4_TWO_LINUX_POLICY50_COHORT_48_20261021/current_two50_closed_models/recovery/final_valid_update77.pt'
actor=FrozenActor(src,f['source_SHA'],f['source_Adam'])
ref=torch.from_numpy(c['policy'].copy()).reshape(-1,35).double();bound=torch.zeros_like(ref);eps=torch.finfo(torch.float32).eps
for n in (0,2,4,6):
 w=actor.weights[f'mlp.{n}.weight'].double();b=actor.weights[f'mlp.{n}.bias'].double();length=w.shape[1]+1;gamma=length*eps/(1-length*eps)
 bound=F.linear(bound,w.abs())+gamma*F.linear(ref.abs(),w.abs(),b.abs())
 ref=F.linear(ref,w,b)
 if n!=6:
  ref=F.elu(ref);bound+=8*eps*torch.maximum(torch.ones_like(ref),ref.abs())
gpu=torch.from_numpy(c['raw_action'].copy()).reshape(-1,6).double();error=(gpu-ref).abs();assert bool((error<=bound+1e-12).all())
same_batch=np.stack([actor.mean(torch.from_numpy(x.copy())).numpy() for x in c['policy']]);rawerr=float(abs(same_batch-c['raw_action']).max());cliperr=float(abs(np.clip(same_batch,-6,6)-np.clip(c['raw_action'],-6,6)).max())
assert actor.exact() and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
h=f['source_health'];assert h['integrity_task_reset_events']==h['unknown_task_reset_events']==0 and h['actual_physics_callbacks']==480 and h['expected_physics_callbacks']==480 and not h['nonfinite_observed']
report=dict(epoch=time.time(),passed_small_diagnostic_native_CPU=True,source_SHA=f['source_SHA'],source_Adam=f['source_Adam'],actual_native60_callbacks480_feedback120=True,all13_all_control_physical_rows_finite=True,source_actor9_STD_literal_exact_and_no_optimizer=True,raw_GPU_CPU_max_abs_difference=rawerr,clipped_GPU_CPU_max_abs_difference=cliperr,GPU_vs_float64_reference_within_conservative_FP32_forward_roundoff_envelope=True,max_forward_envelope=float(bound.max()),old_extra_absolute1e5_guard_error_preserved=True,numeric_validation_not_a_physical_or_skill_threshold_change=True,all_original_mimic01_closure2mm_feedback_action_guards_retained=True,ordinary_episode_resets=h['ordinary_episode_reset_events'],closure_resets=h['closure_episode_reset_events'],ordinary_failed_environments=h['failed_environments'],max_closure_error=h['max_closure_error_m'],mimic_max=h['max_mimic_error_rad'],fraction_raw_components_above_clip6=float(np.mean(abs(c['raw_action'])>6)),not_skill_or_full104_native_qualification=True,next_allowed='fresh same-source15s13case diagnostic only; independent physical-case review still required',actual_shared_GPU_scope_authorized=True)
with (R/'SHARED_H1_NATIVE13_V3_ALL_ROWS_CPU_V2_ACTUAL.json').open('x',encoding='utf8') as file:json.dump(report,file,indent=2)
print(json.dumps(report))
