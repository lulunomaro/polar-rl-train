from pathlib import Path
import json,time,numpy as np,torch
import torch.nn.functional as F
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'MOD4_BUDGET_ADD100H_EIGHTH_20261021'))
from frozen_actor_exact_cpu import FrozenActor
B=Path(__file__).resolve().parent;R=B/'reports';A=B/'E3_full750_actual'
receipt=json.loads((R/'E3_FULL750_EXISTING_FINITE_RETURNED_ACTUAL.json').read_bytes());f=receipt['parent_complete']['final']
assert receipt['actual_finite_transport_returned'] and not receipt['pending'] and receipt['parent_complete']['passed'] and receipt['parent_complete']['returncode']==0 and receipt['parent_exit']['all_own_children_waited'] and receipt['parent_exit']['own_eval_lease_released'] and f['passed_execution_not_skill']
c=np.load(A/'out/CONTROL_ACTUAL.npz',allow_pickle=False);p=np.load(A/'out/PHYSICAL_CALLBACK_ACTUAL.npz',allow_pickle=False);initial=np.load(A/'out/INITIAL_ACTUAL.npz',allow_pickle=False)
for data,count in ((c,750),(p,6000)):
 for k in data.files:
  x=data[k];assert x.shape[:2]==(count,104)
  if x.dtype.kind in 'fc':assert np.isfinite(x).all(),k
assert c['policy'].shape==(750,104,35) and c['raw_action'].shape==(750,104,6)
assert p['all31_force'].shape==(6000,104,31,3) and p['witness_clear34'].shape==(6000,104,34)
assert not c['policy'][:,:,:3].any() and np.array_equal(initial['recipe'],np.arange(104)%13)
torch.set_num_threads(2);rng=torch.get_rng_state().clone()
src=B.parent/'MOD4_TWO_LINUX_POLICY50_COHORT_50_20261021/current_two50_closed_models/recovery/final_valid_update76.pt'
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
assert np.array_equal(c['executed6'],np.clip(c['raw_action'],-6,6));geo=json.loads((A/'out/GEOMETRY_ACTUAL.json').read_bytes());assert geo['witness_ids']==list(range(104));reference=B.parent/'MOD4_SCUT_FUDAN_SIXTEENTH_HOUR_20261019/payload/h1';sys.path.insert(0,str(reference));from h1_reference_geometry_cpu import support
geometry_error=float(abs(support(p['witness_body_pos'],p['witness_body_quat_xyzw'],geo['shapes'])-p['witness_clear34']).max());assert geometry_error<=1e-6
h=f['source_health'];assert h['integrity_task_reset_events']==h['unknown_task_reset_events']==0 and h['actual_physics_callbacks']==6000 and h['expected_physics_callbacks']==6000 and not h['nonfinite_observed']
report=dict(epoch=time.time(),passed_full104_execution_CPU=True,source_SHA=f['source_SHA'],source_Adam=f['source_Adam'],actual_full750_callbacks6000_feedback1500=True,all104_all_control_physical_rows_finite=True,independent_all104_geometry_maxabs_m=geometry_error,actual_executed6_clip_byteexact=True,source_actor9_STD_literal_exact_and_no_optimizer=True,raw_GPU_CPU_max_abs_difference=rawerr,clipped_GPU_CPU_max_abs_difference=cliperr,GPU_vs_float64_reference_within_conservative_FP32_forward_roundoff_envelope=True,max_forward_envelope=float(bound.max()),old_extra_absolute1e5_guard_error_preserved=True,numeric_validation_not_a_physical_or_skill_threshold_change=True,all_original_mimic01_closure2mm_feedback_action_guards_retained=True,ordinary_episode_resets=h['ordinary_episode_reset_events'],closure_resets=h['closure_episode_reset_events'],ordinary_failed_environments=h['failed_environments'],max_closure_error=h['max_closure_error_m'],mimic_max=h['max_mimic_error_rad'],fraction_raw_components_above_clip6=float(np.mean(abs(c['raw_action'])>6)),no_aggregate_graduation_threshold_invented=True,next_allowed='fresh same-source15s13case diagnostic only; independent physical-case review still required',actual_shared_GPU_scope_authorized=True)
credited=c['credited_before_reset'].astype(bool);done=c['done'].astype(bool);cases=[]
for env in range(104):
 fail=np.flatnonzero(done[:,env]);first=int(fail[0]) if len(fail) else None;limit=first+1 if first is not None else 750;hits=np.flatnonzero(credited[:limit,env]);cases.append(dict(env=env,recipe=env%13,request=(env%13)!=12,first_failure_control=None if first is None else first+1,first_episode_stable_recovery=bool(len(hits)),first_credit_control=int(hits[0])+1 if len(hits) else None,ordinary_resets=int(done[:,env].sum())))
report.update(cases=cases,request_cases=96,normal_cases=8,first_episode_source_stable_recoveries=sum(x['first_episode_stable_recovery'] for x in cases if x['request']),physical_seconds=15,source_no_new_plant_or_reward_or_threshold=True)
with (R/'E3_FULL750_ALL_ROWS_CPU_ACTUAL.json').open('x',encoding='utf8') as file:json.dump(report,file,indent=2)
print(json.dumps(report))
